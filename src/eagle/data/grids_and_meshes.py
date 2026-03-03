import logging
from collections.abc import Iterator
from contextlib import contextmanager
from functools import cache
from pathlib import Path
from threading import Lock

import cf_xarray as cfxr
import numpy as np
import xesmf  # type: ignore[import-untyped]
from anemoi.graphs.generate.utils import (  # type: ignore[import-untyped]
    get_coordinates_ordering,
)
from anemoi.transform.spatial import cutout_mask  # type: ignore[import-untyped]
from iotaa import Asset, collection, task
from ufs2arco import sources  # type: ignore[import-untyped]
from uwtools.api.driver import AssetsTimeInvariant
from xarray import Dataset

LOCK = Lock()


class GridsAndMeshes(AssetsTimeInvariant):
    """
    Prepares grids and meshes.
    """

    # Public tasks

    @task
    def combined_global_and_conus_meshes(self):
        """
        The combined global and CONUS meshes, provisioned to the rundir.
        """
        path = self.rundir / self.config["filenames"]["combined_grids"]
        yield self.taskname(f"combined global and conus meshes {path}")
        yield Asset(path, path.is_file)
        yield None
        path.parent.mkdir(parents=True, exist_ok=True)
        gmesh = _global_latent_grid()
        cmesh = _conus_latent_grid(
            _conus_data_grid(self.rundir, self._conus_data_grid_logfile)
        )
        coords = _combined_global_and_conus_meshes(gmesh, cmesh)
        np.savez(path, lon=coords["lon"], lat=coords["lat"])

    @task
    def conus_data_grid(self):
        """
        The CONUS grid, provisioned to the rundir.
        """
        path = self.rundir / self.config["filenames"]["hrrr_target_grid"]
        yield self.taskname(f"conus data grid {path}")
        yield Asset(path, path.is_file)
        yield None
        path.parent.mkdir(parents=True, exist_ok=True)
        _conus_data_grid(self.rundir, self._conus_data_grid_logfile).to_netcdf(path)

    @task
    def global_data_grid(self):
        """
        The global grid, provisioned to the rundir.
        """
        path = self.rundir / self.config["filenames"]["gfs_target_grid"]
        yield self.taskname(f"global data grid {path}")
        yield Asset(path, path.is_file)
        yield None
        path.parent.mkdir(parents=True, exist_ok=True)
        ds = xesmf.util.grid_global(1, 1, cf=True, lon1=360)
        ds = ds.drop_vars("latitude_longitude")
        ds = ds.sortby("lat", ascending=False)  # GFS goes north -> south
        ds.to_netcdf(path)

    @collection
    def provisioned_rundir(self):
        """
        Run directory provisioned with all required content.
        """
        yield self.taskname("provisioned run directory")
        yield [
            self.combined_global_and_conus_meshes(),
            self.conus_data_grid(),
            self.global_data_grid(),
        ]

    # Public methods

    @classmethod
    def driver_name(cls) -> str:
        return "grids_and_meshes"

    # Private methods

    @property
    def _conus_data_grid_logfile(self):
        return (self.rundir / self.config["filenames"]["hrrr_target_grid"]).with_suffix(
            ".log"
        )


# Private functions


def _combined_global_and_conus_meshes(
    gmesh: Dataset, cmesh: Dataset
) -> dict[str, np.ndarray]:
    glon, glat = np.meshgrid(gmesh["lon"], gmesh["lat"])
    mask = cutout_mask(
        lats=cmesh["lat"].values.flatten(),
        lons=cmesh["lon"].values.flatten(),
        global_lats=glat.flatten(),
        global_lons=glon.flatten(),
        min_distance_km=0,
    )
    # Combine.
    lon = np.concatenate([glon.flatten()[mask], cmesh["lon"].values.flatten()])
    lat = np.concatenate([glat.flatten()[mask], cmesh["lat"].values.flatten()])
    # Sort, following exactly what anemoi-graphs does for the data.
    coords = np.stack([lon, lat], axis=-1)
    order = get_coordinates_ordering(coords)
    lon = coords[order, 0]
    lat = coords[order, 1]
    return {"lon": lon, "lat": lat}


@cache
def _conus_data_grid(rundir: Path, logfile: Path) -> Dataset:
    with LOCK:
        with _logging_to_file(logfile):
            hrrr = sources.AWSHRRRArchive(
                t0={"start": "2015-01-15T00", "end": "2015-01-15T06", "freq": "6h"},
                fhr={"start": 0, "end": 0, "step": 6},
                variables=["orog"],
            )
        hds = hrrr.open_sample_dataset(
            dims={"t0": hrrr.t0[0], "fhr": hrrr.fhr[0]},
            open_static_vars=True,
            cache_dir=str(rundir / "cache" / "conus-data-grid"),
        )
        hds = hds.rename({"latitude": "lat", "longitude": "lon"})
        # Get bounds as vertices.
        hds = hds.cf.add_bounds(["lat", "lon"])
        for key in ["lat", "lon"]:
            corners = cfxr.bounds_to_vertices(
                bounds=hds[f"{key}_bounds"],
                bounds_dim="bounds",
                order=None,
            )
            hds = hds.assign_coords({f"{key}_b": corners})
            hds = hds.drop_vars(f"{key}_bounds")
        hds = hds.rename({"x_vertices": "x_b", "y_vertices": "y_b"})
        # Get the nodes and bounds by subsampling.
        hds = hds.isel(
            x=slice(None, -4, None),
            y=slice(None, -4, None),
            x_b=slice(None, -4, None),
            y_b=slice(None, -4, None),
        )
        cds: Dataset = hds.isel(
            x=slice(2, None, 5),
            y=slice(2, None, 5),
            x_b=slice(0, None, 5),
            y_b=slice(0, None, 5),
        )
        return cds.drop_vars("orog")


def _conus_latent_grid(cds: Dataset, trim: int = 10, coarsen: int = 2) -> Dataset:
    mesh = cds[["lat_b", "lon_b"]].isel(
        x_b=slice(trim, -trim - 1, coarsen),
        y_b=slice(trim, -trim - 1, coarsen),
    )
    return mesh.rename(
        {
            "lat_b": "lat",
            "lon_b": "lon",
            "x_b": "x",
            "y_b": "y",
        }
    )


def _global_latent_grid() -> Dataset:
    """
    For the high-res version, this will process the original grid. However, since the
    data grid is on an xESMF generated grid, it works out just fine to generate another
    xESMF grid here.
    """
    mesh: Dataset = xesmf.util.grid_global(2, 2, cf=True, lon1=360)
    return mesh.drop_vars("latitude_longitude")


@contextmanager
def _logging_to_file(path: Path) -> Iterator:
    logger = logging.getLogger()
    stream_handler = logger.handlers[0]
    logger.removeHandler(stream_handler)
    file_handler = logging.FileHandler(path)
    logger.addHandler(file_handler)
    yield
    logger.removeHandler(file_handler)
    logger.addHandler(stream_handler)

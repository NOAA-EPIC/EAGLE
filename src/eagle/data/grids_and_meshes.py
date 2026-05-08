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
from iotaa import Asset, collection, task  # provided by uwtools
from ufs2arco import sources  # type: ignore[import-untyped]
from uwtools.api.driver import AssetsTimeInvariant
from xarray import Dataset
import xarray as xr

LOCK = Lock()


class GridsAndMeshes(AssetsTimeInvariant):
    """
    Prepares grids and meshes.
    """

    # Public tasks

    @task
    def conus_data_grid(self):
        """
        The CONUS grid, provisioned to the rundir.
        """
        if "hrrr_target_grid" not in self.config.get("filenames", {}):
            return
        res = self.config["conus_grid_resolution_km"]
        if res == 3:
            return
        path = self.rundir / self.config["filenames"]["hrrr_target_grid"]
        yield self.taskname(f"conus data grid {path}")
        yield Asset(path, path.is_file)
        yield None
        path.parent.mkdir(parents=True, exist_ok=True)
        _conus_data_grid(self.rundir, self._conus_data_grid_logfile, res).to_netcdf(
            path
        )

    @task
    def global_data_grid(self):
        """
        The global grid, provisioned to the rundir.
        """
        if "gfs_target_grid" not in self.config.get("filenames", {}):
            return
        resolution = self.config["global_grid_resolution_deg"]
        if resolution == 0.25:
            return
        path = self.rundir / self.config["filenames"]["gfs_target_grid"]
        yield self.taskname(f"global data grid {path}")
        yield Asset(path, path.is_file)
        yield None
        path.parent.mkdir(parents=True, exist_ok=True)
        ds = xesmf.util.grid_global(resolution, resolution, cf=True, lon1=360)
        ds = ds.drop_vars("latitude_longitude")
        ds = ds.sortby("lat", ascending=False)  # GFS goes north -> south
        ds.to_netcdf(path)

    @task
    def latent_mesh(self):
        """
        The latent mesh, provisioned to the rundir.
        """
        if "latent_mesh" not in self.config.get("filenames", {}):
            return
        path = self.rundir / self.config["filenames"]["latent_mesh"]
        yield self.taskname(f"latent mesh {path}")
        yield Asset(path, path.is_file)
        yield None
        path.parent.mkdir(parents=True, exist_ok=True)
        res = self.config["conus_grid_resolution_km"]
        gmesh = _global_latent_grid(self.config["latent_mesh_global_resolution_deg"])
        cmesh = _conus_latent_grid(
            _conus_data_grid(self.rundir, self._conus_data_grid_logfile, res),
            coarsen=self.config["latent_mesh_conus_coarsen_factor"],
        )
        coords = _combine_global_and_conus_meshes(gmesh, cmesh)
        np.savez(path, lon=coords["lon"], lat=coords["lat"])

    @collection
    def provisioned_rundir(self):
        """
        Run directory provisioned with all required content.
        """
        yield self.taskname("provisioned run directory")
        tasks = []

        if "hrrr_target_grid" in self.config.get("filenames", {}):
            tasks.append(self.conus_data_grid())

        if "gfs_target_grid" in self.config.get("filenames", {}):
            tasks.append(self.global_data_grid())

        if "latent_mesh" in self.config.get("filenames", {}):
            tasks.append(self.latent_mesh())

        yield tasks

    # Public methods

    @classmethod
    def driver_name(cls) -> str:
        return "grids_and_meshes"

    # Private methods

    @property
    def _conus_data_grid_logfile(self):
        if "hrrr_target_grid" in self.config.get("filenames", {}):
            return (
                self.rundir / self.config["filenames"]["hrrr_target_grid"]
            ).with_suffix(".log")
        else:
            return self.rundir / "hrrr_target_grid.log"


# Private functions


def _combine_global_and_conus_meshes(
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
def _conus_data_grid(rundir: Path, logfile: Path, resolution_km: int = 15) -> Dataset:
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

        stride = resolution_km // 3
        # Get the nodes and bounds by subsampling.
        trim = stride - 1
        if trim > 0:
            hds = hds.isel(
                x=slice(None, -trim),
                y=slice(None, -trim),
                x_b=slice(None, -trim),
                y_b=slice(None, -trim),
            )
        if stride % 2 == 1:
            # Odd stride: centers align with original centers (e.g. 15km, stride=5)
            cds = hds.isel(
                x=slice(stride // 2, None, stride),
                y=slice(stride // 2, None, stride),
                x_b=slice(0, None, stride),
                y_b=slice(0, None, stride),
            ).drop_vars("orog")
        else:
            # Even stride: centers align with original vertices (e.g. 6km, stride=2)
            centers = hds.isel(
                x_b=slice(stride // 2, None, stride),
                y_b=slice(stride // 2, None, stride),
            )
            centers = centers.drop_vars(["lat", "lon", "orog"]).rename(
                {"lat_b": "lat", "lon_b": "lon", "x_b": "x", "y_b": "y"}
            )
            bounds = hds.isel(x_b=slice(0, None, stride), y_b=slice(0, None, stride))
            cds = xr.merge([centers, bounds.drop_vars(["lat", "lon", "orog"])])
        return cds


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


def _global_latent_grid(resolution_deg: float) -> Dataset:
    """
    For the high-res version, this will process the original grid. However, since the
    data grid is on an xESMF generated grid, it works out just fine to generate another
    xESMF grid here.
    """
    mesh: Dataset = xesmf.util.grid_global(resolution_deg, resolution_deg, cf=True, lon1=360)
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

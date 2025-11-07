# Filename: create_grids.py
# Author: Tim Smith, NOAA PSL
# Description: Creation of target grids required for data processing and model training.

import xesmf
import cf_xarray as cfxr
import numpy as np

from ufs2arco import sources

from anemoi.datasets.grids import cutout_mask
from anemoi.graphs.generate.utils import get_coordinates_ordering


def get_global_data_grid():
    ds = xesmf.util.grid_global(1, 1, cf=True, lon1=360)
    ds = ds.drop_vars("latitude_longitude")

    # GFS goes north -> south
    ds = ds.sortby("lat", ascending=False)
    return ds


def get_conus_data_grid():
    hrrr = sources.AWSHRRRArchive(
        t0={"start": "2015-01-15T00", "end": "2015-01-15T06", "freq": "6h"},
        fhr={"start": 0, "end": 0, "step": 6},
        variables=["orog"],
    )
    hds = hrrr.open_sample_dataset(
        dims={"t0": hrrr.t0[0], "fhr": hrrr.fhr[0]},
        open_static_vars=True,
        cache_dir="cache/grid-creation",
    )
    hds = hds.rename({"latitude": "lat", "longitude": "lon"})

    # Get bounds as vertices
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

    # Get the nodes and bounds by subsampling carefully...
    # see notebooks
    hds = hds.isel(
        x=slice(None, -4, None),
        y=slice(None, -4, None),
        x_b=slice(None, -4, None),
        y_b=slice(None, -4, None),
    )
    chds = hds.isel(
        x=slice(2, None, 5),
        y=slice(2, None, 5),
        x_b=slice(0, None, 5),
        y_b=slice(0, None, 5),
    )
    chds = chds.drop_vars("orog")
    return chds


def get_global_latent_grid():
    """For the high rez version, this will process the original grid.
    However, since the data grid is on an xesmf generated grid, it works out just fine to
    generate another xesmf grid here.
    """

    mesh = xesmf.util.grid_global(2, 2, cf=True, lon1=360)
    mesh = mesh.drop_vars("latitude_longitude")
    return mesh


def get_conus_latent_grid(xds, trim=10, coarsen=2):
    mesh = xds[["lat_b", "lon_b"]].isel(
        x_b=slice(trim, -trim - 1, coarsen),
        y_b=slice(trim, -trim - 1, coarsen),
    )
    mesh = mesh.rename(
        {
            "lat_b": "lat",
            "lon_b": "lon",
            "x_b": "x",
            "y_b": "y",
        }
    )
    return mesh


def combine_global_and_conus_meshes(gds, cds):
    glon, glat = np.meshgrid(gmesh["lon"], gmesh["lat"])
    mask = cutout_mask(
        lats=cds["lat"].values.flatten(),
        lons=cds["lon"].values.flatten(),
        global_lats=glat.flatten(),
        global_lons=glon.flatten(),
        min_distance_km=0,
    )

    # combined
    lon = np.concatenate([glon.flatten()[mask], cds["lon"].values.flatten()])
    lat = np.concatenate([glat.flatten()[mask], cds["lat"].values.flatten()])

    # sort, following exactly what anemoi graphs does for the data
    coords = np.stack([lon, lat], axis=-1)
    order = get_coordinates_ordering(coords)
    lon = coords[order, 0]
    lat = coords[order, 1]
    return {"lon": lon, "lat": lat}


if __name__ == "__main__":
    # Data grids
    gds = get_global_data_grid()
    gds.to_netcdf("global_one_degree.nc")

    cds = get_conus_data_grid()
    cds.to_netcdf("hrrr_15km.nc")

    # Latent meshes
    gmesh = get_global_latent_grid()
    cmesh = get_conus_latent_grid(xds=cds)
    coords = combine_global_and_conus_meshes(gmesh, cmesh)
    np.savez(
        "latentx2.spongex1.combined.sorted.npz",
        lon=coords["lon"],
        lat=coords["lat"],
    )

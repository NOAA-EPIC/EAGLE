from pathlib import Path
from unittest.mock import patch

import numpy as np
import xarray as xr
from pytest import fixture, mark

from . import grids_and_meshes
from .grids_and_meshes import GridsAndMeshes


@fixture
def config(tmp_path):
    return {
        "grids_and_meshes": {
            "filenames": {
                "gfs_target_grid": "%s/global_one_degree.nc" % tmp_path,
                "hrrr_target_grid": "%s/hrrr_15km.nc" % tmp_path,
                "latent_mesh": "%s/latentx2.spongex1.combined.sorted.npz" % tmp_path,
            },
            "conus_grid_resolution_km": 15,
            "global_grid_resolution_deg": 1.0,
            "latent_mesh_global_resolution_deg": 2.0,
            "latent_mesh_conus_coarsen_factor": 2,
            "rundir": "%s/rundir" % tmp_path,
        }
    }


@fixture
def dataset():
    data = np.arange(150000).reshape((300, 500))
    return xr.Dataset(
        data_vars={
            "latitude": (["y", "x"], data),
            "longitude": (["y", "x"], data),
            "orog": (["y", "x"], data),
        }
    )


@fixture
def driverobj(config):
    return GridsAndMeshes(
        config=config, schema_file=Path(__file__).parent / "grids_and_meshes.jsonschema"
    )


@fixture
def hrrr_target_grid(driverobj):
    return driverobj.rundir / driverobj.config["filenames"]["hrrr_target_grid"]


# Driver tests.


def test_conus_data_grid(dataset, driverobj, hrrr_target_grid):
    assert not hrrr_target_grid.exists()
    with patch.object(grids_and_meshes, "_conus_data_grid") as _conus_data_grid:
        _conus_data_grid.return_value = dataset
        task = driverobj.conus_data_grid()
    assert hrrr_target_grid.is_file()
    assert task.ready


def test_conus_data_grid__bad_res(driverobj, hrrr_target_grid):
    driverobj._config["conus_grid_resolution_km"] = 3
    task = driverobj.conus_data_grid()
    assert task.ready
    assert not hrrr_target_grid.exists()


def test_conus_data_grid__bad_filenames(driverobj, hrrr_target_grid):
    driverobj._config["filenames"] = {}
    task = driverobj.conus_data_grid()
    assert task.ready
    assert not hrrr_target_grid.exists()


@mark.parametrize("resolution_km", [None, 3, 60])
def test__conus_data_grid(dataset, resolution_km, tmp_path):
    logfile = tmp_path / "logfile"
    with patch.object(grids_and_meshes.sources, "AWSHRRRArchive") as AWSHRRRArchive:  # noqa: N806
        AWSHRRRArchive().open_sample_dataset.return_value = dataset
        args = {"rundir": tmp_path, "logfile": logfile}
        if resolution_km:
            args["resolution_km"] = resolution_km
        cds = grids_and_meshes._conus_data_grid(**args)
        AWSHRRRArchive.assert_called()
        AWSHRRRArchive().open_sample_dataset.assert_called_once()
        shape = {None: (59, 99), 3: (300, 500), 60: (14, 24)}[resolution_km]
        assert cds.lat.shape == cds.lon.shape == shape


# Schema tests.


def test_top(config, logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "grids_and_meshes", tmp_path)
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["grids_and_meshes"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have object values:
    for key in ["grids_and_meshes"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")


def test_grids_and_meshes(config, logged, tmp_path, validator, with_del, with_set):
    ok = validator(
        __file__, "grids_and_meshes", tmp_path, "properties", "grids_and_meshes"
    )
    config = config["grids_and_meshes"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are not allowed:
    assert not ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in [
        "conus_grid_resolution_km",
        "filenames",
        "global_grid_resolution_deg",
        "rundir",
    ]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have object values:
    for key in ["filenames"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")
    # Some keys have string values:
    for key in ["rundir"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")


def test_grids_and_meshes__conus_grid_resolution_km(logged, tmp_path, validator):
    ok = validator(
        __file__,
        "grids_and_meshes",
        tmp_path,
        "properties",
        "grids_and_meshes",
        "properties",
        "conus_grid_resolution_km",
    )
    # Basic correctness:
    assert ok(6)
    assert ok(15)
    # Invalid values:
    assert not ok(4)
    assert logged("is not a multiple of 3")
    assert not ok(1)
    assert logged("is less than the minimum of 3")
    assert not ok("6")
    assert logged("is not of type 'integer'")


def test_grids_and_meshes__global_grid_resolution_deg(logged, tmp_path, validator):
    ok = validator(
        __file__,
        "grids_and_meshes",
        tmp_path,
        "properties",
        "grids_and_meshes",
        "properties",
        "global_grid_resolution_deg",
    )
    # Basic correctness:
    assert ok(0.25)
    assert ok(1.0)
    # Invalid values:
    assert not ok(2.0)
    assert logged(r"is not one of \[0.25, 1.0\]")
    assert not ok("1.0")
    assert logged("is not of type 'number'")


def test_grids_and_meshes__latent_mesh_global_resolution_deg(
    logged, tmp_path, validator
):
    ok = validator(
        __file__,
        "grids_and_meshes",
        tmp_path,
        "properties",
        "grids_and_meshes",
        "properties",
        "latent_mesh_global_resolution_deg",
    )
    # Basic correctness:
    assert ok(2.0)
    # Invalid values:
    assert not ok(0.0)
    assert logged("is less than or equal to the minimum of 0")
    assert not ok(-1.0)
    assert logged("is less than or equal to the minimum of 0")
    assert not ok("2.0")
    assert logged("is not of type 'number'")


def test_grids_and_meshes__latent_mesh_conus_coarsen_factor(
    logged, tmp_path, validator
):
    ok = validator(
        __file__,
        "grids_and_meshes",
        tmp_path,
        "properties",
        "grids_and_meshes",
        "properties",
        "latent_mesh_conus_coarsen_factor",
    )
    # Basic correctness:
    assert ok(1)
    assert ok(2)
    # Invalid values:
    assert not ok(0)
    assert logged("is less than the minimum of 1")
    assert not ok(1.5)
    assert logged("is not of type 'integer'")


def test_grids_and_meshes__filenames(
    config, logged, tmp_path, validator, with_del, with_set
):
    ok = validator(
        __file__,
        "grids_and_meshes",
        tmp_path,
        "properties",
        "grids_and_meshes",
        "properties",
        "filenames",
    )
    config = config["grids_and_meshes"]["filenames"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are not allowed:
    assert not ok(with_set(config, "foo", "bar"))
    # Optional keys:
    for key in ["gfs_target_grid", "hrrr_target_grid", "latent_mesh"]:
        assert ok(with_del(config, key))
    # Some keys have string values:
    for key in ["gfs_target_grid", "hrrr_target_grid", "latent_mesh"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")


def test_grids_and_meshes__latent_mesh_settings_conditional_required(
    config, logged, tmp_path, validator, with_del, with_set
):
    ok = validator(
        __file__, "grids_and_meshes", tmp_path, "properties", "grids_and_meshes"
    )
    config = config["grids_and_meshes"]
    # If latent mesh is requested, latent mesh settings are required.
    assert not ok(with_del(config, "latent_mesh_global_resolution_deg"))
    assert logged("'latent_mesh_global_resolution_deg' is a required property")
    assert not ok(with_del(config, "latent_mesh_conus_coarsen_factor"))
    assert logged("'latent_mesh_conus_coarsen_factor' is a required property")
    # If latent mesh is not requested, latent mesh settings may be omitted.
    filenames_without_latent_mesh = with_del(config["filenames"], "latent_mesh")
    config_without_latent_mesh = with_set(
        config, filenames_without_latent_mesh, "filenames"
    )
    assert ok(with_del(config_without_latent_mesh, "latent_mesh_global_resolution_deg"))
    assert ok(with_del(config_without_latent_mesh, "latent_mesh_conus_coarsen_factor"))

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
def gfs_target_grid(driverobj):
    return driverobj.rundir / driverobj.config["filenames"]["gfs_target_grid"]


@fixture
def hrrr_target_grid(driverobj):
    return driverobj.rundir / driverobj.config["filenames"]["hrrr_target_grid"]


# Driver tests.


def test_conus_data_grid(dataset, driverobj, hrrr_target_grid):
    assert not hrrr_target_grid.exists()
    with patch.object(grids_and_meshes, "_conus_data_grid") as _conus_data_grid:
        _conus_data_grid.return_value = dataset
        assert driverobj.conus_data_grid().ready
    assert hrrr_target_grid.is_file()


def test_conus_data_grid__bad_filenames(driverobj, hrrr_target_grid):
    driverobj._config["filenames"] = {}
    assert driverobj.conus_data_grid().ready
    assert not hrrr_target_grid.exists()


def test_conus_data_grid__bad_res(driverobj, hrrr_target_grid):
    driverobj._config["conus_grid_resolution_km"] = 3
    assert driverobj.conus_data_grid().ready
    assert not hrrr_target_grid.exists()


def test_driver_name():
    assert GridsAndMeshes.driver_name() == "grids_and_meshes"


def test_global_data_grid(driverobj, gfs_target_grid):
    assert not gfs_target_grid.exists()
    assert driverobj.global_data_grid().ready
    assert gfs_target_grid.is_file()


def test_global_data_grid__bad_filenames(driverobj, gfs_target_grid):
    driverobj._config["filenames"] = {}
    assert driverobj.global_data_grid().ready
    assert not gfs_target_grid.exists()


def test_global_data_grid__bad_res(driverobj, gfs_target_grid):
    driverobj._config["global_grid_resolution_deg"] = 0.25
    assert driverobj.global_data_grid().ready
    assert not gfs_target_grid.exists()


def test_latent_mesh(driverobj):
    path = driverobj.rundir / driverobj.config["filenames"]["latent_mesh"]
    assert not path.exists()
    coords = {"lat": np.array([3.0, 4.0]), "lon": np.array([1.0, 2.0])}
    with (
        patch.object(grids_and_meshes, "_global_latent_grid"),
        patch.object(grids_and_meshes, "_conus_data_grid"),
        patch.object(grids_and_meshes, "_conus_latent_grid"),
        patch.object(
            grids_and_meshes, "_combine_global_and_conus_meshes", return_value=coords
        ),
    ):
        assert driverobj.latent_mesh().ready
    assert path.is_file()


def test_latent_mesh__bad_filenames(driverobj):
    path = driverobj.rundir / driverobj.config["filenames"]["latent_mesh"]
    driverobj._config["filenames"] = {}
    assert driverobj.latent_mesh().ready
    assert not path.exists()


@mark.parametrize(
    "remove",
    [
        [],
        ["hrrr_target_grid"],
        ["gfs_target_grid"],
        ["latent_mesh"],
        ["hrrr_target_grid", "gfs_target_grid", "latent_mesh"],
    ],
)
def test_provisioned_rundir(driverobj, readytask, remove):
    for key in remove:
        del driverobj._config["filenames"][key]
    with patch.multiple(
        driverobj,
        conus_data_grid=readytask,
        global_data_grid=readytask,
        latent_mesh=readytask,
    ):
        assert driverobj.provisioned_rundir().ready


def test__combine_global_and_conus_meshes():
    gmesh = xr.Dataset({"lat": ("lat", [0.0, 1.0]), "lon": ("lon", [0.0, 1.0])})
    cmesh = xr.Dataset({"lat": (["y", "x"], [[20.0]]), "lon": (["y", "x"], [[10.0]])})
    mask = np.array([True, True, False, False])
    order = np.array([2, 0, 1])
    with (
        patch.object(grids_and_meshes, "cutout_mask", return_value=mask),
        patch.object(grids_and_meshes, "get_coordinates_ordering", return_value=order),
    ):
        result = grids_and_meshes._combine_global_and_conus_meshes(gmesh, cmesh)
    np.testing.assert_array_equal(result["lat"], [20.0, 0.0, 0.0])
    np.testing.assert_array_equal(result["lon"], [10.0, 0.0, 1.0])


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


def test__conus_data_grid_logfile(driverobj):
    assert driverobj._conus_data_grid_logfile == (
        driverobj.rundir / driverobj.config["filenames"]["hrrr_target_grid"]
    ).with_suffix(".log")


def test__conus_data_grid_logfile__no_hrrr(driverobj):
    del driverobj._config["filenames"]["hrrr_target_grid"]
    assert (
        driverobj._conus_data_grid_logfile == driverobj.rundir / "hrrr_target_grid.log"
    )


def test__conus_latent_grid():
    ny, nx = 100, 200
    cds = xr.Dataset(
        {
            "lat_b": (["y_b", "x_b"], np.zeros((ny, nx))),
            "lon_b": (["y_b", "x_b"], np.zeros((ny, nx))),
        }
    )
    result = grids_and_meshes._conus_latent_grid(cds)
    assert result.lat.shape == result.lon.shape == (40, 90)


def test__global_latent_grid():
    result = grids_and_meshes._global_latent_grid(2.0)
    assert "latitude_longitude" not in result
    assert result.lat.shape == (90,)
    assert result.lon.shape == (180,)


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


def test_grids_and_meshes__conus_grid_settings_conditional_required(
    config, logged, tmp_path, validator, with_del, with_set
):
    ok = validator(
        __file__, "grids_and_meshes", tmp_path, "properties", "grids_and_meshes"
    )
    config = config["grids_and_meshes"]
    # If HRRR target grid is requested, the CONUS resolution is required.
    assert not ok(with_del(config, "conus_grid_resolution_km"))
    assert logged("'conus_grid_resolution_km' is a required property")
    # If no CONUS grid or latent mesh is requested, CONUS resolution may be omitted.
    filenames = with_del(config["filenames"], "hrrr_target_grid")
    filenames = with_del(filenames, "latent_mesh")
    config_without_conus_outputs = with_set(config, filenames, "filenames")
    config_without_conus_outputs = with_del(
        config_without_conus_outputs, "latent_mesh_global_resolution_deg"
    )
    config_without_conus_outputs = with_del(
        config_without_conus_outputs, "latent_mesh_conus_coarsen_factor"
    )
    assert ok(with_del(config_without_conus_outputs, "conus_grid_resolution_km"))


def test_grids_and_meshes__latent_mesh_settings_conditional_required(
    config, logged, tmp_path, validator, with_del, with_set
):
    ok = validator(
        __file__, "grids_and_meshes", tmp_path, "properties", "grids_and_meshes"
    )
    config = config["grids_and_meshes"]
    filenames_without_hrrr = with_del(config["filenames"], "hrrr_target_grid")
    config = with_set(config, filenames_without_hrrr, "filenames")
    # If latent mesh is requested, latent mesh settings are required.
    assert not ok(with_del(config, "conus_grid_resolution_km"))
    assert logged("'conus_grid_resolution_km' is a required property")
    assert not ok(with_del(config, "latent_mesh_global_resolution_deg"))
    assert logged("'latent_mesh_global_resolution_deg' is a required property")
    assert not ok(with_del(config, "latent_mesh_conus_coarsen_factor"))
    assert logged("'latent_mesh_conus_coarsen_factor' is a required property")
    # If latent mesh is not requested, CONUS/latent settings may be omitted.
    filenames_without_latent_mesh = with_del(config["filenames"], "latent_mesh")
    config_without_latent_mesh = with_set(
        config, filenames_without_latent_mesh, "filenames"
    )
    assert ok(with_del(config_without_latent_mesh, "conus_grid_resolution_km"))
    assert ok(with_del(config_without_latent_mesh, "latent_mesh_global_resolution_deg"))
    assert ok(with_del(config_without_latent_mesh, "latent_mesh_conus_coarsen_factor"))

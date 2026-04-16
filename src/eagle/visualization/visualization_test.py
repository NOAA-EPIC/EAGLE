from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import call, patch

import xarray as xr
from iotaa import Asset, task
from pytest import fixture, mark

from . import visualization
from .visualization import Visualization


@fixture
def config():
    return {
        "visualization": {
            "eagle_tools": {
                "end_date": "2026-04-08T12:00:00",
                "freq": "6h",
                "leadtimes": {
                    "start": 0,
                    "step": 3,
                    "stop": 24,
                },
                "start_date": "2026-04-01T00:00:00",
                "stat_prefix": "grid_stat_nested_global",
                "variable_prefixes": [
                    "u10_heightAboveGround_0010",
                    "v10_heightAboveGround_0010",
                ],
                "work_path": "/path/to/work",
            },
            "name": "asdf",
            "rundir": "/path/to/rundir",
            "spatial_stat_plots": {
                "add_states": True,
                "cmap": "RdBu_r",
                "figsize": {
                    "h": 1.1,
                    "w": 2,
                },
                "file_fontsize": 3.3,
                "gridlines": True,
                "stats_root": "/path/to//stats/%s",
                "suptitle_y": 4.4,
                "title_fontsize": 5.5,
            },
            "stats": [
                "RMSE",
            ],
            "variables": [
                "10m_zonal_wind",
                "10m_meridional_wind",
            ],
        }
    }


# Driver tests.


@fixture
def dataset():
    return xr.Dataset(
        data_vars={
            "lat": (["lat"], [-45, 0, +45]),
            "lon": (["lon"], [-90, 0, +90]),
            "DIFF_v": (
                ["lat", "lon"],
                [[11, 22, 33], [44, 55, 66], [77, 88, 99]],
                {"long_name": "variable", "init_time": "t0", "valid_time": "t1"},
            ),
        },
        attrs={"Difference": "fcst - obs"},
    )


@fixture
def driverobj(config):
    return Visualization(
        config=config, schema_file=Path(__file__).parent / "visualization.jsonschema"
    )


@mark.parametrize("omit_spatial_stat_plots", [True, False])
def test_plots(driverobj, omit_spatial_stat_plots, readytask):
    if omit_spatial_stat_plots:
        del driverobj._config["spatial_stat_plots"]
    with (
        patch.object(driverobj, "_basic_plot", wraps=readytask) as _basic_plot,
        patch.object(
            driverobj, "spatial_stat_plots", wraps=readytask
        ) as spatial_stat_plots,
    ):
        assert driverobj.plots().ready
        for var in driverobj.config["variables"]:
            for stat in driverobj.config["stats"]:
                assert call(var, stat) in _basic_plot.call_args_list
        spatial_stat_plots_check = getattr(
            spatial_stat_plots,
            "assert_not_called"
            if omit_spatial_stat_plots
            else "assert_called_once_with",
        )
        spatial_stat_plots_check()


def test_postwxvx(driverobj, tmp_path):
    driverobj._config["eagle_tools"]["work_path"] = tmp_path
    driverobj._config["rundir"] = tmp_path
    yamlcfg = tmp_path / "postwxvx-asdf.yaml"
    assert not yamlcfg.exists()
    ncfiles = [tmp_path / f"{var}.nc" for var in driverobj.config["variables"]]
    for ncfile in ncfiles:
        assert not ncfile.exists()
    with patch.object(visualization, "run") as run:
        run.side_effect = [ncfile.touch() for ncfile in ncfiles]
        assert driverobj.postwxvx().ready
    logfile = tmp_path / "postwxvx.log"
    run.assert_called_once_with(  # noqa: S604
        f"eagle-tools postwxvx {yamlcfg.name} >{logfile} 2>&1",
        check=False,
        cwd=tmp_path,
        shell=True,
    )
    assert yamlcfg.is_file()


def test_spatial_stat_plots(driverobj, readytask):
    ncfiles = [Path(x) for x in ("grid_stat_b_pairs.nc", "grid_stat_a_pairs.nc")]
    with (
        patch.object(Path, "rglob", return_value=ncfiles),
        patch.object(
            driverobj, "_spatial_stat_plot", wraps=readytask
        ) as _spatial_stat_plot,
    ):
        assert driverobj.spatial_stat_plots().ready


def test__basic_plot(driverobj, tmp_path):
    @task
    def postwxvx():
        yield "postwxvx"
        yield Asset({"v": path}, lambda: True)
        yield None

    driverobj._config["rundir"] = tmp_path
    path = tmp_path / "a.nc"
    assert not path.is_file()
    xr.Dataset({"y": (["x"], [1, 2, 3])}).to_netcdf(path)
    with patch.object(driverobj, "postwxvx", postwxvx):
        assert driverobj._basic_plot(var="v", stat="y").ready
    assert path.is_file()


@mark.parametrize("optional", [True, False])
def test__spatial_stat_plot(dataset, driverobj, optional, tmp_path):
    for key in ["add_states", "gridlines"]:
        driverobj._config["spatial_stat_plots"][key] = optional
    pngpath = tmp_path / "a.png"
    assert not pngpath.exists()
    ncpath = tmp_path / "a.nc"
    dataset.to_netcdf(ncpath)
    driverobj._spatial_stat_plot(ncpath=ncpath, pngpath=pngpath)
    assert pngpath.is_file()


@mark.parametrize("remove_attrs", [True, False])
def test__build_main_title(dataset, remove_attrs):
    if remove_attrs:
        del dataset.DIFF_v.attrs["init_time"]
        del dataset.DIFF_v.attrs["valid_time"]
        del dataset.attrs["Difference"]
        expected = "variable"
    else:
        expected = "variable\ninit=t0 valid=t1\nDifference: fcst - obs"
    assert visualization._build_main_title(ds=dataset, var="DIFF_v") == expected


# Schema tests.


def test_top(config, logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "visualization", tmp_path)
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["visualization"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have object values:
    for key in ["visualization"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")


def test_visualization(config, logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "visualization", tmp_path, "properties", "visualization")
    config = config["visualization"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are not allowed:
    assert not ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["eagle_tools", "name", "rundir", "stats", "variables"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have array values:
    for key in ["stats", "variables"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'array'")
    # Some keys have object values:
    for key in ["eagle_tools", "spatial_stat_plots"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")
    # Some keys have string values:
    for key in ["name", "rundir"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")


def test_visualization__eagle_tools(
    caplog, config, logged, tmp_path, validator, with_set
):
    ok = validator(
        __file__,
        "visualization",
        tmp_path,
        "properties",
        "visualization",
        "properties",
        "eagle_tools",
    )
    config = config["visualization"]["eagle_tools"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # No keys are required:
    assert ok({})
    # Some keys have array values:
    for key in ["variable_prefixes"]:
        assert not ok(with_set(config, None, key))
        assert "is not of type 'array'" in caplog.text
        # Any values will do:
        assert ok(with_set(config, [1, 2.2, True, "foo", {}, []], key))
        # An empty array is ok:
        assert ok(with_set(config, [], key))
    # Some keys have datetime values:
    for key in ["end_date", "start_date"]:
        assert not ok(with_set(config, None, key))
        assert "is not of type 'datetime'" in caplog.text
        assert "is not of type 'string'" in caplog.text
        assert logged("At least one must match")
    # Some keys have string values:
    for key in ["freq", "stat_prefix", "work_path"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")


def test_visualization__eagle_tools__leadtimes(
    caplog, config, logged, tmp_path, validator, with_set
):
    ok = validator(
        __file__,
        "visualization",
        tmp_path,
        "properties",
        "visualization",
        "properties",
        "eagle_tools",
        "properties",
        "leadtimes",
    )
    config = config["visualization"]["eagle_tools"]["leadtimes"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Some keys have integer values:
    for key in ["end", "start"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'integer'")
    # Some keys have timedelta values:
    for key in ["step"]:
        assert not ok(with_set(config, None, key))
        assert "is not of type 'timedelta'" in caplog.text
        assert "is not of type 'integer'" in caplog.text
        assert "is not of type 'string'" in caplog.text
        assert logged("At least one must match")


def test_visualization__spatial_stat_plots(
    config, logged, tmp_path, validator, with_del, with_set
):
    ok = validator(
        __file__,
        "visualization",
        tmp_path,
        "properties",
        "visualization",
        "properties",
        "spatial_stat_plots",
    )
    config = config["visualization"]["spatial_stat_plots"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are not allowed:
    assert not ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in [
        "add_states",
        "cmap",
        "figsize",
        "file_fontsize",
        "gridlines",
        "stats_root",
        "suptitle_y",
        "title_fontsize",
    ]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have boolean values:
    for key in ["add_states", "gridlines"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'boolean'")
    # Some keys have number values:
    for key in ["file_fontsize", "suptitle_y", "title_fontsize"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'number'")
    # Some keys have object values:
    for key in ["figsize"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")
    # Some keys have string values:
    for key in ["cmap", "stats_root"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")


def test_visualization__spatial_stat_plots__figsize(
    config, logged, tmp_path, validator, with_del, with_set
):
    ok = validator(
        __file__,
        "visualization",
        tmp_path,
        "properties",
        "visualization",
        "properties",
        "spatial_stat_plots",
        "properties",
        "figsize",
    )
    config = config["visualization"]["spatial_stat_plots"]["figsize"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are not allowed:
    assert not ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["h", "w"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have number values:
    for key in ["h", "w"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'number'")


def test_visualization__defs__datetime(caplog, logged, tmp_path, validator):
    ok = validator(__file__, "visualization", tmp_path, "$defs", "datetime")
    for val in [datetime(2026, 4, 8, 12, tzinfo=timezone.utc), "2026-04-08T01:23:45"]:
        assert ok(val)
    assert not ok("foo")
    assert "is not valid under any of the given schemas" in caplog.text
    assert "is not of type 'datetime'" in caplog.text
    assert logged("does not match")


def test_visualization__defs__timedelta(caplog, logged, tmp_path, validator):
    ok = validator(__file__, "visualization", tmp_path, "$defs", "timedelta")
    for val in [timedelta(hours=6), 6, "6", "06", "06:00", "06:00:00"]:
        assert ok(val)
    assert not ok("foo")
    assert "is not valid under any of the given schemas" in caplog.text
    assert "is not of type 'timedelta'" in caplog.text
    assert "is not of type 'integer'" in caplog.text
    assert logged("does not match")

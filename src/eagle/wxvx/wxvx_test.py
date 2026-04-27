from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from pytest import fixture

from . import wxvx
from .wxvx import WXVX


@fixture
def config():
    return {
        "platform": {
            "account": "a",
            "scheduler": "slurm",
        },
        "wxvx": {
            "execution": {
                # uwtools validates this block.
                "batchargs": {
                    "walltime": "00:30:00",
                },
                "executable": "wxvx",
            },
            "name": "grid2grid-global",
            "prewxvx": {
                "eagle_tools": {
                    "anemoi_reference_dataset_kwargs": {},
                    "end_date": "2026-04-08T12:00:00",
                    "forecast_path": "/path/to/forecast",
                    "forecast_regrid_kwargs": {
                        "open_target_kwargs": {},
                        "regridder_kwargs": {
                            "method": "conservative_normed",
                        },
                        "target_grid_path": "/path/to/target-grid",
                    },
                    "freq": "6h",
                    "lam_index": 1,
                    "lcc_info": {
                        "n_x": 11,
                        "n_y": 22,
                    },
                    "lead_time": 24,
                    "levels": [
                        1,
                        2,
                        3.5,
                    ],
                    "model_type": "global",
                    "output_path": "/path/to/output",
                    "start_date": "2026-04-01T00:00:00",
                    "vars_of_interest": [
                        "t",
                        "u",
                        "v",
                    ],
                },
                "rundir": "/path/to/prewxvx",
            },
            "rundir": "/path/to/rundir",
            "wxvx": {
                # wxvx validates this block.
                "cycles": ["2026-04-09T12:00:00"],
                "forecast": {
                    "coords": {
                        "latitude": "lat",
                        "longitude": "lon",
                        "level": "lvl",
                        "time": {
                            "inittime": "time",
                            "leadtime": "leadtime",
                        },
                    },
                    "name": "test",
                    "path": "/path/to/forecast.nc",
                },
                "leadtimes": [6],
                "paths": {
                    "grids": {
                        "forecast": "/path/to/forecast/grids",
                        "truth": "/path/to/truth/grids",
                    },
                    "run": "/path/to/rundir",
                },
                "truth": {
                    "name": "GFS",
                    "type": "grid",
                    "url": "https://some.url",
                },
                "variables": {
                    "T2M": {
                        "level_type": "heightAboveGround",
                        "levels": [2],
                        "name": "2t",
                    },
                },
            },
        },
    }


# Driver tests.


@fixture
def driverobj(config):
    return WXVX(
        config=config, batch=True, schema_file=Path(__file__).parent / "wxvx.jsonschema"
    )


def test_prewxvx(driverobj, tmp_path):
    driverobj._config["prewxvx"]["eagle_tools"]["output_path"] = tmp_path
    driverobj._config["prewxvx"]["rundir"] = tmp_path
    yamlcfg = tmp_path / "prewxvx-global.yaml"
    assert not yamlcfg.exists()
    ncfile = tmp_path / "nested-global.test.nc"
    assert not ncfile.exists()
    with patch.object(wxvx, "run") as run:
        run.side_effect = [ncfile.touch()]
        assert driverobj.prewxvx().ready
    logfile = tmp_path / "prewxvx.log"
    run.assert_called_once_with(  # noqa: S604
        f"eagle-tools prewxvx {yamlcfg} >{logfile} 2>&1",
        check=False,
        cwd=tmp_path,
        shell=True,
    )
    assert yamlcfg.is_file()


def test_wxvx_provisioned_rundir(driverobj, readytask, tmp_path):
    driverobj._config["rundir"] = tmp_path
    runscript = tmp_path / "runscript.wxvx-grid2grid-global"
    assert not runscript.is_file()
    with patch.object(driverobj, "wxvx_config", wraps=readytask) as wxvx_config:
        driverobj.provisioned_rundir()
    wxvx_config.assert_called_once_with()
    assert runscript.is_file()


def test_wxvx_config(driverobj, tmp_path):
    driverobj._config["rundir"] = tmp_path
    cfgfile = tmp_path / "wxvx-grid2grid-global.yaml"
    assert not cfgfile.is_file()
    driverobj.wxvx_config()
    assert cfgfile.is_file()


def test_driver_name():
    assert WXVX.driver_name() == "wxvx"


def test__name(driverobj):
    assert driverobj._name == "grid2grid-global"


def test__runscript_path(driverobj):
    assert driverobj._runscript_path == Path(
        "/path/to/rundir/runscript.wxvx-grid2grid-global"
    )


# Schema tests.


def test_top(config, logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "wxvx", tmp_path)
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["wxvx"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have object values:
    for key in ["wxvx"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")


def test_wxvx(config, logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "wxvx", tmp_path, "properties", "wxvx")
    config = config["wxvx"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are not allowed:
    assert not ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["execution", "name", "prewxvx", "rundir", "wxvx"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have string values:
    for key in ["name", "rundir"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")
    # Some keys have object values:
    for key in ["execution", "wxvx"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")


def test_prewxvx_schema(config, logged, validator, tmp_path, with_del, with_set):
    ok = validator(
        __file__,
        "wxvx",
        tmp_path,
        "properties",
        "wxvx",
        "properties",
        "prewxvx",
    )
    pwvcfg = config["wxvx"]["prewxvx"]
    # Basic correctness:
    assert ok(pwvcfg)
    # Additional keys are not allowed:
    assert not ok(with_set(pwvcfg, "foo", "bar"))
    # Certain keys are required:
    for key in ["eagle_tools", "rundir"]:
        assert not ok(with_del(pwvcfg, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have object values:
    for key in ["eagle_tools"]:
        assert not ok(with_set(pwvcfg, None, key))
        assert logged("is not of type 'object'")
    # Some keys have string values:
    for key in ["rundir"]:
        assert not ok(with_set(pwvcfg, None, key))
        assert logged("is not of type 'string'")


def test_prewxvx__eagle_tools(config, logged, validator, tmp_path, with_del, with_set):
    ok = validator(
        __file__,
        "wxvx",
        tmp_path,
        "properties",
        "wxvx",
        "properties",
        "prewxvx",
        "properties",
        "eagle_tools",
    )
    eglcfg = config["wxvx"]["prewxvx"]["eagle_tools"]
    # Basic correctness:
    assert ok(eglcfg)
    # Additional keys are allowed:
    assert ok(with_set(eglcfg, "foo", "bar"))
    # Certain keys are required:
    for key in [
        "end_date",
        "forecast_path",
        "freq",
        "lead_time",
        "model_type",
        "output_path",
        "start_date",
    ]:
        assert not ok(with_del(eglcfg, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have array values:
    for key in ["levels"]:
        assert not ok(with_set(eglcfg, None, key))
        assert logged("is not of type 'array'")
    # Some keys have enum values:
    assert not ok(with_set(eglcfg, "foo", "model_type"))
    assert logged("'foo' is not one of")
    # Some keys have integer values:
    for key in ["lam_index", "lead_time"]:
        assert not ok(with_set(eglcfg, None, key))
        assert logged("is not of type 'integer'")
    # Some keys have object values:
    for key in [
        "anemoi_reference_dataset_kwargs",
        "forecast_regrid_kwargs",
        "lcc_info",
    ]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")
    # Some keys have string values:
    for key in ["end_date", "forecast_path", "freq", "output_path", "start_date"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")


def test_prewxvx__eagle_tools__forecast_regrid_kwargs(
    config, logged, validator, tmp_path, with_set
):
    ok = validator(
        __file__,
        "wxvx",
        tmp_path,
        "properties",
        "wxvx",
        "properties",
        "prewxvx",
        "properties",
        "eagle_tools",
        "properties",
        "forecast_regrid_kwargs",
    )
    pwvcfg = config["wxvx"]["prewxvx"]["eagle_tools"]["forecast_regrid_kwargs"]
    # Basic correctness:
    assert ok(pwvcfg)
    # Additional keys are allowed:
    assert ok(with_set(pwvcfg, "foo", "bar"))
    # No keys are required:
    assert ok({})
    # Some keys have object values:
    for key in ["open_target_kwargs", "regridder_kwargs"]:
        assert not ok(with_set(pwvcfg, None, key))
        assert logged("is not of type 'object'")
    # Some keys have string values:
    for key in ["target_grid_path"]:
        assert not ok(with_set(pwvcfg, None, key))
        assert logged("is not of type 'string'")


def test_prewxvx__eagle_tools__forecast_regrid_kwargs__regridder_kwargs(
    config, logged, validator, tmp_path, with_del, with_set
):
    ok = validator(
        __file__,
        "wxvx",
        tmp_path,
        "properties",
        "wxvx",
        "properties",
        "prewxvx",
        "properties",
        "eagle_tools",
        "properties",
        "forecast_regrid_kwargs",
        "properties",
        "regridder_kwargs",
    )
    pwvcfg = config["wxvx"]["prewxvx"]["eagle_tools"]["forecast_regrid_kwargs"][
        "regridder_kwargs"
    ]
    # Basic correctness:
    assert ok(pwvcfg)
    # Additional keys are allowed:
    assert ok(with_set(pwvcfg, "foo", "bar"))
    # Certain keys are required:
    for key in ["method"]:
        assert not ok(with_del(pwvcfg, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have string values:
    for key in ["method"]:
        assert not ok(with_set(pwvcfg, None, key))
        assert logged("is not of type 'string'")


def test_prewxvx__eagle_tools__lcc_info(
    config, logged, validator, tmp_path, with_del, with_set
):
    ok = validator(
        __file__,
        "wxvx",
        tmp_path,
        "properties",
        "wxvx",
        "properties",
        "prewxvx",
        "properties",
        "eagle_tools",
        "properties",
        "lcc_info",
    )
    pwxcfg = config["wxvx"]["prewxvx"]["eagle_tools"]["lcc_info"]
    # Basic correctness:
    assert ok(pwxcfg)
    # Additional keys are allowed:
    assert ok(with_set(pwxcfg, "foo", "bar"))
    # Certain keys are required:
    for key in ["n_x", "n_y"]:
        assert not ok(with_del(pwxcfg, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have integer values:
    for key in ["n_x", "n_y"]:
        assert not ok(with_set(pwxcfg, None, key))
        assert logged("is not of type 'integer'")


def test_prewxvx__eagle_tools__levels(config, logged, validator, tmp_path):
    ok = validator(
        __file__,
        "wxvx",
        tmp_path,
        "properties",
        "wxvx",
        "properties",
        "prewxvx",
        "properties",
        "eagle_tools",
        "properties",
        "levels",
    )
    pwxvcfg = config["wxvx"]["prewxvx"]["eagle_tools"]["levels"]
    # Basic correctness:
    assert ok(pwxvcfg)
    # An empy list os ok:
    assert ok([])
    # Items must be numbers:
    assert ok([1, 2.2, -3])
    assert not ok([None])
    assert logged("is not of type 'number'")


def test_prewxvx__defs__datetime(caplog, logged, tmp_path, validator):
    ok = validator(__file__, "wxvx", tmp_path, "$defs", "datetime")
    for val in [datetime(2026, 4, 8, 12, tzinfo=timezone.utc), "2026-04-08T01:23:45"]:
        assert ok(val)
    assert not ok("foo")
    assert "is not valid under any of the given schemas" in caplog.text
    assert "is not of type 'datetime'" in caplog.text
    assert logged("does not match")

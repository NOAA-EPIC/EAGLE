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
        "name": "grid2grid-global",
        "prewxvx": {
            "rundir": "/path/to/prewxvx",
            "eagle_tools": {
                "output_path": "/path/to/output",
            },
        },
        "rundir": "/path/to/rundir",
        "wxvx": {
            "execution": {
                # uwtools validates this block.
                "batchargs": {
                    "walltime": "00:30:00",
                },
                "executable": "wxvx",
            },
            "name": "grid2grid-global",
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
    for key in ["execution", "name", "rundir", "wxvx"]:
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

from pathlib import Path
from unittest.mock import patch

from pytest import fixture

from . import training
from .training import Training


@fixture
def config():
    return {
        "platform": {
            "account": "a",
            "scheduler": "slurm",
        },
        "training": {
            "anemoi": {
                # anemoi-training validates this block.
            },
            "execution": {
                # uwtools validates this block.
                "batchargs": {
                    "walltime": "01:00:00",
                },
                "executable": "anemoi-training train --config-name=training",
            },
            "remove": [
                "foo.bar",
            ],
            "rundir": "/path/to/rundir",
        },
    }


# Driver tests.


@fixture
def driverobj(config):
    return Training(
        config=config,
        batch=True,
        schema_file=Path(__file__).parent / "training.jsonschema",
    )


def test_anemoi_config(driverobj, tmp_path):
    driverobj._config["rundir"] = tmp_path
    yamlcfg = tmp_path / "training.yaml"
    assert not yamlcfg.exists()
    gencfg = tmp_path / "config.yaml"
    assert not gencfg.exists()
    with patch.object(training, "run") as run:
        run.side_effect = [gencfg.write_text("{}\n")]
        assert driverobj.anemoi_config().ready
    logfile = tmp_path / "config.log"
    run.assert_called_once_with(  # noqa: S604
        f"anemoi-training config generate >{logfile} 2>&1",
        check=False,
        cwd=tmp_path,
        shell=True,
    )
    assert yamlcfg.is_file()


def test_driver_name():
    assert Training.driver_name() == "training"


def test_provisioned_rundir(driverobj, readytask, tmp_path):
    driverobj._config["rundir"] = tmp_path
    runscript = tmp_path / "runscript.training"
    assert not runscript.is_file()
    with patch.object(driverobj, "anemoi_config", wraps=readytask) as anemoi_config:
        driverobj.provisioned_rundir()
    anemoi_config.assert_called_once_with()
    assert runscript.is_file()


def test_runscript__with_multiple_remove(driverobj, tmp_path):
    driverobj._config["remove"] = ["foo.bar", "baz.qux"]
    driverobj._config["rundir"] = tmp_path
    runscript = tmp_path / "runscript.training"
    assert not runscript.is_file()
    driverobj.runscript()
    assert runscript.is_file()
    assert (
        driverobj._config["execution"]["executable"]
        == "anemoi-training train --config-name=training ~foo.bar ~baz.qux"
    )


def test_runscript__with_remove(driverobj, tmp_path):
    driverobj._config["rundir"] = tmp_path
    runscript = tmp_path / "runscript.training"
    assert not runscript.is_file()
    driverobj.runscript()
    assert runscript.is_file()
    assert (
        driverobj._config["execution"]["executable"]
        == "anemoi-training train --config-name=training ~foo.bar"
    )


def test_runscript__without_remove(driverobj, tmp_path):
    del driverobj._config["remove"]
    driverobj._config["rundir"] = tmp_path
    runscript = tmp_path / "runscript.training"
    assert not runscript.is_file()
    driverobj.runscript()
    assert runscript.is_file()
    assert (
        driverobj._config["execution"]["executable"]
        == "anemoi-training train --config-name=training"
    )


# Schema tests.


def test_top(config, logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "training", tmp_path)
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["training"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have object values:
    for key in ["training"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")


def test_training(config, logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "training", tmp_path, "properties", "training")
    config = config["training"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are not allowed:
    assert not ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["anemoi", "execution", "rundir"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have array values:
    for key in ["remove"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'array'")
    # Some keys have object values:
    for key in ["anemoi", "execution"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")
    # Some keys have string values:
    for key in ["rundir"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")


def test_training__remove(config, tmp_path, validator):
    ok = validator(
        __file__, "training", tmp_path, "properties", "training", "properties", "remove"
    )
    config = config["training"]["remove"]
    # Basic correctness:
    assert ok(config)
    # An empty array is ok:
    assert ok([])
    # Any item types are ok:
    assert ok([1, 2.2, True, None, "foo", {}, []])

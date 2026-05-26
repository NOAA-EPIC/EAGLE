from pathlib import Path
from unittest.mock import patch

from pytest import fixture

from .zarr import Zarr


@fixture
def config():
    return {
        "platform": {
            "account": "a",
            "scheduler": "slurm",
        },
        "zarr": {
            "execution": {
                # uwtools validates this block.
                "batchargs": {
                    "walltime": "01:00:00",
                },
                "executable": "ufs2arco",
            },
            "name": "gfs",
            "rundir": "/path/to/rundir",
            "ufs2arco": {
                "attrs": {},
                "directories": {},
                "mover": {
                    "name": "mpidatamover",
                },
                "multisource": [
                    {
                        "source": {
                            "name": "gfs_archive",
                        },
                    },
                ],
                "target": {
                    "name": "anemoi",
                },
                "transforms": {},
            },
        },
    }


# Driver tests.


@fixture
def driverobj(config):
    return Zarr(
        config=config,
        batch=True,
        schema_file=Path(__file__).parent / "zarr.jsonschema",
    )


def test_driver_name():
    assert Zarr.driver_name() == "zarr"


def test_provisioned_rundir(driverobj, readytask, tmp_path):
    driverobj._config["rundir"] = tmp_path
    runscript = tmp_path / "runscript.zarr-gfs"
    assert not runscript.is_file()
    with patch.object(driverobj, "ufs2arco_config", wraps=readytask) as ufs2arco_config:
        driverobj.provisioned_rundir()
    ufs2arco_config.assert_called_once_with()
    assert runscript.is_file()


def test_ufs2arco_config(driverobj, tmp_path):
    driverobj._config["rundir"] = tmp_path
    cfgfile = tmp_path / "ufs2arco-gfs.yaml"
    assert not cfgfile.is_file()
    driverobj.ufs2arco_config()
    assert cfgfile.is_file()


# Schema tests.


def test_top(config, logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "zarr", tmp_path)
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["zarr"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have object values:
    for key in ["zarr"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")


def test_zarr(config, logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "zarr", tmp_path, "properties", "zarr")
    config = config["zarr"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are not allowed:
    assert not ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["execution", "name", "rundir", "ufs2arco"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have object values:
    for key in ["execution", "ufs2arco"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")
    # Some keys have string values:
    for key in ["name", "rundir"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")


def test_zarr__ufs2arco(config, logged, tmp_path, validator, with_del, with_set):
    ok = validator(
        __file__, "zarr", tmp_path, "properties", "zarr", "properties", "ufs2arco"
    )
    config = config["zarr"]["ufs2arco"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["mover", "directories", "target"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have array values:
    for key in ["multisource"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'array'")
    # Some keys have object values:
    for key in ["attrs", "directories", "mover", "target", "transforms"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")


def test_zarr__ufs2arco__multisource(config, logged, tmp_path, validator):
    ok = validator(
        __file__,
        "zarr",
        tmp_path,
        "properties",
        "zarr",
        "properties",
        "ufs2arco",
        "properties",
        "multisource",
    )
    config = config["zarr"]["ufs2arco"]["multisource"]
    # Basic correctness:
    assert ok(config)
    # At least one element is required:
    assert not ok([])
    assert logged("should be non-empty")


def test_zarr__ufs2arco__multisource__item(
    config, logged, tmp_path, validator, with_del, with_set
):
    ok = validator(
        __file__,
        "zarr",
        tmp_path,
        "properties",
        "zarr",
        "properties",
        "ufs2arco",
        "properties",
        "multisource",
        "items",
    )
    config = config["zarr"]["ufs2arco"]["multisource"][0]
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["source"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have object values:
    for key in ["source", "transforms"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")


def test_zarr__ufs2arco__multisource__item__source(
    config, logged, tmp_path, validator, with_del, with_set
):
    ok = validator(
        __file__,
        "zarr",
        tmp_path,
        "properties",
        "zarr",
        "properties",
        "ufs2arco",
        "properties",
        "multisource",
        "items",
        "properties",
        "source",
    )
    config = config["zarr"]["ufs2arco"]["multisource"][0]["source"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["name"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have string values:
    for key in ["name"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")

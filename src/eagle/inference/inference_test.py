from pathlib import Path
from unittest.mock import patch

from pytest import fixture

from .inference import Inference


@fixture
def config():
    return {
        "inference": {
            "anemoi": {
                # anemoi-inference validates this block.
            },
            "checkpoint_dir": "/path/to/checkpoint",
            "execution": {
                # uwtools validates this block.
                "batchargs": {
                    "walltime": "01:00:00",
                },
                "executable": "ufs2arco",
            },
            "rundir": "/path/to/rundir",
        },
        "platform": {
            "account": "a",
            "scheduler": "slurm",
        },
    }


# Driver tests.


@fixture
def driverobj(config):
    return Inference(
        config=config,
        batch=True,
        schema_file=Path(__file__).parent / "inference.jsonschema",
    )


def test_anemoi_config(driverobj, tmp_path):
    ckpt_dir = tmp_path / "checkpoints"
    ckpt_subdir = ckpt_dir / "20260421"
    ckpt_subdir.mkdir(parents=True)
    ckptfile = ckpt_subdir / "inference-last.ckpt"
    ckptfile.touch()
    driverobj._config["checkpoint_dir"] = ckpt_dir
    driverobj._config["rundir"] = tmp_path
    cfgfile = tmp_path / "inference.yaml"
    assert not cfgfile.is_file()
    driverobj.anemoi_config()
    assert cfgfile.is_file()


def test_anemoi_config_explicit_checkpoint(driverobj, tmp_path):
    ckptfile = tmp_path / "inference-last.ckpt"
    ckptfile.touch()
    driverobj._config["checkpoint_dir"] = None
    driverobj._config["rundir"] = tmp_path
    driverobj._config["anemoi"]["checkpoint_path"] = str(ckptfile)
    cfgfile = tmp_path / "inference.yaml"
    assert not cfgfile.is_file()
    driverobj.anemoi_config()
    assert cfgfile.is_file()


def test_driver_name():
    assert Inference.driver_name() == "inference"


def test_provisioned_rundir(driverobj, readytask, tmp_path):
    ckpt_dir = tmp_path / "checkpoints"
    ckpt_subdir = ckpt_dir / "20260421"
    ckpt_subdir.mkdir(parents=True)
    ckptfile = ckpt_subdir / "inference-last.ckpt"
    ckptfile.touch()
    driverobj._config["checkpoint_dir"] = ckpt_dir
    driverobj._config["rundir"] = tmp_path
    runscript = tmp_path / "runscript.inference"
    assert not runscript.is_file()
    with patch.object(driverobj, "anemoi_config", wraps=readytask) as anemoi_config:
        driverobj.provisioned_rundir()
    anemoi_config.assert_called_once_with()
    assert runscript.is_file()


# Schema tests.


def test_top(config, logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "inference", tmp_path)
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["inference"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have object values:
    for key in ["inference"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")


def test_inference(config, logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "inference", tmp_path, "properties", "inference")
    config = config["inference"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are not allowed:
    assert not ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["anemoi", "execution", "rundir"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have object values:
    for key in ["anemoi", "execution"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")
    # Some keys have string values:
    for key in ["checkpoint_dir", "rundir"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")

# Schema tests.

CONFIG = {
    "inference": {
        "anemoi": {
            # anemoi-inference validates its config.
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
    }
}


def test_top(logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "inference", tmp_path)
    config = CONFIG
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


def test_inference(logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "inference", tmp_path, "properties", "inference")
    config = CONFIG["inference"]
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

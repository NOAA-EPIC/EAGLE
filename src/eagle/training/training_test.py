# Schema tests.


CONFIG = {
    "training": {
        "anemoi": {
            # anemoi-training validates this block.
        },
        "execution": {
            # uwtools validates this block.
            "batchargs": {
                "walltime": "01:00:00",
            },
            "executable": "ufs2arco",
        },
        "remove": [
            "graph.nodes.hidden.node_builder.grid",
        ],
        "rundir": "/path/to/rundir",
    }
}


def test_top(logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "training", tmp_path)
    config = CONFIG
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


def test_training(logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "training", tmp_path, "properties", "training")
    config = CONFIG["training"]
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


def test_training__remove(tmp_path, validator):
    ok = validator(
        __file__, "training", tmp_path, "properties", "training", "properties", "remove"
    )
    config = CONFIG["training"]["remove"]
    # Basic correctness:
    assert ok(config)
    # An empty array is ok:
    assert ok([])
    # Any item types are ok:
    assert ok([1, 2.2, True, None, "foo", {}, []])

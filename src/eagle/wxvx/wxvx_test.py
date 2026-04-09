# Schema tests.


CONFIG = {
    "wxvx": {
        "execution": {
            # uwtools validates this block.
            "executable": "wxvx",
        },
        "name": "grid2grid-global",
        "rundir": "/path/to/rundir",
        "wxvx": {
            # wxvx validates this block.
        },
    }
}


def test_top(logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "wxvx", tmp_path)
    config = CONFIG
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


def test_wxvx(logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "wxvx", tmp_path, "properties", "wxvx")
    config = CONFIG["wxvx"]
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

from datetime import datetime, timedelta, timezone

# Schema tests.


CONFIG: dict = {
    "app": {
        "base": "/path/to/base",
        "experiment_name": "eagle",
        "gpu": {
            "batchargs": {"nodes": 1, "partition": "p", "queue": "q"},
        },
        "partitions": {
            "netaccess": "service",
        },
        "platform": {
            "account": "a",
            "scheduler": "slurm",
        },
        "rundir": "/path/to/rundir",
        "time": {
            "inference_start": "2026-04-01T00:00:00",
            "inference_stop": "2026-04-08T12:00:00",
            "leadtime": 24,
            "start": "2026-04-01T00:00:00",
            "step": 6,
            "stop": "2026-04-08T12:00:00",
        },
    },
    "grids_and_meshes": {},  # tested by eagle.data
    "inference": {},  # tested by eagle.inference
    "platform": {},  # tested by uwtools
    "prewxvx": {},  # tested by eagle.wxvx
    "training": {},  # tested by eagle.training
    "ufs2arco": {},  # needs expanded schema
    "val": {  # arbitrary config container
        "baz": "qux",
    },
    "visualization": {},  # tested by eagle.visualization
    "vx": {},  # tested by eagle.wxvx
    "zarrs": {},  # needs expanded schema
}


def test_top(logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "eagle", tmp_path)
    config = CONFIG
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in [
        "app",
        "grids_and_meshes",
        "inference",
        "platform",
        "prewxvx",
        "training",
        "ufs2arco",
        "val",
        "visualization",
        "vx",
        "zarrs",
    ]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have object values:
    for key in [
        "app",
        "grids_and_meshes",
        "inference",
        "platform",
        "prewxvx",
        "training",
        "ufs2arco",
        "val",
        "visualization",
        "vx",
        "zarrs",
    ]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")


def test_app(logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "eagle", tmp_path, "properties", "app")
    config = CONFIG["app"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in [
        "base",
        "experiment_name",
        "gpu",
        "partitions",
        "platform",
        "rundir",
        "time",
    ]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have object values:
    for key in ["gpu", "partitions", "platform", "time"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")
    # Some keys have string values:
    for key in ["base", "experiment_name", "rundir"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")


def test_app__gpu(logged, tmp_path, validator, with_del, with_set):
    ok = validator(
        __file__, "eagle", tmp_path, "properties", "app", "properties", "gpu"
    )
    config = CONFIG["app"]["gpu"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["batchargs"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have object values:
    for key in ["batchargs"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")


def test_app__gpu__batchargs(logged, tmp_path, validator, with_del, with_set):
    ok = validator(
        __file__,
        "eagle",
        tmp_path,
        "properties",
        "app",
        "properties",
        "gpu",
        "properties",
        "batchargs",
    )
    config = CONFIG["app"]["gpu"]["batchargs"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["nodes", "partition", "queue"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have integer values:
    for key in ["nodes"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'integer'")
    # Some keys have string values:
    for key in ["partition", "queue"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")


def test_app__gpu__partitions(logged, tmp_path, validator, with_del, with_set):
    ok = validator(
        __file__, "eagle", tmp_path, "properties", "app", "properties", "partitions"
    )
    config = CONFIG["app"]["partitions"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["netaccess"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have string values:
    for key in ["netaccess"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")


def test_app__gpu__platform(logged, tmp_path, validator, with_set):
    ok = validator(
        __file__, "eagle", tmp_path, "properties", "app", "properties", "platform"
    )
    config = CONFIG["app"]["platform"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # No keys are required:
    assert ok({})
    # Some keys have enum values:
    assert not ok(with_set(config, "foo", "scheduler"))
    assert logged("'foo' is not one of")
    # Some keys have string values:
    for key in ["account"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")


def test_app__gpu__time(caplog, logged, tmp_path, validator, with_del, with_set):
    ok = validator(
        __file__, "eagle", tmp_path, "properties", "app", "properties", "time"
    )
    config = CONFIG["app"]["time"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in [
        "inference_start",
        "inference_stop",
        "leadtime",
        "start",
        "step",
        "stop",
    ]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have datetime values:
    for key in ["inference_start", "inference_stop", "start", "stop"]:
        assert not ok(with_set(config, None, key))
        assert "is not of type 'datetime'" in caplog.text
        assert "is not of type 'string'" in caplog.text
        assert logged("At least one must match")
    # Some keys have integer values:
    for key in ["leadtime"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'integer'")
    # Some keys have timedelta values:
    for key in ["step"]:
        assert not ok(with_set(config, None, key))
        assert "is not of type 'timedelta'" in caplog.text
        assert "is not of type 'integer'" in caplog.text
        assert "is not of type 'string'" in caplog.text
        assert logged("At least one must match")


def test_eagle__defs__datetime(caplog, logged, tmp_path, validator):
    ok = validator(__file__, "eagle", tmp_path, "$defs", "datetime")
    for val in [datetime(2026, 4, 8, 12, tzinfo=timezone.utc), "2026-04-08T01:23:45"]:
        assert ok(val)
    assert not ok("foo")
    assert "is not valid under any of the given schemas" in caplog.text
    assert "is not of type 'datetime'" in caplog.text
    assert logged("does not match")


def test_eagle__defs__timedelta(caplog, logged, tmp_path, validator):
    ok = validator(__file__, "eagle", tmp_path, "$defs", "timedelta")
    for val in [timedelta(hours=6), 6, "6", "06", "06:00", "06:00:00"]:
        assert ok(val)
    assert not ok("foo")
    assert "is not valid under any of the given schemas" in caplog.text
    assert "is not of type 'timedelta'" in caplog.text
    assert "is not of type 'integer'" in caplog.text
    assert logged("does not match")

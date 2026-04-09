from datetime import datetime, timedelta, timezone

# Schema tests.


CONFIG: dict = {
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
                "u_10m_heightAboveGround_0010",
                "v_10m_heightAboveGround_0010",
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
            "stats_root": "/path/to/stats",
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


def test_top(logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "visualization", tmp_path)
    config = CONFIG
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


def test_visualization(logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "visualization", tmp_path, "properties", "visualization")
    config = CONFIG["visualization"]
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


def test_visualization__eagle_tools(caplog, logged, tmp_path, validator, with_set):
    ok = validator(
        __file__,
        "visualization",
        tmp_path,
        "properties",
        "visualization",
        "properties",
        "eagle_tools",
    )
    config = CONFIG["visualization"]["eagle_tools"]
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
    caplog, logged, tmp_path, validator, with_set
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
    config = CONFIG["visualization"]["eagle_tools"]["leadtimes"]
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
    logged, tmp_path, validator, with_del, with_set
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
    config = CONFIG["visualization"]["spatial_stat_plots"]
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
    logged, tmp_path, validator, with_del, with_set
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
    config = CONFIG["visualization"]["spatial_stat_plots"]["figsize"]
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

from datetime import datetime, timezone

# Schema tests.

CONFIG: dict = {
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
        "execution": {
            # uwtools validates this block.
            "batchargs": {
                "walltime": "01:00:00",
            },
            "executable": "ufs2arco",
        },
        "name": "global",
        "rundir": "/path/to/rundir",
    }
}


def test_top(logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "prewxvx", tmp_path)
    config = CONFIG
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["prewxvx"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have object values:
    for key in ["prewxvx"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")


def test_prewxvx(logged, validator, tmp_path, with_del, with_set):
    ok = validator(__file__, "prewxvx", tmp_path, "properties", "prewxvx")
    config = CONFIG["prewxvx"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are not allowed:
    assert not ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["eagle_tools", "execution", "name", "rundir"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have object values:
    for key in ["eagle_tools", "execution"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")
    # Some keys have string values:
    for key in ["name", "rundir"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")


def test_prewxvx__eagle_tools(logged, validator, tmp_path, with_del, with_set):
    ok = validator(
        __file__,
        "prewxvx",
        tmp_path,
        "properties",
        "prewxvx",
        "properties",
        "eagle_tools",
    )
    config = CONFIG["prewxvx"]["eagle_tools"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
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
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have array values:
    for key in ["levels"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'array'")
    # Some keys have enum values:
    assert not ok(with_set(config, "foo", "model_type"))
    assert logged("'foo' is not one of")
    # Some keys have integer values:
    for key in ["lam_index", "lead_time"]:
        assert not ok(with_set(config, None, key))
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
    logged, validator, tmp_path, with_set
):
    ok = validator(
        __file__,
        "prewxvx",
        tmp_path,
        "properties",
        "prewxvx",
        "properties",
        "eagle_tools",
        "properties",
        "forecast_regrid_kwargs",
    )
    config = CONFIG["prewxvx"]["eagle_tools"]["forecast_regrid_kwargs"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # No keys are required:
    assert ok({})
    # Some keys have object values:
    for key in ["open_target_kwargs", "regridder_kwargs"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")
    # Some keys have string values:
    for key in ["target_grid_path"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")


def test_prewxvx__eagle_tools__forecast_regrid_kwargs__regridder_kwargs(
    logged, validator, tmp_path, with_del, with_set
):
    ok = validator(
        __file__,
        "prewxvx",
        tmp_path,
        "properties",
        "prewxvx",
        "properties",
        "eagle_tools",
        "properties",
        "forecast_regrid_kwargs",
        "properties",
        "regridder_kwargs",
    )
    config = CONFIG["prewxvx"]["eagle_tools"]["forecast_regrid_kwargs"][
        "regridder_kwargs"
    ]
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["method"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have string values:
    for key in ["method"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")


def test_prewxvx__eagle_tools__lcc_info(
    logged, validator, tmp_path, with_del, with_set
):
    ok = validator(
        __file__,
        "prewxvx",
        tmp_path,
        "properties",
        "prewxvx",
        "properties",
        "eagle_tools",
        "properties",
        "lcc_info",
    )
    config = CONFIG["prewxvx"]["eagle_tools"]["lcc_info"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["n_x", "n_y"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have integer values:
    for key in ["n_x", "n_y"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'integer'")


def test_prewxvx__eagle_tools__levels(logged, validator, tmp_path):
    ok = validator(
        __file__,
        "prewxvx",
        tmp_path,
        "properties",
        "prewxvx",
        "properties",
        "eagle_tools",
        "properties",
        "levels",
    )
    config = CONFIG["prewxvx"]["eagle_tools"]["levels"]
    # Basic correctness:
    assert ok(config)
    # An empy list os ok:
    assert ok([])
    # Items must be numbers:
    assert ok([1, 2.2, -3])
    assert not ok([None])
    assert logged("is not of type 'number'")


def test_prewxvx__defs__datetime(caplog, tmp_path, validator):
    ok = validator(__file__, "prewxvx", tmp_path, "$defs", "datetime")
    for val in [datetime(2026, 4, 8, 12, tzinfo=timezone.utc), "2026-04-08T01:23:45"]:
        assert ok(val)
    assert not ok("foo")
    assert "is not valid under any of the given schemas" in caplog.text
    assert "is not of type 'datetime'" in caplog.text
    assert "does not match" in caplog.text

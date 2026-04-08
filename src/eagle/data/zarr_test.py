CONFIG_ZARR: dict = {
    "zarr": {
        "execution": {
            # Rigorous schema checking of this block is provided by uwtools. Provide
            # minimum viable config here.
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


def test_top(logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "zarr", tmp_path)
    config = CONFIG_ZARR
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


def test_zarr(logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "zarr", tmp_path, "properties", "zarr")
    config = CONFIG_ZARR["zarr"]
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


def test_zarr__ufs2arco(logged, tmp_path, validator, with_del, with_set):
    ok = validator(
        __file__, "zarr", tmp_path, "properties", "zarr", "properties", "ufs2arco"
    )
    config = CONFIG_ZARR["zarr"]["ufs2arco"]
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


def test_zarr__ufs2arco__multisource(logged, tmp_path, validator):
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
    config = CONFIG_ZARR["zarr"]["ufs2arco"]["multisource"]
    # Basic correctness:
    assert ok(config)
    # At least one element is required:
    assert not ok([])
    assert logged("should be non-empty")


def test_zarr__ufs2arco__multisource__item(
    logged, tmp_path, validator, with_del, with_set
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
    config = CONFIG_ZARR["zarr"]["ufs2arco"]["multisource"][0]
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
    logged, tmp_path, validator, with_del, with_set
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
    config = CONFIG_ZARR["zarr"]["ufs2arco"]["multisource"][0]["source"]
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

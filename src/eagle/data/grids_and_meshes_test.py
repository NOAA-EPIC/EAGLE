# Schema tests.

CONFIG = {
    "grids_and_meshes": {
        "filenames": {
            "gfs_target_grid": "/path/to/global_one_degree.nc",
            "hrrr_target_grid": "/path/to/hrrr_15km.nc",
            "latent_mesh": "/path/to/latentx2.spongex1.combined.sorted.npz",
        },
        "rundir": "/path/to/rundir",
    },
}


def test_top(logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "grids_and_meshes", tmp_path)
    config = CONFIG
    # Basic correctness:
    assert ok(config)
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["grids_and_meshes"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have object values:
    for key in ["grids_and_meshes"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")


def test_grids_and_meshes(logged, tmp_path, validator, with_del, with_set):
    ok = validator(
        __file__, "grids_and_meshes", tmp_path, "properties", "grids_and_meshes"
    )
    config = CONFIG["grids_and_meshes"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are not allowed:
    assert not ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["filenames", "rundir"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have object values:
    for key in ["filenames"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")
    # Some keys have string values:
    for key in ["rundir"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")


def test_grids_and_meshes__filenames(logged, tmp_path, validator, with_del, with_set):
    ok = validator(
        __file__,
        "grids_and_meshes",
        tmp_path,
        "properties",
        "grids_and_meshes",
        "properties",
        "filenames",
    )
    config = CONFIG["grids_and_meshes"]["filenames"]
    # Basic correctness:
    assert ok(config)
    # Additional keys are not allowed:
    assert not ok(with_set(config, "foo", "bar"))
    # Certain keys are required:
    for key in ["gfs_target_grid", "hrrr_target_grid", "latent_mesh"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Some keys have string values:
    for key in ["gfs_target_grid", "hrrr_target_grid", "latent_mesh"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")

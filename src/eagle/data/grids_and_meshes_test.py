# Schema tests.

CONFIG = {
    "grids_and_meshes": {
        "filenames": {
            "gfs_target_grid": "/path/to/global_one_degree.nc",
            "hrrr_target_grid": "/path/to/hrrr_15km.nc",
            "latent_mesh": "/path/to/latentx2.spongex1.combined.sorted.npz",
        },
        "conus_grid_resolution_km": 15,
        "global_grid_resolution_deg": 1.0,
        "latent_mesh_global_resolution_deg": 2.0,
        "latent_mesh_conus_coarsen_factor": 2,
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
    for key in [
        "conus_grid_resolution_km",
        "filenames",
        "global_grid_resolution_deg",
        "rundir",
    ]:
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


def test_grids_and_meshes__conus_grid_resolution_km(
    logged, tmp_path, validator
):
    ok = validator(
        __file__,
        "grids_and_meshes",
        tmp_path,
        "properties",
        "grids_and_meshes",
        "properties",
        "conus_grid_resolution_km",
    )
    # Basic correctness:
    assert ok(6)
    assert ok(15)
    # Invalid values:
    assert not ok(4)
    assert logged("is not a multiple of 3")
    assert not ok(1)
    assert logged("is less than the minimum of 3")
    assert not ok("6")
    assert logged("is not of type 'integer'")


def test_grids_and_meshes__global_grid_resolution_deg(
    logged, tmp_path, validator
):
    ok = validator(
        __file__,
        "grids_and_meshes",
        tmp_path,
        "properties",
        "grids_and_meshes",
        "properties",
        "global_grid_resolution_deg",
    )
    # Basic correctness:
    assert ok(0.25)
    assert ok(1.0)
    # Invalid values:
    assert not ok(2.0)
    assert logged("is not one of [0.25, 1.0]")
    assert not ok("1.0")
    assert logged("is not of type 'number'")


def test_grids_and_meshes__latent_mesh_global_resolution_deg(
    logged, tmp_path, validator
):
    ok = validator(
        __file__,
        "grids_and_meshes",
        tmp_path,
        "properties",
        "grids_and_meshes",
        "properties",
        "latent_mesh_global_resolution_deg",
    )
    # Basic correctness:
    assert ok(2.0)
    # Invalid values:
    assert not ok(0.0)
    assert logged("is less than or equal to the minimum of 0")
    assert not ok(-1.0)
    assert logged("is less than or equal to the minimum of 0")
    assert not ok("2.0")
    assert logged("is not of type 'number'")


def test_grids_and_meshes__latent_mesh_conus_coarsen_factor(
    logged, tmp_path, validator
):
    ok = validator(
        __file__,
        "grids_and_meshes",
        tmp_path,
        "properties",
        "grids_and_meshes",
        "properties",
        "latent_mesh_conus_coarsen_factor",
    )
    # Basic correctness:
    assert ok(1)
    assert ok(2)
    # Invalid values:
    assert not ok(0)
    assert logged("is less than the minimum of 1")
    assert not ok(1.5)
    assert logged("is not of type 'integer'")


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
    # Optional keys:
    for key in ["gfs_target_grid", "hrrr_target_grid", "latent_mesh"]:
        assert ok(with_del(config, key))
    # Some keys have string values:
    for key in ["gfs_target_grid", "hrrr_target_grid", "latent_mesh"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'string'")


def test_grids_and_meshes__latent_mesh_settings_conditional_required(
    logged, tmp_path, validator, with_del, with_set
):
    ok = validator(
        __file__, "grids_and_meshes", tmp_path, "properties", "grids_and_meshes"
    )
    config = CONFIG["grids_and_meshes"]
    # If latent mesh is requested, latent mesh settings are required.
    assert not ok(with_del(config, "latent_mesh_global_resolution_deg"))
    assert logged("'latent_mesh_global_resolution_deg' is a required property")
    assert not ok(with_del(config, "latent_mesh_conus_coarsen_factor"))
    assert logged("'latent_mesh_conus_coarsen_factor' is a required property")
    # If latent mesh is not requested, latent mesh settings may be omitted.
    filenames_without_latent_mesh = with_del(config["filenames"], "latent_mesh")
    config_without_latent_mesh = with_set(
        config, filenames_without_latent_mesh, "filenames"
    )
    assert ok(with_del(config_without_latent_mesh, "latent_mesh_global_resolution_deg"))
    assert ok(with_del(config_without_latent_mesh, "latent_mesh_conus_coarsen_factor"))

CONFIG_ZARR = {
    "zarr": {
        "execution": {
            # uwtools provides rigorous schema checking of this block, so only a
            # minimal treatment is given here.
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


def test_zarr(logged, tmp_path, validator, with_del, with_set):
    ok = validator(__file__, "zarr", tmp_path)
    config = CONFIG_ZARR
    # Basic correctness:
    assert ok(config)
    # Certain top-level keys are required:
    for key in ["zarr"]:
        assert not ok(with_del(config, key))
        assert logged(f"'{key}' is a required property")
    # Additional keys are allowed:
    assert ok(with_set(config, "foo", "bar"))
    # Some keys have object values:
    for key in ["zarr"]:
        assert not ok(with_set(config, None, key))
        assert logged("is not of type 'object'")

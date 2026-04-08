from datetime import datetime, timedelta, timezone

# Schema tests.


def test_top():
    pass


def test_visualization__defs__datetime(caplog, tmp_path, validator):
    ok = validator(__file__, "visualization", tmp_path, "$defs", "datetime")
    for val in [datetime(2026, 4, 8, 12, tzinfo=timezone.utc), "2026-04-08T01:23:45"]:
        assert ok(val)
    assert not ok("foo")
    assert "is not valid under any of the given schemas" in caplog.text
    assert "is not of type 'datetime'" in caplog.text
    assert "does not match" in caplog.text


def test_visualization__defs__timedelta(caplog, tmp_path, validator):
    ok = validator(__file__, "visualization", tmp_path, "$defs", "timedelta")
    for val in [timedelta(hours=6), 6, "6", "06", "06:00", "06:00:00"]:
        assert ok(val)
    assert not ok("foo")
    assert "is not valid under any of the given schemas" in caplog.text
    assert "is not of type 'timedelta'" in caplog.text
    assert "is not of type 'integer'" in caplog.text
    assert "does not match" in caplog.text

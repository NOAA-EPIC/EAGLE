import json
import re
from collections.abc import Callable
from copy import deepcopy
from pathlib import Path
from typing import Any

from iotaa import Asset, task
from pytest import fixture
from uwtools.api.config import validate


@fixture
def logged(caplog):
    def f(s: str):
        found = any(re.match(rf"^.*{s}.*$", message) for message in caplog.messages)
        caplog.clear()
        return found

    return f


@fixture
def readytask():
    @task
    def f(*_args, **_kwargs):
        yield "readyteask"
        yield Asset(None, lambda: True)
        yield None

    return f


@fixture
def validator():
    def f(testpath: str, name: str, tmp_path: Path, *args: Any) -> Callable:
        """
        Returns a lambda that validates an eventual config argument.

        :param testpath: Path to calling test module.
        :param name: Schema filename stem in driver package directory.
        :param args: Keys leading to sub-schema to be used to validate config.
        """
        schema = json.loads((Path(testpath).parent / f"{name}.jsonschema").read_text())
        defs = schema.get("$defs", {})
        for arg in args:
            schema = schema[arg]
        if args and args[0] != "$defs":
            schema.update({"$defs": defs})
        path = tmp_path / "test.schema"
        path.write_text(json.dumps(schema))
        return lambda c: validate(schema_file=path, config_data=c)

    return f


@fixture
def with_del():
    def f(d: dict, *args: Any) -> dict:
        """
        Delete a value at a given chain of keys in a dict.

        :param d: The dict to update.
        :param args: One or more keys navigating to the value to delete.
        """
        new = deepcopy(d)
        p = new
        for key in args[:-1]:
            p = p[key]
        del p[args[-1]]
        return new

    return f


@fixture
def with_set():
    def f(d: dict, val: Any, *args: Any) -> dict:
        """
        Set a value at a given chain of keys in a dict.

        :param d: The dict to update.
        :param val: The value to set.
        :param args: One or more keys navigating to the value to set.
        """
        new = deepcopy(d)
        p = new
        for key in args[:-1]:
            p = p[key]  # pragma: no cover
        p[args[-1]] = val
        return new

    return f

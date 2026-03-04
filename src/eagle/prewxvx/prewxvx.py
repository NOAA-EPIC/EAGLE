from pathlib import Path
from typing import cast

from iotaa import Asset, collection, task
from uwtools.api.config import get_yaml_config
from uwtools.api.driver import DriverTimeInvariant


class PreWXVX(DriverTimeInvariant):
    """
    Prepares the config for and runs eagle-tools' prewxvx component.
    """

    # Public tasks

    @task
    def eagle_tools_config(self):
        """
        Prewxvx config for this run, provisioned to the rundir.
        """
        yield self.taskname(f"{self.driver_name()} {self._name} config")
        path = self.rundir / f"{self.driver_name()}-{self._name}.yaml"
        yield Asset(path, path.is_file)
        yield None
        path.parent.mkdir(parents=True, exist_ok=True)
        get_yaml_config(self.config["eagle_tools"]).dump(path)

    @collection
    def provisioned_rundir(self):
        """
        Run directory provisioned with all required content.
        """
        yield self.taskname(f"{self._name} provisioned run directory")
        yield [
            self.eagle_tools_config(),
            self.runscript(),
        ]

    # Public methods

    @classmethod
    def driver_name(cls) -> str:
        return "prewxvx"

    # Private methods

    @property
    def _name(self) -> str:
        return cast("str", self.config["name"])

    @property
    def _runscript_path(self) -> Path:
        return self.rundir / f"runscript.{self.driver_name()}-{self._name}"

from pathlib import Path
from typing import cast

from iotaa import Asset, collection, task
from uwtools.api.config import get_yaml_config
from uwtools.api.driver import DriverTimeInvariant


class VX(DriverTimeInvariant):
    """
    Run verification for a single method (grid2grid or grid2obs) and domain (global or
    lam).
    """

    @collection
    def provisioned_rundir(self):
        """
        Run directory provisioned with all required content.
        """
        yield self.taskname(f"{self._name} provisioned run directory")
        yield [
            self.runscript(),
            self.wxvx_config(),
        ]

    @task
    def wxvx_config(self):
        """
        The wxvx config, provisioned to the rundir.
        """
        yield self.taskname(f"{self._name} config")
        path = self.rundir / f"{self.driver_name()}-{self._name}.yaml"
        yield Asset(path, path.is_file)
        yield None
        get_yaml_config(self.config["wxvx"]).dump(path)

    # Public methods

    @classmethod
    def driver_name(cls) -> str:
        return "vx"

    # Private methods

    @property
    def _name(self) -> str:
        return cast("str", self.config["name"])

    @property
    def _runscript_path(self) -> Path:
        return self.rundir / f"runscript.{self.driver_name()}-{self._name}"

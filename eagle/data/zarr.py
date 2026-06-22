from pathlib import Path
from typing import cast

from iotaa import Asset, collection, task  # provided by uwtools
from uwtools.api.config import get_yaml_config
from uwtools.api.driver import DriverTimeInvariant


class Zarr(DriverTimeInvariant):
    """
    Creates Zarr-formatted training datasets.
    """

    # Public tasks

    @collection
    def provisioned_rundir(self):
        """
        Run directory provisioned with all required content.
        """
        yield self.taskname(f"{self._name} provisioned run directory")
        yield [
            self.runscript(),
            self.ufs2arco_config(),
        ]

    @task
    def ufs2arco_config(self):
        """
        The ufs2arco config, provisioned to the rundir.
        """
        yield self.taskname(f"ufs2arco {self._name} config")
        path = self.rundir / f"ufs2arco-{self._name}.yaml"
        yield Asset(path, path.is_file)
        yield None
        get_yaml_config(self.config["ufs2arco"]).dump(path)

    # Public methods

    @classmethod
    def driver_name(cls) -> str:
        return "zarr"

    # Private methods

    @property
    def _name(self) -> str:
        return cast("str", self.config["name"])

    @property
    def _runscript_path(self) -> Path:
        return self.rundir / f"runscript.{self.driver_name()}-{self._name}"

from pathlib import Path
from typing import cast

from iotaa import Asset, collection, task  # provided by uwtools
from uwtools.api.config import get_yaml_config
from uwtools.api.driver import DriverTimeInvariant


class WXVX(DriverTimeInvariant):
    """
    Run verification for a single method (grid2grid or grid2obs) and domain (global or
    lam).
    """

    @task
    def prewxvx(self):
        """
        todo
        global or lam
        """
        yield self.taskname(f"{self.driver_name()} {self._name}")
        path = self.rundir / f"prewxvx-{self._name}.yaml"
        vx_dir = Path(self.config["eagle_tools"]["work_path"])
        ncfiles = {var: vx_dir / f"{var}.nc" for var in self.config["variables"]}
        yield {
            "config": Asset(path, path.is_file),
            **{var: Asset(ncpath, ncpath.is_file) for var, ncpath in ncfiles.items()},
        }
        yield None
        path.parent.mkdir(parents=True, exist_ok=True)
        get_yaml_config(self.config["eagle_tools"]).dump(path)
        logfile = self.rundir / "prewxvx.log"
        run(
            "eagle-tools prewxvx prewxvx-%s.yaml >%s 2>&1" % (self._name, logfile),
            check=False,
            cwd=self.rundir,
            shell=True,
        )

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
        return "wxvx"

    # Private methods

    @property
    def _name(self) -> str:
        return cast("str", self.config["name"])

    @property
    def _runscript_path(self) -> Path:
        return self.rundir / f"runscript.{self.driver_name()}-{self._name}"

from pathlib import Path
from subprocess import run
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
        Prepares netCDF files for wxvx.
        """
        extent = "global" if "global" in self._name else "lam"
        yield self.taskname(f"prewxvx {extent}")
        nc_dir = Path(self.config["prewxvx"]["eagle_tools"]["output_path"])
        pre_dir = Path(self.config["prewxvx"]["rundir"])
        pre_path = pre_dir / f"prewxvx-{extent}.yaml"
        nc = f"nested-{extent}.*.nc"
        yield {
            "config": Asset(pre_path, pre_path.is_file),
            "ncfiles": Asset(nc_dir, lambda: any(nc_dir.glob(nc))),
        }
        yield None
        pre_path.parent.mkdir(parents=True, exist_ok=True)
        nc_dir.mkdir(parents=True, exist_ok=True)
        get_yaml_config(self.config["prewxvx"]["eagle_tools"]).dump(pre_path)
        logfile = pre_dir / "prewxvx.log"
        run(
            "eagle-tools prewxvx %s >%s 2>&1" % (pre_path, logfile),
            check=False,
            cwd=pre_dir,
            shell=True,
        )

    @collection
    def provisioned_rundir(self):
        """
        Run directory provisioned with all required content.
        """
        yield self.taskname(f"{self._name} provisioned run directory")
        yield [
            self.prewxvx(),
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

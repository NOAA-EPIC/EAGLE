from pathlib import Path
from subprocess import run
from typing import cast

import matplotlib as mpl
import matplotlib.pyplot as plt
import xarray as xr
from iotaa import Asset, collection, task
from uwtools.api.config import get_yaml_config
from uwtools.api.driver import AssetsTimeInvariant

mpl.use("Agg")


class Visualization(AssetsTimeInvariant):
    """
    Plots wxvx output from postwxvx's netCDF files.
    """

    # Public tasks

    @collection
    def plots(self):
        """
        Plots for all variables and stats.
        """
        yield self.taskname(f"{self._name} plots")
        yield [
            self._plot(var, stat)
            for var in self.config["variables"]
            for stat in self.config["stats"]
        ]

    @task
    def postwxvx(self):
        """
        Creates postwxvx config and runs eagle-tools.
        """
        yield self.taskname(f"{self.driver_name()} {self._name} config")
        path = self.rundir / f"postwxvx-{self._name}.yaml"
        yield Asset(path, path.is_file)
        yield None
        path.parent.mkdir(parents=True, exist_ok=True)
        get_yaml_config(self.config["eagle_tools"]).dump(path)
        logfile = self.rundir / "postwxvx.log"
        run(
            "eagle-tools postwxvx postwxvx-%s.yaml >%s 2>&1" % (self._name, logfile),
            check=False,
            cwd=self.rundir,
            shell=True,
        )

    @collection
    def provisioned_rundir(self):
        """
        Run directory provisioned with all required content.
        """
        yield self.taskname("provisioned run directory")
        yield [
            self.plots(),
            self.postwxvx(),
        ]

    # Private tasks

    @task
    def _plot(self, var: str, stat: str):
        yield self.taskname(f"{self._name} {var} {stat} plot")
        path = self.rundir / f"{var}_{stat}.png"
        yield Asset(path, path.is_file)
        req = self.postwxvx()
        yield req
        self.rundir.mkdir(parents=True, exist_ok=True)
        nc = Path(self.config["eagle_tools"]["work_path"]) / f"{var}.nc"
        ds = xr.open_dataset(nc)
        var_stat = cast("xr.DataArray", ds[stat])
        var_stat.plot()  # type: ignore[call-arg]
        plt.savefig(path)
        plt.close()

    # Public methods

    @classmethod
    def driver_name(cls) -> str:
        return "visualization"

    # Private methods

    @property
    def _name(self) -> str:
        return cast("str", self.config["name"])

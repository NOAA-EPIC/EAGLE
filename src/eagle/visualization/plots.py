from pathlib import Path
from typing import cast

import matplotlib
import matplotlib.pyplot as plt
import xarray as xr
from iotaa import Asset, collection, task
from uwtools.api.config import get_yaml_config
from uwtools.api.driver import AssetsTimeInvariant
from xarray import Dataset
matplotlib.use("Agg")


class Plots(AssetsTimeInvariant):
    """
    Plots postwxvx output. 
    """

    # Public tasks

    @collection
    def plots(self):
        """Plots for all variables and stats."""
        yield self.taskname(f"{self._name} plots")
        yield [
            self._plot(var, stat)
            for var in self.config["variables"]
            for stat in self.config["stats"]
        ]


    @collection
    def provisioned_rundir(self):
        """
        Run directory provisioned with all required content.
        """
        yield self.taskname("provisioned run directory")
        yield [
            self.plots(),
        ]
    
    # Private tasks

    @task
    def _plot(self, var: str, stat: str):
        yield self.taskname(f"{self._name} {var} {stat} plot")
        path = self.rundir / f"{var}_{stat}.png"
        yield Asset(path, path.is_file)
        yield None
        self.rundir.mkdir(parents=True, exist_ok=True)
        nc = Path(self.config["netcdfs"]) / f"{var}.nc"
        ds = xr.open_dataset(nc)
        ds[stat].plot()
        plt.savefig(path)
        plt.close()

    # Public methods

    @classmethod
    def driver_name(cls) -> str:
        return "plots"
    
    # Private methods

    @property
    def _name(self) -> str:
        return cast("str", self.config["name"])

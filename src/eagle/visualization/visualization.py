from pathlib import Path
from subprocess import run
from typing import cast

import matplotlib as mpl
import matplotlib.pyplot as plt
import xarray as xr
from iotaa import Asset, collection, task
from uwtools.api.config import get_yaml_config
from uwtools.api.driver import AssetsTimeInvariant

from eagle.visualization.plot_wxvx_stats_var import run_spatial_stat_plots

mpl.use("Agg")


class Visualization(AssetsTimeInvariant):
    """
    Plots wxvx output from postwxvx's netCDF files and optionally generates
    grid2grid spatial-stat plots into the existing vx run/plots directories.
    """

    # Public tasks

    @collection
    def plots(self):
        """
        Plots for all variables and stats, plus optional grid2grid spatial-stat plots.
        """
        yield self.taskname(f"{self._name} plots")

        tasks = [
            self._plot(var, stat)
            for var in self.config["variables"]
            for stat in self.config["stats"]
        ]

        spatial_cfg = self._grid2grid_spatial_cfg
        if spatial_cfg.get("enabled", False):
            tasks.append(self.spatial_stat_plots())

        yield tasks

    @task
    def postwxvx(self):
        """
        Prepares postwxvx config, runs eagle-tools, and produces one netCDF file per
        output variable.
        """
        yield self.taskname(f"{self.driver_name()} {self._name}")
        path = self.rundir / f"postwxvx-{self._name}.yaml"
        vx_dir = Path(self.config["eagle_tools"]["work_path"])
        ncfiles = {var: vx_dir / f"{var}.nc" for var in self.config["variables"]}
        yield {
            "config": Asset(path, path.is_file),
            **{var: Asset(ncpath, ncpath.is_file) for var, ncpath in ncfiles.items()},
        }
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

    @task
    def spatial_stat_plots(self):
        """
        Generate grid2grid spatial-stat plots from verification NetCDF files and
        write PNGs into the same vx/grid2grid/*/run/plots directories used by the
        existing verification outputs.
        """
        yield self.taskname(f"{self._name} spatial stat plots")

        spatial_cfg = self._grid2grid_spatial_cfg
        lam_plots_root = Path(spatial_cfg["lam_plots_root"])
        global_plots_root = Path(spatial_cfg["global_plots_root"])

        yield {
            "lam_plots_root": Asset(lam_plots_root, lam_plots_root.is_dir),
            "global_plots_root": Asset(global_plots_root, global_plots_root.is_dir),
        }

        req = self.postwxvx()
        yield req
        yield None

        lam_plots_root.mkdir(parents=True, exist_ok=True)
        global_plots_root.mkdir(parents=True, exist_ok=True)

        run_spatial_stat_plots(
            lam_stats_root=spatial_cfg["lam_stats_root"],
            lam_plots_root=spatial_cfg["lam_plots_root"],
            global_stats_root=spatial_cfg["global_stats_root"],
            global_plots_root=spatial_cfg["global_plots_root"],
            pattern=spatial_cfg.get("pattern", "*.nc"),
            lam_prefix=spatial_cfg.get("lam_prefix", "grid_stat_nested"),
            global_prefix=spatial_cfg.get("global_prefix", "grid_stat_nested"),
            vmin=spatial_cfg.get("vmin"),
            vmax=spatial_cfg.get("vmax"),
            cmap=spatial_cfg.get("cmap", "RdBu_r"),
            figsize=spatial_cfg.get("figsize", "9.75,4.875"),
            add_states=bool(spatial_cfg.get("add_states", False)),
            gridlines=bool(spatial_cfg.get("gridlines", False)),
            max_files=int(spatial_cfg.get("max_files", 0)),
            file_fontsize=float(spatial_cfg.get("file_fontsize", 8.0)),
            title_fontsize=float(spatial_cfg.get("title_fontsize", 11.0)),
            suptitle_y=float(spatial_cfg.get("suptitle_y", 0.995)),
        )

    # Private tasks

    @task
    def _plot(self, var: str, stat: str):
        yield self.taskname(f"{self._name} {var} {stat} plot")
        path = self.rundir / f"{var}_{stat}.png"
        yield Asset(path, path.is_file)

        req = self.postwxvx()
        yield req

        ds = xr.open_dataset(req.ref[var])
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

    @property
    def _grid2grid_spatial_cfg(self) -> dict:
        """
        Read the shared grid2grid spatial plotting config added under
        visualization.grid2grid.spatial_stat_plots in base.yaml.
        """
        root_cfg = get_yaml_config(self.config["config"])
        return cast(
            "dict",
            root_cfg["visualization"]["grid2grid"]["spatial_stat_plots"],
        )

import logging
from pathlib import Path
from subprocess import run
from typing import TYPE_CHECKING, Any, cast

import cartopy.crs as ccrs  # type: ignore[import-untyped]
import cartopy.feature as cfeature  # type: ignore[import-untyped]
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
from iotaa import Asset, Node, collection, task  # provided by uwtools
from uwtools.api.config import get_yaml_config
from uwtools.api.driver import AssetsTimeInvariant

if TYPE_CHECKING:
    from cartopy.mpl.geoaxes import GeoAxes  # type: ignore[import-untyped]

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
        reqs: list[Node] = [
            self._plot(var, stat)
            for var in self.config["variables"]
            for stat in self.config["stats"]
        ]
        if self.config.get("spatial_stat_plots"):
            reqs.append(self.spatial_stat_plots())
        yield reqs

    @task
    def postwxvx(self):
        """
        netCDF files from eagle-tools per output variable.
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

    @collection
    def spatial_stat_plots(self):
        """
        Spatial-stat PNG plots of all grid2grid verification results.
        """
        yield self.taskname(f"{self._name} spatial stat plots")
        extent = "global" if "global" in self.config["name"] else "lam"
        stats_root = Path(self.config["spatial_stat_plots"]["stats_root"] % extent)
        ncpaths = sorted(stats_root.rglob("grid_stat_*_pairs.nc"))
        outdir = Path(self.config["rundir"], "plots-spatial-stats")
        pngpath = lambda ncpath: outdir / f"{ncpath.stem}_spatial.png"
        yield [self._spatial_stat_plot(ncpath, pngpath(ncpath)) for ncpath in ncpaths]

    # Private tasks

    @task
    def _spatial_stat_plot(self, ncpath: Path, pngpath: Path):
        """
        Spatial-stat PNG plot of one grid2grid verification result.
        """
        taskname = self.taskname(f"{self._name} spatial stat plot {pngpath.name}")
        yield taskname
        yield Asset(pngpath, pngpath.is_file)
        yield None
        cfg = self.config["spatial_stat_plots"]
        logging.debug("%s: Plotting %s -> %s", taskname, ncpath, pngpath)
        ds = xr.open_dataset(ncpath)
        var = _choose_diff_var(ds)
        if var is None:
            logging.error("%s: No DIFF_ var in %s", taskname, ncpath)
            return
        # if "lat" not in ds:
        #     logging.error("%s: Missing lat in %s", taskname, ncpath)
        #     return
        # if "lon" not in ds:
        #     logging.error("%s: Missing lon in %s", taskname, ncpath)
        #     return
        lat2d = np.asarray(ds["lat"].values)
        lon2d = _to_lon180(np.asarray(ds["lon"].values))
        da = _mask_fill(_pick_2d(ds[var]))
        vmin, vmax = _finite_min_max(da)
        fig = plt.figure(figsize=(cfg["figsize"]["w"], cfg["figsize"]["h"]))
        fig.suptitle(ncpath.name, fontsize=cfg["file_fontsize"], y=cfg["suptitle_y"])
        ax = cast("GeoAxes", plt.axes(projection=ccrs.PlateCarree()))
        extent = list(
            map(
                float,
                [
                    np.nanmin(lon2d),
                    np.nanmax(lon2d),
                    np.nanmin(lat2d),
                    np.nanmax(lat2d),
                ],
            )
        )
        extent = [
            float(x)
            for x in (
                np.nanmin(lon2d),
                np.nanmax(lon2d),
                np.nanmin(lat2d),
                np.nanmax(lat2d),
            )
        ]
        ax.set_extent(extent, crs=ccrs.PlateCarree())
        mesh = ax.pcolormesh(
            lon2d,
            lat2d,
            np.asarray(da.values),
            transform=ccrs.PlateCarree(),
            vmin=vmin,
            vmax=vmax,
            cmap=cfg["cmap"],
        )
        ax.coastlines(resolution="50m", linewidth=0.8)
        ax.add_feature(cfeature.BORDERS, linewidth=0.6)
        if cfg["add_states"]:
            ax.add_feature(cfeature.STATES, linewidth=0.4)
        if cfg["gridlines"]:
            gl: Any = ax.gridlines(draw_labels=True, linewidth=0.3, alpha=0.6)
            gl.right_labels = False
            gl.top_labels = False
        ax.set_title(_build_main_title(ds, var), fontsize=cfg["title_fontsize"])
        units = str(ds[var].attrs.get("units", "")).strip()
        cb = fig.colorbar(
            mesh, ax=ax, orientation="horizontal", pad=0.12, fraction=0.06
        )
        cb.set_label(units or var)
        plt.tight_layout(rect=(0, 0, 1, 0.94))
        pngpath.parent.mkdir(parents=True, exist_ok=True)
        plt.savefig(pngpath, dpi=150)
        plt.close(fig)
        logging.info("%s: Wrote %s", taskname, pngpath.name)

    @task
    def _plot(self, var: str, stat: str):
        yield self.taskname(f"{self._name} {var} {stat} plot")
        path = self.rundir / "plots-basic" / f"{var}_{stat}.png"
        yield Asset(path, path.is_file)
        req = self.postwxvx()
        yield req
        path.parent.mkdir(parents=True, exist_ok=True)
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


def _build_main_title(ds: xr.Dataset, var: str) -> str:
    long_name = str(ds[var].attrs.get("long_name", "")).strip() or var
    init_time = str(ds[var].attrs.get("init_time", "")).strip()
    valid_time = str(ds[var].attrs.get("valid_time", "")).strip()
    diff_desc = str(ds.attrs.get("Difference", "")).strip()
    lines: list[str] = [long_name]
    if init_time or valid_time:
        lines.append(f"init={init_time}  valid={valid_time}")
    if diff_desc:
        lines.append(f"Difference: {diff_desc}")
    return "\n".join(lines)


def _choose_diff_var(ds: xr.Dataset) -> str | None:
    for k in ds.data_vars:
        v = cast("str", k)
        if v.startswith("DIFF_"):
            return v
    return None


def _finite_min_max(da: xr.DataArray) -> tuple[float, float]:
    a = np.asarray(da.values).astype("float64", copy=False)
    a = a[np.isfinite(a)]
    if a.size == 0:
        msg = "All values are NaN/inf after masking fill values."
        raise ValueError(msg)
    return float(a.min()), float(a.max())


def _infer_date_hour_from_path(nc_path: Path) -> tuple[str, str]:
    parts = nc_path.parts
    yyyymmdd = "unknown_date"
    hh = "unknown_hour"
    for i, part in enumerate(parts):
        if len(part) == 8 and part.isdigit():
            yyyymmdd = part
            if i + 1 < len(parts) and len(parts[i + 1]) == 2 and parts[i + 1].isdigit():
                hh = parts[i + 1]
            break
    return yyyymmdd, hh


def _mask_fill(da: xr.DataArray) -> xr.DataArray:
    fill = da.attrs.get("_FillValue", None)
    if fill is None:
        fill = da.encoding.get("_FillValue", None)
        miss = da.attrs.get("missing_value", None)
    out = da
    if fill is not None:
        out = out.where(out != fill)
    if miss is not None:
        out = out.where(out != miss)
    return out


def _pick_2d(da: xr.DataArray) -> xr.DataArray:
    out = da
    while out.ndim > 2:
        out = out.isel({out.dims[0]: 0})
    return out


def _to_lon180(lon2d: np.ndarray) -> np.ndarray:
    lon = np.asarray(lon2d, dtype="float64")
    return ((lon + 180.0) % 360.0) - 180.0

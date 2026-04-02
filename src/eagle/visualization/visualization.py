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
from iotaa import Asset, collection, task  # provided by uwtools
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
        reqs = [
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

    @task
    def spatial_stat_plots(self):
        """
        Spatial-stat PNG plots of grid2grid verification results.
        """
        yield self.taskname(f"{self._name} spatial stat plots")
        yield Asset(None, lambda: False)
        # yield {
        #     "lam_plots_root": Asset(lam_plots_root, lam_plots_root.is_dir),
        #     "global_plots_root": Asset(global_plots_root, global_plots_root.is_dir),
        # }
        yield self.postwxvx()
        extent = "global" if "global" in self.config["name"] else "lam"
        sspcfg = self.config["spatial_stat_plots"]
        _process_one_target(
            plots_root=Path(self.config["rundir"]) / "spatial-stat-plots" / extent,
            extent=extent,
            add_states=sspcfg["add_states"],
            cmap=sspcfg["cmap"],
            figsize=sspcfg["figsize"],
            file_fontsize=sspcfg["file_fontsize"],
            gridlines=sspcfg["gridlines"],
            max_files=sspcfg["max_files"],
            pattern=sspcfg["pattern"],
            prefix=sspcfg["prefix"],
            stats_root=sspcfg["stats_root"],
            suptitle_y=sspcfg["suptitle_y"],
            title_fontsize=sspcfg["title_fontsize"],
            vmax_arg=sspcfg["vmax"],
            vmin_arg=sspcfg["vmin"],
        )
        # _process_one_target(
        #     **common,
        # )
        # _process_one_target(
        #     label="LAM",
        #     stats_root=Path(lam_stats_root),
        #     plots_root=Path(lam_plots_root),
        #     prefix=lam_prefix,
        #     **common,
        # )
        # _run_spatial_stat_plots(
        #     lam_stats_root=spatial_cfg["lam_stats_root"],
        #     lam_plots_root=spatial_cfg["lam_plots_root"],
        #     global_stats_root=spatial_cfg["global_stats_root"],
        #     global_plots_root=spatial_cfg["global_plots_root"],
        #     pattern=spatial_cfg.get("pattern", "*.nc"),
        #     lam_prefix=spatial_cfg.get("lam_prefix", "grid_stat_nested"),
        #     global_prefix=spatial_cfg.get("global_prefix", "grid_stat_nested"),
        #     vmin=spatial_cfg.get("vmin"),
        #     vmax=spatial_cfg.get("vmax"),
        #     cmap=spatial_cfg.get("cmap", "RdBu_r"),
        #     figsize=spatial_cfg.get("figsize", "9.75,4.875"),
        #     add_states=bool(spatial_cfg.get("add_states", False)),
        #     gridlines=bool(spatial_cfg.get("gridlines", False)),
        #     max_files=int(spatial_cfg.get("max_files", 0)),
        #     file_fontsize=float(spatial_cfg.get("file_fontsize", 8.0)),
        #     title_fontsize=float(spatial_cfg.get("title_fontsize", 11.0)),
        #     suptitle_y=float(spatial_cfg.get("suptitle_y", 0.995)),
        # )

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


def _out_png_for_nc(nc_path: Path, plots_root: Path) -> Path:
    yyyymmdd, hh = _infer_date_hour_from_path(nc_path)
    out_dir = plots_root / yyyymmdd / hh
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir / f"{nc_path.stem}_spatial.png"


def _pick_2d(da: xr.DataArray) -> xr.DataArray:
    out = da
    while out.ndim > 2:
        out = out.isel({out.dims[0]: 0})
    return out


def _process_one_target(  # noqa: C901
    *,
    add_states: bool,
    cmap: str,
    figsize: dict[str, float],
    file_fontsize: float,
    gridlines: bool,
    extent: str,
    max_files: int,
    pattern: str,
    plots_root: Path,
    prefix: str,
    stats_root: str,
    suptitle_y: float,
    title_fontsize: float,
    vmax_arg: float | None,
    vmin_arg: float | None,
) -> tuple[int, int]:
    stats_path = Path(stats_root % extent)
    if not stats_path.exists():
        logging.warning("[%s] SKIP: stats root not found: %s", extent, stats_path)
        return (0, 0)
    plots_root.mkdir(parents=True, exist_ok=True)
    found = sorted(stats_path.rglob(pattern))
    if not found:
        logging.warning(
            "[%s] No files matched under: %s (pattern=%s)", extent, stats_path, pattern
        )
        return (0, 0)
    nc_files = [p for p in found if p.name.startswith(prefix)]
    logging.warning(
        "[%s] Found %s files, keeping %s with prefix %s",
        extent,
        len(found),
        len(nc_files),
        prefix,
    )
    plotted = 0
    skipped = 0
    for idx, nc_path in enumerate(nc_files, start=1):
        if max_files and idx > max_files:
            break
        out_png = _out_png_for_nc(nc_path, plots_root)
        try:
            ds = xr.open_dataset(nc_path)
            var = _choose_diff_var(ds)
            if var is None:
                skipped += 1
                logging.warning("[%s] SKIP (no DIFF_ var): %s", extent, nc_path.name)
                continue
            if "lat" not in ds or "lon" not in ds:
                skipped += 1
                logging.warning(
                    "[%s]  SKIP (missing lat/lon): %s", extent, nc_path.name
                )
                continue
            lat2d = np.asarray(ds["lat"].values)
            lon2d = _to_lon180(np.asarray(ds["lon"].values))
            da = _mask_fill(_pick_2d(ds[var]))
            if vmin_arg is None or vmax_arg is None:
                auto_vmin, auto_vmax = _finite_min_max(da)
                vmin = auto_vmin if vmin_arg is None else vmin_arg
                vmax = auto_vmax if vmax_arg is None else vmax_arg
            else:
                vmin, vmax = vmin_arg, vmax_arg
            fig = plt.figure(figsize=(figsize["w"], figsize["h"]))
            fig.suptitle(f"({nc_path.name})", fontsize=file_fontsize, y=suptitle_y)
            ax = cast("GeoAxes", plt.axes(projection=ccrs.PlateCarree()))
            ax.set_extent(
                [
                    float(np.nanmin(lon2d)),
                    float(np.nanmax(lon2d)),
                    float(np.nanmin(lat2d)),
                    float(np.nanmax(lat2d)),
                ],
                crs=ccrs.PlateCarree(),
            )
            mesh = ax.pcolormesh(
                lon2d,
                lat2d,
                np.asarray(da.values),
                transform=ccrs.PlateCarree(),
                vmin=vmin,
                vmax=vmax,
                cmap=cmap,
            )
            ax.coastlines(resolution="50m", linewidth=0.8)
            ax.add_feature(cfeature.BORDERS, linewidth=0.6)
            if add_states:
                ax.add_feature(cfeature.STATES, linewidth=0.4)
            if gridlines:
                gl: Any = ax.gridlines(draw_labels=True, linewidth=0.3, alpha=0.6)
                gl.right_labels = False
                gl.top_labels = False
            ax.set_title(_build_main_title(ds, var), fontsize=title_fontsize)
            units = str(ds[var].attrs.get("units", "")).strip()
            cb = fig.colorbar(
                mesh, ax=ax, orientation="horizontal", pad=0.12, fraction=0.06
            )
            cb.set_label(units or var)
            plt.tight_layout(rect=(0, 0, 1, 0.94))
            plt.savefig(out_png, dpi=150)
            plt.close(fig)
            plotted += 1
            logging.warning("[%s] WROTE: %s", extent, out_png)
        except Exception as e:  # noqa: BLE001
            skipped += 1
            logging.warning("[%s]  SKIP (error): %s -> %s", extent, nc_path.name, e)
    return (plotted, skipped)


def _to_lon180(lon2d: np.ndarray) -> np.ndarray:
    lon = np.asarray(lon2d, dtype="float64")
    return ((lon + 180.0) % 360.0) - 180.0


# def _run_spatial_stat_plots(
#     *,
#     lam_stats_root: str,
#     lam_plots_root: str,
#     global_stats_root: str,
#     global_plots_root: str,
#     pattern: str = "*.nc",
#     lam_prefix: str = "grid_stat_nested",
#     global_prefix: str = "grid_stat_nested",
#     vmin: float | None = None,
#     vmax: float | None = None,
#     cmap: str = "RdBu_r",
#     figsize: str = "9.75,4.875",
#     add_states: bool = False,
#     gridlines: bool = False,
#     max_files: int = 0,
#     file_fontsize: float = 8.0,
#     title_fontsize: float = 11.0,
#     suptitle_y: float = 0.995,
# ) -> None:
#     fig_w, fig_h = _parse_figsize(figsize)
#     common: dict = dict(
#         add_states=add_states,
#         cmap=cmap,
#         fig_h=fig_h,
#         fig_w=fig_w,
#         file_fontsize=file_fontsize,
#         gridlines=gridlines,
#         max_files=max_files,
#         pattern=pattern,
#         suptitle_y=suptitle_y,
#         title_fontsize=title_fontsize,
#         vmax_arg=vmax,
#         vmin_arg=vmin,
#     )
#     _process_one_target(
#         label="GLOBAL",
#         stats_root=Path(global_stats_root),
#         plots_root=Path(global_plots_root),
#         prefix=global_prefix,
#         **common,
#     )
#     _process_one_target(
#         label="LAM",
#         stats_root=Path(lam_stats_root),
#         plots_root=Path(lam_plots_root),
#         prefix=lam_prefix,
#         **common,
#     )

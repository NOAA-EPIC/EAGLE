#!/usr/bin/env python3
"""
plot_wxvx_stats_var.py.

Generate grid2grid spatial PNG plots from wxvx NetCDF stats files in the current
src-based EAGLE pipeline.

Expected defaults:
- read:
    run/<experiment>/vx/grid2grid/global/run/stats/**/grid_stat_nested*.nc
    run/<experiment>/vx/grid2grid/lam/run/stats/**/grid_stat_nested*.nc
- write:
    run/<experiment>/vx/grid2grid/global/run/plots/YYYYMMDD/HH/<same_basename>.png
    run/<experiment>/vx/grid2grid/lam/run/plots/YYYYMMDD/HH/<same_basename>.png
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

if TYPE_CHECKING:
    from cartopy.mpl.geoaxes import GeoAxes


def choose_diff_var(ds: xr.Dataset) -> str | None:
    for k in ds.data_vars:
        v = cast("str", k)
        if v.startswith("DIFF_"):
            return v
    return None


def pick_2d(da: xr.DataArray) -> xr.DataArray:
    out = da
    while out.ndim > 2:  # noqa: PLR2004
        out = out.isel({out.dims[0]: 0})
    return out


def mask_fill(da: xr.DataArray) -> xr.DataArray:
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


def finite_min_max(da: xr.DataArray) -> tuple[float, float]:
    a = np.asarray(da.values).astype("float64", copy=False)
    a = a[np.isfinite(a)]
    if a.size == 0:
        msg = "All values are NaN/inf after masking fill values."
        raise ValueError(msg)
    return float(a.min()), float(a.max())


def to_lon180(lon2d: np.ndarray) -> np.ndarray:
    lon = np.asarray(lon2d, dtype="float64")
    return ((lon + 180.0) % 360.0) - 180.0


def parse_figsize(s: str) -> tuple[float, float]:
    try:
        w, h = (float(x.strip()) for x in s.split(","))
    except Exception as e:
        msg = 'figsize must look like "9.75,4.875"'
        raise ValueError(msg) from e
    return w, h


def infer_date_hour_from_path(nc_path: Path) -> tuple[str, str]:
    parts = nc_path.parts
    yyyymmdd = "unknown_date"
    hh = "unknown_hour"

    for i, part in enumerate(parts):
        if len(part) == 8 and part.isdigit():  # noqa: PLR2004
            yyyymmdd = part
            if (
                i + 1 < len(parts)
                and len(parts[i + 1]) == 2  # noqa: PLR2004
                and parts[i + 1].isdigit()
            ):
                hh = parts[i + 1]
            break

    return yyyymmdd, hh


def out_png_for_nc(nc_path: Path, plots_root: Path) -> Path:
    yyyymmdd, hh = infer_date_hour_from_path(nc_path)
    out_dir = plots_root / yyyymmdd / hh
    out_dir.mkdir(parents=True, exist_ok=True)
    return (out_dir / nc_path.name).with_suffix(".png")


def build_main_title(ds: xr.Dataset, var: str) -> str:
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


def process_one_target(  # noqa: C901, PLR0913, PLR0915
    *,
    label: str,
    stats_root: Path,
    plots_root: Path,
    pattern: str,
    prefix: str,
    vmin_arg: float | None,
    vmax_arg: float | None,
    cmap: str,
    fig_w: float,
    fig_h: float,
    add_states: bool,
    gridlines: bool,
    max_files: int,
    file_fontsize: float,
    title_fontsize: float,
    suptitle_y: float,
) -> tuple[int, int]:
    if not stats_root.exists():
        print(f"[{label}] SKIP: stats root not found: {stats_root}")  # noqa: T201
        return (0, 0)

    plots_root.mkdir(parents=True, exist_ok=True)

    found = sorted(stats_root.rglob(pattern))
    if not found:
        print(  # noqa: T201
            f"[{label}] No files matched under: {stats_root} (pattern={pattern})"
        )
        return (0, 0)

    nc_files = [p for p in found if p.name.startswith(prefix)]
    print(  # noqa: T201
        f"[{label}] Found {len(found)} files, keeping {len(nc_files)} with prefix "
        f"'{prefix}'"
    )

    plotted = 0
    skipped = 0

    for idx, nc_path in enumerate(nc_files, start=1):
        if max_files and idx > max_files:
            break

        out_png = out_png_for_nc(nc_path, plots_root)

        try:
            ds = xr.open_dataset(nc_path)

            var = choose_diff_var(ds)
            if var is None:
                skipped += 1
                print(f"[{label}] SKIP (no DIFF_ var): {nc_path.name}")  # noqa: T201
                continue

            if "lat" not in ds or "lon" not in ds:
                skipped += 1
                print(f"[{label}] SKIP (missing lat/lon): {nc_path.name}")  # noqa: T201
                continue

            lat2d = np.asarray(ds["lat"].values)
            lon2d = to_lon180(np.asarray(ds["lon"].values))
            da = mask_fill(pick_2d(ds[var]))

            if vmin_arg is None or vmax_arg is None:
                auto_vmin, auto_vmax = finite_min_max(da)
                vmin = auto_vmin if vmin_arg is None else vmin_arg
                vmax = auto_vmax if vmax_arg is None else vmax_arg
            else:
                vmin, vmax = vmin_arg, vmax_arg

            extent = [
                float(np.nanmin(lon2d)),
                float(np.nanmax(lon2d)),
                float(np.nanmin(lat2d)),
                float(np.nanmax(lat2d)),
            ]

            fig = plt.figure(figsize=(fig_w, fig_h))
            fig.suptitle(f"({nc_path.name})", fontsize=file_fontsize, y=suptitle_y)

            ax = cast("GeoAxes", plt.axes(projection=ccrs.PlateCarree()))
            ax.set_extent(extent, crs=ccrs.PlateCarree())

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

            ax.set_title(build_main_title(ds, var), fontsize=title_fontsize)

            units = str(ds[var].attrs.get("units", "")).strip()
            cb = fig.colorbar(
                mesh,
                ax=ax,
                orientation="horizontal",
                pad=0.12,
                fraction=0.06,
            )
            cb.set_label(units or var)

            plt.tight_layout(rect=(0, 0, 1, 0.94))
            plt.savefig(out_png, dpi=150)
            plt.close(fig)

            plotted += 1
            print(f"[{label}] WROTE: {out_png}")  # noqa: T201

        except Exception as e:  # noqa: BLE001
            skipped += 1
            print(f"[{label}] SKIP (error): {nc_path.name} -> {e}")  # noqa: T201

    return (plotted, skipped)


def run_spatial_stat_plots(  # noqa: PLR0913
    *,
    lam_stats_root: str,
    lam_plots_root: str,
    global_stats_root: str,
    global_plots_root: str,
    pattern: str = "*.nc",
    lam_prefix: str = "grid_stat_nested",
    global_prefix: str = "grid_stat_nested",
    vmin: float | None = None,
    vmax: float | None = None,
    cmap: str = "RdBu_r",
    figsize: str = "9.75,4.875",
    add_states: bool = False,
    gridlines: bool = False,
    max_files: int = 0,
    file_fontsize: float = 8.0,
    title_fontsize: float = 11.0,
    suptitle_y: float = 0.995,
) -> None:
    fig_w, fig_h = parse_figsize(figsize)

    process_one_target(
        label="LAM",
        stats_root=Path(lam_stats_root),
        plots_root=Path(lam_plots_root),
        pattern=pattern,
        prefix=lam_prefix,
        vmin_arg=vmin,
        vmax_arg=vmax,
        cmap=cmap,
        fig_w=fig_w,
        fig_h=fig_h,
        add_states=add_states,
        gridlines=gridlines,
        max_files=max_files,
        file_fontsize=file_fontsize,
        title_fontsize=title_fontsize,
        suptitle_y=suptitle_y,
    )

    process_one_target(
        label="GLOBAL",
        stats_root=Path(global_stats_root),
        plots_root=Path(global_plots_root),
        pattern=pattern,
        prefix=global_prefix,
        vmin_arg=vmin,
        vmax_arg=vmax,
        cmap=cmap,
        fig_w=fig_w,
        fig_h=fig_h,
        add_states=add_states,
        gridlines=gridlines,
        max_files=max_files,
        file_fontsize=file_fontsize,
        title_fontsize=title_fontsize,
        suptitle_y=suptitle_y,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pattern", default="*.nc")
    ap.add_argument("--lam-stats-root", default="run/vx/grid2grid/lam/run/stats")
    ap.add_argument("--lam-plots-root", default="run/vx/grid2grid/lam/run/plots")
    ap.add_argument("--lam-prefix", default="grid_stat_nested")
    ap.add_argument("--global-stats-root", default="run/vx/grid2grid/global/run/stats")
    ap.add_argument("--global-plots-root", default="run/vx/grid2grid/global/run/plots")
    ap.add_argument("--global-prefix", default="grid_stat_nested")
    ap.add_argument("--do-lam", action="store_true")
    ap.add_argument("--do-global", action="store_true")
    ap.add_argument("--vmin", type=float, default=None)
    ap.add_argument("--vmax", type=float, default=None)
    ap.add_argument("--cmap", default="RdBu_r")
    ap.add_argument("--figsize", default="9.75,4.875")
    ap.add_argument("--add_states", action="store_true")
    ap.add_argument("--gridlines", action="store_true")
    ap.add_argument("--max-files", type=int, default=0)
    ap.add_argument("--file_fontsize", type=float, default=8.0)
    ap.add_argument("--title_fontsize", type=float, default=11.0)
    ap.add_argument("--suptitle_y", type=float, default=0.995)

    args = ap.parse_args()
    do_lam = args.do_lam or (not args.do_lam and not args.do_global)
    do_global = args.do_global or (not args.do_lam and not args.do_global)

    if do_lam:
        process_one_target(
            label="LAM",
            stats_root=Path(args.lam_stats_root),
            plots_root=Path(args.lam_plots_root),
            pattern=args.pattern,
            prefix=args.lam_prefix,
            vmin_arg=args.vmin,
            vmax_arg=args.vmax,
            cmap=args.cmap,
            fig_w=parse_figsize(args.figsize)[0],
            fig_h=parse_figsize(args.figsize)[1],
            add_states=args.add_states,
            gridlines=args.gridlines,
            max_files=args.max_files,
            file_fontsize=args.file_fontsize,
            title_fontsize=args.title_fontsize,
            suptitle_y=args.suptitle_y,
        )

    if do_global:
        process_one_target(
            label="GLOBAL",
            stats_root=Path(args.global_stats_root),
            plots_root=Path(args.global_plots_root),
            pattern=args.pattern,
            prefix=args.global_prefix,
            vmin_arg=args.vmin,
            vmax_arg=args.vmax,
            cmap=args.cmap,
            fig_w=parse_figsize(args.figsize)[0],
            fig_h=parse_figsize(args.figsize)[1],
            add_states=args.add_states,
            gridlines=args.gridlines,
            max_files=args.max_files,
            file_fontsize=args.file_fontsize,
            title_fontsize=args.title_fontsize,
            suptitle_y=args.suptitle_y,
        )


if __name__ == "__main__":
    main()

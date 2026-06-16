#!/usr/bin/env python3
import argparse
import os
import sys
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER

#---------------------------------------------------------------------------------------------------
# Safe import validation for the YAML parsing module
try:
    import yaml
except ImportError:
    print("[ERROR] The 'pyyaml' package is required. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

#---------------------------------------------------------------------------------------------------
class EAGLEVisualizer:
    def __init__(self, config):
        """Initializes the visualizer and verifies file integrity."""
        self.config = config

        # Automatically run file integrity checks upon initialization
        self._validate_input_files()

        self.longitude = None
        self.latitude = None
        self.x_coords = None
        self.y_coords = None

        self.t2m = None
        self.t2m_units = "unknown"
        self.lcc_proj = None

    def _validate_input_files(self):
        """Checks if all required input NetCDF paths exist before allocating system memory."""
        print(f"Check input data files:")
        missing_files = []
        ncfilelist = ["nc_2m_t", "nc_10m_u", "nc_10m_v", "nc_500hPa_gh", "nc_sfp",
                      "nc_850hPa_t", "nc_250hPa_u", "nc_250hPa_v"]
        n = 0
        for item in ncfilelist:
            n += 1
            if item in self.config:
                ncflnm = self.config[item]
                print(f"Item No. {n}: {item} -> {ncflnm}")
                if not os.path.exists(ncflnm):
                    print(f"  - {item}: Path not found -> '{nclnm}'")
                    sys.exit(1)

        self.show_on_screen = self.config["show_on_screen"]
        print(f"self.show_on_screen = {self.show_on_screen}")

    def load_and_process_data(self):
        """Opens datasets, extracts coordinate arrays, and calculates wind metrics."""
        try:
            self.nc_2m_t_path = self.config["nc_2m_t"]
            self.dt = xr.open_dataset(self.nc_2m_t_path)
        except Exception as e:
            print(f"\n[ERROR] Failed to open NetCDF files. File structure might be corrupt.\nDetails: {e}", file=sys.stderr)
            sys.exit(1)

        # Extract variables and drop single-value dimensions
        self.t2m = self.dt["t2m"].squeeze().values
        self.longitude = self.dt["longitude"].values
        self.latitude = self.dt["latitude"].values
        self.x_coords = self.dt["x"].values
        self.y_coords = self.dt["y"].values

        # Extract Temperature metadata units
        self.t2m_units = self.dt["t2m"].attrs.get("units", "unknown")

        # Build Map Projections
        self._setup_projection()

    def _setup_projection(self):
        """Parses CRS metadata map parameters to set up Lambert Conformal Conic."""
        crs_attrs = self.dt["CRS"].attrs
        lat_origin = crs_attrs["latitude_of_projection_origin"]
        lon_central = crs_attrs["longitude_of_central_meridian"]
        std_parallels = crs_attrs["standard_parallel"]

        self.lcc_proj = ccrs.LambertConformal(
            central_longitude=lon_central,
            central_latitude=lat_origin,
            standard_parallels=(std_parallels[0], std_parallels[1]),
        )

    def _create_base_map(self):
        """Initializes figure canvas, map frame layers, and standard grid lines."""
        fig, ax = plt.subplots(figsize=(12, 9), subplot_kw={"projection": self.lcc_proj})

        # Clip tightly using native coordinate ranges
        ax.set_extent(
            [self.x_coords.min(), self.x_coords.max(), self.y_coords.min(), self.y_coords.max()],
            crs=self.lcc_proj,
        )

        # Add basic geography boundaries
        ax.add_feature(cfeature.COASTLINE, edgecolor="black", linewidth=1.2)
        ax.add_feature(cfeature.BORDERS, edgecolor="black", linestyle=":")

        # Grid line properties configuration
        gl = ax.gridlines(draw_labels=True, linewidth=1, color="dimgray", alpha=0.4, linestyle="--")
        gl.top_labels = False
        gl.right_labels = False
        gl.xlocator = mticker.FixedLocator(range(-180, 180, 5))
        gl.ylocator = mticker.FixedLocator(range(-90, 90, 5))
        gl.xformatter = LONGITUDE_FORMATTER
        gl.yformatter = LATITUDE_FORMATTER
        gl.xlabel_style = {"size": 10, "weight": "bold"}
        gl.ylabel_style = {"size": 10, "weight": "bold"}
        gl.xpadding = 10
        gl.edge_labels = False
        gl.x_inline = False
        gl.y_inline = False

        return fig, ax

    def _add_color_bar(self, fig, ax, mesh, cb_label):
        """Appends color bar metadata underneath frame display box."""
        cbar = fig.colorbar(mesh, ax=ax, orientation="horizontal", pad=0.12, shrink=0.7, aspect=30)
        cbar.set_label(cb_label, fontsize=11)

    def _finalize_and_save(self, fig, output_filename):
        """Handles screen display rendering or exports map file to disk."""
        plt.tight_layout()
        if self.show_on_screen:
            plt.show()
        else:
            fig.savefig(output_filename, dpi=150, bbox_inches='tight')
            print(f"[INFO] Successfully exported plot frame: '{output_filename}'")
            plt.close(fig)

    def plot_t2m_only(self, image_name):
        """Plot 2m Temperature field"""
        fig, ax = self._create_base_map()

        # color raster
        mesh = ax.pcolormesh(self.longitude, self.latitude, self.t2m,
                             transform=ccrs.PlateCarree(), cmap="turbo", shading="auto")

        title="Temperature at 2 meter height"
        cb_label = "Temperature ({self.t2m_units})"
        self._add_color_bar(fig, ax, mesh, cb_label)
        plt.title(title, fontsize=14, pad=20)
        self._finalize_and_save(fig, image_name)

    def plot_10m_windbarb_only(self, image_name):
        """Plot 20 meter barbs."""

        try:
            self.nc_10m_u_path = self.config["nc_10m_u"]
            self.nc_10m_v_path = self.config["nc_10m_v"]
            self.nc_10m_u = xr.open_dataset(self.nc_10m_u_path)
            self.nc_10m_v = xr.open_dataset(self.nc_10m_v_path)
        except Exception as e:
            print(f"\n[ERROR] Failed to open NetCDF files. File structure might be corrupt.\nDetails: {e}", file=sys.stderr)
            sys.exit(1)

        # Extract variables and drop single-value dimensions
        self.u = self.nc_10m_u["u10"].squeeze().values
        self.v = self.nc_10m_v["v10"].squeeze().values

        # Calculate wind speed magnitude (m/s) before knot conversion
        self.wind_speed = np.sqrt(self.u**2 + self.v**2)

        fig, ax = self._create_base_map()

        # Wind Speed lines
        contour_levels = np.arange(5, self.wind_speed.max(), 5)
        if len(contour_levels) > 0:
            contours = ax.contour(self.longitude, self.latitude, self.wind_speed, levels=contour_levels,
                                  colors="white", linewidths=0.8, alpha=0.7, transform=ccrs.PlateCarree())
            ax.clabel(contours, inline=True, fmt="%d m/s", fontsize=8, colors="blue")

        # 2. Convert raw m/s vector arrays dynamically to Knots for windbarb specifications
        u_knots = self.u * 1.94384
        v_knots = self.v * 1.94384

        skip_barbs = 12
        ax.barbs(
            self.longitude[::skip_barbs, ::skip_barbs],
            self.latitude[::skip_barbs, ::skip_barbs],
            u_knots[::skip_barbs, ::skip_barbs],
            v_knots[::skip_barbs, ::skip_barbs],
            transform=ccrs.PlateCarree(),
            color="black",
            length=5.5,
            linewidth=0.8
        )

        plt.title("Wind Barb at 10 meter (Velocity Vectors in Knots)", fontsize=14, pad=20)
        self._finalize_and_save(fig, image_name)

    def plot_10m_windbarb_overlay_2m_t(self, image_name):
        """Plot Type 3: Full composition with background heat mapping, contour lines, and barbs."""
        fig, ax = self._create_base_map()

        # 1. Background raster
        mesh = ax.pcolormesh(self.longitude, self.latitude, self.t2m,
                             transform=ccrs.PlateCarree(), cmap="turbo", shading="auto")

        # 2. Add Contour lines
        contour_levels = np.arange(5, self.wind_speed.max(), 5)
        if len(contour_levels) > 0:
            contours = ax.contour(self.longitude, self.latitude, self.wind_speed,
                                  levels=contour_levels, colors="white",
                                  linewidths=0.8, alpha=0.7, transform=ccrs.PlateCarree())
            ax.clabel(contours, inline=True, fmt="%d m/s", fontsize=8, colors="white")

        # 3. Add Wind Barbs
        u_knots = self.u * 1.94384
        v_knots = self.v * 1.94384
        skip_barbs = 12
        ax.barbs(
            self.longitude[::skip_barbs, ::skip_barbs],
            self.latitude[::skip_barbs, ::skip_barbs],
            u_knots[::skip_barbs, ::skip_barbs],
            v_knots[::skip_barbs, ::skip_barbs],
            transform=ccrs.PlateCarree(),
            color="black",
            length=5.5,
            linewidth=0.8
        )

        cb_label = "Temperature ({self.t2m_units})"
        self._add_color_bar(fig, ax, mesh, cb_label)
        plt.title("Wind Field Composition (Temperature, Contours & Barbs)", fontsize=14, pad=20)
        self._finalize_and_save(fig, image_name)

#---------------------------------------------------------------------------------------------------
def load_yaml_config(filepath="config.yaml"):
    """Reads configuration values or falls back to an error message if missing."""
    if not os.path.exists(filepath):
        print(f"[ERROR] Required configuration layout file '{filepath}' missing.", file=sys.stderr)
        sys.exit(1)
    try:
        with open(filepath, 'r') as f:
            config = yaml.safe_load(f)
            return config.get("default_paths", {})
    except Exception as e:
        print(f"[ERROR] Critical formatting error within '{filepath}': {e}", file=sys.stderr)
        sys.exit(1)

#---------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    # Load configuration attributes directly from the YAML file layout
    config = load_yaml_config("config.yaml")
    print(f"config: {config}")

    # Initialize the class and run the rendering composition
    visualizer = EAGLEVisualizer(config)
    visualizer.load_and_process_data()

    t2m_img = config.get("eagle_2m_t_image", "eagle_2m_t.png")
    visualizer.plot_t2m_only(t2m_img)

    barb_10m_img = config.get("eagle_10m_barb_image", "eagle_10m_barb.png")
    visualizer.plot_10m_windbarb_only(barb_10m_img)

    t2m_10m_wind_overlay_img = config.get("eagle_2m_t_10m_wind_image", "eagle_2m_t_10m_wind.png")
    visualizer.plot_10m_windbarb_overlay_2m_t(t2m_10m_wind_overlay_img)

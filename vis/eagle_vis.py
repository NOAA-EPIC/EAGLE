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

class WindFieldVisualizer:
    def __init__(self, nc_t, nc_u, nc_v):
        """Initializes the visualizer and verifies file integrity."""
        self.nc_t_path = nc_t
        self.nc_u_path = nc_u
        self.nc_v_path = nc_v
        
        # Automatically run file integrity checks upon initialization
        self._validate_input_files()
        
        self.dt = None
        self.du = None
        self.dv = None
        
        self.longitude = None
        self.latitude = None
        self.x_coords = None
        self.y_coords = None
        
        self.temp = None
        self.u = None
        self.v = None
        self.wind_speed = None
        self.temp_units = "unknown"
        self.lcc_proj = None

    def _validate_input_files(self):
        """Checks if all required input NetCDF paths exist before allocating system memory."""
        missing_files = []
        for file_label, file_path in [("Temperature (-t)", self.nc_t_path), 
                                      ("U-Wind (-u)", self.nc_u_path), 
                                      ("V-Wind (-v)", self.nc_v_path)]:
            if not os.path.exists(file_path):
                missing_files.append(f"  - {file_label}: Path not found -> '{file_path}'")
        
        if missing_files:
            print("\n[ERROR] Missing input datasets. Execution halted:", file=sys.stderr)
            for error in missing_files:
                print(error, file=sys.stderr)
            sys.exit(1)

    def load_and_process_data(self):
        """Opens datasets, extracts coordinate arrays, and calculates wind metrics."""
        try:
            self.dt = xr.open_dataset(self.nc_t_path)
            self.du = xr.open_dataset(self.nc_u_path)
            self.dv = xr.open_dataset(self.nc_v_path)
        except Exception as e:
            print(f"\n[ERROR] Failed to open NetCDF files. File structure might be corrupt.\nDetails: {e}", file=sys.stderr)
            sys.exit(1)
        
        # Extract variables and drop single-value dimensions
        self.temp = self.dt["t2m"].squeeze().values
        self.longitude = self.dt["longitude"].values
        self.latitude = self.dt["latitude"].values
        self.x_coords = self.dt["x"].values
        self.y_coords = self.dt["y"].values
        
        self.u = self.du["u10"].squeeze().values
        self.v = self.dv["v10"].squeeze().values
        
        # Calculate wind speed magnitude (m/s) before knot conversion
        self.wind_speed = np.sqrt(self.u**2 + self.v**2)
        
        # Extract Temperature metadata units
        self.temp_units = self.dt["t2m"].attrs.get("units", "unknown")
        
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

    def _add_color_bar(self, fig, ax, mesh):
        """Appends color bar metadata underneath frame display box."""
        cbar = fig.colorbar(mesh, ax=ax, orientation="horizontal", pad=0.12, shrink=0.7, aspect=30)
        cbar.set_label(f"Temperature ({self.temp_units})", fontsize=11)

    def plot_contour_only(self, output_filename):
        """Plot Type 1: Renders Temperature fields and Wind Speed contour layout maps."""
        fig, ax = self._create_base_map()
        
        # 1. Background Temperature color raster
        mesh = ax.pcolormesh(self.longitude, self.latitude, self.temp, transform=ccrs.PlateCarree(), cmap="turbo", shading="auto")
        
        # 2. Wind Speed lines overlay
        contour_levels = np.arange(5, self.wind_speed.max(), 5)
        contours = ax.contour(self.longitude, self.latitude, self.wind_speed, levels=contour_levels, colors="white", linewidths=0.8, alpha=0.7, transform=ccrs.PlateCarree())
        ax.clabel(contours, inline=True, fmt="%d m/s", fontsize=8, colors="white")
        
        self._add_color_bar(fig, ax, mesh)
        plt.title("Wind Speed Contour Field", fontsize=14, pad=20)
        self._finalize_and_save(fig, output_filename)

    def plot_windbarb_only(self, output_filename):
        """Plot Type 2: Renders Background Temperature maps alongside isolated text barbs."""
        fig, ax = self._create_base_map()
        
        # 1. Background Temperature color raster
        mesh = ax.pcolormesh(self.longitude, self.latitude, self.temp, transform=ccrs.PlateCarree(), cmap="turbo", shading="auto")
        
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
        
        self._add_color_bar(fig, ax, mesh)
        plt.title("Wind Barb Field (Velocity Vectors in Knots)", fontsize=14, pad=20)
        self._finalize_and_save(fig, output_filename)

    def plot_windbarb_overlay_contour(self, output_filename):
        """Plot Type 3: Full composition with background heat mapping, contour lines, and barbs."""
        fig, ax = self._create_base_map()
        
        # 1. Background raster
        mesh = ax.pcolormesh(self.longitude, self.latitude, self.temp, transform=ccrs.PlateCarree(), cmap="turbo", shading="auto")
        
        # 2. Add Contour lines
        contour_levels = np.arange(5, self.wind_speed.max(), 5)
        contours = ax.contour(self.longitude, self.latitude, self.wind_speed, levels=contour_levels, colors="white", linewidths=0.8, alpha=0.7, transform=ccrs.PlateCarree())
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
        
        self._add_color_bar(fig, ax, mesh)
        plt.title("Temperature & Wind Velocity Vector Composite Field", fontsize=14, pad=20)
        self._finalize_and_save(fig, output_filename)

    def _finalize_and_save(self, fig, output_filename):
        """Handles final positioning transforms, saves image assets, and safely closes window context."""
        fig.subplots_adjust(bottom=0.15)
        plt.tight_layout()
        fig.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.05)
        
        plt.savefig(output_filename, bbox_inches="tight", dpi=300)
        print(f"Successfully generated plot artifact: {output_filename}")
        plt.close(fig)

def main():
    parser = argparse.ArgumentParser(description="Object-Oriented Meteorological Wind & Temperature Visualization Pipeline Engine")
    
    # INPUT FILES ARGUMENTS
    input_group = parser.add_argument_group("Input Data File Options")
    input_group.add_argument("-t", "--temperature_nc", type=str, 
                             default="/scratch5/purged/Wei.Huang/src/nv/data/eagle/forecast/2t-heightAboveGround-0002.nc",
                             help="File path to target Temperature NetCDF file profile.")
    input_group.add_argument("-u", "--u_wind_nc", type=str, 
                             default="/scratch5/purged/Wei.Huang/src/nv/data/eagle/forecast/10u-heightAboveGround-0010.nc",
                             help="File path to target U-component Wind NetCDF file profile.")
    input_group.add_argument("-v", "--v_wind_nc", type=str,
                             default="/scratch5/purged/Wei.Huang/src/nv/data/eagle/forecast/10v-heightAboveGround-0010.nc",
                             help="File path to target V-component Wind NetCDF file profile.")

    # OUTPUT FILES ARGUMENTS
    output_group = parser.add_argument_group("Output Image Name Options")
    output_group.add_argument("--out_contour", type=str, default="1_contour_only.png",
                              help="Filename for the contour-only plot layer output.")
    output_group.add_argument("--out_windbarb", type=str, default="2_windbarb_only.png",
                              help="Filename for the windbarb-only plot layer output.")
    output_group.add_argument("--out_overlay", type=str, default="3_windbarb_overlay_contour.png",
                              help="Filename for the combined overlay plot layer output.")

    args = parser.parse_args()

    # Initialization automatically checks file paths; will exit early if an path doesn't exist

    visualizer = WindFieldVisualizer(nc_t=args.temperature_nc,nc_u=args.u_wind_nc,nc_v=args.v_wind_nc)

    # Process pipeline calculations
    visualizer.load_and_process_data()

    # Generate the requested plot images using customized filenames

    visualizer.plot_contour_only(args.out_contour)
    visualizer.plot_windbarb_only(args.out_windbarb)
    visualizer.plot_windbarb_overlay_contour(args.out_overlay)

########################################################################################################################################################
if name == "main":
    main()
### New Execution Syntax Examples

# You can run the script with its defaults, or modify any inputs/outputs cleanly:

# Changing an input and its corresponding output name**:
#  ```bash
#  ./plotwindbarb.py -t alternative_temp.nc
#                    --out_contour custom_contour_view.png

#Assigning completely clean unique tracks:
#bash
#  ./plotwindbarb.py --out_contour c1.png --out_windbarb b2.png --out_overlay composite3.png


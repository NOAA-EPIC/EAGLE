import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.cm import get_cmap

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER

from netCDF4 import Dataset

# Open the NetCDF file
nc_t = "/scratch5/purged/Wei.Huang/src/nv/data/eagle/forecast/2t-heightAboveGround-0002.nc"
nc_u = "/scratch5/purged/Wei.Huang/src/nv/data/eagle/forecast/10u-heightAboveGround-0010.nc"
nc_v = "/scratch5/purged/Wei.Huang/src/nv/data/eagle/forecast/10v-heightAboveGround-0010.nc"

# Open and interact with dataset
# with xr.open_dataset(ncfilename) as ds:
dt = xr.open_dataset(nc_t)
du = xr.open_dataset(nc_u)
dv = xr.open_dataset(nc_v)
# print(dt)
# Extract data directly and remove the single-value dimensions (squeeze to 2D)
temp = dt["t2m"].squeeze().values  # Now shape is (190, 338)
# Direct 2D extraction using xarray indexing
# temp_2d = ds["t"].isel(forecast_reference_time=0, time=0)
longitude = dt["longitude"].values
latitude = dt["latitude"].values
CRS = dt["CRS"]

#print("CRS")
#print(CRS)

# View all attributes for the variable
#print("CRS.attrs")
#print(CRS.attrs)

# 1. Pull the native projected grid coordinates (in meters) from xarray
x_coords = dt["x"].values
y_coords = dt["y"].values

u = du["u10"].squeeze().values  # Now shape is (190, 338)
v = dv["v10"].squeeze().values  # Now shape is (190, 338)

# Calculate Wind Speed (Magnitude) for the contours
wind_speed = np.sqrt(u**2 + v**2)

# false_easting:                  0.0
# false_northing:                 0.0
# grid_mapping_name:              lambert_conformal_conic
# latitude_of_projection_origin:  38.5
# longitude_of_central_meridian:  262.5
# standard_parallel:              [38.5 38.5]

false_easting = CRS.attrs["false_easting"]
false_northing = CRS.attrs["false_northing"]
grid_mapping_name = CRS.attrs["grid_mapping_name"]
latitude_of_projection_origin = CRS.attrs["latitude_of_projection_origin"]
longitude_of_central_meridian = CRS.attrs["longitude_of_central_meridian"]
standard_parallel = CRS.attrs["standard_parallel"]

#print(f"grid_mapping_name = {grid_mapping_name}")
#print(f"latitude_of_projection_origin = {latitude_of_projection_origin}")
#print(f"longitude_of_central_meridian = {longitude_of_central_meridian}")
#print(f"standard_parallel = {standard_parallel}")

# Setup LCC projection parameters using your CRS metadata
lat_origin = CRS.attrs["latitude_of_projection_origin"]
lon_central = CRS.attrs["longitude_of_central_meridian"]
std_parallels = CRS.attrs["standard_parallel"]

lcc_proj = ccrs.LambertConformal(
    central_longitude=lon_central,
    central_latitude=lat_origin,
    standard_parallels=(std_parallels[0], std_parallels[1]),
)

# 4. Initialize figure and fit map extent to your data coordinates
#fig, ax = plt.subplots(figsize=(14, 10), subplot_kw={"projection": lcc_proj})
# Update line 37 to change the figure geometry shape
fig, ax = plt.subplots(figsize=(12, 9), subplot_kw={"projection": lcc_proj})

# padding = 0.25
# ax.set_extent(
#     [
#         longitude.min() - padding,
#         longitude.max() + padding,
#         latitude.min() - padding,
#         latitude.max() + padding,
#     ],
#     crs=ccrs.PlateCarree(),
# )

# Set the map boundaries tightly using native grid coordinates
# CRUCIAL: Change 'crs=ccrs.PlateCarree()' to 'crs=lcc_proj'
ax.set_extent(
    [x_coords.min(), x_coords.max(), y_coords.min(), y_coords.max()],
    crs=lcc_proj,
)

# 5. Plot Temperature Data as background colors
mesh = ax.pcolormesh(
    longitude,
    latitude,
    temp,
    transform=ccrs.PlateCarree(),
    cmap="turbo",
    shading="auto",
)

# 6. Plot Wind Speed Contours as lines over the Temperature map
# This adds labeled line tracks at intervals of 5 m/s
contour_levels = np.arange(5, wind_speed.max(), 5)
contours = ax.contour(
    longitude,
    latitude,
    wind_speed,
    levels=contour_levels,
    colors="white",
    linewidths=0.8,
    alpha=0.7,
    transform=ccrs.PlateCarree(),
)
ax.clabel(contours, inline=True, fmt="%d m/s", fontsize=8, colors="white")

# convert m/s to knots
u *= 1.94384
v *= 1.94384

# 7. Plot Wind Barbs as an overlay layer
# Wind barbs require standard subsampling to look clean (every 12th or 15th point)
skip_barbs = 12
ax.barbs(
    longitude[::skip_barbs, ::skip_barbs],
    latitude[::skip_barbs, ::skip_barbs],
    u[::skip_barbs, ::skip_barbs],
    v[::skip_barbs, ::skip_barbs],
    transform=ccrs.PlateCarree(),
    color="black",
    length=5.5,  # Size of the individual barb shafts
    linewidth=0.8,
)

# 7. Map boundaries and styled gridlines
ax.add_feature(cfeature.COASTLINE, edgecolor="black", linewidth=1.2)
ax.add_feature(cfeature.BORDERS, edgecolor="black", linestyle=":")

gl = ax.gridlines(
    draw_labels=True, linewidth=1, color="dimgray", alpha=0.4, linestyle="--"
)
gl.top_labels = False
gl.right_labels = False

# Set clean grid ticks and format labels
gl.xlocator = mticker.FixedLocator(range(-180, 180, 5))
gl.ylocator = mticker.FixedLocator(range(-90, 90, 5))
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER
gl.xlabel_style = {"size": 10, "weight": "bold"}
gl.ylabel_style = {"size": 10, "weight": "bold"}

# Force longitude labels to draw strictly below the bottom boundary line
gl.xpadding = 10        # Pushes text labels further outward away from the map data
gl.edge_labels = False  # Stops labels from trying to anchor along the curved inner edges

# Tell Cartopy to draw labels relative to the outer bounding box frame
gl.x_inline = False
gl.y_inline = False

# 8. Add Colorbar and Title
#cbar = plt.colorbar(
#    mesh, ax=ax, orientation="horizontal", pad=0.06, shrink=0.6, aspect=30
#)

#  Increase 'pad' to shift the horizontal colorbar down (e.g., from 0.05 to 0.12)
cbar = plt.colorbar(
    mesh,
    ax=ax,
    orientation="horizontal",
    pad=0.12,           # Increased space to clear the longitude text labels safely
    shrink=0.7,
    aspect=30           # Optional: Makes the colorbar slightly thinner and sleeker
)

temp_units = dt['t2m'].attrs.get('units', 'unknown')

cbar.set_label(f"Temperature ({temp_units})", fontsize=11)

plt.title("Temperature & Wind Velocity Vector Field", fontsize=14, pad=20)

# Increase the canvas spacing buffer specifically below the bottom frame axis
fig.subplots_adjust(bottom=0.15)

# Replace plt.show() at the bottom of your script with this:
plt.savefig("wind_temperature.png", bbox_inches="tight", dpi=300)

# Insert this block right before plt.show()
plt.tight_layout()

# Force the axis to tightly hug the map boundaries
fig.subplots_adjust(left=0.02, right=0.98, top=0.95, bottom=0.05)

plt.show()


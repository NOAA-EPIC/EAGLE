import xarray as xr

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from matplotlib.cm import get_cmap

import cartopy.crs as ccrs
import cartopy.feature as cfeature
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER

from netCDF4 import Dataset

# Open the NetCDF file
ncfilename = "/scratch5/purged/Wei.Huang/src/nv/data/eagle/forecast/t-isobaricInhPa-0850.nc"

# Open and interact with dataset
# with xr.open_dataset(ncfilename) as ds:
ds = xr.open_dataset(ncfilename)
#print(ds)
# Extract data directly and remove the single-value dimensions (squeeze to 2D)
temp = ds["t"].squeeze().values  # Now shape is (190, 338)
# Direct 2D extraction using xarray indexing
# temp_2d = ds["t"].isel(forecast_reference_time=0, time=0)
longitude = ds["longitude"].values
latitude = ds["latitude"].values
CRS = ds["CRS"]

x_coords = ds["x"].values
y_coords = ds["y"].values

#print("CRS")
#print(CRS)

# false_easting:                  0.0
# false_northing:                 0.0
# grid_mapping_name:              lambert_conformal_conic
# latitude_of_projection_origin:  38.5
# longitude_of_central_meridian:  262.5
# standard_parallel:              [38.5 38.5]

# View all attributes for the variable
#print("CRS.attrs")
#print(CRS.attrs)

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

# 1. Define projection parameters
lat_origin = latitude_of_projection_origin
lon_central = longitude_of_central_meridian
std_parallels = (standard_parallel[0], standard_parallel[1])

# 2. Setup the LCC map projection
lcc_proj = ccrs.LambertConformal(
    central_longitude=lon_central,
    central_latitude=lat_origin,
    standard_parallels=std_parallels,
)

fig, ax = plt.subplots(figsize=(12, 9), subplot_kw={"projection": lcc_proj})

# --- Setup the map layout and automatically bound to data extent ---
# Calculate boundaries from your longitude and latitude arrays
# lon_min, lon_max = longitude.min(), longitude.max()
# lat_min, lat_max = latitude.min(), latitude.max()

# Set the map window boundary [xmin, xmax, ymin, ymax]
# ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
# padding = 0.25
# ax.set_extent(
#     [lon_min - padding, lon_max + padding,
#     lat_min - padding, lat_max + padding],
#     crs=ccrs.PlateCarree(),
# )

# Set the map boundaries tightly using native grid coordinates
# CRUCIAL: Change 'crs=ccrs.PlateCarree()' to 'crs=lcc_proj'
ax.set_extent(
    [x_coords.min(), x_coords.max(), y_coords.min(), y_coords.max()],
    crs=lcc_proj,
)

# 3. Plot the data (Crucial: use transform=ccrs.PlateCarree())
mesh = ax.pcolormesh(
    longitude,
    latitude,
    temp,
    transform=ccrs.PlateCarree(),
    cmap="turbo",
    shading="auto",
)

# 4. Add map boundaries and gridlines
ax.add_feature(cfeature.COASTLINE, edgecolor="black")
ax.add_feature(cfeature.BORDERS, edgecolor="black", linestyle=":")
# Generate gridlines
gl = ax.gridlines(
    draw_labels=True,
    linewidth=1,
    color="gray",
    alpha=0.5,
    linestyle="--"
)

# Set gridline spacing (e.g., every 5 degrees longitude, 2 degrees latitude)
gl.xlocator = mticker.FixedLocator(range(-180, 180, 5))
gl.ylocator = mticker.FixedLocator(range(-90, 90, 5))

# Hide labels at the top and right boundaries
gl.top_labels = False
gl.right_labels = False

# Customize text font appearance
gl.xlabel_style = {"size": 10, "color": "darkblue", "weight": "bold"}
gl.ylabel_style = {"size": 10, "color": "darkblue", "weight": "bold"}

# Force longitude labels to draw strictly below the bottom boundary line
gl.xpadding = 10        # Pushes text labels further outward away from the map data
gl.edge_labels = False  # Stops labels from trying to anchor along the curved inner edges

# Tell Cartopy to draw labels relative to the outer bounding box frame
gl.x_inline = False
gl.y_inline = False

# Standard cartopy formatters for degrees
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER

# 5. Add colorbar and labels
#cbar = plt.colorbar(
#    mesh, ax=ax, orientation="horizontal", pad=0.05, shrink=0.7
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
cbar.set_label(f"Temperature ({ds['t'].attrs.get('units', 'unknown')})", labelpad=10)

plt.title("Variable 't' on Lambert Conformal Conic Projection", pad=20)

# Increase the canvas spacing buffer specifically below the bottom frame axis
fig.subplots_adjust(bottom=0.15)

plt.savefig("temperature.png", bbox_inches="tight", dpi=300)

plt.show()

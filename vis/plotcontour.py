import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from netCDF4 import Dataset
from matplotlib.cm import get_cmap

# Open the NetCDF file
ncfilename = "/scratch5/purged/Wei.Huang/src/nv/data/eagle/forecast/t-isobaricInhPa-0850.nc"

# Open and interact with dataset
# with xr.open_dataset(ncfilename) as ds:
ds = xr.open_dataset(ncfilename)
print(ds)
# Extract data directly and remove the single-value dimensions (squeeze to 2D)
temp = ds["t"].squeeze().values  # Now shape is (190, 338)
# Direct 2D extraction using xarray indexing
# temp_2d = ds["t"].isel(forecast_reference_time=0, time=0)
longitude = ds["longitude"].values
latitude = ds["latitude"].values
CRS = ds["CRS"]

print("CRS")
print(CRS)

# false_easting:                  0.0
# false_northing:                 0.0
# grid_mapping_name:              lambert_conformal_conic
# latitude_of_projection_origin:  38.5
# longitude_of_central_meridian:  262.5
# standard_parallel:              [38.5 38.5]

# View all attributes for the variable
print("CRS.attrs")
print(CRS.attrs)

false_easting = CRS.attrs["false_easting"]
false_northing = CRS.attrs["false_northing"]
grid_mapping_name = CRS.attrs["grid_mapping_name"]
latitude_of_projection_origin = CRS.attrs["latitude_of_projection_origin"]
longitude_of_central_meridian = CRS.attrs["longitude_of_central_meridian"]
standard_parallel = CRS.attrs["standard_parallel"]

print(f"grid_mapping_name = {grid_mapping_name}")
print(f"latitude_of_projection_origin = {latitude_of_projection_origin}")
print(f"longitude_of_central_meridian = {longitude_of_central_meridian}")
print(f"standard_parallel = {standard_parallel}")

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
lon_min, lon_max = longitude.min(), longitude.max()
lat_min, lat_max = latitude.min(), latitude.max()

# Set the map window boundary [xmin, xmax, ymin, ymax]
# ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
padding = 0.25
ax.set_extent(
    [lon_min - padding, lon_max + padding,
    lat_min - padding, lat_max + padding],
    crs=ccrs.PlateCarree(),
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
gl.xlocator = mticker.FixedLocator(range(0, 360, 5))
gl.ylocator = mticker.FixedLocator(range(-90, 90, 5))

# Hide labels at the top and right boundaries
gl.top_labels = False
gl.right_labels = False

# Customize text font appearance
gl.xlabel_style = {"size": 10, "color": "darkblue", "weight": "bold"}
gl.ylabel_style = {"size": 10, "color": "darkblue", "weight": "bold"}

# Format labels to show degree symbols (e.g., 40°N, 100°W)
gl.xformatter = cz_formatter if hasattr(gl, 'xformatter') else None # Optional fallback
# Standard cartopy formatters for degrees
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER
gl.xformatter = LONGITUDE_FORMATTER
gl.yformatter = LATITUDE_FORMATTER

# 5. Add colorbar and labels
cbar = plt.colorbar(
    mesh, ax=ax, orientation="horizontal", pad=0.05, shrink=0.7
)
cbar.set_label(f"Temperature ({ds['t'].attrs.get('units', 'unknown')})")

plt.title("Variable 't' on Lambert Conformal Conic Projection", pad=20)
plt.show()

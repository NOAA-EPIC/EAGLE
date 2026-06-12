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
print(dt)
# Extract data directly and remove the single-value dimensions (squeeze to 2D)
temp = dt["t2m"].squeeze().values  # Now shape is (190, 338)
# Direct 2D extraction using xarray indexing
# temp_2d = ds["t"].isel(forecast_reference_time=0, time=0)
longitude = dt["longitude"].values
latitude = dt["latitude"].values
CRS = dt["CRS"]

u = du["u10"].squeeze().values  # Now shape is (190, 338)
v = dv["v10"].squeeze().values  # Now shape is (190, 338)

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
fig, ax = plt.subplots(figsize=(14, 10), subplot_kw={"projection": lcc_proj})

padding = 0.25
ax.set_extent(
    [
        longitude.min() - padding,
        longitude.max() + padding,
        latitude.min() - padding,
        latitude.max() + padding,
    ],
    crs=ccrs.PlateCarree(),
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

# 6. Plot Wind Vectors as an overlay layer
# Adjust 'skip' if your map looks too sparse or too crowded
skip = 10
q = ax.quiver(
    longitude[::skip, ::skip],
    latitude[::skip, ::skip],
    u[::skip, ::skip],
    v[::skip, ::skip],
    transform=ccrs.PlateCarree(),
    color="black",  # Changed to black for maximum visibility against 'turbo' colors
    scale=150,  # Increase to make arrows shorter, decrease to make them longer
    width=0.0015,
)

# Add reference key for wind speed scale
ax.quiverkey(q, X=0.9, Y=0.04, U=20, label="20 m/s", labelpos="E", color="black")

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

# 8. Add Colorbar and Title
cbar = plt.colorbar(
    mesh, ax=ax, orientation="horizontal", pad=0.06, shrink=0.6, aspect=30
)

temp_units = dt['t2m'].attrs.get('units', 'unknown')

cbar.set_label(f"Temperature ({temp_units})", fontsize=11)

plt.title("Temperature & Wind Velocity Vector Field", fontsize=14, pad=20)
plt.show()


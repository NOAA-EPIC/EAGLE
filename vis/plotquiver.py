import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from netCDF4 import Dataset
from matplotlib.cm import get_cmap

# Open the NetCDF file
nc_u = "/scratch5/purged/Wei.Huang/src/nv/data/eagle/forecast/10u-heightAboveGround-0010.nc"
nc_v = "/scratch5/purged/Wei.Huang/src/nv/data/eagle/forecast/10v-heightAboveGround-0010.nc"
#nc_u = "/scratch5/purged/Wei.Huang/src/nv/data/eagle/forecast/u-isobaricInhPa-0250.nc"
#nc_v = "/scratch5/purged/Wei.Huang/src/nv/data/eagle/forecast/v-isobaricInhPa-0250.nc"

# Open and interact with dataset
# with xr.open_dataset(ncfilename) as ds:
du = xr.open_dataset(nc_u)
dv = xr.open_dataset(nc_v)
print(du)
print(dv)
# Extract data directly and remove the single-value dimensions (squeeze to 2D)
u = du["u10"].squeeze().values  # Now shape is (190, 338)
v = dv["v10"].squeeze().values  # Now shape is (190, 338)
# Direct 2D extraction using xarray indexing
longitude = du["longitude"].values
latitude = du["latitude"].values
CRS = du["CRS"]

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
ax.set_extent(
    [longitude.min(), longitude.max(), latitude.min(), latitude.max()],
    crs=ccrs.PlateCarree(),
)

# 3. Add base map layers
ax.add_feature(cfeature.COASTLINE, edgecolor="black")
ax.add_feature(cfeature.BORDERS, edgecolor="gray", linestyle=":")

# 4. Plot Wind Vectors using quiver
# Subsample your grid (take every 10th point) to make arrows readable
skip = 10
q = ax.quiver(
    longitude[::skip, ::skip],
    latitude[::skip, ::skip],
    u[::skip, ::skip],
    v[::skip, ::skip],
    transform=ccrs.PlateCarree(),  # Crucial for directional alignment
    color="darkred",
    scale=150,  # Increase to make arrows shorter, decrease to make them longer
    width=0.002,
)

# Add a reference vector key box at the bottom right corner
ax.quiverkey(q, X=0.9, Y=0.05, U=10, label="10 m/s", labelpos="E")

plt.title("Wind Vector Field (Quiver Plot)", pad=20)
plt.show()


import xarray as xr
import numpy as np
import pandas as pd
from typing import List
import yaml
import sys
from datetime import datetime


def open_raw_inference(path_to_raw_inference: str) -> xr.Dataset:
    """
    Open one Anemoi-Inference run.

    Args:
        path_to_raw_inference (str): Path to an Anemoi-Inference run.

    Returns:
        xr.Dataset: One initialization of an Anemoi-Inference run.
    """
    return xr.open_dataset(path_to_raw_inference)


def create_2D_grid(
    ds: xr.Dataset,
    vars_of_interest: List[str],
) -> xr.Dataset:
    """
    Reshape dataset from 1D 'values' dimension to 2D latitude and longitude.

    Args:
        ds (xr.Dataset): Anemoi dataset with a flattened "values" dimension.
        vars_of_interest (List[str]): Variables to reshape.

    Returns:
        xr.Dataset: Dataset with shape (time, latitude, longitude).
    """
    ds_to_reshape = ds.copy()

    lats = ds_to_reshape.latitude.values
    lons = ds_to_reshape.longitude.values
    sort_index = np.lexsort((lons, lats))
    ds_to_reshape = ds_to_reshape.isel(values=sort_index)

    lat_length = len(np.unique(ds_to_reshape.latitude.values))
    lon_length = len(np.unique(ds_to_reshape.longitude.values))
    time_length = len(ds["time"].values)

    lats = ds_to_reshape["latitude"][:].values.reshape((lat_length, lon_length))
    lons = ds_to_reshape["longitude"][:].values.reshape((lat_length, lon_length))
    lat_1d = lats[:, 0]
    lon_1d = lons[0, :]

    data_vars = {}
    for v in vars_of_interest:
        reshaped_var = ds_to_reshape[v].values.reshape(
            (time_length, lat_length, lon_length)
        )
        data_vars[v] = (["time", "latitude", "longitude"], reshaped_var)

    reshaped = xr.Dataset(
        data_vars=data_vars, coords={"latitude": lat_1d, "longitude": lon_1d}
    )

    return make_contiguous(reshaped)


def make_contiguous(
    reshaped,
):
    """
    xesmf was complaining about array not being in C format?
    apparently just a performance issue - but was tired of getting the warnings :)
    """
    for var in reshaped.data_vars:
        reshaped[var].data = np.ascontiguousarray(reshaped[var].values)
    for coord in reshaped.coords:
        if coord not in reshaped.dims:
            reshaped = reshaped.assign_coords(
                {coord: np.ascontiguousarray(reshaped[coord].values)}
            )
    return reshaped


def add_level_dim_for_individual_var(
    ds: xr.Dataset, var: str, levels: List[int]
) -> xr.Dataset:
    """
    Add level dimensions instead of flattened variables (e.g. geopotential_500, geopotential_800)

    Args:
        ds (xr.Dataset): Input dataset.
        var (str): Variable name to process.
        levels (List[int]): List of levels to process.

    Returns:
        xr.Dataset: Dataset with added level dimension for the specified variables.
    """
    var_level_list = []
    names_to_drop = []

    for level in levels:
        var_name = f"{var}_{str(level)}"
        var_level_list.append(ds[var_name])
        names_to_drop.append(var_name)

    stacked = xr.concat(var_level_list, dim="level")
    stacked = stacked.assign_coords(level=levels)
    ds[var] = stacked

    return ds.drop_vars(names_to_drop)


def add_level_dim(
    ds: xr.Dataset, level_variables: List[str], levels: List[int]
) -> xr.Dataset:
    """
    Wrapper function to add level dimension for all relevant variables.

    Args:
        ds (xr.Dataset): Input dataset.
        level_variables (List[str]): List of variables that have levels.
        levels (List[int]): List of levels to process.

    Returns:
        xr.Dataset: Dataset with added level dimensions for all variables.
    """
    for var in level_variables:
        ds = add_level_dim_for_individual_var(ds=ds, var=var, levels=levels)
    return ds


def final_steps(ds: xr.Dataset, time: xr.DataArray) -> xr.Dataset:
    """
    Add helpful attributes and reorganize dimensions for verification pipelines.

    Args:
        ds (xr.Dataset): Input dataset.
        time (xr.DataArray): Time coordinate.

    Returns:
        xr.Dataset: Dataset with necessary attributes for verification pipelines.
    """
    ds = ds.assign_coords(time=time)
    ds.attrs["forecast_reference_time"] = str(ds["time"][0].values)
    if {"x", "y"}.issubset(ds.dims):
        return ds.transpose("time", "level", "y", "x").rename(
            {"x": "longitude", "y": "latitude"}
        )
    elif {"latitude", "longitude"}.issubset(ds.dims):
        return ds.transpose("time", "level", "latitude", "longitude")


def postprocess(
    ds: xr.Dataset,
    vars_of_interest: List[str],
    level_variables: List[str],
    levels: List[int],
) -> xr.Dataset:
    """
    Postprocess Anemoi Inference Forecast.

    Args:
        ds (xr.Dataset): Anemoi inference dataset.
        vars_of_interest (List[str]): All variables to process.
        level_variables (List[str]): Variables that have levels.
        levels (List[int]): List of levels to process.

    Returns:
        xr.Dataset: Processed forecast ready for verification :)
    """
    time = ds["time"]

    ds_post = create_2D_grid(ds=ds, vars_of_interest=vars_of_interest)
    ds_post = add_level_dim(ds=ds_post, level_variables=level_variables, levels=levels)
    ds_post = final_steps(ds=ds_post, time=time)

    return ds_post


def run(
    initialization: pd.Timestamp,
    config,
    input_path,
):
    """
    Run full pipeline.

    """
    vars_of_interest = config["vars_of_interest"]
    level_variables = config["level_variables"]
    levels = config["levels"]
    raw_inference_files_base_path = input_path
    file_date = datetime.fromisoformat(initialization).strftime("%Y-%m-%dT%H")
    file_name = f"{file_date}"

    ds = open_raw_inference(
        path_to_raw_inference=f"{raw_inference_files_base_path}/{file_name}.nc"
    )

    ds_postprocessed = postprocess(
        ds=ds,
        vars_of_interest=vars_of_interest,
        level_variables=level_variables,
        levels=levels,
    )

    file_name_post = f"{file_name}_postprocessed.nc"

    ds_postprocessed.to_netcdf(file_name_post)

    print(f"Postprocessed file saved file as {file_name}")

    return


if __name__ == "__main__":
    input_path = sys.argv[1]

    with open("postprocess_config.yaml", "r") as f:
        config = yaml.safe_load(f)

    start_date = config["initializations_to_run"]["start"]
    end_date = config["initializations_to_run"]["end"]
    freq = config["initializations_to_run"]["freq"]

    dates = pd.date_range(start=start_date, end=end_date, freq=freq)
    for i in dates:
        run(
            initialization=str(i),
            config=config,
            input_path=input_path,
        )

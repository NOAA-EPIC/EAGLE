import os
import sys
import yaml
import logging

from datetime import datetime
import pandas as pd

from anemoi.inference.config.run import RunConfiguration
from anemoi.inference.runners import create_runner


def date_to_str(
    date: str,
) -> str:
    """
    Format initializtion date to a nicely formatted string that is used for writing out files.

    Args:
        date (str): date of initialization.

    Returns:
        str -- date of initialization in str format.
    """
    dt = datetime.fromisoformat(date)
    return dt.strftime("%Y-%m-%dT%H")


def create_config(
    init_date: str,
    checkpoint,
    input_data,
    output_folder,
) -> dict:
    """
    Create the config that will be passed to anemoi-inference.

    Args:
        init_date (str): date of initialization.
        checkpoint: path to checkpoint
        input_data: path to folder where input zarr lives
        output_folder: path to save output data

    Returns:
        dict -- formatted config for anemoi-inference.
    """
    date_str = date_to_str(date=init_date)
    config = {
        "checkpoint": checkpoint,
        "date": date_str,
        "lead_time": 240,
        "input": {
            "dataset": f"{input_data}/replay.zarr",
        },
        "output": {"netcdf": f"{output_folder}/test.nc"},
    }

    return config


def run_forecast(
    init_date: str,
    checkpoint,
    input_data,
    output_folder,
) -> None:
    """
    Inference pipeline.

    Args:
        init_date (str): date of initialization.

    Returns:
        None -- files saved out to output path.
    """
    config_dict = create_config(
        init_date=init_date,
        checkpoint=checkpoint,
        input_data=input_data,
        output_folder=output_folder,
    )
    config = RunConfiguration.load(config_dict)
    runner = create_runner(config)
    runner.execute()

    return


if __name__ == "__main__":
    checkpoint = sys.argv[1]
    input_data = sys.argv[2]
    output_folder = sys.argv[3]

    dates = pd.date_range(start="2023-01-01T12", end="2023-01-01T12", freq="12h")

    for d in dates:
        run_forecast(
            init_date=str(d),
            checkpoint=checkpoint,
            input_data=input_data,
            output_folder=output_folder,
        )

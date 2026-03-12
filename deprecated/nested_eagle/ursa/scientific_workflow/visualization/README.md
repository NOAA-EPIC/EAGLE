## Tools for Visualizing Model Output and Performance

The eagle-tools package provides a variety of tools to visualize model output and analyze overall performance. See below for instructions to view various metrics or create your own plots.

### Aggregate statistics from verification across multiple initializations and lead times

The `wxvx` saves out a plot for each initialization and variable separately. If you wish to aggregate statistics over many initializations to analyze performance of your model over a longer period of time, simply run the following commands:

Gather all statistics for global domain:

```
eagle-tools postwxvx postwxvx_global.yaml
```

Gather all statistics for CONUS (lam) domain:

```
eagle-tools postwxvx postwxvx_lam.yaml
```

These commands will then save `.nc` files with all relevant statistics in the wxvx directories. If you were to run these commands in this directory, the files would then be saved here: `../verification/{grid2obs or grid2grid}/wxvx_workdir/global` and `../verification/{grid2obs or grid2grid}/wxvx_workdir/lam`.

You will then see a nc file for each variable. To view statistics for 2m_temperature, for example, run the following:

```
import xarray as xr
ds = xr.open_dataset("2m_temperature.nc")
ds["RMSE"].plot()
```

Additional tools will be added soon.

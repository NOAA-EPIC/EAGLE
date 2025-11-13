## Workflow

#### Step 1: Go to `/prewxvx`

Postprocess inference output to ensure it is correctly formatted for wxvx.

Run `sbatch submit_postprocessing.sh`

After this step is complete, move to Step 2.

#### Step 2: Verify forecasts

There are two options for forecast verification.

Option 1: grid to observations found in `/grid2obs`
- To verify both the global and CONUS domains against observations, run `sbatch submit_obs_verification.sh`

Option 2: grid to grid found in `/grid2grid`
- To verify global and CONUS domains against gridded analysis, run `sbatch submit_grid_verification.sh`
- CONUS domain is verifed against the HRRR
- Global domain is verified against the GFS

#### Step 3: Find results

Now check the folder that you ran verification within, and look for `wxvx_workdir/{DOMAIN}/run/plots/`. 
There will be numerous plots showing RMSE and ME for various variables. There will be a plot separately saved for each initialization and variable.

Additionally, feel free to move to the `visualization` folder for further resources on viewing model output and performance.

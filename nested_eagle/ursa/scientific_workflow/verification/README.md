## Workflow

#### Step 1:
Postprocess inference output to ensure it is correctly formatted for wxvx:
`sbatch submit_postprocessing.sh`

#### Step 2:
After post-processing is complete, run:
`sbatch submit_verification.sh`

Two separate verification tasks were performed:
1) A verification of the CONUS only domain against observations
2) A verficiation of the global domain against observations

Now go to `wxvx_workdir/{DOMAIN}/run/plots/` and open some plots showing RMSE and ME for various variables. There will be a plot separately saved for each initialization and variable.

Additionally, feel free to move to the visualization folder for further resources on viewing model output and performance.

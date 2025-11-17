## Inference Workflow

Please see our [documentation](https://epic-eagle.readthedocs.io/en/latest/inference.html) for further information about generating forecasts. For more in-depth information about inference capabilities, see the [anemoi-inference documentation](https://anemoi.readthedocs.io/projects/inference/en/latest/)

### Steps

Step 1: Make sure that you update `#SBATCH --account=epic` within the slurm scripts to reflect your account.

Step 2: Run the following to submit a job to create a 10-day forecast: `sbatch submit_inference.sh`

This script will use `eagle-tools` to execute `anemoi-inference`. Your forecast files will be saved as NetCDF's in a `inference_files` directory.

Note: Within `inference_config.yaml` you will find a path to a checkpoint. The submit script programatically updates that for you. However, if you have trained multiple models (due to model testing, something failed the first time, etc.) you may have to go edit the checkpoint path yourself. To do this, go back to the `/training` folder to find the specific run_id and checkpoint you wish to use. If you do this, then delete the first 2 lines of the submit_inference.sh script, as they are no longer needed.

## Model Training Workflow

Please see our [documentation](https://epic-eagle.readthedocs.io/en/latest/train_a_model.html) for more information about model training, how to interpret model outputs and plots, and quick tips on configuration changes for testing.

### Steps

Step 1: Make sure that you update `#SBATCH --account=epic` within the slurm scripts to reflect your account.

Step 2: Run`sbatch submit_training.sh`

This slurm job will run the entire training process. After job submission, go into the `outputs/` folder to monitor training. You will see the following model output:

1. Logs: found within a folder including the date of your run (e.g. `2025-10-22`)

2. Checkpoints: found within a folder that matches the run_id of your training. It will resemble something like `cf574663-cfa7-4ff2-aafd-37fb5af6bef5`.

3. Plots: also found within a run_id folder (e.g. `cf574663-cfa7-4ff2-aafd-37fb5af6bef5`).

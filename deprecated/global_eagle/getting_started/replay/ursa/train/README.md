First, update `submit_training.sh` with your project account and path to your miniconda installation.

Then run the following to submit a job to train on your data:

`sbatch submit_training.sh`

STDOUT and STDERR from the job will be placed in the `slurm` directory.

After training is complete, go to the output directory to access checkpoints and view interesting plots. Note the run ID (the long alpha-numeric directory inside of `trainig/training-output/checkpoint`); you will need that ID in the next step.

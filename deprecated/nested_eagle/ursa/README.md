## nested-EAGLE Setup on Ursa

There are two folders:

1) `scientific_workflow` will guide you through the entire ML pipeline to create training data, train a model, run inference, verify a forecast, and visualize model output.

2) `operational_inference` provides scripts to run inference from a checkpoint in near real-time. These scripts assume the user has a checkpoint from completing `scientific_workflow` and wants to run a near real-time forecast.

### Conda Environments

Two conda environments are required to complete this pipeline:
1) `eagle` environment to use for data creation, training, and inference
2) `wxvx` environment to use for verification

These environments have already been made for you on Ursa. You do not need to activate these environments on your own, as each individual slurm job will activate the environment for you.

If you wish to do local testing, the environments can be found by running `source /scratch4/NAGAPE/epic/role-epic/miniconda/bin/activate`

### Conda Environment Setup Elsewhere

If you are not running on Ursa, or wish to create the environments yourself, run the following commands:

`eagle` environment to use for data creation, training, and inference:
```
module load cuda gcc openmpi
conda env create -f environment.yaml
conda activate eagle
pip install 'flash-attn<2.8' --no-build-isolation
```

`wxvx` environment to use for verification:
```
conda create -y -n wxvx -c ufs-community -c paul.madden wxvx -c conda-forge --override-channels
```

Then, simply activate the environments by running `conda activate eagle` or `conda activate wxvx`

Note: These commands currently work on Ursa and may require tweaking for other machines.

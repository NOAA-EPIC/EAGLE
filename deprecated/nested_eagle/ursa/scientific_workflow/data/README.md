## Data Preprocessing Workflow

Please see our [documentation](https://epic-eagle.readthedocs.io/en/latest/data_creation.html) for further information about data processing and some tips for local testing. For more in-depth information about ufs2arco capabilities, see the [ufs2arco documentation](https://ufs2arco.readthedocs.io/en/latest/)

### Steps

Step 1: Make sure that you update `#SBATCH --account=epic` within the slurm scripts to reflect your account.

Step 2: Run `sbatch submit_grids.sh`

This creates static grid files that will be used for regridding data throughout the pipeline and creating a static grid for the latent mesh during training. Once this jobs has completed you can move onto Step 3 (training data creation).

Note: This step creates static files that you can reuse, so if you run through this pipeline multiple times it may not be necessary to always re-run this. In general, this job is only needed if you wish to regrid your data, or need to create latent mesh if that is part of your model training. As provided, the nested-EAGLE configurations require these grids.

Step 3: Run `sbatch submit_gfs.sh` followed by `sbatch submit_hrrr.sh`

These jobs can run at the same time. One job is loading GFS data, while the other is loading HRRR data. It is possible to submit these together within one job, but separate jobs makes the process faster. 

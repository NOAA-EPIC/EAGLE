Verification needs a different python environment than previous steps, so the first time you run you will need to create a new one:

```
conda create -y -n wxvx -c ufs-community -c paul.madden wxvx -c conda-forge --override-channels
```

You should not need to do this again unless you reinstall miniconda.


Verification is a two-step process run in an interactive prompt.

First, activate the python environment we created above:

```conda activate wxvx```

The first processing step will postprocess inference run into a format that will seamlessly work with wxvx

```python postprocess.py postprocess_config.yaml```

This will create a new NetCDF in `verification` that is ready for the verification step.

The second step will verify against GFS and create plots. First, modify the meta:workdir setting in `wxvx_config.yaml` with the **full path** to your `verification/output` directory. Then run the following:

```wxvx -c wxvx_config.yaml -t plots```

This will create MET stat files for each variable and forecast hour in `output/run/stats` and plots in `output/run/plots`.

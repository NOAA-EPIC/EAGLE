This folder contains what we will consider a "hello world" configuration for the full `ufs2arco + Anemoi + wxvx` pipeline.

You will be able to:
1) Use `ufs2arco` to create training and validation datasets with NOAA Replay reanalysis
    - 1 year of data for training and 0.25 years for validation
    - 1-degree global data
2) Use `anemoi-core` modules to train a graph-based model
3) Use `anemoi-inference` to run inference
4) Use `wxvx` to run grid-to-grid verification on a forecast

There are configurations for running this set up in the following locations:
- Perlmutter
- Ursa
- AzureML

The scripts and config files to submit jobs in each location are found in the respective folders.
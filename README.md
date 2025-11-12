# Welcome to Eagle!

This repository contains various configurations to guide users through a full machine learning pipeline for weather prediction!

You will find multiple directories showcasing various model configurations ranging from a "hello world" setup to operational quality models.

The key steps to this pipeline include:
1) Data preprocessing using `ufs2arco` to create training, validation, and test datasets
2) Model training using `anemoi-core` modules to train a graph-based model
3) Creating a forecast with `anemoi-inference` to run inference from a model checkpoint
4) Verifying forecasts with `wxvx` against gridded analysis or observervations

This pipeline also implements an `eagle-tools` library that provides various utilites for tasks such as executing modules or post-processing needs.

For more information about model configurations or the various steps of the pipeline, please see our [documentation](https://epic-eagle.readthedocs.io/en/latest/).

---------------------

### Acknowledgments

ufs2arco: Tim Smith (NOAA Physical Sciences Laboratory)
- [Github](https://github.com/NOAA-PSL/ufs2arco)
- [Documentation](https://ufs2arco.readthedocs.io/en/latest/)

Anemoi: European Centre for Medium-Range Weather Forecasts
- [anemoi-core github](https://github.com/ecmwf/anemoi-core)
- [anemoi-inference github](https://github.com/ecmwf/anemoi-inference)
- Documentation: [anemoi-models](https://anemoi.readthedocs.io/projects/models/en/latest/index.html), [anemoi-graphs](https://anemoi.readthedocs.io/projects/graphs/en/latest/), [anemoi-training](https://anemoi.readthedocs.io/projects/training/en/latest/), [anemoi-inference](https://anemoi.readthedocs.io/projects/inference/en/latest/)

wxvx: Paul Madden (NOAA Global Systems Laboratory/Cooperative Institute for Research In Environmental Sciences)
- [Github](https://github.com/maddenp-cu/wxvx)

eagle-tools: Tim Smith (NOAA Physical Sciences Laboratory)
- [Github](https://github.com/NOAA-PSL/eagle-tools)

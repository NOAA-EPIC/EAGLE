# Welcome to EAGLE!

This repository contains various configurations to guide users through a full machine learning pipeline for weather prediction! You will find multiple directories showcasing various model configurations ranging from a "hello world" setup to operational quality models. While various model configurations will differ, they will all follow the same steps of an end-to-end machine learning pipeline. This includes:

1) Proper environment setup: Users are provided with ready-to-use conda environments
2) Prepare training data: Use `ufs2arco` to create training, validation, and test datasets
3) Train an AI model: use `anemoi-core` modules to train a graph-based model for weather prediction
4) Generate a forecast: use `anemoi-inference` to run inference from a model checkpoint
5) Verify model performance: use `wxvx` to verify forecasts against gridded analysis or observervations
6) View model output: use `eagle-tools` to visualize model output and scores

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

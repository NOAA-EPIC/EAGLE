# EAGLE

This repository contains configuration and driver code for running an end-to-end machine learning pipeline for weather prediction. The pipeline is orchestrated with `make` targets and `uwtools`-based drivers, and it provisions a self-contained set of conda environments to support each step of the workflow. A typical run follows these steps:

- **Environment setup:** Creates the runtime environments used by each stage of the pipeline.
- **Prepare training and inference data:** Provisions required static assets (e.g., grids and meshes) and produces Zarr-formatted datasets via `ufs2arco`.
- **Train an AI model:** Trains an Anemoi model using the provisioned datasets, producing checkpoints for inference.
- **Generate a forecast:** Runs inference from training checkpoints using `anemoi-inference` to produce forecast output.
- **Prepare output for verification:** Postprocesses forecast output into the formats and directory structure expected by `wxvx`.
- **Verify model performance:** Runs `wxvx` verification against gridded analysis and/or observations, producing MET statistics and plots.

## Documentation

To learn about EAGLE and how to use the provided workflows, please see our [documentation](https://epic-eagle.readthedocs.io/en/latest/).

## Collaboration

- If you encounter a problem using EAGLE that appears to be a bug, please open an [issue](https://github.com/NOAA-EPIC/EAGLE/issues) with us.
- For free-form sharing of ideas, questions, tips and tricks, etc., please start or join a [discussion](https://github.com/NOAA-EPIC/EAGLE/discussions).
- To contribute to the codebase, please see our [docs](https://epic-eagle.readthedocs.io/en/latest/contributing.html).

## Acknowledgments

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

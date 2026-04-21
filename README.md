# EAGLE

## Description

The Earth Prediction Innovation Center (EPIC) and the NOAA Artificial Intelligence for Numerical Weather Prediction (AI4NWP) Working Group announce the public release of the nested‑Experimental AI Global and Limited‑area Ensemble forecast system (nested‑EAGLE) v1.0.0.

This release complements the Environmental Modeling Center's (EMC) GraphCast‑based global‑EAGLE‑solo and global‑EAGLE ensemble forecast systems, now operational within NOAA. Nested‑EAGLE v1.0.0 provides a machine-learning (ML) based forecast workflow integrated with the European Centre for Medium-Range Weather Forecasts (ECMWF) and partner agencies' anemoi ML framework, supporting an end-to-end (E2E) pipeline from training data preprocessing through forecast generation, verification, and visualization.

## Scope and Capabilities

The nested‑EAGLE application is designed for ML model training on both:

- a global domain (~25 km)
- a nested CONUS domain (~6 km or 15 km)

It produces atmosphere‑only forecasts for multiple variables.

This initial release is supported on the NOAA Research and Development High Performance Computing System (RDHPCS) Ursa, which provides the GPU resources required for the EAGLE ML model training workflow. Advanced users may replicate the workflow on other HPC platforms. Future releases will expand support to native Microsoft Azure cloud environments.

## Workflow Components

The nested‑EAGLE workflow includes:

- environment setup
- data preprocessing
- ML training
- inference
- postprocessing
- verification
- visualization

Preprocessing uses NOAA PSL's `ufs2arco` utility to convert NOAA and non-NOAA datasets into anemoi‑ready training formats, such as Unified Forecast System (UFS) to Analysis Ready, Cloud Optimized (ARCO) format. ECMWF and partner agencies' `anemoi-core` performs model training and produces checkpoint files for `anemoi‑inference`, which generates forecast outputs. Postprocessing converts these outputs into verification-ready formats.

Verification is performed using NOAA GSL's `wxvx` package, which leverages Model Evaluation Tools (MET) to compute a wide range of statistics and generate diagnostic plots, such as RMSE and ME, for standard 2‑D and 3‑D variables across forecast lead times. The `eagle‑tools` Python package provides lightweight utilities for postprocessing and visualization of model performance metrics. Repository testing includes optimized end‑to‑end workflow tests and static code analysis.

## Collaboration

- If you encounter a problem using EAGLE that appears to be a bug, please open an [issue](https://github.com/NOAA-EPIC/EAGLE/issues) with us.
- For free-form sharing of ideas, questions, tips and tricks, etc., please start or join a [discussion](https://github.com/NOAA-EPIC/EAGLE/discussions).
- To contribute to the codebase, please see our [docs](https://epic-eagle.readthedocs.io/en/v1.0.0/contributing.html).

## Acknowledgments

ufs2arco: Tim Smith (NOAA Physical Sciences Laboratory)
- [Github](https://github.com/NOAA-PSL/ufs2arco)
- [Documentation](https://ufs2arco.readthedocs.io/en/latest/)

Anemoi: ECMWF and partner agencies
- [anemoi-core github](https://github.com/ecmwf/anemoi-core)
- [anemoi-inference github](https://github.com/ecmwf/anemoi-inference)
- Documentation: [anemoi-models](https://anemoi.readthedocs.io/projects/models/en/latest/index.html), [anemoi-graphs](https://anemoi.readthedocs.io/projects/graphs/en/latest/), [anemoi-training](https://anemoi.readthedocs.io/projects/training/en/latest/), [anemoi-inference](https://anemoi.readthedocs.io/projects/inference/en/latest/)

wxvx: Paul Madden (NOAA Global Systems Laboratory/Cooperative Institute for Research In Environmental Sciences)
- [Github](https://github.com/maddenp-cu/wxvx)

eagle-tools: Tim Smith (NOAA Physical Sciences Laboratory)
- [Github](https://github.com/NOAA-PSL/eagle-tools)

## Citation 

UFS Development Team, & NOAA AI for Numerical Weather Prediction (AI4NWP) Working Group. (2026, Apr. 22). nested-EAGLE (Experimental AI Global and Limited-area Ensemble Forecast System) (Version v1.0.0). Zenodo. https://doi.org/10.5281/zenodo.19672026

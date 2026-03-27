=============================
Train a Graph-Based Model
=============================

anemoi-core Overview
-------------------------

Anemoi-core provides the infrastructure to train various types of (mostly graph-based) ML models. It handles 
the entire training workflow so that users can focus on model detail choices instead of complicated orchestration. 
Within the EAGLE repo, the anemoi-core packages are used to train various EAGLE ML models at scale.

See Anemoi documentation for further information:

- `anemoi-graphs <https://anemoi.readthedocs.io/projects/graphs/en/latest/>`_
- `anemoi-training <https://anemoi.readthedocs.io/projects/training/en/latest/>`_
- `anemoi-models <https://anemoi.readthedocs.io/projects/models/en/latest/index.html>`_

Anemoi was created by the European Centre for Medium-Range Weather Forecasts.

Helpful quick tips for using anemoi-core
----------------------------------------------

The workflows in the EAGLE repository handle config management for you. Here are a few tips to help you understand 
what is going on behind the scenes, and to hopefully help you make desired config changes.

Brief Config Overview
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The configs used by anemoi-training contain a lot of information. At the top of a main config you will see something like

.. code-block:: yaml

    defaults:
    - data: zarr
    - dataloader: native_grid
    - diagnostics: evaluation
    - system: slurm
    - graph: encoder_decoder_only
    - model: transformer
    - training: stretched
    - _self_

This points the training job to the appropriate YAML file needed for various model configurations. For example, the first 
line points to ``zarr.yaml`` within the data folder, which then provides the training job with information about the training 
data such as variable names and temporal frequency. 

The EAGLE workflow consolidates all information required by the model within the main ``config.yaml``. This setup ensures 
that users only have to edit one YAML config file for training.

If you have any questions about the available model configurations within anemoi-core, go see the 
`anemoi-training <https://anemoi.readthedocs.io/projects/training/en/latest/>`_ documentation.

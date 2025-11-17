=================
Train a Graph-Based Model
=================

anemoi-core Overview
-------------------------

We deploy the anemoi-core modules to train a graph-based model.

See Anemoi documentation for further information:

- `anemoi-graphs <https://anemoi.readthedocs.io/projects/graphs/en/latest/>`_
- `anemoi-training <https://anemoi.readthedocs.io/projects/training/en/latest/>`_
- `anemoi-models <https://anemoi.readthedocs.io/projects/models/en/latest/index.html>`_

Anemoi was created by the European Center for Medium-Range Weather Forecasting.

Helpful quick tips for using anemoi-core
------------------

Throughout this repository, all anemoi configs are typically provided for you and should work out of the box. 
See below for various tips and explanations if you wish to learn more about the configs or want to change the configurations.

Brief Config Overview
~~~~~~~~~~~~~~~~~~~~~~

The configs used by anemoi-training contain a lot of information. At the top of a main config you will see something like

.. code-block:: yaml

    defaults:
    - data: zarr
    - dataloader: native_grid
    - datamodule: single
    - diagnostics: evaluation
    - hardware: slurm
    - graph: encoder_decoder_only
    - model: transformer
    - training: stretched
    - _self_

This points the training process to the appropriate yaml file needed for various steps. 
For example, the first line points to zarr.yaml within the data folder, 
which then provides the training process with information on the training data such as variables used and temporal frequency. 

Throughout this repository, we have consolidated a lot of very useful information within the main config.yaml. 
This makes it so the main config.yaml contains most model configurations that are worth noting, and additionally makes those 
configurations easy to change.

Generating Configs Yourself
~~~~~~~~~~~~~~~~~~~~~~

If you wish to use brand new configs and configure a model yourself, run the following command while within 
a conda environemnt that contains all of the anemoi-core modules:

```
anemoi-training config generate
```

This will generate new anemoi configs for you. If you have any questions about the configs go see the anemoi-training documentation.
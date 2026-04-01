.. _TrainGraphBasedModel:

==============================================================================
Train a Graph-Based Model
==============================================================================

anemoi-core Overview
------------------------------------------------------------------------------

We use the :term:`anemoi` training stack to train a graph-based model.
anemoi-core provides the infrastructure to train various types of mostly
graph-based ML models. It handles the training workflow so users can focus on
model-design choices instead of more complicated orchestration.

See the anemoi documentation for further information:

- `anemoi-graphs <https://anemoi.readthedocs.io/projects/graphs/en/latest/>`_
- `anemoi-training <https://anemoi.readthedocs.io/projects/training/en/latest/>`_
- `anemoi-models <https://anemoi.readthedocs.io/projects/models/en/latest/index.html>`_

anemoi was created by the European Centre for Medium-Range Weather Forecasts
(:term:`ECMWF`).

anemoi-core Quick Tips
------------------------------------------------------------------------------

Throughout this repository, the anemoi configs are typically provided for you
and should work out of the box. See below for tips and explanations if you
want to learn more about the configs or modify them.
The workflows in the EAGLE repository handle config management for you. The
notes below are intended to help explain what is happening behind the scenes
and to make it easier to modify configs when needed.

Brief Config Overview
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The configs used by ``anemoi-training`` contain a lot of information. At the
top of a main config, you will see something like:

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

This points the training process to the appropriate YAML file needed for
various steps. For example, the first line points to ``zarr.yaml`` within the
data folder, which then provides the training process with information on the
training data such as variables used and temporal frequency.

Throughout this repository, we have consolidated a lot of useful information in
``src/config/base.yaml``, especially under the ``training.anemoi`` section.
This means ``src/config/base.yaml`` contains many of the model configurations
that are most useful to note, and it also makes those configurations easier to
change.

If you have questions about the available model configurations within
anemoi-core, see the `anemoi-training documentation
<https://anemoi.readthedocs.io/projects/training/en/latest/>`_.

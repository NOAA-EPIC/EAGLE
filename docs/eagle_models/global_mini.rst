=================
global-mini
=================

The global-mini model is a small, global, 1-degree configuration
designed to sit **between a toy model and an operational-quality model**.

* It is **not a toy**. It uses the same pipeline, data tooling, and
  architecture family (Graph Transformer encoder/decoder with a Transformer
  processor) as the other EAGLE models.
* It is **not operational quality**. Its reduced resolution, smaller network,
  and shorter training budget mean its skill is lower than the
  :doc:`global-EAGLE <global_eagle>` and :doc:`nested-EAGLE <nested_eagle>` models.

It is trained so that **inference can run on a CPU or a local laptop**, with no
GPU or HPC system required. This makes it useful for learning the workflow,
testing code and configuration changes, training sessions, and demos.

.. note::

   global-mini is intended for education and demonstration. For scientific or
   near-real-time forecasting, use the :doc:`global-EAGLE <global_eagle>` or
   :doc:`nested-EAGLE <nested_eagle>` models.


Training Data
------------------

At a glance:

* :term:`GFS` initial conditions, conservatively regridded to 1 degree.
* 6-hourly data.
* The training period spans ``2020-01-01`` through ``2024-12-31``.
* The validation period spans ``2025-01-01`` through ``2025-12-31``.
* The testing period spans ``2026-01-01`` through ``2026-09-30``.

The model uses the same variable categories as the other EAGLE models:

.. list-table:: global-mini variables by category
   :widths: 20 80
   :header-rows: 1

   * - Category
     - Fields
   * - Diagnostic
     - ``u80``, ``v80``, ``accum_tp``
   * - Forcing
     - ``lsm``, ``orog``, ``cos_latitude``, ``sin_latitude``,
       ``cos_longitude``, ``sin_longitude``, ``cos_julian_day``,
       ``sin_julian_day``, ``cos_local_time``, ``sin_local_time``,
       ``insolation``

All remaining dataset fields are treated as prognostic variables.


Model Architecture
------------------

.. list-table:: global-mini architecture
   :widths: 30 70
   :header-rows: 1

   * - Component
     - Setting
   * - Encoder and decoder
     - Graph Transformer (4 heads, MLP hidden ratio 2)
   * - Processor
     - Transformer, 8 layers, 8 heads, window size 256, MLP hidden ratio 2
   * - Channels
     - 512
   * - Latent mesh
     - Triangular mesh, refinement level 4 (2,562 nodes, roughly 250 km)
   * - Attention backend
     - ``scaled_dot_product_attention`` (processor), ``pyg``
       (encoder and decoder), so no GPU-specific kernels are needed

For comparison, nested-EAGLE uses a 16-layer processor with a window size of
4320 and requires GPU-specific kernels (flash attention and Triton).


Configuration
------------------

The model is configured in ``config/global_mini.yaml``, which is composed on top
of ``config/base.yaml``:

.. code-block:: bash

   uw config compose config/base.yaml config/global_mini.yaml > eagle.yaml

For Google Colab, an additional overlay, ``config/colab.yaml``, reduces the
time range and training length and removes the scheduler launcher so each step
runs directly in the notebook:

.. code-block:: bash

   uw config compose config/base.yaml config/global_mini.yaml config/colab.yaml > eagle.yaml


Demonstration Notebook
----------------------

The ``notebooks/global_mini.ipynb`` notebook walks through the full EAGLE
pipeline on a small dataset and can be run in Google Colab:

.. image:: https://colab.research.google.com/assets/colab-badge.svg
   :alt: Open In Colab
   :target: https://colab.research.google.com/github/NOAA-EPIC/EAGLE/blob/main/notebooks/global_mini.ipynb

The notebook covers:

#. **Environment setup**: creates the ``base``, ``data``, ``anemoi``, and
   ``wxvx`` conda environments.
#. **Config composition**: builds the main config with ``uwtools``.
#. **Data preprocessing**: creates training and validation datasets from GFS
   with ``ufs2arco``.
#. **Training**: trains a graph-based model with ``anemoi-core`` modules.
#. **Inference**: creates a forecast from the trained checkpoint with
   ``anemoi-inference`` and ``eagle-tools``, then plots the output.

The notebook trains for only a few steps on a very short period, so the
resulting forecasts are for demonstration of the workflow and are not
meaningful in terms of skill. A T4 GPU is required for training in Colab.

.. note::

   Planned notebook additions include loading a checkpoint pretrained for
   40,000 steps, running near-real-time inference, and verifying the forecast
   with ``wxvx``.
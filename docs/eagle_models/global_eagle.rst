=================
global-EAGLE
=================

:term:`EAGLE` currently includes a prototype EAGLE model trained with
global :term:`GFS` data.

EAGLE configurations were provided by Tim Smith at NOAA Physical
Sciences Laboratory.

Training Data
------------------

The EAGLE training dataset combines regridded global and regional
forecast data.

At a glance:

* :term:`GFS` is conservatively regridded to 1 degree.
* The training period spans ``2015-02-01T06`` through ``2023-01-31T18``.
* The validation period spans ``2023-02-01T06`` through ``2024-01-31T18``.
* The testing period spans ``2024-02-01T06`` through ``2025-01-31T18``.

.. list-table:: EAGLE input variables by category
   :widths: 20 80
   :header-rows: 1

   * - Category
     - Fields
   * - Prognostic
     - ``gh``, ``u``, ``v``, ``w``, ``t``, ``q``, ``sp``, ``u10``, ``v10``,
       ``t2m``, ``t_surface``, ``sh2``
   * - Diagnostic
     - ``u80``, ``v80``, ``accum_tp`` using ``fhr=6``
   * - Forcing
     - ``lsm``, ``orog``, ``cos_latitude``, ``sin_latitude``,
       ``cos_longitude``, ``sin_longitude``, ``cos_julian_day``,
       ``sin_julian_day``, ``cos_local_time``, ``sin_local_time``,
       ``insolation``

The vertical levels used in the dataset are ``100``, ``150``, ``200``,
``250``, ``300``, ``400``, ``500``, ``600``, ``700``, ``850``, ``925``, and
``1000``.


Model Architecture
------------------

The EAGLE model uses the following architecture:

* Encoder and Decoder: Graph Transformer
* Processor: Sliding Window Transformer
* Latent space is a 4x coarsened data space

The graph configuration connects targets to nodes through nearest neighbors in
the encoder and decoder, with ``encoder_knn=12`` and ``decoder_knn=3``.

The latent mesh is four times coarser than the native data resolution.

Near-Real-Time Forecasting
--------------------------

The global-EAGLE model can be run in near real time (NRT) using the
``feature/global_eagle`` branch in this repository. That branch includes the required 
dependencies (including compatible ``anemoi`` versions) and is the recommended
starting point for NRT runs of global-EAGLE.

To run NRT:

#. Check out the ``feature/global_eagle`` branch.

   .. code-block:: bash

      git checkout feature/global_eagle

#. EPIC hosts the checkpoint on Azure. To download the checkpoint to your machine, simply run: 

   .. code-block:: bash

      wget -O inference-last.ckpt https://eaglecheckpoints.blob.core.windows.net/eagle-checkpoints/global-eagle/era5_gdas_global_check.ckpt

#. Follow the :ref:`NRT workflow <NRT>` but, before running its ``make realize`` step, update:

   * ``app.base`` to the absolute path of your local repository root
   * ``inference.anemoi.checkpoint_dir`` to the checkpoint you downloaded from Azure (inference-last.ckpt)

After those updates, realize the config and continue with the remaining quickstart 
NRT steps for the global configuration.

.. _Quickstart:

====================
Quickstart Guide
====================

This section provides a recipe for an end-to-end run of nested-EAGLE on Ursa. At present, Ursa is the only supported 
platform. Future development will include additional platforms.

.. note::

   GNU ``make`` version 3.82 or higher is required.

**Complete the following steps from the ``src/`` directory.**

.. _QuickstartWorkflow:

Building and Running EAGLE
=========================================

#. Create all environments

   .. code-block:: bash

      make env cudascript=ursa

   This step creates the runtime software environment, comprising conda virtual environments to support data preparation, 
   training, inference, and verification. The ``conda/`` subdirectory it creates is self-contained and can be removed 
   and recreated by running the ``make env`` command again, as long as pipeline steps are not currently running.

   Developers who will be modifying Python driver code should replace ``make env`` with ``make devenv``, which will 
   create the same environments but also install additional code-quality tools for formatting, linting, shellchecking, 
   typechecking, and YAML linting.

#. Create the EAGLE YAML config

   .. code-block:: bash

      make config compose=base:ursa >eagle.yaml

   The ``config`` target operates on ``.yaml`` files in the ``config/`` directory, so this command composes ``config/base.yaml`` 
   and ``config/ursa.yaml`` and redirects the composed config into ``eagle.yaml``.

#. Set the ``app.base`` value in ``eagle.yaml`` to the absolute path to the current ``src/`` directory.

   The run directories from subsequent steps, along with the output of those steps, will be created in the ``run/<expname>`` 
   subdirectory of ``app.base``, where ``<expname>`` is the value of ``app.experiment_name``.

   Verify the ``app.account`` value. The default configuration sets ``app.account`` to ``epic``. If you do not have access to the ``epic`` account on Ursa, update this value to an account you are authorized to use.

#. Create training data

   .. code-block:: bash

      make data config=eagle.yaml

   This step provisions data required for training and inference. The ``data`` target delegates to targets 
   ``grids-and-meshes``, ``zarr-gfs``, and ``zarr-hrrr``, which can also be run individually (e.g. ``make grids-and-meshes config=eagle.yaml``), but note that ``grids-and-meshes``, which runs locally, must be run first. The ``zarr-gfs`` and ``zarr-hrrr`` targets can be run in quick succession, as they submit batch jobs: Do not proceed until their batch jobs complete successfully (see the files ``run/<expname>/data/*.out``).

#. Train the ML model

   .. code-block:: bash

      make training config=eagle.yaml

   This step trains a model using data provisioned by the previous step. It submits a batch job; do not proceed until 
   the batch job completes successfully (see the file ``run/<expname>training/runscript.training.out``).

#. Run inference

   .. code-block:: bash

      make inference config=eagle.yaml

   This step performs inference, producing a forecast. It submits a batch job. Do not proceed until the batch job 
   completes successfully (see the file ``run/<expname>inference/runscript.inference.out``.)

#. Postprocess model output

   .. code-block:: bash
      
      make prewxvx-global config=eagle.yaml
      make prewxvx-lam config=eagle.yaml

   These steps prepare forecast output from the previous step for verification by ``wxvx``. They run locally, so it is 
   safe to proceed when the commands return. See the files ``run/<expname>vx/prewxvx/{global,lam}/runscript.prewxvx-*.out`` for details.

.. _QuickstartVerification:

#. Model verification

   .. code-block:: bash
      
      make vx-grid-global config=eagle.yaml
      make vx-grid-lam config=eagle.yaml
      make vx-obs-global config=eagle.yaml
      make vx-obs-lam config=eagle.yaml

   These steps perform verification of the ``global`` or ``lam`` forecasts against gridded analyses (``*-grid-*``) or 
   PrepBUFR observations (``*-obs-*``) as truth. Each submits a batch job, so the four ``make`` commands can be run in quick 
   succession to get all the batch jobs running in parallel. When each batch job completes, MET ``.stat`` files and ``.png`` 
   plot files can be found under the ``stats/`` and ``plots/`` subdirectories of ``run/<expname>vx/grid2{grid,obs}/{global,lam}/run/``. 
   The files ``run/<expname>vx/*.log`` contain the logs from each verification run.

#. Make additional visualizations

   .. code-block:: bash

      make vis-grid-global config=eagle.yaml
      make vis-grid-lam config=eagle.yaml
      make vis-obs-global config=eagle.yaml
      make vis-obs-lam config=eagle.yaml

   These steps will first call ``eagle-tools``'s ``postwxvx`` tool which will create and save a series of netCDF files with all relevant statistics in the corresponding ``wxvx`` directory for each variable. It will then create a series of plots in the ``run/<expname>visualization/grid2{grid,obs}/{global,lam}/`` directory.

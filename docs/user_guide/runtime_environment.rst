.. _RuntimeEnvironment:

=========================
Runtime Environment
=========================

Build the Environment
------------------------------------------------------------------------------

To build the EAGLE runtime virtual environments:

.. code-block:: bash

   make env # alternatively: ./setup

This will install :term:`Miniforge conda` as ``conda/`` in the current directory and create the various virtual environments.

Custom Anemoi Installation
^^^^^^^^^^^^^^^^^^^^^^^^^^

It may sometimes be useful to install a version of an Anemoi package other than the EAGLE default version, including from code that can be modified and immediately tested. This can be done by activating the ``anemoi`` conda environment provided by EAGLE and doing an editable install of the Anemoi package, replacing the package version currently installed by EAGLE. In the following example, the currently installed ``anemoi-training`` version ``0.17.1`` is replaced with an editable install of on-disk ``0.17.2`` code. It assumes that the previous ``make env`` step has already been carried out.

First, in your EAGLE clone, create a temporary bash shell, activate conda and its ``anemoi`` environment, and note the currently installed ``anemoi-training`` version:

.. code-block:: bash

   bash
   . conda/etc/profile.d/conda.sh
   conda activate anemoi
   conda list anemoi-training
   # packages in environment at ./conda/envs/anemoi:
   #
   # Name                     Version          Build            Channel
   anemoi-training            0.17.1           pypi_0           pypi

Next, clone the ``anemoi-core`` repo, navigate to its ``training`` directory, and check out the required tag:

.. code-block:: bash

   git git@github.com:ecmwf/anemoi-core.git /path/to/clone
   cd /path/to/clone
   cd training
   git checkout training-0.17.2

Finally, perform the editable install and return to your EAGLE clone and original shell:

.. code-block:: bash

   pip install --editable --force-reinstall .
   conda list anemoi-training
   # packages in environment at ./conda/envs/anemoi:
   #
   # Name                     Version          Build            Channel
   anemoi-training            0.17.2           pypi_0           pypi
   exit

At this point, EAGLE will be using ``anemoi-training`` as represented by the code in the ``anemoi-core`` clone: Any changes made to this code will be immediately seen by the EAGLE ``anemoi`` runtime environment and reflected in its behavior.

To obtain a default set of EAGLE runtime environments, remove the ``./conda`` directory and run ``make env`` again.

Available Make Targets
------------------------------------------------------------------------------

A variety of ``make`` targets are available to execute pipeline steps.

Run ``make`` with no arguments to list available targets.

.. list-table:: Available make targets
   :widths: 20 20 20 20
   :header-rows: 1

   * - Target
     - Purpose
     - Depends on target
     - Uses environment
   * - data
     - Implies grids-and-meshes, zarr-gfs, zarr-hrrr
     - ---
     - data
   * - grids-and-meshes
     - Prepare grids and meshes
     - ---
     - data
   * - zarr-gfs
     - Prepare :term:`Zarr`-formatted :term:`GFS` input data
     - grids-and-meshes
     - data
   * - zarr-hrrr
     - Prepare Zarr-formatted :term:`HRRR` input data
     - grids-and-meshes
     - data
   * - training
     - Performs anemoi training
     - data
     - anemoi
   * - inference
     - Performs anemoi inference
     - training
     - anemoi
   * - vx-grid-global
     - Verify global against gridded analysis
     - inference
     - wxvx
   * - vx-grid-lam
     - Verify LAM against gridded analysis
     - inference
     - wxvx
   * - vx-obs-global
     - Verify global against obs
     - inference
     - wxvx
   * - vx-obs-lam
     - Verify LAM against obs
     - inference
     - wxvx
   * - vx-stageiv-lam
     - Verify LAM accumulated precipitation against Stage IV
     - inference
     - wxvx
   * - vis-grid-global
     - Visualize global VX results against gridded analysis
     - vx-grid-global
     - visualization
   * - vis-grid-lam
     - Visualize LAM VX results against gridded analysis
     - vx-grid-lam
     - visualization
   * - vis-obs-global
     - Visualize global VX results against obs
     - vx-obs-global
     - visualization
   * - vis-obs-lam
     - Visualize LAM VX results against obs
     - vx-obs-lam
     - visualization

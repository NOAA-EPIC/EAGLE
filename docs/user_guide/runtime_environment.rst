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

It may sometimes be necessary to install a version of an Anemoi package other than the defined EAGLE default version, including from code that can be modified and immediately tested. This can be done by activating the ``anemoi`` conda environment provided by EAGLE and doing an "editable" install of the Anemoi package, replacing the package version previously installed by EAGLE. In the following example, the previously installed ``anemoi-training`` version ``0.17.1`` is replaced with an editable install of version ``0.17.2``. It assumes that the previous ``make env`` step has already been carried out.

. conda/etc/profile.d/conda.sh
conda activate anemoi
conda list anemoi-training
# packages in environment at /scratch4/BMC/gsd-hpcs/Paul.Madden/eagle-152/conda/envs/anemoi:
#
# Name                     Version          Build            Channel
anemoi-training            0.17.1           pypi_0           pypi

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

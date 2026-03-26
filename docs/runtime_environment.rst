=========================
Runtime Environment
=========================

To build the EAGLE runtime virtual environments:

.. code-block:: text

    make env cudascript=<name-or-path> # alternatively: ./setup cudascript=<name-or-path>

This will install Miniforge conda in the current directory and create the various virtual environments.

The value of the ``cudascript=`` argument should be either the name of a file under ``src/cuda/`` (e.g. ``cudascript=ursa``), 
or an arbitrary path to a file (e.g. ``cudascript=/path/to/file``). The file should contain a list of commands that need 
to be executed on the current system to make the CUDA ``nvcc`` program available on ``PATH``. The ``setup`` script uses ``nvcc`` 
to determine the CUDA release number, used to select a matching ``flash-attn`` package. For systems needing no special 
setup to make ``nvcc`` available, ``cudascript=none`` may be specified.

A variety of ``make`` targets are available to execute pipeline steps.

Run ``make`` with no argument to list available targets.

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
     - Prepare Zarr-formatted GFS input data
     - grids-and-meshes
     - data
   * - zarr-hrrr
     - Prepare Zarr-formatted HRRR input data
     - grids-and-meshes
     - data
   * - training
     - Performs Anemoi training
     - data
     - training
   * - inference
     - Performs Anemoi inference
     - training
     - inference
   * - prewxvx-global
     - Postprocesses global inference output
     - inference
     - prewxvx
   * - prewxvx-lam
     - Postprocesses LAM inference output
     - inference
     - prewxvx
   * - vis-grid-global
     - Visualize global vx results against grided analysis
     - vx-grid-global
     - visualization
   * - vis-grid-lam
     - Visualize LAM vx results against grided analysis
     - vx-grid-lam
     - visualization
   * - vis-obs-global
     - Visualize global vx results against obs
     - vx-obs-global
     - visualization
   * - vis-obs-lam
     - Visualize LAM vx results against obs
     - vx-obs-lam
     - visualization
   * - vx-grid-global
     - Verify global against gridded analysis
     - prewxvx-global
     - wxvx
   * - vx-grid-lam
     - Verify LAM against gridded analysis
     - prewxvx-lam
     - wxvx
   * - vx-obs-global
     - Verify global against obs
     - prewxvx-global
     - wxvx
   * - vx-obs-lam
     - Verify lam against obs
     - prewxvx-lam
     - wxvx

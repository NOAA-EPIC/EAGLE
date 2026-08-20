.. _FAQ:

****
FAQ
****

.. contents::
   :depth: 2
   :local:

=====================
Using EAGLE
=====================

.. _SupportedPlatformsFAQ:

What platforms are currently supported?
===============================================================================

At present, :term:`Ursa` is supported for the standard EAGLE workflow.
Microsoft Azure CycleCloud with Slurm is supported for nested-EAGLE
near-real-time (NRT) runs using the documented ``release/public-v1.1.0`` branch.
Support for additional platforms is coming soon.

How can users set up EAGLE for near-real-time runs on Azure?
===============================================================================

Azure-based nested-EAGLE near-real-time (NRT) runs are supported on Microsoft
Azure CycleCloud with Slurm using the documented ``release/public-v1.1.0``
branch. This FAQ is intended as the first line of support for users setting up
an Azure cluster for EAGLE NRT. Users should follow these instructions first; if
issues remain after setup and validation, contact EPIC support at
``support.epic@noaa.gov``.

EPIC can provide EAGLE code support, workflow guidance, and help with Azure VM
configuration questions. Users and their organizations remain responsible for
their own Azure subscription access, quota requests, compute hours, storage
costs, and cloud spending controls.

Before recreating or launching an Azure-based environment, confirm current Azure
region availability, quota, pricing, VM image support, storage configuration,
networking requirements, security requirements, and the latest approved
deployment templates.

Historical team testing and training used the following Azure CycleCloud
baseline:

.. list-table:: Azure CycleCloud baseline for EAGLE NRT testing
   :widths: 25 30 45
   :header-rows: 1

   * - Component
     - Azure setting
     - Notes
   * - CPU compute nodes
     - ``Standard_HC44rs``
     - Non-GPU HPC compute nodes; 44 vCPUs and 352 GB memory per node.
   * - GPU compute nodes
     - ``Standard_NC24ads_A100_v4``
     - NVIDIA A100 GPU nodes; 24 vCPUs, 220 GB memory, and one 80 GB A100 GPU
       per node.
   * - Controller nodes
     - ``Standard_D4as_v5``
     - Controller/head-node services; 4 vCPUs and 16 GB memory per node.
   * - Network
     - ``10.0.0.0/24``
     - Default virtual network range used in prior testing.
   * - Storage
     - Defaults
     - Azure CycleCloud storage defaults were used in prior testing.

The historical notes identify the VM sizes, network range, and storage defaults,
but not a confirmed number of CPU or GPU compute nodes. Set node counts based on
the target experiment size, expected queue depth, Azure regional quota, and cost
controls. Confirm the suitability of ``Standard_HC44rs`` before using it for a
long-lived deployment because Azure HC-series VMs are scheduled for retirement on
May 31, 2027.

Use ``Standard_D4as_v5`` for the controller/head-node role unless the platform
team provides a newer approved template. The controller coordinates CycleCloud
and Slurm services; it is not the main EAGLE compute resource. Users should
verify the controller image and submitted job scripts before running EAGLE jobs.

The EAGLE NRT workflow uses an existing trained checkpoint and writes forecast
output under the configured EAGLE run directory for the selected experiment and
cycle time. The NRT nested configuration computes the active cycle from ``NOW``,
applies a 6-hour latency, and uses a 48-hour forecast lead time. Users should
confirm that data preparation and inference jobs complete successfully before
using downstream forecast output. For the Azure-specific NRT workflow, see the
:doc:`nested-EAGLE documentation <../eagle_models/nested_eagle>`.

For GPU-based runs, job scripts should use Bash and the runtime environment must
provide compatible NVIDIA drivers, CUDA libraries, conda environments, and
GPU-enabled machine learning packages. On systems where ``/bin/sh`` points to
Dash, use an explicit Bash shebang in job scripts:

.. code-block:: bash

   #!/usr/bin/env bash

GPU runs may also need CUDA paths exported in the runscript if the image or
environment does not already provide them:

.. code-block:: bash

   export CUDA_HOME=/usr/local/cuda
   export CUDA_PATH=/usr/local/cuda
   export CPATH=$CUDA_HOME/include:$CPATH
   export C_INCLUDE_PATH=$CUDA_HOME/include:$C_INCLUDE_PATH
   export CPLUS_INCLUDE_PATH=$CUDA_HOME/include:$CPLUS_INCLUDE_PATH

CUDA paths should only be set explicitly when required by the target image or
environment. Users should verify the CUDA installation before hard-coding paths
such as ``/usr/local/cuda``.

H100 GPU nodes can be considered for EAGLE workloads when Azure quota, pricing,
image support, and deployment templates are available. H100 testing on other
platforms has shown improved training and forecast performance, but Azure H100
configurations should be validated with an end-to-end EAGLE NRT run before they
are used for production or shared results.

Can I generate Anemoi training plots only for the nested HRRR domain?
===============================================================================

Yes. Users can define multiple bounding boxes to specify subset regions, such
as :term:`CONUS` or Europe, by adding focus-area configuration to the
``PlotSample`` callback in the EAGLE pipeline ``base.yaml``. This configuration
generates plots that exclude the surrounding global domain. Define named boxes
under ``focus_areas`` and reference the selected box from ``PlotSample`` with
``focus_area``.

Although users can modify ``base.yaml`` directly for reference, it is
recommended that they instead add the configuration to the ``eagle.yaml`` file
created during the Quickstart workflow. Changes made directly to ``base.yaml``
may be overwritten during configuration composition, whereas updates made in
``eagle.yaml`` are preserved.

For example, for the :term:`HRRR`/:term:`CONUS` domain, use
``latlon_bbox: [22.0, -135.0, 50.0, -60.0]`` or adjust as needed. Once added,
the diagnostics will generate plots restricted to the configured region. For
more information, see the `plot adaptor compatibility section
<https://anemoi.readthedocs.io/projects/training/en/latest/modules/diagnostics.html#plot-adapter-compatibility>`_
of the `Anemoi Training diagnostic documentation
<https://anemoi.readthedocs.io/projects/training/en/latest/modules/diagnostics.html>`_.

Can I add an HRRR-only variable, such as reflectivity, to nested-EAGLE training?
================================================================================

Not directly with the current nested :term:`HRRR`-over-:term:`GFS` training
setup. The nested pipeline combines HRRR and GFS data into a single Anemoi
training dataset, so the variables used for training must be compatible across
the nested domains.

To train with an HRRR-only variable, users would need a :term:`CONUS`-only
configuration or a design that provides a compatible global counterpart,
placeholder, or derived field, along with corresponding data, normalization, and
model configuration changes.

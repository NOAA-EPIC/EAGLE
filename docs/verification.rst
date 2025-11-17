=================
Verify Model Performance
=================

wxvx Overview
----------------------------------------------------

wxvx: A Lightweight MET-Driven Verification Workflow

NOAA is developing **wxvx**, a Python-based workflow that streamlines verification of rapidly evolving AI-based weather models.  
Traditional tools like **MET** are powerful but can be difficult to install, configure, and adapt to non-standard AI datasets.  

**wxvx** drives MET end-to-end—handling baseline data acquisition, CF-Conventions metadata decoration, statistics generation, and simple plotting—using a modular, dependency-graph design and familiar Python packages such as ``xarray``, ``requests``, and ``uwtools``.

Distributed as a **conda** package and paired with **met2go** (pre-built MET executables and core data), **wxvx** installs in minutes on Linux systems—from HPCs to cloud instances to laptops—without requiring administrator support.  
It has already been used to verify global and regional AI forecasts and is equally useful for non-AI verification tasks. Documentation covers capabilities, design principles, use cases, and future plans.

See the `wxvx repository <https://github.com/maddenp-cu/wxvx>`_ for further information.

**wxvx** was created by Paul Madden at NOAA/CIRES.

Helpful Quick Tips for Using wxvx
---------------------------------

* Use the provided conda environment for a fully configured MET setup.
* Ensure forecast and baseline data follow CF-Conventions for best compatibility.
* Refer to ``wxvx --help`` for command-line usage examples.
* Visit the `met2go documentation <https://github.com/maddenp-cu/met2go/blob/main/README.md>`_ for details about bundled MET executables and datasets.


Installation
~~~~~~~~~~~~~~~~~~~~~~

This guide explains how to install **wxvx** using **Miniforge**, the conda-forge project’s lightweight implementation of Miniconda.  
You can skip the first step if you already have a working **conda** installation.

Currently supported platforms are **Linux aarch64** (ARM) and **Linux x86_64** (Intel/AMD).  
The example below shows installation for **aarch64**. If your system uses Intel or AMD hardware, download the **x86_64** installer instead.

Install Miniforge
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: bash

   wget https://github.com/conda-forge/miniforge/releases/download/25.3.0-3/Miniforge3-Linux-aarch64.sh
   bash Miniforge3-Linux-aarch64.sh -bfp conda
   rm Miniforge3-Linux-aarch64.sh
   . conda/etc/profile.d/conda.sh
   conda activate

Install wxvx
~~~~~~~~~~~~~~~~~~~~~~

Create and activate a conda virtual environment with the latest **wxvx**.  
If you are using a non-conda-forge conda installation, add the flags  
``-c conda-forge --override-channels`` to the ``conda create`` command.

.. code-block:: bash

   conda create -y -n wxvx -c ufs-community -c paul.madden wxvx
   conda activate wxvx
   wxvx --version

When activated, the environment automatically includes the **met2go** package,  
which provides **MET**, select **METplus** executables, and supporting data files.  

For more details, see the `met2go documentation <https://github.com/maddenp-cu/met2go/blob/main/README.md>`_.


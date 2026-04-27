.. _VerifyModelPerformance:

=========================
Verify Model Performance
=========================

eagle-tools Overview
-------------------------

We use the eagle-tools package for postprocessing model output and visualizing model performance.
The eagle-tools library provides command-line utilities that are configured via
:term:`YAML` files.

This library currently supports:

* Running anemoi-inference across many initial conditions at scale, for
  example over a validation set
* Postprocessing inference output into a format ready for the ``wxvx`` package
* Computing aggregated error metrics such as RMSE and MAE while preserving the
  initial-condition dimension
* Visualizing spatial error across lead times
* Computing power spectra
* Visualizing predictions alongside targets through figures and GIFs

At a high level, eagle-tools enables users to analyze model performance at
scale. For more information, see the `eagle-tools GitHub repository
<https://github.com/NOAA-PSL/eagle-tools>`_.

wxvx Overview
----------------------------------------------------

:term:`EAGLE` uses :term:`wxvx` to verify model forecasts against either gridded
analyses or point observations.

Within the EAGLE workflow, ``wxvx`` is responsible for running the underlying
verification tasks and producing the statistics and plots used to evaluate
forecast performance. In practice, this means you can compare both ``global``
and :term:`LAM` forecasts against:

* gridded analyses with MET's
  `grid_stat <https://metplus.readthedocs.io/projects/met/en/latest/Users_Guide/grid-stat.html>`_
* point observations with MET's
  `point_stat <https://metplus.readthedocs.io/projects/met/en/latest/Users_Guide/point-stat.html>`_

Before running verification, the driver runs the ``prewxvx`` component from ``eagle-tools`` to postprocess forecast output from the previous step.

See the `wxvx repository <https://github.com/maddenp-cu/wxvx>`_ for further
information about the project itself.

wxvx Quick Tips
----------------------------------------------------

* Run the provided :term:`PreWXVX` steps before starting verification.
* Use the ``vx-grid-*`` targets to verify against gridded analyses.
* Use the ``vx-obs-*`` targets to verify against PrepBUFR observations.
* The ``global`` and ``lam`` targets are independent, so they can be run in
  parallel.
* Check the ``run/<expname>/vx/*.log`` files if a verification job fails.


Running Verification
~~~~~~~~~~~~~~~~~~~~~~

EAGLE provides four standard verification targets:

.. code-block:: bash

   make vx-grid-global config=eagle.yaml
   make vx-grid-lam config=eagle.yaml
   make vx-obs-global config=eagle.yaml
   make vx-obs-lam config=eagle.yaml

These commands submit batch jobs for:

* ``grid-global``: global forecasts verified against gridded analyses
* ``grid-lam``: limited-area forecasts verified against gridded analyses
* ``obs-global``: global forecasts verified against point observations
* ``obs-lam``: limited-area forecasts verified against point observations

Because these are separate jobs, they can be launched in quick succession to
run in parallel.


Verification Output
~~~~~~~~~~~~~~~~~~~~~~

When a verification job completes successfully, ``wxvx`` writes output beneath
the corresponding verification run directory:

.. code-block:: text

   run/<expname>/vx/grid2{grid,obs}/{global,lam}/run/

The most useful outputs are:

* ``stats/`` for MET ``.stat`` files
* ``plots/`` for generated ``.png`` plots
* ``run/<expname>/vx/*.log`` for verification logs

The output for ``eagle-tools prewxvx`` can be found under: ``run/<expname>/vx/prewxvx/{global,lam}/runscript.prewxvx-*.out`


Additional Visualization
~~~~~~~~~~~~~~~~~~~~~~~~

After verification is complete, you can generate additional postprocessed
:term:`visualization` outputs with:

.. code-block:: bash

   make vis-grid-global config=eagle.yaml
   make vis-grid-lam config=eagle.yaml
   make vis-obs-global config=eagle.yaml
   make vis-obs-lam config=eagle.yaml

These targets run ``eagle-tools postwxvx`` to create netCDF summary files and
additional plots under:

.. code-block:: text

   run/<expname>/visualization/grid2{grid,obs}/{global,lam}/

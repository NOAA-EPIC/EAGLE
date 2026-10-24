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

See the `wxvx repository <https://github.com/NOAA-GSL/wxvx>`_ for further
information about the project itself.

Precipitation Skill Scores
~~~~~~~~~~~~~~~~~~~~~~~~~~

The ``vx-stageiv-lam`` target verifies the LAM model's six-hour accumulated
precipitation field, ``accum_tp``, as the canonical ``wxvx`` variable ``tp``.
The truth source is the hourly Stage IV APCP analysis distributed by NOMADS.
For each forecast valid time, ``wxvx`` downloads the six hourly Stage IV files
ending at that time and uses MET's ``pcp_combine`` to create the six-hour truth
accumulation. MET's ``grid_stat`` then regrids Stage IV to the LAM forecast grid.

The default URL uses NOMADS' recent operational Stage IV archive, so this target
is intended primarily for NRT forecasts. Data availability may lag the valid
time. For historical verification, override
``vx.grid2stageiv.lam.wxvx.wxvx.truth.url`` with a URL or local-path template for
an archive that contains the required hourly files.

``wxvx`` computes the categorical CSI and HSS scores and the neighborhood FSS
at precipitation thresholds of 1, 5, 10, and 25 kg m\ :sup:`-2`. FSS is computed
with circular neighborhoods 3, 5, and 11 grid points wide.

Accumulated precipitation is not included in the grid-to-observation targets
because the PrepBUFR point-observation truth source does not provide the
corresponding field.

wxvx Quick Tips
----------------------------------------------------

* Use the ``vx-grid-*`` targets to verify against gridded analyses.
* Use the ``vx-obs-*`` targets to verify against PrepBUFR observations.
* Use ``vx-stageiv-lam`` to verify LAM accumulated precipitation against Stage IV.
* The ``global`` and ``lam`` targets are independent, so they can be run in
  parallel.
* Check the ``run/<expname>/vx/*.log`` files if a verification job fails.


Running Verification
~~~~~~~~~~~~~~~~~~~~~~

EAGLE provides five standard verification targets for a nested forecast:

.. code-block:: bash

   make vx-grid-global config=eagle.yaml
   make vx-grid-lam config=eagle.yaml
   make vx-obs-global config=eagle.yaml
   make vx-obs-lam config=eagle.yaml
   make vx-stageiv-lam config=eagle.yaml

These commands submit batch jobs for:

* ``grid-global``: global forecasts verified against gridded analyses
* ``grid-lam``: limited-area forecasts verified against gridded analyses
* ``obs-global``: global forecasts verified against point observations
* ``obs-lam``: limited-area forecasts verified against point observations
* ``stageiv-lam``: limited-area accumulated precipitation verified against Stage IV

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

The output for ``eagle-tools prewxvx`` can be found under: ``run/<expname>/vx/prewxvx/{global,lam}/runscript.prewxvx-*.out``.


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

.. _GenerateForecast:

=========================
Generate a Forecast
=========================

anemoi-inference Overview
-----------------------------

We use the :term:`anemoi` inference package to create a forecast.
The anemoi-inference package helps users take trained ML models and generate
forecasts for production or evaluation settings. Overall, it provides the
workflows required to take trained ML models into real-world use.

See `anemoi-inference documentation <https://anemoi.readthedocs.io/projects/inference/en/latest/>`_ for further information.

anemoi-inference Quick Tips
--------------------------------------------------

anemoi-inference requires a :term:`YAML` configuration to run via the CLI. A
simplified YAML configuration looks like:

.. code-block:: yaml

    checkpoint: path/to/inference-last.cpkt
    lead_time: 240 # hours
    date: 2026-01-01T00

    # lots of input options (see anemoi-inference documentation)
    input: my_hrrr_initial_conditions.zarr

    # lots of output options (see anemoi-inference documentation)
    output: 2026-01-01T00.240hr.nc

This simple setup will successfully execute inference.

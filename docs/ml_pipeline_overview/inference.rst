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

Using the Official Nested-EAGLE Checkpoint
--------------------------------------------------

The official pretrained nested-EAGLE checkpoint can be downloaded with:

.. code-block:: bash

    wget -O inference-last.ckpt https://eaglecheckpoints.blob.core.windows.net/eagle-checkpoints/nested-eagle/inference-last.ckpt

To use this checkpoint for inference, set ``inference.anemoi.checkpoint_path``
to the downloaded file:

.. code-block:: yaml

    inference:
      anemoi:
        checkpoint_path: /path/to/inference-last.ckpt

If ``inference.checkpoint_dir`` is also present, the ``Inference`` driver will
use the latest checkpoint from that directory instead of the explicit
``checkpoint_path``. Remove or override ``checkpoint_dir`` when you want to
force use of a specific pretrained checkpoint.

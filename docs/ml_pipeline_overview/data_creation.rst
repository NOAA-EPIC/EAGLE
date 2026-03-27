.. _CreateTrainingData:

==============================================================================
Create Training Data
==============================================================================

.. _Ufs2ArcoOverview:

ufs2arco Overview
------------------------------------------------------------------------------

EAGLE uses :term:`ufs2arco` to generate training, validation, and test datasets.
The ``ufs2arco`` package preprocesses weather data and writes it in a
:term:`Zarr` format suitable for machine learning workflows.

To begin, create a :term:`YAML` recipe file named ``recipe.yaml``. A simplified
example is shown below:

.. code-block:: yaml

    mover:
      name: mpidatamover

    directories:
      zarr: hrrr.zarr
      cache: cache
      logs: logs

    source:
      name: aws_hrrr_archive
      t0:
        start: 2022-01-01T06
        end: 2022-12-31T18
        freq: 6h

      fhr:
        start: 0
        end: 0
        step: 6

      variables:
        - gh
        - u
        - v
        - t
        - u10
        - v10
        - t2m

      levels:
        - 500
        - 850

    target:
      name: anemoi
      sort_channels_by_levels: true
      compute_temporal_residual_statistics: true
      statistics_period:
        start: 2022-01-01T06
        end: 2022-12-31T18
      forcings:
        - cos_latitude
        - sin_latitude
        - cos_longitude
        - sin_longitude

    chunks:
      time: 1
      variable: -1
      ensemble: 1
      cell: -1

Next, run:

.. code-block:: bash

    ufs2arco recipe.yaml

For more information, see the `ufs2arco documentation <https://ufs2arco.readthedocs.io/en/latest/>`_.

``ufs2arco`` was developed by Tim Smith at NOAA Physical Sciences Laboratory.

.. _Ufs2ArcoTips:

Helpful Tips for ufs2arco
------------------------------------------------------------------------------

.. _ChooseDates:

Choosing Dates
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Update the dates to include in your dataset by modifying the ``t0`` block in
your recipe. These dates should cover all data that you plan to use for
training, validation, and testing. The full dataset can be split into those
subsets later.

.. code-block:: yaml

    t0:
      start: 2022-01-01T06
      end: 2022-12-31T18
      freq: 6h

Then ensure that the ``statistics_period`` block is also updated as needed:

.. code-block:: yaml

    statistics_period:
      start: 2022-01-01T06
      end: 2022-10-31T18

As a best practice, keep the statistics period limited to the dates used for
the training dataset.

.. _ChangeVariables:

Changing Variables and Levels
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To change the variables or vertical levels in the dataset, add or remove items
in the ``source`` block of ``recipe.yaml``. See the `ufs2arco documentation
<https://ufs2arco.readthedocs.io/en/latest/>`_ for the supported variables and
configuration details.

.. _MPIUsage:

MPI Usage
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``ufs2arco`` can use :term:`MPI` to parallelize data preprocessing. If you do
not want to use MPI, update the ``mover`` block as follows:

.. code-block:: yaml

    mover:
      name: datamover
      batch_size: 2

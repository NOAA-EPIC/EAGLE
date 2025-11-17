=================
Create Training Data
=================

ufs2arco Overview
-------------------------

We use ufs2arco to generate training, validation, and test datasets. The ufs2arco library helps preprocess weather data and makes it ready to be used to train a machine learning model.

First, create a recipe.yaml. A simplified example of a `recipe.yaml` could be as follows:

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
    sort_channels_by_levels: True
    compute_temporal_residual_statistics: True
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

. Next, run the following:

```
ufs2arco recipe.yaml
```

For further information see the ufs2arco `github <https://ufs2arco.readthedocs.io/en/latest/>`_ or `documentation <https://ufs2arco.readthedocs.io/en/latest/>`_

ufs2arco was created by Tim Smith at NOAA Physical Sciences Laboratory.

Helpful quick tips for ufs2arco
------------------

Choosing Dates
~~~~~~~~~~~~~~~~~~~~~~
Update the dates you wish to include in your dataset by changing the below section in your recipe. 
These dates will include all data that you plan to use for training, validation, and testing.
The full dataset will be split into these individual sets later on.

.. code-block:: yaml

    start: 2022-01-01T06
    end: 2022-12-31T18
    freq: 6h

Then ensure that you have updated the statistics_period section to match:

.. code-block:: yaml
    
    start: 2022-01-01T06
    end: 2022-10-31T18

Note: it is best practice to ensure that your statistics period only includes dates you plan to include in your training dataset.

Changing Variables
~~~~~~~~~~~~~~~~~~~~~~

To change variables or levels desired, simply add or remove variables or levels within the `source` section of a recipe.yaml. Please see ufs2arco documentation for further information on exactly what variables are available.

MPI Usage
~~~~~~~~~~~~~~~~~~~~~~

ufs2arco uses MPI to parallelize data preprocessing. If you wish to not use MPI, change the top line of the yaml to say

.. code-block:: yaml

    mover:
    name: datamover
    batch_size: 2

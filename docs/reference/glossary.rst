.. _Glossary:

==============================================================================
Glossary
==============================================================================

.. glossary::
   :sorted:

   anemoi
      The ECMWF-led machine learning weather prediction software stack used by EAGLE for training and inference. See the `anemoi-core repository <https://github.com/ecmwf/anemoi-core>`__.

   EAGLE
      Experimental AI Global and Limited-area Ensemble forecast system.

   GFS
      Global Forecast System. See the `NOAA GFS page <https://www.emc.ncep.noaa.gov/emc/pages/numerical_forecast_systems/gfs.php>`__.

   HRRR
      High-Resolution Rapid Refresh. See the `NOAA HRRR page <https://www.emc.ncep.noaa.gov/emc/pages/numerical_forecast_systems/hrrr.php>`__.

   inference
      The workflow stage that uses a trained model checkpoint to generate forecasts.

   LAM
      Limited-area model.

   Miniforge conda
      The Miniforge-based Conda installation used by EAGLE runtime environment setup. See the `Miniforge repository <https://github.com/conda-forge/miniforge>`__.

   PreWXVX
      The EAGLE driver that prepares forecast output for downstream :term:`wxvx` verification steps.

   ufs2arco
      The component used by EAGLE to prepare Zarr-formatted forecast and analysis data. See the `ufs2arco repository <https://github.com/NOAA-PSL/ufs2arco>`__.

   Ursa
      A NOAA RDHPCS platform currently supported by EAGLE. See the `NOAA RDHPCS Ursa page <https://noaa-rdhpcs.readthedocs.io/systems/ursa_user_guide.html>`__.

   uwtools
      The workflow utility framework used by EAGLE to compose configuration, validate schemas, and execute drivers. See the `uwtools repository <https://github.com/ufs-community/uwtools>`__.

   visualization
      The workflow stage that plots verification results derived from processed forecast statistics.

   wxvx
      The verification component used by EAGLE to run MET-based statistical verification tasks.

   Zarr
      A chunked, cloud-friendly array storage format used in EAGLE data preparation workflows.

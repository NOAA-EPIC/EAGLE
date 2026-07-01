.. _Glossary:

==============================================================================
Glossary
==============================================================================

.. glossary::
   :sorted:

   AORC
      Analysis of Record for Calibration. A NOAA gridded meteorological forcing dataset used for land surface and hydrologic applications.

   anemoi
      The ECMWF-led machine learning weather prediction software stack used by EAGLE for training and inference. See the `anemoi-core repository <https://github.com/ecmwf/anemoi-core>`__.

   checkpoint
      A saved snapshot of a trained machine learning model that can be used to resume training or perform inference.

   CONUS
      Continental United States.

   ECMWF
      European Centre for Medium-Range Weather Forecasts.

   EAGLE
      Experimental AI Global and Limited-area Ensemble forecast system.

   ERA5
      The fifth-generation atmospheric reanalysis produced by the European Centre for Medium-Range Weather Forecasts (ECMWF).

   GEFS
      Global Ensemble Forecast System. NOAA's global ensemble weather prediction system.

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

   MPI
      Message Passing Interface. A standard used for parallel computing across multiple processes.

   MET
      Model Evaluation Tools. A community-developed verification package used to evaluate numerical weather prediction and machine learning weather forecasts.

   netCDF
      Network Common Data Form. A file format commonly used for storing and sharing scientific array-based data.

   NRT
      Near real-time. Refers to workflows that generate forecasts using the latest available input data shortly after it becomes available.

   PrepBUFR
      A BUFR-formatted observational dataset used for numerical weather prediction and forecast verification.

   prewxvx
      The component used by EAGLE to prepare forecast output for :term:`wxvx` verification steps.

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

   YAML
      YAML Ain't Markup Language. A human-readable data serialization format commonly used for configuration files.

   Zarr
      A chunked, cloud-friendly array storage format used in EAGLE data preparation workflows.

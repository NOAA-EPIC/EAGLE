.. _Glossary:

==============================================================================
Glossary
==============================================================================

.. glossary::
   :sorted:

   Anemoi
      The ECMWF-led machine learning weather prediction software stack used by EAGLE for training and inference. See the `anemoi-core repository <https://github.com/ecmwf/anemoi-core>`__.

   EAGLE
      Experimental AI Global and Limited-area Ensemble forecast system.

   inference
      The workflow stage that uses a trained model checkpoint to generate forecasts.

   LAM
      Limited-area model.

   PreWXVX
      The EAGLE driver that prepares forecast output for downstream :term:`wxvx` verification steps.

   ufs2arco
      The component used by EAGLE to prepare Zarr-formatted forecast and analysis data. See the `ufs2arco repository <https://github.com/NOAA-PSL/ufs2arco>`__.

   uwtools
      The workflow utility framework used by EAGLE to compose configuration, validate schemas, and execute drivers. See the `uwtools repository <https://github.com/ufs-community/uwtools>`__.

   visualization
      The workflow stage that plots verification results derived from processed forecast statistics.

   wxvx
      The verification component used by EAGLE to run MET-based statistical verification tasks.

   Zarr
      A chunked, cloud-friendly array storage format used in EAGLE data preparation workflows.

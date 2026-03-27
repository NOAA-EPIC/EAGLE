=========================
Postprocessing
=========================

eagle-tools Overview
-------------------------

We use the eagle-tools library for postprocessing inference and visualizing model performance. The eagle-tools library 
provides command-line utilities that are all configured via YAML files.

This library currently supports:

    * Running anemoi-inference across many initial conditions at scale (e.g. over a validation set)
    * Postprocess inference output into a format ready for the ``wxvx`` package
    * Computing aggregated error metrics such as RMSE and MAE, while preserving the initial condition dimension
    * Visualizing spatial error (RMSE and MAE) across lead times
    * Computing the power spectra
    * Visualizing predictions alongside targets (truth) through figures and movies (GIF)

At a high level, eagle-tools enables users to analyze model performance at scale. For more information about eagle-tools, 
please see the `eagle-tools Github repository <https://github.com/NOAA-PSL/eagle-tools>`_.

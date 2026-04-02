.. _Postprocessing:

=========================
Postprocessing
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


eagle-tools Quick Tips
--------------------------------------------------

Coming soon!

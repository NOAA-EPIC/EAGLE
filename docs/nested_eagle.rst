==================================
Nested-EAGLE
==================================

The Nested-EAGLE model is a prototype model trained on the global NOAA Global Forecast System (GFS) data 
with High Resolution Rapid Refresh (HRRR) data over the Contiguous United States (CONUS). 
This builds on previous work from Met Norway (Nipen et al., 2024, arXiv:2409.02891) by creating a 
nested model with lower resolution global data and high resolution over an area of interest.

.. image:: images/nested-eagle-domain.jpg
   :alt: Overview of the Nested-EAGLE domain
   :width: 75%
   :align: center

.. centered:: Overview of the Nested-EAGLE domain

Nested-EAGLE configurations were provided by Tim Smith at NOAA Physical Sciences Laboratory.

Version 1 of Nested-EAGLE was trained with the following configurations:

* Data

   * GFS (0.25-degree)
   * HRRR conservatively regridded to 6-km 
   * Training: Feb 2015-Jan 2023
   * Validation: Feb 2023 to Jan 2024
   * Testing: Feb 2024 to Jan 2025

* Variables

   * Prognostic: gh, u, v, w, t, q, sp, u10, v10, t2m, t_surface, sh2
   * Diagnostic: u80, v80, accum_tp (use fhr 6)
   * Forcing: lsm, orog, cos_latitude, sin_latitude, cos_longitude, sin_longitude, cos_julian_day, sin_julian_day, cos_local_time, sin_local_time, insolation
   * Levels: 100, 150, 200, 250, 300, 400, 500, 600, 700, 850, 925, 1000

* Model Architecture

   * Encoder and Decoder: Graph Transformer
   * Processor: Sliding Window Transformer
   * Latent space is a 4x coarsened data space

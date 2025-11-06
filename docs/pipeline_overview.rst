=================
DAB
Overview of Full Pipeline
=================

An end-to-end machine learning pipeline for weather prediction.

The steps of this pipeline include:

Step 1: Dataset Creation 
~~~~~~~~~~~~~~~~~~~~~~
Use `ufs2arco` to create training, validation, and test datasets.

Step 2: Train a Graph-Based Model
~~~~~~~~~~~~~~~~~~~~~~
Use `anemoi-core` modules to train a graph-based model.

Step 3: Create a Forecast
~~~~~~~~~~~~~~~~~~~~~~
Use `anemoi-inference` to run inference.

Step 4: Verify a Forecast
~~~~~~~~~~~~~~~~~~~~~~
Use `wxvx` to verify a forecast against gridded analysis or observations.

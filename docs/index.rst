###################
Welcome to EAGLE!
###################

Welcome to the Github repository for Project EAGLE (Experimental AI Global and Limited-area Ensemble forecast system)! 
EAGLE is a joint effort between NOAA Research Laboratories and the Earth Prediction Innovation Center (EPIC) in the 
Office of Oceanic and Atmospheric Research (OAR), and the National Weather Service (NWS). 
The goal of Project EAGLE is to provide the community with tools to test and deploy their own AI models for weather prediction. 
As a part of Project EAGLE, this repository current contains various configurations to guide users through 
a complete scientific workflow to train an AI model. This pipeline includes environment creation, data preprocessing, model training, 
inference to create a forecast, verification of forecasts, and visualization tools. See the various pages below for more details.

For further information about Project EAGLE, please see the `NOAA EPIC website <https://www.epic.noaa.gov/ai/eagle-overview/>`_

###################
Table of Contents
###################

.. toctree::
   :maxdepth: 2
   :caption: User Guide
   :numbered:

   user_guide/quickstart
   user_guide/runtime_environment
   user_guide/configuration
   user_guide/drivers

.. toctree::
   :maxdepth: 2
   :caption: ML Pipeline Overview
   :numbered:

   ml_pipeline_overview/data_creation
   ml_pipeline_overview/train_a_model
   ml_pipeline_overview/inference
   ml_pipeline_overview/postprocessing
   ml_pipeline_overview/verification

.. toctree::
   :maxdepth: 1
   :caption: EAGLE Models

   eagle_models/nested_eagle
   eagle_models/global_eagle

.. toctree::
   :maxdepth: 1
   :caption: Reference

   reference/glossary
   reference/faq

.. toctree::
   :maxdepth: 1
   :caption: Community

   community/contributing
   community/support

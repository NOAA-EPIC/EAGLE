## nested-EAGLE Workflow

Please see our [nested-EAGLE documentation](https://epic-eagle.readthedocs.io/en/latest/nested_eagle.html) for more information about the nested-EAGLE setup, such as a description of the model architecture or overview of the nested domain.

### Workflow Instructions

Before beginning, clone this repository:

```
git clone https://github.com/NOAA-EPIC/EAGLE.git
```

Reminder: Conda environments are provided for you on Ursa!

#### Step 1: Data Creation (/data)

Data preprocessing using `ufs2arco` to create training, validation, and test datasets

#### Step 2: Model Training (/training)

Model training using `anemoi-core` modules to train a graph-based model

#### Step 3: Create a Forecast (/inference)

Creating a forecast with `anemoi-inference` to run inference from a model checkpoint

#### Step 4: Post-processing needs and Verification (/verification)

Verifying your forecasts with `wxvx` against gridded analysis or observervations

#### Step 5: Tools for visualizing model output and performance (/visualization)

See this folder for further instructions on how to view model output and overall performance.

## Nested-Eagle Workflow

Follow the workflow outlined below to complete the entire pipeline.

Please see our [nested-eagle documentation](https://global-eagle.readthedocs.io/en/latest/nested_eagle.html) for more information about the Nested-Eagle setup, such as a description of the model architucture and an explanation about the nested domain.

#### Step 1: Data Creation (/data)

Data preprocessing using `ufs2arco` to create training, validation, and test datasets

#### Step 2: Model Training (/training)

Model training using `anemoi-core` modules to train a graph-based model

#### Step 3: Create a Forecast (/inference)

Creating a forecast with `anemoi-inference` to run inference from a model checkpoint

#### Step 4: Post-processing needs and Verificatino (/verification)

Verifying your forecast (or multiple) with `wxvx` to verify against gridded analysis or observervations

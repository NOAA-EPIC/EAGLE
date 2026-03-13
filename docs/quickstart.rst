=================
Quickstart Guide
=================

This section provides a recipe for an end-to-end run of Nested EAGLE on Ursa. As of right now the only supported 
platform is Ursa. Future development will include additional platforms. Stay tuned! 

GNU `make` version 3.82 or higher is required.

Complete the steps below in the `src/` directory.

**1. Create all environments**

Run::
    
    make env cudascript=ursa

This step creates the runtime software environment, comprising conda virtual environments to support data prep, 
training, inference, and verification. The `conda/` subdirectory it creates is self-contained and can be removed 
and recreated by running the `make env` command again, as long as pipeline steps are not currently running.

Developers who will be modifying Python driver code should replace `make env` with `make devenv`, which will 
create the same environments but also install additional code-quality tools for formatting, linting, shellchecking, 
typechecking, and YAML linting.
 
**2. Create the EAGLE YAML config**

Run::
    
    make config compose=base:ursa >eagle.yaml

The `config` target operates on `.yaml` files in the `config/` directory, so this command composes `config/base.yaml` 
and `config/ursa.yaml` and redirects the composed config into `eagle.yaml`.

**3. Set the app.base value in eagle.yaml to the absolute path to the current (src/) directory.**

The run directories from subsequent steps, along with the output of those steps, will be created in the `run/<expname>` 
subdirectory of `app.base`, where `<expname>` is the value of `app.experiment_name`.

**4. Create training data**

Run::
    
    make data config=eagle.yaml

This step provisions data required for training and inference. The `data` target delegates to targets 
`grids-and-meshes`, `zarr-gfs`, and `zarr-hrrr`, which can also be run individually (e.g. `make grids-and-meshes config=eagle.yaml`), but note that `grids-and-meshes`, which runs locally, must be run first. The `zarr-gfs` and `zarr-hrrr` targets can be run in quick succession, as they submit batch jobs: Do not proceed until their batch jobs complete successfully (see the files `run/<expname>/data/*.out`).

**5. Train the ML model.**

Run::
    
    make training config=eagle.yaml

This step trains a model using data provisioned by the previous step. It submits a batch job: Do not proceed until 
the batch job completes successfully (see the file `run/<expname>training/runscript.training.out`).

**6. Run inference**

Run::
    
    make inference config=eagle.yaml

This step performs inference, producing a forecast. It submits a batch job: Do not proceed until the batch job 
completes successfully (see the file `run/<expname>inference/runscript.inference.out`.)

**7. Postprocess model output**

Run::
    
    make prewxvx-global config=eagle.yaml
    make prewxvx-lam config=eagle.yaml

These steps prepare forecast output from the previous step for verification by `wxvx`. They run locally, so it is 
safe to proceed when the commands return. See the files `run/<expname>vx/prewxvx/{global,lam}/runscript.prewxvx-*.out` for details.

**8. Model verification**

Run::
    
    make vx-grid-global config=eagle.yaml
    make vx-grid-lam config=eagle.yaml
    make vx-obs-global config=eagle.yaml
    make vx-obs-lam config=eagle.yaml

These steps perform verification, either of the `global` or `lam` forecasts, and against gridded analyses (`*-grid-*`) or 
prepbufr observations (`*-obs-*`) as truth. Each submits a batch job, so the four `make` commands can be run in quick 
succession to get all the batch jobs running in parallel. When each batch job completes, MET `.stat` files and `.png` 
plot files can be found under the `stats/` and `plots/` subdirectories of `run/<expname>vx/grid2{grid,obs}/{global,lam}/run/`. 
The files `run/<expname>vx/*.log` contain the logs from each verification run.

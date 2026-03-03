# EAGLE

This repository contains configuration and driver code for running an end-to-end machine learning pipeline for weather prediction. The pipeline is orchestrated with `make` targets and `uwtools`-based drivers, and it provisions a self-contained set of conda environments to support each step of the workflow. A typical run follows these steps:

- **Environment setup:** Creates the runtime environments used by each stage of the pipeline.
- **Prepare training and inference data:** Provisions required static assets (e.g., grids and meshes) and produces Zarr-formatted datasets via `ufs2arco`.
- **Train an AI model:** Trains an Anemoi model using the provisioned datasets, producing checkpoints for inference.
- **Generate a forecast:** Runs inference from training checkpoints using `anemoi-inference` to produce forecast output.
- **Prepare output for verification:** Postprocesses forecast output into the formats and directory structure expected by `wxvx`.
- **Verify model performance:** Runs `wxvx` verification against gridded analysis and/or observations, producing MET statistics and plots.

## Quickstart

This section provides a recipe for an end-to-end run of Nested EAGLE on Ursa.

In the `src/` directory:

**1. Run `make env cudascript=ursa`.**

This step creates the runtime software environment, comprising conda virtual environments `data`, `training`, `inference`, and `vx` for data prep, training, inference, and verification, respectively. The `conda/` subdirectory it creates is self-contained and can be removed and recreated by running the `make env` command again, as long as pipeline steps are not currently running.

Developers who will be modifying Python driver code should replace `make env` with `make devenv`, which will create the same environments but also install additional code-quality tools for formatting, linting, shellchecking, typechecking, and unit testing.
 
**2. Run `make config compose=base:ursa >eagle.yaml` to create the EAGLE YAML config.**

The `config` target operates on `.yaml` files in the `config/` directory, so this command composes `config/base.yaml` and `config/ursa.yaml` and redirects the composed config into `eagle.yaml`.

**3. Set the `app.base` value in `eagle.yaml` to the absolute path to the current (`src/`) directory.**

The run directories from subsequent steps, along with the output of those steps, will be created in the `run/` subdirectory of `app.base`.

**4. Run `make data config=eagle.yaml`.**

This step provisions data required for training and inference. The `data` target delegates to targets `grids-and-meshes`, `zarr-gfs`, and `zarr-hrrr`, which can also be run individually (e.g. `make grids-and-meshes config=eagle.yaml`), but note that `grids-and-meshes`, which runs locally, must be run first. The `zarr-gfs` and `zarr-hrrr` targets can be run in quick succession, as they submit batch jobs: Do not proceed until their batch jobs complete successfully (see the files `run/data/*.out`).

**5. Run `make training config=eagle.yaml`.**

This step trains a model using data provisioned by the previous step. It submits a batch job: Do not proceed until the batch job completes successfully (see the file `run/training/runscript.training.out`).

**6. Run `make inference config=eagle.yaml`.**

This step performs inference, producing a forecast. It submits a batch job: Do not proceed until the batch job completes successfully (see the file `run/inference/runscript.inference.out`.)

**7. Run `make prewxvx-global config=eagle.yaml` followed by `make prewxvx-lam config=eagle.yaml`.**

These steps prepare forecast output from the previous step for verification by `wxvx`. They run locally, so it is safe to proceed when the commands return. See the files `run/vx/prewxvx/{global,lam}/runscript.prewxvx-*.out` for details.

**8. Run any or all of `make vx-grid-global config=eagle.yaml`, `make vx-grid-lam config=eagle.yaml`, `make vx-obs-global config=eagle.yaml`, `make vx-obs-lam config=eagle.yaml`.**

These steps perform verification, either of the `global` or `lam` forecasts, and against gridded analyses (`*-grid-*`) or prepbufr observations (`*-obs-*`) as truth. Each submits a batch job, so the four `make` commands can be run in quick succession to get all the batch jobs running in parallel. When each batch job completes, MET `.stat` files and `.png` plot files can be found under the `stats/` and `plots/` subdirectories of `run/vx/grid2{grid,obs}/{global,lam}/run/`. The files `run/vx/*.log` contain the logs from each verification run.

## Runtime Environment

To build the EAGLE runtime virtual environments:

``` bash
make env cudascript=<name-or-path> # alternatively: ./setup cudascript=<name-or-path>
```

This will install Miniforge conda in the current directory and create the virtual environments `data`, `training`, `inference`, and `vx`.

The value of the `cudascript=` argument should be either the name of a file under `src/cuda/` (e.g. `cudascript=ursa`), or an arbitrary path to a file (e.g. `cudascript=/path/to/file`). The file should contain a list of commands that need to be executed on the current system to make the CUDA `nvcc` program available on `PATH`. The `setup` script uses `nvcc` to determine the CUDA release number, used to select a matching `flash-attn` package. For systems needing no special setup to make `nvcc` available, `cudascript=none` may be specified.

A variety of `make` targets are available to execute pipeline steps:

| Target           | Purpose                                       | Depends on target | Uses environment |
|------------------|-----------------------------------------------|-------------------|------------------|
| data             | Implies grids-and-meshes, zarr-gfs, zarr-hrrr | -                 | data             |
| grids-and-meshes | Prepare grids and meshes                      | -                 | data             |
| zarr-gfs         | Prepare Zarr-formatted GFS input data         | grids-and-meshes  | data             |
| zarr-hrrr        | Prepare Zarr-formatted HRRR input data        | grids-and-meshes  | data             |
| training         | Performs Anemoi training                      | data              | training         |
| inference        | Performs Anemoi inference                     | training          | inference        |
| prewxvx-global   | Postprocesses global inference output         | inference         | vx               |
| prewxvx-lam      | Postprocesses LAM inference output            | inference         | vx               |
| vx-grid-global   | Verify global against gridded analysis        | prewxvx-global    | vx               |
| vx-grid-lam      | Verify LAM against gridded analysis           | prewxvx-lam       | vx               |
| vx-obs-global    | Verify global against obs                     | prewxvx-global    | vx               |
| vx-obs-lam       | Verify LAM against obs                        | prewxvx-lam       | vx               |

Run `make` with no argument to list available targets.

## Configuration

### Config Creation

The final EAGLE YAML config is created by composing a base config together with one or more fragments providing values for specific platforms, use cases, etc. The command `make config compose=a:b:c` would compose together `config/a.yaml`, `config/b.yaml`, and `config/c.yaml`. In practice, composition should begin with the `base` config (i.e. `config/base.yaml`), which provides generally applicable settings for EAGLE runs (see the [Quickstart](#quickstart) for an example.) The composed config can then be manually edited for experiment-specific requirements.

For advanced use cases, for example for composing configs in arbitrary locations, the underlying `uwtools` command can be used. In the `src/` directory:

``` bash
bash
source conda/etc/profile.d/conda.sh
conda activate base
uw config compose /path/to/some/a.yaml /path/to/another/b.yaml >eagle.yaml
exit
```

### Config Description

The following subsections describe various parts of the EAGLE YAML config.

Some configuration parameters are common across `uwtools`-based component drivers and occur in multiple configuration blocks:

- The [execution:](https://uwtools.readthedocs.io/en/stable/sections/user_guide/yaml/components/execution.html) block provides information required to correctly execute the component.
- The [platform:](https://uwtools.readthedocs.io/en/stable/sections/user_guide/yaml/components/platform.html) block provides information about the system EAGLE is running on.
- The `rundir:` parameter specifies where driver runtime assets will be created.

Additionally, many configuration blocks include a `common:` block, which provides parameters shared by several configurations, to avoid unnecessary repetition.

### Config Realization

EAGLE YAML configs contain a variety of Jinja2 expressions that are normally resolved by the various pipeline steps at run time. Sometimes it can be helpful to resolve these references ("realize" the config in `uwtools` terms) in advance, to get a better understanding of the final configuration parameters. To do so, run:

``` bash
make realize config=eagle.yaml
```

The resulting config could be used in place of the unrealized `eagle.yaml`, as the two should be equivalent -- though the realized config may be significantly longer due to, for example, repetition of common elements previously factored out using Jinja2.

Note that the realized config may still contain some Jinja2 expressions that can only be realized at run time by the component using a particular config block.

### Config Validation

To validate the EAGLE YAML config:

``` bash
make validate config=eagle.yaml
```

This will perform validation of config blocks that are not owned by drivers; driver config blocks will be validated at run time by the drivers themselves.

### app

This block provides various global configuration parameters for the application, especially those thought most likely to require configuration by users.

### grids_and_meshes

Configuration for the `GridsAndMeshes` driver.

- The `filenames:` block provides paths to data files created by this step.

### inference

Configuration for the `Inference` driver.

- The `anemoi:` block provides the YAML config for the [anemoi-inference](https://anemoi.readthedocs.io/projects/inference/en/latest/index.html#) component.
- The `checkpoint_dir:` parameter specifies the location of the checkpoints created by the training step.

### platform

In the EAGLE base config, this `uwtools`-required parameter delegates to `app.platform`.

### prewxvx

Configuration for the `PreWXVX` driver.

- This driver executes the [eagle-tools](https://pypi.org/project/eagle-tools/) component.
- The `global:` and `lam:` blocks provide configurations for global and limited-area extents, respectively, each borrowing from `common:`. Their `prewxvx:` sub-blocks are ultimately passed to the `PreWXVX` driver as its runtime configuration.

### training

Configuration for the `Training` driver.

- The `anemoi:` block provides the YAML config for the [anemoi-training](https://anemoi.readthedocs.io/projects/training/en/latest/index.html#) component.
- The `remove:` block specifies values from the default configurations [generated by Anemoi](https://anemoi.readthedocs.io/projects/training/en/stable/start/hydra-intro.html#generating-user-config-files) that should be removed at execution time, via the [override syntax](https://hydra.cc/docs/advanced/override_grammar/basic/#basic-override-syntax) of [Hydra](https://hydra.cc/), the YAML-processing tool used by Anemoi.

### ufs2arco

This block provides general configuration parameters for the [ufs2arco](https://ufs2arco.readthedocs.io/en/latest/) component. This configuration is used as a source for default/common configuration parameters, which are supplemented by the `Zarr` driver then it executes `ufs2arco` for specific use cases.

### val

This block provides both static and derived values that are referenced by other configuration blocks. It is the appropriate place to define values that need to be shared and kept in-sync across pipeline steps, but less likely to be manually modified by users like values in the `app:` block.

### vx

Configuration for the `VX` driver.

- This driver executes the [wxvx](https://github.com/NOAA-GSL/wxvx) component.
- The `grid2grid:` block provides configuration for running `wxvx` with MET's [grid_stat](https://metplus.readthedocs.io/projects/met/en/latest/Users_Guide/grid-stat.html) tool to verify against gridded analyses. Sub-blocks `global:` and `lam:` provide configuration refinements for verifying global and limited-area grids, respectively.
- The `grid2obs:` block provides configuration for running `wxvx` with MET's [point_stat](https://metplus.readthedocs.io/projects/met/en/develop/Users_Guide/point-stat.html) tool to verify against point observations. Sub-blocks `global:` and `lam:` provide configuration refinements for verifying global and limited-area grids, respectively.

### zarrs

Configuration for the `Zarr` driver.

- This driver executes the [ufs2arco](https://ufs2arco.readthedocs.io/en/latest/) component.
- The `gfs:` and `hrrr:` sub-blocks provide refinements for ingesting GFS and HRRR data, respectively, for EAGLE.

## Drivers

The various software components required by EAGLE are executed by `uwtools` drivers implemented as Python modules under `src/eagle/`. By default, the targets in `src/Makefile` invoke drivers' most comprehensive tasks, i.e. those that configure and execute the component to produce its final output. However, each driver provides a number of tasks, some depending on others, and lower-level tasks can be invoked to request less than full execution of the driver, which can be useful during development and debugging.

To request a specific task, add a `task=` clause to the appropriate `make` target. To see a list of available tasks, specify `task=?`.

For example:

``` bash
$ make inference config=eagle.yaml task=?
+ uw execute --module eagle/inference/inference.py --classname Inference
[2026-02-27T23:58:43]    ERROR Available tasks:
[2026-02-27T23:58:43]    ERROR   anemoi_config
[2026-02-27T23:58:43]    ERROR     Anemoi-inference config created with specified checkpoint path.
[2026-02-27T23:58:43]    ERROR   provisioned_rundir
[2026-02-27T23:58:43]    ERROR     Run directory provisioned with all required content.
[2026-02-27T23:58:43]    ERROR   run
[2026-02-27T23:58:43]    ERROR     A run.
[2026-02-27T23:58:43]    ERROR   runscript
[2026-02-27T23:58:43]    ERROR     The runscript.
[2026-02-27T23:58:43]    ERROR   show_output
[2026-02-27T23:58:43]    ERROR     Show the output to be created by this component.
[2026-02-27T23:58:43]    ERROR   validate
[2026-02-27T23:58:43]    ERROR     Validate the UW driver config.
```

For example, the `provisioned_rundir` task would provision the run directory with all its required content, but would not execute the `anemoi-inference` component. The `run` task would fully execute inference.

To invoke the `Inference` driver's `runscript` task, provisioning only the component's runscript:

``` bash
$ make inference config=eagle.yaml task=runscript
+ uw execute --config-file eagle.yaml --module eagle/inference/inference.py --classname Inference --task runscript --batch
[2026-02-27T22:35:11]     INFO Schema validation succeeded for inference config
[2026-02-27T22:35:11]     INFO Validating config against internal schema: platform
[2026-02-27T22:35:11]     INFO Schema validation succeeded for platform config
[2026-02-27T22:35:11]     INFO inference runscript.inference: Executing
[2026-02-27T22:35:11]     INFO inference runscript.inference: Ready
```

The previously non-existent `run/inference/` directory now contains:

``` bash
$ tree run/inference/
run/inference/
└── runscript.inference

1 directory, 1 file
```

Since `uwtools` driver tasks are idempotent, now that `runscript.inference` exists, it will not be overwritten by subsequent driver invocations. So, it could now be manually edited to e.g. add debugging statements, and the `run` task then invoked to execute inference with the debugging statements in place. If `runscript.inference` were manually deleted and the driver invoked again, the runscript would be recreated with its default contents.

## Development

### Environment

To build the runtime virtual environments **and** install all required development packages in each environment:

``` bash
make devenv cudascript=<name-or-path> # alternatively: EAGLE_DEV=1 ./setup cudascript=<name-or-path>
```

See [Runtime Environment](#runtime-environment) for a description of the `cudascript=` argument.

After successful completion, the following `make` targets will be available:

``` bash
make format     # format Python code
make lint       # run the linter on Python code
make shellcheck # run shellcheck on Bash scripts
make typecheck  # run the typechecker on Python code
make test       # all of the above except formatting
```

The `lint` and `typecheck` targets accept an optional `env=<name>` key-value pair that, if provided, will restrict the tool to the code associated with a particular virtual environment. For example, `make lint env=data` will lint only the code associated with the `data` environment. If no `env` value is provided, all code will be tested.

## Notes

- For each `make` target that executes an EAGLE driver, the following files will be created in the appropriate run directory:
    - `runscript.<target>`: The script to run the core component of the pipeline step. A runscript that submits a batch job will contain batch-system directives. These scripts are self-contained and can also be manually executed (or passed to e.g. `sbatch` if they contain batch directives) to force re-execution, potentially after manual edits for debugging or experimentation purposes.
    - `runscript.<target>.out`: The captured `stdout` and `stderr` of the batch job.
    - `runscript.<target>.submit`: A file containing the job ID of the submitted batch job, if applicable.
    - `runscript.<target>.done`: Created if the core component completes successfully (i.e. exits with status code 0).
- EAGLE drivers are idempotent and, as such, will not take further action if run again unless the output they previously created is removed. In general, removing `.done` (and, when present, `.submit`) files in the appropriate run directory should suffice to reset a driver to allow it to run again, potentially overwriting its previous output. Removing or renaming the entire run directory also works.

## Further Reading 

For more information about model configurations, please see our [documentation](https://epic-eagle.readthedocs.io/en/latest/). 

## Acknowledgments

ufs2arco: Tim Smith (NOAA Physical Sciences Laboratory)
- [Github](https://github.com/NOAA-PSL/ufs2arco)
- [Documentation](https://ufs2arco.readthedocs.io/en/latest/)

Anemoi: European Centre for Medium-Range Weather Forecasts
- [anemoi-core github](https://github.com/ecmwf/anemoi-core)
- [anemoi-inference github](https://github.com/ecmwf/anemoi-inference)
- Documentation: [anemoi-models](https://anemoi.readthedocs.io/projects/models/en/latest/index.html), [anemoi-graphs](https://anemoi.readthedocs.io/projects/graphs/en/latest/), [anemoi-training](https://anemoi.readthedocs.io/projects/training/en/latest/), [anemoi-inference](https://anemoi.readthedocs.io/projects/inference/en/latest/)

wxvx: Paul Madden (NOAA Global Systems Laboratory/Cooperative Institute for Research In Environmental Sciences)
- [Github](https://github.com/maddenp-cu/wxvx)

eagle-tools: Tim Smith (NOAA Physical Sciences Laboratory)
- [Github](https://github.com/NOAA-PSL/eagle-tools)

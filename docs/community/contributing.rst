.. _Contributing:

==============================================================================
Contributing
==============================================================================

.. _Dev:

Development
------------------------------------------------------------------------------

Before starting development, follow the :ref:`Branch and PR Overview <BranchPR>` to clone the upstream
:term:`EAGLE` repository, update your local ``main`` branch, and create a dedicated branch for your
change. All development work should be committed to that branch, not directly to ``main``.

To build the runtime virtual environments **and** install all required
development packages in each environment:

.. code-block:: bash

    make devenv cudascript=<name-or-path> # alternatively: EAGLEDEV=1 ./setup cudascript=<name-or-path>

The ``cudascript=`` argument is described :ref:`here <RuntimeEnvironment>`.

.. hint::

    If an existing, non-development :ref:`runtime environment <RuntimeEnvironment>` has already been built, the ``make devenv`` command can be used to quickly upgrade it to a development environment. There is no need to remove existing conda environments or the underlying conda installation: The development packages will be installed into the existing environments.

    Likewise, if local changes are made to package versions defined in the ``envs/*.yaml`` files, re-running the ``make devenv`` or ``make env`` commands will quickly bring the existing conda environments up-to-date with those newly specified versions: There is no need to remove existing environments or the underlying conda installation.

After successful completion, the following ``make`` targets will be available:

.. code-block:: text

    make format     # format Python code
    make lint       # run a linter on Python code
    make shellcheck # run a checker on Bash scripts
    make typecheck  # run a typechecker on Python code
    make unittest   # run unit tests on Python code and JSON Schema schemas
    make yamllint   # run a linter on :term:`YAML` configs
    make test       # all of the above except formatting

By default, these targets run their tests for every virtual environment. The ``lint``, ``typecheck``, ``unittest``, and ``test`` targets accept an optional ``mod=<name>`` key-value pair that, if provided, will restrict the tool to the code associated with a particular virtual environment. For example, ``make lint mod=data``  will lint only the code associated with the ``data`` environment, and ``make test mod=data`` will run all code-quality checks on ``data`` environment. Specify ``mod=eagle`` to restrict tests to the small amount of code in the top level of the ``eagle`` Python package. If no ``env`` value is provided, all code will be tested.

For each ``make`` target that executes an EAGLE driver, the following
files will be created in the appropriate run directory:

- ``runscript.<target>``: The script to run the core component of the pipeline step. A runscript that submits a batch job will contain batch-system directives. These scripts are self-contained and can also be manually executed (or passed to e.g. ``sbatch`` if they contain batch directives) to force re-execution, potentially after manual edits for debugging or experimentation purposes.
- ``runscript.<target>.out``: The captured ``stdout`` and ``stderr`` of the batch job.
- ``runscript.<target>.submit``: A file containing the job ID of the submitted batch job, if applicable.
- ``runscript.<target>.done``: Created if the core component completes successfully (i.e. exits with status code 0).

EAGLE drivers are idempotent and, as such, will not take further action if run again unless the output they previously
created is removed. In general, removing ``.done`` (and, when present, ``.submit``) files in the appropriate run directory
should suffice to reset a driver to allow it to run again, potentially overwriting its previous output. Removing or
renaming the entire run directory also works.

Debugging Execution
==============================================================================

A number of ``make`` targets, including those that execute EAGLE drivers, invoke the ``uwtools`` CLI and display the full underlying ``uw`` command they run. For example:

.. code-block:: text

    $ make vis-grid-global config=eagle.yaml
    + uw execute --config-file eagle.yaml --module eagle/visualization/visualization.py --classname Visualization --task plots --key-path visualization.grid2grid.global
    ...

Setting the ``DEBUG`` environment variable when executing such a ``make`` target will add the ``--verbose`` flag to the ``uw`` command. For example:

.. code-block:: text

    $ DEBUG=1 make vis-obs-global config=eagle.yaml 2>&1 | head
    + uw execute --verbose --config-file eagle.yaml --module eagle/visualization/visualization.py --classname Visualization --task plots --key-path visualization.grid2obs.global
    ...

The resulting verbose logging, which will include stacktraces from any unhandled Python exceptions, can be invaluable for debugging.

.. _PRs:

Pull Requests
------------------------------------------------------------------------------

.. _BranchPR:

Branch and PR Overview
==============================================================================

Contributions to the ``EAGLE`` project should currently be made through a branch and pull request model in the upstream ``NOAA-EPIC/EAGLE`` repository. Pull request CI does not currently run for branches opened from outside forks. GitHub provides a thorough overview of pull requests in their `Contributing to a project quickstart <https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project>`_, but the process for EAGLE can be summarized as:

#. Create or identify a GitHub issue to document the proposed change.
#. Clone the `EAGLE repository <https://github.com/NOAA-EPIC/EAGLE>`_ onto your development system.

   .. code-block:: bash

      git clone https://github.com/NOAA-EPIC/EAGLE.git
      cd EAGLE

#. Update your local ``main`` branch.

   .. code-block:: bash

      git checkout main
      git pull origin main

#. Create a branch in your clone for the change. All development should take place on a branch, not directly on ``main``.

   .. code-block:: bash

      git checkout -b <branch-name>

#. Make and commit your changes to that branch.

   .. code-block:: bash

      git add <files>
      git commit -m "<commit-message>"

#. Push your branch to the upstream repository.

   .. code-block:: bash

      git push origin <branch-name>

#. Open a pull request to merge your changes into the upstream repository.
#. When merging your PR, select "Squash and merge" unless there's a reason to preserve all individual commits from the feature branch.

Open or review issues on the `EAGLE issues page <https://github.com/NOAA-EPIC/EAGLE/issues>`_.

If you do not have permission to push a branch to ``NOAA-EPIC/EAGLE``, coordinate with a maintainer before opening a pull request so the branch can be hosted where CI will run.

.. _DevTest:

Development and Testing Process
==============================================================================

#. **Branch and develop:** Work on a branch dedicated to a single change or closely related set of changes.
#. **Build the development environment:** Use the commands in the `Development` section above to create the required environments and install development tools.
#. **Format code/data and run code-quality checks:** Before opening a pull request, format code and data and perform code-quality checks by running ``make format && make test``.
#. **Update documentation:** If your change affects workflow behavior, capabilities, or developer setup, update the appropriate RST files in ``docs/``.
#. **Open the pull request:** Push your branch to GitHub and open a pull request against the upstream repository.

When your changes are ready, open a pull request through this repository's `PR page <https://github.com/NOAA-EPIC/EAGLE/pulls>`_. For general guidance on creating pull requests, see this `GitHub documentation <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request>`_.

.. _PRTemplate:

PR Template
==============================================================================

GitHub will automatically populate the PR description with the repository's
`pull request template <https://github.com/NOAA-EPIC/EAGLE/blob/main/.github/pull_request_template.md>`_.
Complete the checklist, including the subcomponent PR check, before requesting
review.

.. _BranchPRCI:

CI for Branch-Based Pull Requests
==============================================================================

Pull requests from branches in the upstream ``NOAA-EPIC/EAGLE`` repository use
the repository's normal GitHub Actions checks.

The Ursa end-to-end workflow is intentionally opt-in. After a maintainer has
reviewed the PR and is comfortable running it on the self-hosted Ursa runner,
they can add the ``eagle-ursa`` label to trigger the label-gated workflow.

.. _Docs:

Documentation
------------------------------------------------------------------------------

If you are adding to or updating the documentation, wish to build and review changes locally, and have already built the EAGLE runtime software environment environment (i.e., ``conda/`` exists), then from the root directory of a clone of this repository:

.. code-block:: bash

    make -C docs

If wish to use some other conda installation:

.. code-block:: text

    <command to activate your conda installation>
    make -C docs

Note that, if you use your own conda installation, an environment called ``docs`` will be created, or an existing one will be updated.

After that, open the generated HTML files in your web browser:

.. code-block:: bash

    docs/build/html/index.html

After you submit the changes as a pull request, the docs will build automatically.

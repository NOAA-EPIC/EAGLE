.. _Contributing:

==============================================================================
Contributing
==============================================================================

.. _Dev:

Development
------------------------------------------------------------------------------

First, fork the main :term:`EAGLE` repository into your GitHub account, then
clone your fork on the machine where you will do the development work. External
contributions should be submitted as pull requests from a branch in your fork.

.. code-block:: text

    git clone https://github.com/<github-username>/EAGLE.git
    cd EAGLE
    git remote add upstream https://github.com/NOAA-EPIC/EAGLE.git
    git fetch upstream

.. code-block:: text

    git checkout -b <branch-name> upstream/main

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

.. _ForkPR:

Fork and PR Overview
==============================================================================

Contributions to the ``EAGLE`` project are made through a fork and pull request model. GitHub provides a thorough overview in their `Contributing to a project quickstart <https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project>`_, but the process for EAGLE can be summarized as:

#. Create or identify a GitHub issue to document the proposed change.
#. Fork the `EAGLE repository <https://github.com/NOAA-EPIC/EAGLE>`_ into your personal GitHub account.
#. Clone your fork onto your development system.
#. Add the upstream remote, if your clone does not already have one: ``git remote add upstream https://github.com/NOAA-EPIC/EAGLE.git``.
#. Create a branch in your clone for the change. All development should take place on a branch in your fork, not on ``main``.
#. Make, commit, and push your changes to that branch in your fork.
#. Open a pull request to merge your changes into the upstream repository.
#. When merging your PR, select "Squash and merge" unless there's a reason to preserve all individual commits from the feature branch.

Open or review issues on the `EAGLE issues page <https://github.com/NOAA-EPIC/EAGLE/issues>`_.

For future contributions, keep your fork current by syncing it with the upstream ``NOAA-EPIC/EAGLE`` repository.

.. _DevTest:

Development and Testing Process
==============================================================================

#. **Branch and develop:** Work on a fork branch dedicated to a single change or closely related set of changes.
#. **Build the development environment:** Use the commands in the `Development` section above to create the required environments and install development tools.
#. **Format code/data and run code-quality checks:** Before opening a pull request, format code and data and perform code-quality checks by running ``make format && make test``.
#. **Update documentation:** If your change affects workflow behavior, capabilities, or developer setup, update the appropriate RST files in ``docs/``.
#. **Open the pull request:** Push your branch to GitHub and open a pull request against the upstream repository.

When your changes are ready, commit them on your feature branch and push the branch to your fork:

.. code-block:: bash

    git add <files>
    git commit -m "<commit-message>"
    git push origin <branch-name>

Then open a pull request from your fork branch to the upstream ``NOAA-EPIC/EAGLE`` repository through this repository's `PR page <https://github.com/NOAA-EPIC/EAGLE/pulls>`_. For general guidance on creating pull requests, see this `GitHub documentation <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request>`_.

.. _PRTemplate:

PR Template
==============================================================================

GitHub will automatically populate the PR description with the repository's
`pull request template <https://github.com/NOAA-EPIC/EAGLE/blob/main/.github/pull_request_template.md>`_.
Complete the checklist, including the subcomponent PR check, before requesting
review.

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

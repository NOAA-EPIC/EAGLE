.. _Contributing:

==============================================================================
Contributing
==============================================================================

.. _Dev:

Development
------------------------------------------------------------------------------

First, clone the :term:`EAGLE` repository's ``release/public-v1.0.0`` branch and create a branch on the machine where you will
do the development work. Contributions should be submitted as pull requests from a
branch separate from the release branch.

.. code-block:: text

    git clone --branch release/public-v1.0.0 https://github.com/NOAA-EPIC/EAGLE.git
    cd EAGLE

.. code-block:: text

    git checkout -b <branch-name>

To build the runtime virtual environments **and** install all required
development packages in each environment:

.. code-block:: bash

    make devenv cudascript=<name-or-path> # alternatively: EAGLEDEV=1 ./setup cudascript=<name-or-path>

See :ref:`Runtime Environment <RuntimeEnvironment>` for a description of the ``cudascript=`` argument.

After successful completion, the following ``make`` targets will be available:

.. code-block:: text

    make format     # format Python code
    make lint       # run a linter on Python code
    make shellcheck # run a checker on Bash scripts
    make typecheck  # run a typechecker on Python code
    make unittest   # run unit tests on Python code and JSON Schema schemas
    make yamllint   # run a linter on :term:`YAML` configs
    make test       # all of the above except formatting

The ``lint``, ``typecheck``, and ``unittest`` targets accept an optional ``env=<name>`` key-value pair that, if provided, will restrict the tool to the code associated with a particular virtual environment. For example, ``make lint env=data``  will lint only the code associated with the ``data`` environment. If no ``env`` value is provided, all code will be tested. (Specify `env=eagle` to restrict the tool to the small amount of code in the top level of the ``eagle`` Python package.)

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

Branch and PR Overview
==============================================================================

Contributions to the ``EAGLE`` project should currently be made through a branch and pull request model in the upstream ``NOAA-EPIC/EAGLE`` repository. Pull request CI does not currently run for branches opened from outside forks. GitHub provides a thorough overview of pull requests in their `Contributing to a project quickstart <https://docs.github.com/en/get-started/exploring-projects-on-github/contributing-to-a-project>`_, but the process for EAGLE can be summarized as:

#. Create or identify a GitHub issue to document the proposed change.
#. Clone the `EAGLE repository <https://github.com/NOAA-EPIC/EAGLE>`_ onto your development system.
#. Create a branch in your clone for the change. All development should take place on a branch, not directly on ``release/public-v1.0.0``.
#. Make, commit, and push your changes to that branch in the upstream repository.
#. Open a pull request to merge your changes into the upstream repository.

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

When your changes are ready, commit them on your feature branch and push the branch to GitHub:

.. code-block:: bash

    git add <files>
    git commit -m "<commit-message>"
    git push origin <branch-name>

Then open a pull request through this repository's `PR page <https://github.com/NOAA-EPIC/EAGLE/pulls>`_. For general guidance on creating pull requests, see this `GitHub documentation <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request>`_.

.. _PRTemplate:

PR Template
==============================================================================

Use the following pull request template when opening a PR:

.. code-block:: md

    <!-- INSTRUCTIONS:
    - READ/FOLLOW THE DIRECTIONS IN EACH SECTION
    - Complete the 'Commit Requirements' below
    - Use GitHub markup as much as possible (https://docs.github.com/en/get-started/writing-on-github)
    - Leave your PR in a draft state until all underlying work is completed.
    -->

    ## Description:
    <!-- This description will become the commit message for the PR. -->
    <!-- See https://cbea.ms/git-commit for commit message suggestions. -->
    <!--
    Provide a clear and concise description of *what* this PR does and *why*.
    Explain why this change is needed and any context that helps reviewers.
    Add the related GitHub Issues here.
    Please be sure to add the issue this PR resolves using the word "Resolves". If there are any issues that are related but not yet resolved (including in other repos), you may use "Refs".
    Resolves #1234
    Refs #4321
    Refs NOAA-EPIC/repo#5678
    -->

    ## Type of change:
    <!--
    Indicate PR type of change.
    Delete options that are not applicable.
    -->
    - [ ] Bug fix
    - [ ] New feature
    - [ ] Refactor / cleanup
    - [ ] Documentation
    - [ ] CI/CD or tooling
    - [ ] Other:

    ## Area(s) affected
    <!-- Check all that apply -->
    - [ ] nested_eagle workflow
    - [ ] Verification / evaluation (via WXVX)
    - [ ] Data prep / UFS2ARCO
    - [ ] Config (YAML)
    - [ ] Plotting / post-processing
    - [ ] Infrastructure / Slurm scripts
    - [ ] Other:

    ## Commit Requirements:
    <!--
    - Check off completed items. Use [X] for a filled in checkbox or leave it [ ] for an empty checkbox
    - Your pull request (PR) will not be considered until all requirements are met.
    - THIS IS YOUR RESPONSIBILITY
    -->
    - [ ] This PR addresses a relevant NOAA-EPIC/EAGLE issue (if not, create an issue); a person responsible for submitting the update has been assigned to the issue (link issue)
    - [ ] Fill out all sections of this template.
    - [ ] I have performed a self-review of my own code
    - [ ] My changes generate no new warnings
    - [ ] I have made corresponding changes to the system documentation if necessary

    ## Testing / Verification:
    <!--
    Provide minimal reproducible steps and results.
    Include configs, commands, and expected outputs where possible.
    Delete this section if not applicable.
    -->
    - [ ] I ran and/or verified the changes (or provided a test plan)
    - Commands/config used:
      -
    - Evidence (logs, key output paths, screenshots if relevant):
      -

    ## Runtime Environment:
    <!--
    Fill in if you ran on HPC or a specific system. Delete if not applicable.
    -->
    - System/HPC:
    - Account/role:
    - Conda env:
    - Key versions (optional):
      - `python --version`:
      - `wxvx --version` (if applicable):
      - MET version (if applicable):

    ## Commit Message:
    <!--
    Provide a concise commit message for any subcomponents; delete unnecessary info.
    -->
    * UFS2ARCO -
    * WXVX (verification) -

    ## Subcomponent Pull Requests:
    <!--
    Provide a list of NOAA-EPIC/EAGLE and subcomponents involved with this PR and include links to subcomponent PRs.
    Example:
    * EAGLE: NOAA-EPIC/EAGLE#13
    * UFS2ARCO: NOAA-PSL/UFS2ARCO#734
    * WXVX: NOAA-EPIC/WXVX#33
    Delete sections that are not needed.
    -->
    * EAGLE: NOAA-EPIC/EAGLE#
    * UFS2ARCO: NOAA-PSL/UFS2ARCO#
    * WXVX (verification): NOAA-EPIC/WXVX#
    * None

.. _Docs:

Documentation
------------------------------------------------------------------------------

If you are adding to or updating the documentation, wish to build and review changes locally, and have already built the EAGLE runtime software environment environment under ``src/`` (i.e., ``src/conda`` exists), then from the root directory of a clone of this repository:

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

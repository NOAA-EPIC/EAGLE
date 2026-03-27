.. _Contributing:

==============================================================================
Contributing
==============================================================================

.. _Dev:

Development
------------------------------------------------------------------------------

First, clone the main repository and create a branch on the machine where you will 
do the development work. Contributions should be submitted as pull requests from a 
branch separate from the main branch.

.. code-block:: bash

    git clone https://github.com/NOAA-EPIC/EAGLE.git
    cd EAGLE

.. code-block:: bash

    git checkout -b <branch-name>

To build the runtime virtual environments **and** install all required development packages in each environment:

.. code-block:: bash

    make devenv cudascript=<name-or-path> # alternatively: EAGLE_DEV=1 ./setup cudascript=<name-or-path>

See :ref:`Runtime Environment <RuntimeEnvironment>` for a description of the ``cudascript=`` argument.

After successful completion, the following ``make`` targets will be available:

.. code-block:: bash

    make format     # format Python code
    make lint       # run a linter on Python code
    make shellcheck # run a checker on Bash scripts
    make typecheck  # run a typechecker on Python code
    make yamllint   # run a linter on YAML configs
    make test       # all of the above except formatting

The ``lint`` and ``typecheck`` targets accept an optional ``env=<name>`` key-value pair that, if provided, will 
restrict the tool to the code associated with a particular virtual environment. For example, ``make lint env=data`` 
will lint only the code associated with the ``data`` environment. If no ``env`` value is provided, all code will be tested.

For each ``make`` target that executes an EAGLE driver, the following files will be created in the appropriate run directory:

- ``runscript.<target>``: The script to run the core component of the pipeline step. A runscript that submits a batch job will contain batch-system directives. These scripts are self-contained and can also be manually executed (or passed to e.g. ``sbatch`` if they contain batch directives) to force re-execution, potentially after manual edits for debugging or experimentation purposes.
- ``runscript.<target>.out``: The captured ``stdout`` and ``stderr`` of the batch job.
- ``runscript.<target>.submit``: A file containing the job ID of the submitted batch job, if applicable.
- ``runscript.<target>.done``: Created if the core component completes successfully (i.e. exits with status code 0).

EAGLE drivers are idempotent and, as such, will not take further action if run again unless the output they previously 
created is removed. In general, removing ``.done`` (and, when present, ``.submit``) files in the appropriate run directory 
should suffice to reset a driver to allow it to run again, potentially overwriting its previous output. Removing or 
renaming the entire run directory also works.

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
#. Create a branch in your clone for the change. All development should take place on a branch, not on ``main``.
#. Make, commit, and push your changes to that branch in your fork.
#. Open a pull request to merge your changes into the upstream repository.

Open or review issues on the `EAGLE issues page <https://github.com/NOAA-EPIC/EAGLE/issues>`_.

For future contributions, keep your fork current by syncing it with the upstream ``NOAA-EPIC/EAGLE`` repository.

.. _DevTest:

Development and Testing Process
==============================================================================

#. **Branch and develop:** Work on a branch dedicated to a single change or closely related set of changes.
#. **Build the development environment:** Use the commands in the `Development` section above to create the required environments and install development tools.
#. **Run checks:** Before opening a pull request, run the relevant quality checks such as ``make lint``, ``make typecheck``, ``make yamllint``, and ``make test``.
#. **Update documentation:** If your change affects workflow behavior, capabilities, or developer setup, update the appropriate RST files in ``docs/``.
#. **Open the pull request:** Push your branch to GitHub and open a pull request against the upstream repository.

When your changes are ready, commit them on your feature branch and push the branch to GitHub:

.. code-block:: bash

    git add <files>
    git commit -m "<commit-message>"
    git push origin <branch-name>

Then open a pull request through this repository's `PR page <https://github.com/NOAA-EPIC/EAGLE/pulls>`_. For general guidance on creating pull requests, see this `GitHub documentation <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request>`_.

.. _Docs:

Documentation
------------------------------------------------------------------------------

If you are adding to the documentation and wish to build and review changes locally:

.. code-block:: bash
    
    conda create -y -n docs sphinx sphinx_rtd_theme
    conda activate docs
    cd EAGLE/docs
    make html

After that, open the generated HTML files in your web browser:

.. code-block:: bash

    _build/html/index.html

After you submit the changes as a pull request, the docs will build automatically.

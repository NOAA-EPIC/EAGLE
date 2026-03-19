=================
Contributing
=================

Development
------------------

First you will want clone the main repository, and create a branch on the machine where you will 
do the development work. We want any contribution in the form of a pull request that is on a 
separate branch from the main branch.

To build the runtime virtual environments **and** install all required development packages in each environment::

    make devenv cudascript=<name-or-path> # alternatively: EAGLE_DEV=1 ./setup cudascript=<name-or-path>

See Runtime Environment above for a description of the ``cudascript=`` argument.

After successful completion, the following ``make`` targets will be available:

.. code-block:: text

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

Pull Requests
------------------

Submit pull requests through this repository's `PR page <https://github.com/NOAA-EPIC/EAGLE/pulls>`_, as outlined in 
this `GitHub documentation <https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request>`_.

Documentation
------------------

If you are adding to the documentation and wish to build and review changes locally::
    
    conda create -y -n docs sphinx sphinx_rtd_theme
    conda activate docs
    cd EAGLE/docs
    make html

After that, you can open the generated html files to view in your web browser::

    open _build/html/index.html

After you submit the changes as a PR the changes will build automatically.
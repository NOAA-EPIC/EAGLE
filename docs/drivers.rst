=================
Drivers
=================

The various software components required by EAGLE are executed by ``uwtools`` drivers implemented as Python 
modules under ``src/eagle/``. By default, the targets in ``src/Makefile`` invoke drivers' most comprehensive 
tasks, i.e. those that configure and execute the component to produce its final output. However, each driver 
provides a number of tasks, some depending on others, and lower-level tasks can be invoked to request less 
than full execution of the driver, which can be useful during development and debugging.

To request a specific task, add a ``task=`` clause to the appropriate ``make`` target. To see a list of available 
tasks, specify ``task=?``.

For example::
    
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

For example, the ``provisioned_rundir`` task would provision the run directory with all its required content, but 
would not execute the ``anemoi-inference`` component. The ``run`` task would fully execute inference.

To invoke the ``Inference`` driver's ``runscript`` task, provisioning only the component's runscript::

    $ make inference config=eagle.yaml task=runscript
    + uw execute --config-file eagle.yaml --module eagle/inference/inference.py --classname Inference --task runscript --batch
    [2026-02-27T22:35:11]     INFO Schema validation succeeded for inference config
    [2026-02-27T22:35:11]     INFO Validating config against internal schema: platform
    [2026-02-27T22:35:11]     INFO Schema validation succeeded for platform config
    [2026-02-27T22:35:11]     INFO inference runscript.inference: Executing
    [2026-02-27T22:35:11]     INFO inference runscript.inference: Ready

The previously non-existent ``run/<expname>inference/`` directory now contains::

    $ tree run/<expname>/inference/
    run/<expname>inference/
    └── runscript.inference

    1 directory, 1 file

Since ``uwtools`` driver tasks are idempotent, now that ``runscript.inference`` exists, it will not be overwritten 
by subsequent driver invocations. So, it could now be manually edited to e.g. add debugging statements, and 
the ``run`` task then invoked to execute inference with the debugging statements in place. If ``runscript.inference`` 
were manually deleted and the driver invoked again, the runscript would be recreated with its default contents.

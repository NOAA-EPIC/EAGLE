.. _FAQ:

****
FAQ
****

.. contents::
   :depth: 2
   :local:

=====================
Using EAGLE
=====================

.. _SupportedPlatformsFAQ:

What platforms are currently supported?
===============================================================================

At present, :term:`Ursa` is the only supported platform for EAGLE, but support for additional platforms is coming soon.

Can I generate Anemoi training plots only for the nested HRRR domain?
===============================================================================

Yes. Users can define multiple bounding boxes to specify subset regions, such
as :term:`CONUS` or Europe, by adding focus-area configuration to the
``PlotSample`` callback in the EAGLE pipeline ``base.yaml``. This configuration
generates plots that exclude the surrounding global domain. Define named boxes
under ``focus_areas`` and reference the selected box from ``PlotSample`` with
``focus_area``.

Although users can modify ``base.yaml`` directly for reference, it is
recommended that they instead add the configuration to the ``eagle.yaml`` file
created during the Quickstart workflow. Changes made directly to ``base.yaml``
may be overwritten during configuration composition, whereas updates made in
``eagle.yaml`` are preserved.

For example, for the :term:`HRRR`/:term:`CONUS` domain, use
``latlon_bbox: [22.0, -135.0, 50.0, -60.0]`` or adjust as needed. Once added,
the diagnostics will generate plots restricted to the configured region. For
more information, see the `plot adaptor compatibility section
<https://anemoi.readthedocs.io/projects/training/en/latest/modules/diagnostics.html#plot-adapter-compatibility>`_
of the `Anemoi Training diagnostic documentation
<https://anemoi.readthedocs.io/projects/training/en/latest/modules/diagnostics.html>`_.

Can I add an HRRR-only variable, such as reflectivity, to nested-EAGLE training?
================================================================================

Not directly with the current nested :term:`HRRR`-over-:term:`GFS` training
setup. The nested pipeline combines HRRR and GFS data into a single Anemoi
training dataset, so the variables used for training must be compatible across
the nested domains.

To train with an HRRR-only variable, users would need a :term:`CONUS`-only
configuration or a design that provides a compatible global counterpart,
placeholder, or derived field, along with corresponding data, normalization, and
model configuration changes.

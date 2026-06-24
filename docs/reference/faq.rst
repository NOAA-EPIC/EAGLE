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

Yes. Anemoi Training plotting callbacks support a ``focus_area`` setting that
can restrict plots to a latitude/longitude bounding box or graph mask. For a
:term:`CONUS` area similar to the :term:`HRRR` domain, a bounding box such as
``latlon_bbox: [22.0, -135.0, 50.0, -60.0]`` may be used and adjusted as
needed. The values are ordered as ``[lat_min, lon_min, lat_max, lon_max]``.

In EAGLE, define the focus area in the nested training diagnostics plot
configuration and apply it to the relevant ``PlotSample`` callback with
``focus_area``. See the `Anemoi Training diagnostics documentation
<https://anemoi.readthedocs.io/projects/training/en/latest/modules/diagnostics.html#plot-adapter-compatibility>`_
for details.

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

BUILDDIR   = build
CONDAFLAGS = $(CONDAOPTS) $(CONDAPKGS)
CONDAOPTS  = -y -n docs -c conda-forge --override-channels
CONDAPKGS  = sphinx sphinx_rtd_theme sphinxcontrib-bibtex

.ONESHELL:
.PHONY: clean docs help Makefile

docs:
	which conda 2>/dev/null || source ../src/conda/etc/profile.d/conda.sh
	conda activate docs 2>/dev/null && conda install $(CONDAFLAGS) || conda create $(CONDAFLAGS)
	conda activate docs
	$(MAKE) html

clean:
	rm -rf $(BUILDDIR)

%: Makefile
	mkdir -p $(BUILDDIR)
	sphinx-build -M $@ . $(BUILDDIR) --fail-on-warning --nitpicky -w $(BUILDDIR)/warnings.log

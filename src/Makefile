BASHSRCS = $(wildcard ../.github/scripts/*) format setup
ENVS     = data inference training visualization wxvx
HELPERS  = vx zarr
PACKAGE  = eagle
STEPS    = data grids-and-meshes inference training vis-grid-global vis-grid-lam vis-obs-global vis-obs-lam vx-grid-global vx-grid-lam vx-obs-global vx-obs-lam zarr-gfs zarr-hrrr
TOOLING  = config devenv env format lint realize shellcheck test typecheck unittest validate yamllint
VERBOSE  = $(if $(filter undefined,$(origin DEBUG)),, --verbose)

INSTALLDIR ?= conda
SHELL      := $(shell which bash)

NOW = $(shell date -uIseconds)
ifeq ($(nrt),true)
export NOW
endif

activate = @source $(INSTALLDIR)/etc/profile.d/conda.sh && conda activate $(1)
check    = @$(if $(1),,$(error $(2)= argument required))
envloop  = @set -e && for env in $(PACKAGE) $(ENVS); do $(make) env=$$env $(1); done
exec     = set -x && uw execute$(VERBOSE) --config-file $(config) --module $(PACKAGE)/$(1)/$(2).py --classname $(3) --task $(4)
make     = $(MAKE) --no-print-directory
tasklist = @(set -x && uw execute$(VERBOSE) --module $(PACKAGE)/$(1)/$(2).py --classname $(3)) || true

.ONESHELL:
.PHONY: $(HELPERS) $(STEPS) $(TOOLING)

all:
	@echo Available targets:
	@echo
	@echo Pipeline steps: $(STEPS)
	@echo Tooling: $(TOOLING)
	@echo
	false

config:
	$(call check,$(compose),compose)
	$(call activate,base)
	@(set -x && uw config compose$(VERBOSE) $(foreach x,$(subst :, ,$(compose)),config/$(x).yaml))

data:
	@$(make) grids-and-meshes
	@$(make) zarr-gfs
	@$(make) zarr-hrrr

devenv:
	$(call check,$(cudascript),cudascript)
	EAGLEDEV=1 INSTALLDIR=$(INSTALLDIR) ./setup cudascript=$(cudascript)
env:
	$(call check,$(cudascript),cudascript)
	INSTALLDIR=$(INSTALLDIR) ./setup cudascript=$(cudascript)

format:
	$(call activate,base)
	./format $(PACKAGE)

grids-and-meshes:
	$(call activate,data)
ifeq ($(task),?)
	$(call tasklist,data,grids_and_meshes,GridsAndMeshes)
else
	$(call check,$(config),config)
	$(call exec,data,grids_and_meshes,GridsAndMeshes,$(or $(task),provisioned_rundir))
endif

inference:
	$(call activate,inference)
ifeq ($(task),?)
	$(call tasklist,inference,inference,Inference)
else
	$(call check,$(config),config)
	$(call exec,inference,inference,Inference,$(or $(task),run) --batch)
endif

lint:
ifdef env
	@echo "=> Linting package: $$env"
	$(call activate,$(if $(filter $(PACKAGE),$(env)),base,$(env)))
	ruff check $(PACKAGE)/$(if $(filter $(PACKAGE),$(env)),*.py,$(env))
else
	$(call envloop,lint)
endif

realize:
	$(call check,$(config),config)
	$(call activate,base)
	@(set -x && uw config realize$(VERBOSE) --input-file $(config))

shellcheck:
	$(call activate,base)
	@echo "=> Checking shell scripts"
	@(set -x && shellcheck --format=gcc --severity=info --shell=bash $(BASHSRCS))

test: lint shellcheck typecheck yamllint unittest

training:
	$(call activate,training)
ifeq ($(task),?)
	$(call tasklist,training,training,Training)
else
	$(call check,$(config),config)
	$(call exec,training,training,Training,$(or $(task),run) --batch)
endif

typecheck:
ifdef env
	@echo "=> Typechecking package: $$env"
	$(call activate,$(if $(filter $(PACKAGE),$(env)),base,$(env)))
	mypy $(PACKAGE)/$(if $(filter $(PACKAGE),$(env)),*.py,$(env))
else
	$(call envloop,typecheck)
endif

unittest:
ifdef env
	@echo "=> Unit testing package: $$env"
	$(call activate,$(if $(filter $(PACKAGE),$(env)),base,$(env)))
	pytest $(if $(filter $(PACKAGE),$(env)),,--cov=$(PACKAGE).$(env) )$(PACKAGE)/$(if $(filter $(PACKAGE),$(env)),*.py,$(env))
else
	$(call envloop,unittest)
endif

validate:
	$(call check,$(config),config)
	$(call activate,base)
	@(set -x && uw config validate$(VERBOSE) --input-file $(config) --schema-file $(PACKAGE)/$(PACKAGE).jsonschema)

vis:
	$(call activate,visualization)
ifeq ($(task),?)
	$(call tasklist,visualization,visualization,Visualization)
else
	$(call check,$(config),config)
	$(call check,$(extent),extent)
	$(call check,$(truth),truth)
	$(call exec,visualization,visualization,Visualization,$(or $(task),plots) --key-path visualization.grid2$(truth).$(extent))
endif

vis-grid-global:
	@$(make) vis truth=grid extent=global

vis-grid-lam:
	@$(make) vis truth=grid extent=lam

vis-obs-global:
	@$(make) vis truth=obs extent=global

vis-obs-lam:
	@$(make) vis truth=obs extent=lam

vx:
	$(call activate,wxvx)
ifeq ($(task),?)
	$(call tasklist,wxvx,wxvx,VX)
else
	$(call check,$(config),config)
	$(call check,$(extent),extent)
	$(call check,$(truth),truth)
	$(call exec,wxvx,wxvx,WXVX,$(or $(task),run) --key-path vx.grid2$(truth).$(extent) --batch)
endif

vx-grid-global:
	@$(make) vx truth=grid extent=global

vx-grid-lam:
	@$(make) vx truth=grid extent=lam

vx-obs-global:
	@$(make) vx truth=obs extent=global

vx-obs-lam:
	@$(make) vx truth=obs extent=lam

yamllint:
	$(call activate,base)
	@echo "=> Linting YAML configs"
	@(set -x && yamllint --no-warnings config/ envs/)

zarr:
	$(call activate,data)
ifeq ($(task),?)
	$(call tasklist,data,zarr,Zarr)
else
	$(call check,$(config),config)
	$(call check,$(source),source)
	$(call exec,data,zarr,Zarr,$(or $(task),run) --key-path zarrs.$(source) --batch)
endif

zarr-gfs:
	@$(make) zarr source=gfs

zarr-hrrr:
	@$(make) zarr source=hrrr

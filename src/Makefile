BASHSRCS = format setup
ENVS     = data inference prewxvx training wxvx
HELPERS  = prewxvx vx zarr
PACKAGE  = eagle
STEPS    = data grids-and-meshes inference prewxvx-global prewxvx-lam training vx-grid-global vx-grid-lam vx-obs-global vx-obs-lam zarr-gfs zarr-hrrr
TOOLING  = config devenv env format lint realize shellcheck test typecheck validate yamllint

INSTALLDIR ?= conda

activate = @source $(INSTALLDIR)/etc/profile.d/conda.sh && conda activate $(1)
check    = @$(if $(1),,$(error $(2)= argument required))
envloop  = @for env in $(ENVS); do $(make) env=$$env $(1); done
exec     = set -x && uw execute --config-file $(config) --module $(PACKAGE)/$(1)/$(2).py --classname $(3) --task $(4)
make     = $(MAKE) --no-print-directory
tasklist = @(set -x && uw execute --module $(PACKAGE)/$(1)/$(2).py --classname $(3)) || true

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
	@(set -x && uw config compose $(foreach x,$(subst :, ,$(compose)),config/$(x).yaml))

data:
	@$(make) grids-and-meshes
	@$(make) zarr-gfs
	@$(make) zarr-hrrr

devenv:
	$(call check,$(cudascript),cudascript)
	EAGLE_DEV=1 INSTALLDIR=$(INSTALLDIR) ./setup cudascript=$(cudascript)
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
	$(call activate,$(env))
	ruff check $(PACKAGE)/$(env)
else
	$(call envloop,lint)
endif

prewxvx:
	$(call activate,prewxvx)
ifeq ($(task),?)
	$(call tasklist,prewxvx,prewxvx,PreWXVX)
else
	$(call check,$(config),config)
	$(call check,$(extent),extent)
	$(call exec,prewxvx,prewxvx,PreWXVX,$(or $(task),run) --key-path prewxvx.$(extent))
endif

prewxvx-global:
	@$(make) prewxvx extent=global

prewxvx-lam:
	@$(make) prewxvx extent=lam

realize:
	$(call check,$(config),config)
	$(call activate,base)
	@(set -x && uw config realize --input-file $(config))

shellcheck:
	$(call activate,base)
	@echo "=> Checking shell scripts"
	@(set -x && shellcheck --format=gcc --severity=info --shell=bash $(BASHSRCS))

test: lint shellcheck typecheck yamllint

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
	$(call activate,$(env))
	mypy $(PACKAGE)/$(env)
else
	$(call envloop,typecheck)
endif

validate:
	$(call check,$(config),config)
	$(call activate,base)
	@(set -x && uw config validate --input-file $(config) --schema-file eagle/eagle.jsonschema)

vx:
	$(call activate,wxvx)
ifeq ($(task),?)
	$(call tasklist,wxvx,wxvx,VX)
else
	$(call check,$(config),config)
	$(call check,$(extent),extent)
	$(call check,$(truth),truth)
	$(call exec,wxvx,wxvx,WXVX,$(or $(task),run) --key-path vx.$(truth).$(extent) --batch)
endif

vx-grid-global:
	@$(make) vx truth=grid2grid extent=global

vx-grid-lam:
	@$(make) vx truth=grid2grid extent=lam

vx-obs-global:
	@$(make) vx truth=grid2obs extent=global

vx-obs-lam:
	@$(make) vx truth=grid2obs extent=lam

yamllint:
	$(call activate,base)
	@echo "=> Linting YAML configs"
	@(set -x && yamllint --no-warnings config/)

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

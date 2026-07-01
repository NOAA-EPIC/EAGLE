#!/usr/bin/env bash

set -x

EAGLEhome=/scratch5/purged/Wei.Huang/src/EAGLE

source ${EAGLEhome}/conda/etc/profile.d/conda.sh

# Ensure EAGLEhome is expanded cleanly
conda_bin_path="${EAGLEhome}/conda/bin"

eval "$(mamba shell hook --shell bash)"

mamba activate visualization

export BASE_DIR="/scratch5/purged/Wei.Huang/src/nv/data/eagle/forecast"
envsubst < config.yaml.template > config.yaml && python eagle_vis.py

exit 0


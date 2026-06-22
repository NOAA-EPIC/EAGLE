#!/usr/bin/env bash

set -x

vis=`pwd`
EAGLEhome="${vis}/../src"

source ${EAGLEhome}/conda/etc/profile.d/conda.sh

# Ensure EAGLEhome is expanded cleanly
conda_bin_path="${EAGLEhome}/conda/bin"

if [[ ":$PATH:" =~ ":${conda_bin_path}:" ]]; then
    if [[ "${verbose}" == "YES" ]]; then
        echo "Success: ${conda_bin_path} is already in your PATH."
    fi
else
    # echo "Warning: ${conda_bin_path} is missing from your PATH. Adding it now..."
    export PATH="${conda_bin_path}:$PATH"
fi

eval "$(mamba shell hook --shell bash)"

mamba activate ${EAGLEhome}/conda/envs/visualization

export BASE_DIR="/scratch5/purged/Wei.Huang/src/nv/data/eagle/forecast"
envsubst < config.yaml.template > config.yaml && python eagle_vis.py

exit 0


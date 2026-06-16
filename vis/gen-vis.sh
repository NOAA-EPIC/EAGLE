#!/usr/bin/env bash

set -x

#EAGLEhome=/scratch3/NAGAPE/epic/Wei.Huang/src/EAGLE/src
#source ${EAGLEhome}/conda/etc/profile.d/conda.sh
#eval "$(mamba shell hook --shell bash)"
#mamba activate ${EAGLEhome}/conda/envs/visualization

python ./plotwindbarb.py

exit 0


#!/usr/bin/env bash

# default setting
EAGLEhome=`pwd`
MACHINE_ID=ursa
#expname=default
expname="wei_learning_nrt"
verbose="NO"
step="training"

function _usage() {
    cat << EOF
Run EAGLE on head node (ursa).

Usage: ${BASH_SOURCE[0]} [-h][-v] -n name_of_experiment -s [env devenv config data training inference verification visualization] -m machine_id
  -h:
    Print this help message and exit
  -v:
    Verbose mode
  -n:
    Name of the experiment
  -s:
    Steps of EAGLE
  -m:
    Machine ID (default: ursa)

  Input arguments are the step(s) to run.
  Valid options are
    env devenv config data training inference verification visualization
    (default is "training")
EOF
    exit 0
}

set -eu

# FIXED: Added colons after n, s, and m so they handle trailing arguments properly!
while getopts ":hn:s:m:v" option; do
    case "${option}" in
        h) _usage ;;
        n) expname=${OPTARG} ;;  # Changed from e to n to match documentation
        s) step=${OPTARG} ;;
        m) MACHINE_ID=${OPTARG} ;;
        v) verbose="YES" ;;
        *)
            echo "[${BASH_SOURCE[0]}]: Unrecognized option: ${option}"
            _usage
            ;;
    esac
done

if [[ "${verbose}" == "YES" ]]; then
    set -x
fi

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

case "${step}" in
    env|devenv)
	mamba activate ${EAGLEhome}/conda/envs/anemoi
        make env cudascript=${MACHINE_ID}
        ;;
    config)
	mamba activate ${EAGLEhome}/conda/envs/anemoi
        make config compose=base:nested:ursa:nrt > nrt-composed.yaml
        sed -i "s?/path/to/eagle/src?${EAGLEhome}?g" nrt-composed.yaml
	make realize config=nrt-composed.yaml > nrt.yaml
        ;;
    data)
	mamba activate ${EAGLEhome}/conda/envs/data
        make data config=nrt.yaml
        ;;
    inference)
	# Check if training is done:
	#if [[ ! -f "${EAGLEhome}/run/${expname}/training/runscript.training.done" ]]; then
        #    echo "Training is not done, need to run ${BASH_SOURCE[0]} -n ${expname} -s training"
        #    echo "Then wait and re-run when training is done."
        #    exit 15
        #fi
	mamba activate ${EAGLEhome}/conda/envs/inference
        make inference config=nrt.yaml
        ;;
    veri*)
	# Check if training is done:
	if [[ ! -f "${EAGLEhome}/run/${expname}/inference/runscript.inference.done" ]]; then
            echo "Inference is not done, need to run ${BASH_SOURCE[0]} -n ${expname} -s inference"
            echo "Then wait and re-run when inference is done."
            exit 16
        fi
	mamba activate ${EAGLEhome}/conda/envs/wxvx
        make vx-grid-global config=nrt.yaml &
        make vx-grid-lam config=nrt.yaml &
        make vx-obs-global config=nrt.yaml &
        make vx-obs-lam config=nrt.yaml &
	wait
        ;;
    visu*)
	mamba activate ${EAGLEhome}/conda/envs/visualization
        make vis-grid-global config=nrt.yaml &
        make vis-grid-lam config=nrt.yaml &
        make vis-obs-global config=nrt.yaml &
        make vis-obs-lam config=nrt.yaml &
	wait
        ;;
    *)
        echo "Unrecognized step: ${step}"
        ;;
esac

exit 0


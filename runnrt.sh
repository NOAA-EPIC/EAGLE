#!/usr/bin/env bash

# default setting
EAGLEhome=`pwd`
MACHINE_ID=ursa
#expname=default
expname="eagle_case"
verbose="NO"
step="training"

function _usage() {
    cat << EOF
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
    config data inference verification visualization all
    (default is "training")
EOF
    exit 0
}

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

wait_for_file() {
    local file_path="$1"
    local timeout=1800 # 30 minutes in seconds (30 * 60)
    local interval=10  # Check every 10 seconds

    # Initail check to see if the file exists
    if [ -f "$file_path" ]; then
        return 0
    fi

    echo "Checking for file: $file_path..."

    # Initialize Bash's builtin SECONDS counter
    SECONDS=0

    # Loop until the file exists or the 30-minute timeout is reached
    until [ -f "$file_path" ] || (( SECONDS >= timeout )); do
        sleep "$interval"
        echo "Still waiting... ($((SECONDS))s elapsed)"
    done

    # Final check to see if the file exists or if we timed out
    if [ -f "$file_path" ]; then
        echo "Success! File '$file_path' is ready."
        return 0
    else
        echo "Error: File '$file_path' was not produced within 30 minutes."
        return 1
    fi
}

case "${step}" in
    config)
	mamba activate ${EAGLEhome}/conda/envs/anemoi
	make config compose=base:nested:${MACHINE_ID}:nrt-nested > nrt-composed.yaml
        sed -i "s?/path/to/eagle?${EAGLEhome}?g" nrt-composed.yaml
	sed -i "s|experiment_name: default|experiment_name: \'${expname}\'|g" nrt-composed.yaml
	make realize config=nrt-composed.yaml > nrt.yaml
	mamba deactivate
        ;;
    data)
	mamba activate ${EAGLEhome}/conda/envs/data
        make data config=nrt.yaml
	mamba deactivate
        ;;
    inference)
	# Check if training is done:
	#if [[ ! -f "${EAGLEhome}/run/${expname}/training/runscript.training.done" ]]; then
        #    echo "Training is not done, need to run ${BASH_SOURCE[0]} -n ${expname} -s training"
        #    echo "Then wait and re-run when training is done."
        #    exit 15
        #fi
	mamba activate ${EAGLEhome}/conda/envs/anemoi
        make inference config=nrt.yaml
	mamba deactivate
        ;;
    veri*)
	# Check if training is done:
	if [[ ! -f "${EAGLEhome}/run/${expname}/inference/runscript.inference.done" ]]; then
            echo "Inference is not done, need to run ${BASH_SOURCE[0]} -n ${expname} -s inference"
            echo "Then wait and re-run when inference is done."
            exit 16
        fi
	mamba activate ${EAGLEhome}/conda/envs/wxvx
	for kind in grid obs
        do
            for region in global lam
            do
                make vx-${kind}-${region} config=nrt.yaml &
            done
        done
        wait
	mamba deactivate
        ;;
    visu*)
	mamba activate ${EAGLEhome}/conda/envs/visualization
	for kind in grid obs
        do
            for region in global lam
            do
                make vis-${kind}-${region} config=nrt.yaml &
            done
        done
	wait
	mamba deactivate
        ;;
    all)
	# config
	mamba activate ${EAGLEhome}/conda/envs/anemoi
        make config compose=base:nested:${MACHINE_ID}:nrt > nrt-composed.yaml
        sed -i "s?/path/to/eagle/src?${EAGLEhome}?g" nrt-composed.yaml
	sed -i "s|experiment_name: default|experiment_name: \'${expname}\'|g" nrt-composed.yaml
	make realize config=nrt-composed.yaml > nrt.yaml
	mamba deactivate

        # prepare data
	mamba activate ${EAGLEhome}/conda/envs/data
        make data config=nrt.yaml
	mamba deactivate
        
        # inference
	mamba activate ${EAGLEhome}/conda/envs/inference
        make inference config=nrt.yaml
	mamba deactivate

        # verification
        # PREV_TIME=$(date -u -d "6 hours ago" +%Y%m%d%H)
        # echo "The target timestamp is: $PREV_TIME"
	nrt_inference_dir="${EAGLEhome}/run/${expname}/nrt_inference"
        # --- 1. HANDLE YEAR ---
        years=( ${nrt_inference_dir}/* )
        year=$(basename "${years[-1]}")
        # --- 2. HANDLE MONTH ---
        months=( ${nrt_inference_dir}/${year}/* )
        month=$(basename "${months[-1]}")
        # --- 3. HANDLE DAY ---
        days=( ${nrt_inference_dir}/${year}/${month}/* )
        day=$(basename "${days[-1]}")
        # --- 4. HANDLE HOUR ---
        hours=( ${nrt_inference_dir}/${year}/${month}/${day}/* )
        hour=$(basename "${hours[-1]}")

	nrtworkdir=${nrt_inference_dir}/${year}/${month}/${day}/${hour}/inference
	runscript=${nrtworkdir}/runscript.inference
        done_file=${runscript}.done
        wait_for_file ${done_file}
	if [[ -f ${runscript} ]] && [[ ! -f ${done_file} ]]; then
            sbatch ${runscript}
	    wait_for_file ${done_file}
        fi

	mamba activate ${EAGLEhome}/conda/envs/wxvx
	for kind in grid obs
        do
            for region in global lam
            do
                make vx-${kind}-${region} config=nrt.yaml &
            done
        done
        wait

	# re-check output data
	vxdir==${nrt_inference_dir}/${year}/${month}/${day}/${hour}/vx
	for kind in grid obs
        do
            for region in global lam
            do
                vxscript=${vxdir}/runscript.wxvx-grid2${kind}-${region}
		if [[ -f ${vxscript} ]] && [[ ! -f ${vxdir}/surface_pressure.nc ]]; then
                    sbatch ${vxscript}
                    wait_for_file ${vxdir}/surface_pressure.nc
		fi
            done
        done
        wait
	mamba deactivate

        # visualization
	mamba activate ${EAGLEhome}/conda/envs/visualization
	for kind in grid obs
        do
            for region in global lam
            do
                make vis-${kind}-${region} config=nrt.yaml &
            done
        done
	wait
	mamba deactivate
        ;;
    *)
        echo "Unrecognized step: ${step}"
        ;;
esac

exit 0


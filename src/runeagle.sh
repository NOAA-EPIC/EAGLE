#!/usr/bin/env bash

# default setting
EAGLEhome=`pwd`
MACHINE_ID=ursa
#expname=default
expname="wei_learning_main"
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

#set +u

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

# Example of how to use it:
# wait_for_file "/path/to/your/file.txt"

case "${step}" in
    env|devenv)
        if [[ -f "${EAGLEhome}/conda/bin/mamba" ]]; then
            echo "Conda env already install....."
            # Prompt the user (-n 1 limits input to exactly 1 character, -r prevents backslash escapes)
            read -n 1 -r -p "Do you want to overwrite? (y/n): " response
            echo "" # Prints a clean newline after the user keypress

            case "${response}" in
                [Yy])
                    echo "Proceeding to overwrite..."
                    ;;
                [Nn]|*)
                    echo "Stop signal received. Exiting script."
                    exit 11
                    ;;
            esac
        fi

        mamba activate /scratch5/purged/Wei.Huang/src/EAGLE/src/conda/envs/anemoi
        make env cudascript=${MACHINE_ID}
        ;;
    config)
        mamba activate /scratch5/purged/Wei.Huang/src/EAGLE/src/conda/envs/anemoi
        make config compose=base:nested:${MACHINE_ID} > eagle.yaml
        sed -i "s?/path/to/eagle/src?${EAGLEhome}?g" eagle.yaml
        sed -i "s|experiment_name: default|experiment_name: \'${expname}\'|g" eagle.yaml
        sed -i "s?/path/to/checkpoint?'{{ app.rundir }}/checkpoint'?g" eagle.yaml
        ;;
    data)
	mamba activate ${EAGLEhome}/conda/envs/data
        make data config=eagle.yaml
        ;;
    training)
	# Check if training data are ready:
	if [[ ! -f "${EAGLEhome}/run/${expname}/data/runscript.zarr-gfs.done" ]] || \
           [[ ! -f "${EAGLEhome}/run/${expname}/data/runscript.zarr-hrrr.done" ]]; then
            echo "Training data are not ready, need to run ${BASH_SOURCE[0]} -n ${expname} -s data"
            echo "Then wait and check data are available."
            exit 14
        fi
	mamba activate ${EAGLEhome}/conda/envs/training
        make training config=eagle.yaml
        ;;
    inference)
	# Check if training is done:
	if [[ ! -f "${EAGLEhome}/run/${expname}/training/runscript.training.done" ]]; then
            echo "Training is not done, need to run ${BASH_SOURCE[0]} -n ${expname} -s training"
            echo "Then wait and re-run when training is done."
	    squeue -u $USER
            exit 15
        fi
	mamba activate ${EAGLEhome}/conda/envs/inference
        make inference config=eagle.yaml
        ;;
    veri*)
	# Check if inference is done:
	if [[ ! -f "${EAGLEhome}/run/${expname}/inference/runscript.inference.done" ]]; then
            echo "Inference is not done, need to run ${BASH_SOURCE[0]} -n ${expname} -s inference"
            echo "Then wait and re-run when inference is done."
	    squeue -u $USER
            exit 16
        fi
	mamba activate ${EAGLEhome}/conda/envs/wxvx
	for kind in grid obs
	do
	    for region in global lam
	    do
                make vx-${kind}-${region} config=eagle.yaml &
            done
        done
	wait
        mamba deactivate
	;;
    visu*)
	# re-check if verifications are done:
        mamba activate ${EAGLEhome}/conda/envs/wxvx
	for kind in grid obs
	do
	    for region in global lam
	    do
	        script="${EAGLEhome}/run/${expname}/vx/grid2${kind}/${region}/runscript.wxvx-grid2${kind}-${region}"
                done_file="${script}.done"
	        if [[ -f "${script}" ]] && [[ ! -f "${done_file}" ]]; then
                    sbatch ${script}
		    wait_for_file "${done_file}" &
                fi
            done
        done
	wait
        mamba deactivate

	mamba activate ${EAGLEhome}/conda/envs/visualization
	for kind in grid obs
	do
	    for region in global lam
	    do
                make vis-${kind}-${region} config=eagle.yaml &
            done
        done
	wait
        mamba deactivate
        ;;
    all)
	# 1. setup env
	if [[ -f "${EAGLEhome}/conda/bin/mamba" ]]; then
	    echo "Conda env already install....."
	    # Prompt the user (-n 1 limits input to exactly 1 character, -r prevents backslash escapes)
            read -n 1 -r -p "Do you want to overwrite? (y/n): " response
	    echo "" # Prints a clean newline after the user keypress

	    case "${response}" in
    	        [Yy])
        	    echo "Proceeding to overwrite..."
                    mamba activate /scratch5/purged/Wei.Huang/src/EAGLE/src/conda/envs/anemoi
                    make env cudascript=${MACHINE_ID}
	            mamba deactivate
        	    ;;
    	        [Nn]|*)
        	    echo "Continue to config..."
        	    ;;
	    esac
        else
            mamba activate /scratch5/purged/Wei.Huang/src/EAGLE/src/conda/envs/anemoi
            make env cudascript=${MACHINE_ID}
	    mamba deactivate
        fi

        # 2. config
        mamba activate /scratch5/purged/Wei.Huang/src/EAGLE/src/conda/envs/anemoi
        make config compose=base:nested:${MACHINE_ID} > eagle.yaml
        sed -i "s?/path/to/eagle/src?${EAGLEhome}?g" eagle.yaml
        sed -i "s|experiment_name: default|experiment_name: \'${expname}\'|g" eagle.yaml
        sed -i "s?/path/to/checkpoint?'{{ app.rundir }}/checkpoint'?g" eagle.yaml
	mamba deactivate

        # 3. prepare data
	mamba activate ${EAGLEhome}/conda/envs/data
        make data config=eagle.yaml
	mamba deactivate

        # 4. training
	nwait=0
	while [[ ! -f "${EAGLEhome}/run/${expname}/data/runscript.zarr-gfs.done" ]] || \
              [[ ! -f "${EAGLEhome}/run/${expname}/data/runscript.zarr-hrrr.done" ]]; do
            echo "Training data are not ready, waiting..."
            sleep 30
            nwait=$(( nwait+1 ))
	    if [[ "${nwait}" -ge 60 ]]; then
                 echo "Waited to long for training data. quit..."
		 exit 22
            fi
        done
	mamba activate ${EAGLEhome}/conda/envs/training
        make training config=eagle.yaml
	mamba deactivate

        # 5. inference
	nwait=0
	while [[ ! -f "${EAGLEhome}/run/${expname}/training/runscript.training.done" ]]; do
            echo "Waiting for training..."
            sleep 30
            nwait=$(( nwait+1 ))
	    if [[ "${nwait}" -ge 60 ]]; then
                 echo "Waited to long for training. quit..."
		 exit 23
            fi
        done
	mamba activate ${EAGLEhome}/conda/envs/inference
        make inference config=eagle.yaml
	mamba deactivate

        # 6. Verification
	nwait=0
	while [[ ! -f "${EAGLEhome}/run/${expname}/inference/runscript.inference.done" ]]; do
            echo "Waiting for inference..."
            sleep 30
            nwait=$(( nwait+1 ))
	    if [[ "${nwait}" -ge 60 ]]; then
                 echo "Waited to long for inference. quit..."
		 exit 24
            fi
        done
	mamba activate ${EAGLEhome}/conda/envs/wxvx
	for kind in grid obs
	do
	    for region in global lam
	    do
                make vx-${kind}-${region} config=eagle.yaml &
            done
        done
	wait
	# re-check verification
	for kind in grid obs
	do
	    for region in global lam
	    do
	        script="${EAGLEhome}/run/${expname}/vx/grid2${kind}/${region}/runscript.wxvx-grid2${kind}-${region}"
                done_file="${script}.done"
	        if [[ -f "${script}" ]] && [[ ! -f "${done_file}" ]]; then
                    sbatch ${script}
		    wait_for_file "${done_file}" &
                fi
            done
        done
	wait
	mamba deactivate
       
        # 7. visualization
	mamba activate ${EAGLEhome}/conda/envs/visualization
	for kind in grid obs
	do
	    for region in global lam
	    do
                make vis-${kind}-${region} config=eagle.yaml &
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


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

        set +u
        echo "Activating anemoi environment..."
        mamba activate /scratch5/purged/Wei.Huang/src/EAGLE/src/conda/envs/anemoi
        # Re-enable strict checking for the rest of your EAGLE script steps
        set -u
        make env cudascript=${MACHINE_ID}
        ;;
    config)
        set +u
        echo "Activating anemoi environment..."
        mamba activate /scratch5/purged/Wei.Huang/src/EAGLE/src/conda/envs/anemoi
        # Re-enable strict checking for the rest of your EAGLE script steps
        set -u
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
            exit 15
        fi
	mamba activate ${EAGLEhome}/conda/envs/inference
        make inference config=eagle.yaml
        ;;
    veri*)
	# Check if training is done:
	if [[ ! -f "${EAGLEhome}/run/${expname}/inference/runscript.inference.done" ]]; then
            echo "Inference is not done, need to run ${BASH_SOURCE[0]} -n ${expname} -s inference"
            echo "Then wait and re-run when inference is done."
            exit 16
        fi
	mamba activate ${EAGLEhome}/conda/envs/wxvx
        make vx-grid-global config=eagle.yaml &
        make vx-grid-lam config=eagle.yaml &
        make vx-obs-global config=eagle.yaml &
        make vx-obs-lam config=eagle.yaml &
	wait
        ;;
    visu*)
	mamba activate ${EAGLEhome}/conda/envs/visualization
        make vis-grid-global config=eagle.yaml &
        make vis-grid-lam config=eagle.yaml &
        make vis-obs-global config=eagle.yaml &
        make vis-obs-lam config=eagle.yaml &
	wait
        ;;
    all)
	# 1. setup env
	if [[ -f "${EAGLEhome}/conda/bin/mamba" ]]; then
	    echo "Conda env already install....."
	    # Prompt the user (-n 1 limits input to exactly 1 character, -r prevents backslash escapes)
	    read -n 1 -r "Do you want to overwrite? (y/n): " response
	    echo "" # Prints a clean newline after the user keypress

	    case "${response}" in
    	        [Yy])
        	    echo "Proceeding to overwrite..."
                    set +u
                    echo "Activating anemoi environment..."
                    mamba activate /scratch5/purged/Wei.Huang/src/EAGLE/src/conda/envs/anemoi
                    set -u
                    make env cudascript=${MACHINE_ID}
	            mamba deactivate
        	    ;;
    	        [Nn]|*)
        	    echo "Continue to config..."
        	    ;;
	    esac
        else
            set +u
            echo "Activating anemoi environment..."
            mamba activate /scratch5/purged/Wei.Huang/src/EAGLE/src/conda/envs/anemoi
            set -u
            make env cudascript=${MACHINE_ID}
	    mamba deactivate
        fi

        # 2. config
        # Save state or turn off strict unbound variable checking
        set +u
        echo "Activating anemoi environment..."
        mamba activate /scratch5/purged/Wei.Huang/src/EAGLE/src/conda/envs/anemoi
        # Re-enable strict checking for the rest of your EAGLE script steps
        set -u
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
        make vx-grid-global config=eagle.yaml &
        make vx-grid-lam config=eagle.yaml &
        make vx-obs-global config=eagle.yaml &
        make vx-obs-lam config=eagle.yaml &
	wait
	mamba deactivate
       
        # 7. visualization
	nwait=0
	while [[ ! -f "${EAGLEhome}/run/${expname}/vx/grid2grid/global/runscript.wxvx-grid2grid-global.done" ]] || \
              [[ ! -f "${EAGLEhome}/run/${expname}/vx/grid2grid/lam/runscript.wxvx-grid2grid-lam.done" ]] || \
              [[ ! -f "${EAGLEhome}/run/${expname}/vx/grid2obs/global/runscript.wxvx-grid2obs-global.done" ]] || \
              [[ ! -f "${EAGLEhome}/run/${expname}/vx/grid2obs/lam/runscript.wxvx-grid2obs-lam.done" ]]; do
            echo "Waiting for verification..."
            sleep 30
            nwait=$(( nwait+1 ))
	    if [[ "${nwait}" -ge 60 ]]; then
                 echo "Waited to long for verification. quit..."
		 exit 25
            fi
        done
	mamba activate ${EAGLEhome}/conda/envs/visualization
        make vis-grid-global config=eagle.yaml &
        make vis-grid-lam config=eagle.yaml &
        make vis-obs-global config=eagle.yaml &
        make vis-obs-lam config=eagle.yaml &
	wait
        ;;
    *)
        echo "Unrecognized step: ${step}"
        ;;
esac

exit 0


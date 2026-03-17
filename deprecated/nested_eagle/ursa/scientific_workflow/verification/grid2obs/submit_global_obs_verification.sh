#!/bin/bash
#SBATCH -J nested_eagle_obs_verification
#SBATCH -o slurm/global_erification.%j.out
#SBATCH -e slurm/global_verification.%j.err
#SBATCH --account=epic
#SBATCH --partition=u1-service
#SBATCH --mem=128g
#SBATCH -t 30:00
#SBATCH --nodes=1
#SBATCH --ntasks=1

# shellcheck disable=SC1091
source /scratch4/NAGAPE/epic/role-epic/miniconda/bin/activate
conda activate wxvx

export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
export WORKDIR_BASE_PATH=$PWD

sed -i "/^.*workdir:.*$/c\  workdir: $WORKDIR_BASE_PATH\/wxvx_workdir\/global" wxvx_global.yaml

wxvx -c wxvx_global.yaml -t plots

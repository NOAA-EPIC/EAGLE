#!/bin/bash
#SBATCH -J nested_eagle_grid_verification
#SBATCH -o slurm/verification.%j.out
#SBATCH -e slurm/verification.%j.err
#SBATCH --account=epic
#SBATCH --partition=u1-service
#SBATCH --mem=128g
#SBATCH -t 01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=4

# shellcheck disable=SC1091
source /scratch4/NAGAPE/epic/role-epic/miniconda/bin/activate
conda activate wxvx

export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH
export WORKDIR_BASE_PATH=$PWD

sed -i "/^.*workdir:.*$/c\  workdir: $WORKDIR_BASE_PATH\/wxvx_workdir\/lam" wxvx_lam.yaml
sed -i "/^.*workdir:.*$/c\  workdir: $WORKDIR_BASE_PATH\/wxvx_workdir\/global" wxvx_global.yaml

srun wxvx -c wxvx_lam.yaml -t plots
srun wxvx -c wxvx_global.yaml -t plots

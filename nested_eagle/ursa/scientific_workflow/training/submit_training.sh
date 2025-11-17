#!/bin/bash
#SBATCH -J nested_eagle_training
#SBATCH -o slurm/training.%j.out
#SBATCH -e slurm/training.%j.err
#SBATCH --nodes=1
#SBATCH --account=epic
#SBATCH -t 03:00:00
#SBATCH --partition=u1-h100
#SBATCH --gres=gpu:h100:1
#SBATCH --mem=128g
#SBATCH --qos=gpuwf
#SBATCH --ntasks-per-node=1

# shellcheck disable=SC1091
source /scratch4/NAGAPE/epic/role-epic/miniconda/bin/activate
conda activate eagle
module load openmpi cuda gcc

export SLURM_GPUS_PER_NODE=1
export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

anemoi-training train --config-name=config

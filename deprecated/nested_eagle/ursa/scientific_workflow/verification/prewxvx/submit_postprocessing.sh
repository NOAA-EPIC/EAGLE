#!/bin/bash
#SBATCH -J nested_eagle_postprocessing
#SBATCH -o slurm/postprocessing.%j.out
#SBATCH -e slurm/postprocessing.%j.err
#SBATCH --account=epic
#SBATCH --partition=u1-service
#SBATCH --mem=128g
#SBATCH -t 30:00
#SBATCH --nodes=1
#SBATCH --ntasks=1

# shellcheck disable=SC1091
source /scratch4/NAGAPE/epic/role-epic/miniconda/bin/activate
conda activate eagle

export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

eagle-tools prewxvx postprocess_global.yaml

eagle-tools prewxvx postprocess_lam.yaml

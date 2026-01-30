#!/bin/bash
#SBATCH -J nested_eagle_hrrr_preprocessing
#SBATCH -o slurm/hrrr_preprocessing.%j.out
#SBATCH -e slurm/hrrr_preprocessing.%j.err
#SBATCH --account=epic
#SBATCH --partition=u1-service
#SBATCH --mem=128g
#SBATCH --nodes=1
#SBATCH --ntasks=15
#SBATCH --cpus-per-task=1
#SBATCH --time=30:00

# shellcheck disable=SC1091
source /scratch4/NAGAPE/epic/role-epic/miniconda/bin/activate
conda activate eagle
module load openmpi gcc

export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

srun ufs2arco hrrr.yaml --overwrite

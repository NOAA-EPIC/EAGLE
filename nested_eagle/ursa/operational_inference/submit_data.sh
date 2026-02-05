#!/bin/bash

#SBATCH -J datap
#SBATCH -o data/slurm.out
#SBATCH -e data/slurm.err
#SBATCH --account=epic
#SBATCH --partition=u1-service
#SBATCH --mem=128g
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=10:00

source /scratch4/NAGAPE/epic/Mariah.Pope/conda/bin/activate
conda activate ufs2arco_dev
module load openmpi gcc

python prepare_configs.py

ufs2arco gfs.yaml

ufs2arco hrrr.yaml

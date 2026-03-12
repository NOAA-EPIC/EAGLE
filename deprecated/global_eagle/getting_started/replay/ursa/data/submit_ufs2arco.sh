#!/bin/bash

#SBATCH -J data
#SBATCH -o logs/preprocessing.out
#SBATCH -e logs/preprocessing.err
#SBATCH --account=enter_your_account
#SBATCH --partition=u1-service
#SBATCH --mem=128g
#SBATCH -t 01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=4
#SBATCH --cpus-per-task=1

#export OMP_NUM_THREADS=2  # this line is unessesary right now, but you may need if you change mpi things.

source /pathtoyourminiconda3/miniconda3/bin/activate
module load openmpi
conda activate anemoi

srun ufs2arco replay.yaml --overwrite

echo "Training dataset is complete"

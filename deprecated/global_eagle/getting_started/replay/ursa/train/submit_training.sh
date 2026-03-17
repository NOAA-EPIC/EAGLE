#!/bin/bash

#SBATCH -J replay_training
#SBATCH -o slurm/training.out
#SBATCH -e slurm/training.err
#SBATCH --nodes=1
#SBATCH --account=enteraccount
#SBATCH -t 01:00:00
#SBATCH --partition=u1-h100
#SBATCH --gres=gpu:h100:1
#SBATCH --mem=96g
#SBATCH --qos=gpuwf

source /enterpathtominiconda/miniconda3/bin/activate
conda activate anemoi
module load openmpi
module load cuda

export SLURM_GPUS_PER_NODE=1

srun anemoi-training train --config-name=config.yaml

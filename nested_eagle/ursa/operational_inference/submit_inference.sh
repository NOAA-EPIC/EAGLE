#!/bin/bash

#SBATCH -J inference
#SBATCH -o inference/slurm.out
#SBATCH -e inference/slurm.err
#SBATCH --nodes=1
#SBATCH --account=gpu-ai4wp
#SBATCH -t 00:10:00
#SBATCH --partition=u1-h100
#SBATCH --gres=gpu:h100:1
#SBATCH --mem=64g
#SBATCH --qos=gpu

source /scratch4/NAGAPE/epic/role-epic/miniconda/bin/activate
conda activate eagle
module load cuda

eagle-tools inference inference.yaml

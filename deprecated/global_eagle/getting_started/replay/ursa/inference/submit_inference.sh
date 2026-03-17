#!/bin/bash

#SBATCH -J inference
#SBATCH -o inference.out
#SBATCH -e inference.err
#SBATCH --nodes=1
#SBATCH --account=enteraccount
#SBATCH -t 10:00
#SBATCH --partition=u1-h100
#SBATCH --gres=gpu:h100:1
#SBATCH --mem=96g
#SBATCH --qos=gpuwf

source /enterpathtominiconda/miniconda3/bin/activate
conda activate anemoi
module load cuda
anemoi-inference run inference_config.yaml

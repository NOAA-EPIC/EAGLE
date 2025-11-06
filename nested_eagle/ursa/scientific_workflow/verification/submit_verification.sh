#!/bin/bash

<<<<<<< HEAD:nested_eagle/ursa/scientific_workflow/validation/submit_verification.sh
<<<<<<<< HEAD:nested_eagle/ursa/scientific_workflow/verification/submit_verification.sh
#SBATCH -J nested_eagle_verification 
#SBATCH -o slurm/verification.%j.out
#SBATCH -e slurm/verification.%j.err
========
#SBATCH -J perform_postprocessing
#SBATCH -o slurm-%j.out
#SBATCH -e slurm-%j.err
>>>>>>>> 8a4c16f2046b03ca8ec5cc53b4e9a2eabc4dfdae:nested_eagle/ursa/scientific_workflow/verification/submit_postprocessing.sh
=======
#SBATCH -J perform_verification 
#SBATCH -o slurm-%j.out
#SBATCH -e slurm-%j.err
>>>>>>> 8a4c16f2046b03ca8ec5cc53b4e9a2eabc4dfdae:nested_eagle/ursa/scientific_workflow/verification/submit_verification.sh
#SBATCH --account=epic
#SBATCH --partition=u1-service
#SBATCH --mem=128g
#SBATCH -t 01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1

source /scratch4/NAGAPE/epic/role-epic/miniconda/bin/activate

export LD_LIBRARY_PATH=$CONDA_PREFIX/lib:$LD_LIBRARY_PATH

<<<<<<< HEAD:nested_eagle/ursa/scientific_workflow/validation/submit_verification.sh
conda activate eagle 

python postprocess.py
=======
export WORKDIR_BASE_PATH=$PWD

sed -i "/^.*workdir:.*$/c\  workdir: $WORKDIR_BASE_PATH\/wxvx_workdir\/lam" wxvx_lam.yaml

sed -i "/^.*workdir:.*$/c\  workdir: $WORKDIR_BASE_PATH\/wxvx_workdir\/global" wxvx_global.yaml

conda activate wxvx 

wxvx -c wxvx_lam.yaml -t plots

wxvx -c wxvx_global.yaml -t plots
>>>>>>> 8a4c16f2046b03ca8ec5cc53b4e9a2eabc4dfdae:nested_eagle/ursa/scientific_workflow/verification/submit_verification.sh

#!/bin/bash
#SBATCH -J diff_var_plots
#SBATCH -o slurm/diff_plots.%j.out
#SBATCH -e slurm/diff_plots.%j.err
#SBATCH --account=epic
#SBATCH --partition=u1-service
#SBATCH --mem=128g
#SBATCH -t 00:30:00
#SBATCH --nodes=1
#SBATCH --ntasks=1

set -euo pipefail

mkdir -p slurm

# shellcheck disable=SC1091
source /scratch4/NAGAPE/epic/role-epic/miniconda/bin/activate
conda activate wxvx

export LD_LIBRARY_PATH="$CONDA_PREFIX/lib:${LD_LIBRARY_PATH:-}"

# run from the directory where you submitted (so relative paths work)
cd "$SLURM_SUBMIT_DIR"

python plot_wxvx_stats_var.py --pattern "*pairs.nc" --add_states
# python plot_wxvx_stats_var.py --pattern "*pairs.nc" --vmin -2 --vmax 2 --add_states

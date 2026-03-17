DATA_PATH=$1
OUTPUT_DIR=$2

echo "Input data: $DATA_PATH"
echo "Directory for output files: $OUTPUT_DIR"

mkdir -p /workdir/data
mkdir -p /workdir/training_output

# Symlinks so we can connect with data within blob storage
ln -s "$DATA_PATH" /workdir/data/replay.zarr
ln -s "$OUTPUT_DIR" /workdir/training_output/

export WORLD_SIZE=1
export ANEMOI_BASE_SEED=1000
export SLURM_GPUS_PER_NODE=1
export SLURM_NNODES=1
export RANK=0

anemoi-training train --config-name=config.yaml

cp -R /workdir/training_output/* $OUTPUT_DIR
echo "Model output saved to: $OUTPUT_DIR"

# TODO: This should formally log within azureml.
# As of right now, we are just saving everything to blob storage and loading it from there later.
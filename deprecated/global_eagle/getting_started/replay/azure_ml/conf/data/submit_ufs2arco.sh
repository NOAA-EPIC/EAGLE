OUTPUT_BLOB=$1
OUTPUT_PATH=$2
OUTPUT_ZARR=$3

echo "Output blob directory: $OUTPUT_BLOB"
echo "Output path: $OUTPUT_PATH"
echo "Output zarr: $OUTPUT_ZARR"

mkdir -p $OUTPUT_PATH
ln -s $OUTPUT_BLOB "$OUTPUT_PATH/$OUTPUT_ZARR"

mpirun --allow-run-as-root -np 8 ufs2arco replay.yaml

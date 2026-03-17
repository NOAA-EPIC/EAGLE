INPUT_ZARR=$1
OUTPUT_DIR=$2

echo "Input zarr: $INPUT_ZARR"
echo "Directory for output files: $OUTPUT_DIR"

mkdir -p /replay/verification

ln -s "$OUTPUT_DIR" /replay/verification

echo "Starting post-processing"
python postprocess.py $INPUT_ZARR

echo "Starting verification"
wxvx -c wxvx_config.yaml -t plots

cp -R /replay/verification/* $OUTPUT_DIR
echo "wxvx output saved to: $OUTPUT_DIR"

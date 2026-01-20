#!/bin/bash
# Setup script for downloading and processing the DREAMS dataset from Zenodo
#
# This script automates the complete pipeline:
# 1. Downloads DREAMS dataset from Zenodo (record 2650142)
# 2. Converts EDF files to HDF5 format
# 3. Creates train/val/test splits
#
# Usage:
#   ./setup_dreams_dataset.sh [output_base_dir]
#
# Example:
#   ./setup_dreams_dataset.sh ./data/dreams

set -e  # Exit on error

# Default output directory
OUTPUT_BASE_DIR="${1:-./data/dreams}"
RAW_DATA_DIR="${OUTPUT_BASE_DIR}/raw"
PROCESSED_DATA_DIR="${OUTPUT_BASE_DIR}/processed"

echo "==============================================="
echo "DREAMS Dataset Setup Pipeline"
echo "==============================================="
echo ""
echo "Output directories:"
echo "  Raw data:       ${RAW_DATA_DIR}"
echo "  Processed data: ${PROCESSED_DATA_DIR}"
echo ""

# Step 1: Download dataset
echo "Step 1/3: Downloading DREAMS dataset from Zenodo..."
echo "---------------------------------------------------"
python download_zenodo_data.py \
    --record_id 2650142 \
    --output_dir "${RAW_DATA_DIR}"

echo ""
echo "Download complete!"
echo ""

# Step 2: Scan dataset structure
echo "Step 2/3: Scanning dataset structure..."
echo "---------------------------------------------------"
python process_dreams_data.py \
    --input_dir "${RAW_DATA_DIR}" \
    --output_dir "${PROCESSED_DATA_DIR}" \
    --scan_only

echo ""

# Step 3: Convert and create splits
echo "Step 3/3: Converting EDF to HDF5 and creating splits..."
echo "---------------------------------------------------"
python process_dreams_data.py \
    --input_dir "${RAW_DATA_DIR}" \
    --output_dir "${PROCESSED_DATA_DIR}" \
    --convert \
    --create_splits \
    --resample_rate 256 \
    --num_threads 4

echo ""
echo "==============================================="
echo "Setup Complete!"
echo "==============================================="
echo ""
echo "Dataset ready for use with SleepFM!"
echo ""
echo "Files are located at:"
echo "  - HDF5 files: ${PROCESSED_DATA_DIR}/hdf5/"
echo "  - Splits:     ${PROCESSED_DATA_DIR}/dataset_splits.json"
echo ""
echo "To use this dataset in your config, set:"
echo "  data_path: '${PROCESSED_DATA_DIR}/hdf5/'"
echo "  split_path: '${PROCESSED_DATA_DIR}/dataset_splits.json'"
echo ""

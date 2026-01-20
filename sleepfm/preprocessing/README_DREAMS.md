# DREAMS Dataset Integration

This directory contains scripts to download and preprocess the **DREAMS (Database for REcording and Analysis of Multiple Sleep) dataset** from Zenodo for use with SleepFM.

The download script uses **zenodo_get**, a dedicated Python package for downloading Zenodo datasets, providing robust downloading with MD5 verification, retry logic, and resume capability.

## About the DREAMS Dataset

The DREAMS dataset ([Zenodo Record 2650142](https://zenodo.org/records/2650142)) contains polysomnographic (PSG) recordings collected during the DREAMS project funded by Région Wallonne (Belgium).

### Dataset Contents

1. **DREAMS Subjects Database**: 20 whole-night PSG recordings from healthy subjects
2. **DREAMS Patients Database**: 27 whole-night PSG recordings from patients with various pathologies
3. **DREAMS Artifacts Database**: 20 excerpts (15 minutes each) annotated for artifacts
4. **DREAMS Sleep Spindles Database**: 8 excerpts (30 minutes each) of central EEG channels

### Annotations

- Sleep stages according to both:
  - Rechtschaffen and Kales (R&K) criteria
  - American Academy of Sleep Medicine (AASM) standard
- Micro-events: sleep spindles, K-complexes, REM, PLM, apnea
- Artifacts annotations

### Technical Specifications

- Format: European Data Format (EDF)
- Acquisition: Digital 32-channel polygraph (Brainnet™ System, MEDATEC, Brussels)
- Source: Sleep laboratory of a Belgian hospital

## Prerequisites

### Install zenodo-get

The download script requires `zenodo-get`, a robust tool for downloading Zenodo datasets:

```bash
pip install zenodo-get
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

### Why zenodo-get?

We use `zenodo-get` instead of manual API calls because it provides:
- **MD5 verification**: Automatically verifies file integrity after download
- **Resume capability**: Can resume interrupted downloads
- **Retry logic**: Automatically retries failed downloads
- **Progress tracking**: Built-in progress bars for large downloads
- **Robust error handling**: Continues downloading other files if one fails
- **Community tested**: Widely used in the scientific community

## Quick Start

### Option 1: Automated Setup (Recommended)

Run the all-in-one setup script:

```bash
cd sleepfm/preprocessing
./setup_dreams_dataset.sh ./data/dreams
```

This will:
1. Download the complete DREAMS dataset from Zenodo
2. Convert EDF files to HDF5 format
3. Create train/validation/test splits

### Option 2: Step-by-Step Setup

#### Step 1: Download the Dataset

```bash
python download_zenodo_data.py \
    --record_id 2650142 \
    --output_dir ./data/dreams/raw
```

**Optional: Download only specific file types**

```bash
# Download only EDF files
python download_zenodo_data.py \
    --record_id 2650142 \
    --output_dir ./data/dreams/raw \
    --patterns "*.edf"
```

**Optional: List available files without downloading**

```bash
python download_zenodo_data.py \
    --record_id 2650142 \
    --output_dir ./data/dreams/raw \
    --list_only
```

#### Step 2: Scan Dataset Structure

```bash
python process_dreams_data.py \
    --input_dir ./data/dreams/raw \
    --output_dir ./data/dreams/processed \
    --scan_only
```

#### Step 3: Convert EDF to HDF5

```bash
python process_dreams_data.py \
    --input_dir ./data/dreams/raw \
    --output_dir ./data/dreams/processed \
    --convert \
    --resample_rate 256 \
    --num_threads 4
```

#### Step 4: Create Dataset Splits

```bash
python process_dreams_data.py \
    --input_dir ./data/dreams/raw \
    --output_dir ./data/dreams/processed \
    --create_splits \
    --train_ratio 0.7 \
    --val_ratio 0.15
```

## Using DREAMS with SleepFM

After processing, update your SleepFM config file to use the DREAMS dataset:

```yaml
# In your config YAML file
data_path: './data/dreams/processed/hdf5/'
split_path: './data/dreams/processed/dataset_splits.json'

# Other settings remain the same
sampling_freq: 256
sampling_duration: 5
# ...
```

## Directory Structure

After setup, your directory structure will look like:

```
data/dreams/
├── raw/
│   ├── metadata.json              # Zenodo record metadata
│   ├── *.edf                      # Raw PSG recordings
│   ├── *.txt                      # Annotation files
│   └── ...
└── processed/
    ├── hdf5/                      # Converted HDF5 files
    │   ├── recording1.hdf5
    │   ├── recording2.hdf5
    │   └── ...
    └── dataset_splits.json        # Train/val/test splits
```

## Script Reference

### download_zenodo_data.py

Downloads datasets from Zenodo using the `zenodo_get` package.

**Arguments:**
- `--record_id`: Zenodo record ID (default: 2650142)
- `--output_dir`: Output directory for downloaded files (required)
- `--patterns`: File patterns to download (e.g., `*.edf *.txt`)
- `--list_only`: List files without downloading
- `--no_verify_md5`: Skip MD5 checksum verification (faster but less safe)
- `--stop_on_error`: Stop if any file fails (default: continue on error)

**Features:**
- Automatic MD5 verification for data integrity
- Resume capability for interrupted downloads
- Parallel downloading where possible
- Detailed progress tracking
- Metadata saving for record information

### process_dreams_data.py

Processes downloaded DREAMS data for use with SleepFM.

**Arguments:**
- `--input_dir`: Input directory with raw DREAMS data (required)
- `--output_dir`: Output directory for processed files (required)
- `--resample_rate`: Target sampling rate in Hz (default: 256)
- `--num_threads`: Parallel threads for conversion (default: 4)
- `--scan_only`: Only scan dataset structure
- `--convert`: Convert EDF to HDF5
- `--create_splits`: Create train/val/test splits
- `--train_ratio`: Training set ratio (default: 0.7)
- `--val_ratio`: Validation set ratio (default: 0.15)

### setup_dreams_dataset.sh

All-in-one wrapper script that runs the complete pipeline.

**Usage:**
```bash
./setup_dreams_dataset.sh [output_base_dir]
```

## Requirements

The scripts use the following Python packages (included in requirements.txt):
- **zenodo-get** (>=2.0.0) - For downloading Zenodo datasets
- requests (>=2.31.0) - For API metadata fetching
- tqdm - Progress bars
- loguru - Logging
- h5py - HDF5 file operations
- numpy - Numerical operations
- pandas - Data manipulation
- pyedflib or mne - EDF file reading

Install all requirements:
```bash
pip install -r requirements.txt
```

## Citation

If you use the DREAMS dataset in your research, please cite:

```
Devuyst, S. (2019). The DREAMS Databases and Assessment Algorithm [Data set].
Zenodo. https://doi.org/10.5281/zenodo.2650142
```

## License

The DREAMS dataset is licensed under **Creative Commons Attribution Non Commercial No Derivatives 3.0 Unported**.

## Troubleshooting

### zenodo_get not found

If you get an error that `zenodo_get` is not installed:
```bash
pip install zenodo-get
# or
python -m pip install zenodo-get
```

### Download fails with network errors

`zenodo_get` has built-in retry logic, but if downloads continue to fail:
1. Check your internet connection
2. Try downloading without MD5 verification: `--no_verify_md5`
3. Use the `--stop_on_error` flag to identify problematic files
4. As a fallback, manually download from: https://zenodo.org/records/2650142

### Interrupted downloads

`zenodo_get` supports resume capability. Simply run the same command again, and it will skip already downloaded files and resume incomplete ones.

### Conversion errors

If you encounter errors during EDF to HDF5 conversion:
- Check that the EDF files are not corrupted
- Verify that all required channels are present
- Try processing with a single thread (`--num_threads 1`) for debugging

### Memory issues

If you run out of memory during processing:
- Reduce the number of parallel threads (`--num_threads 1`)
- Process files in smaller batches
- Increase system swap space

## Support

For issues related to:
- SleepFM model: Open an issue in the main repository
- DREAMS dataset: Visit the Zenodo record or contact the dataset authors
- These scripts: Open an issue with error logs and system information

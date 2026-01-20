#!/usr/bin/env python3
"""
Process DREAMS dataset for use with SleepFM.

This script preprocesses the downloaded DREAMS dataset by:
1. Converting EDF files to HDF5 format
2. Extracting and organizing sleep stage annotations
3. Creating dataset splits for training/validation/testing

The DREAMS dataset includes:
- DREAMS Subjects Database: 20 recordings from healthy subjects
- DREAMS Patients Database: 27 recordings from patients with pathologies
- Sleep stage annotations according to R&K and AASM standards
- Various micro-events (spindles, K-complexes, artifacts, etc.)

Usage:
    python process_dreams_data.py --input_dir ./data/dreams --output_dir ./data/dreams_processed
"""

import os
import argparse
import json
from pathlib import Path
from loguru import logger
from preprocessing import EDFToHDF5Converter
import glob
import pandas as pd


class DREAMSDataProcessor:
    """Processes the DREAMS dataset for use with SleepFM."""

    def __init__(self, input_dir, output_dir):
        """
        Initialize the DREAMS data processor.

        Args:
            input_dir: Directory containing downloaded DREAMS dataset
            output_dir: Directory to save processed HDF5 files
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def scan_dataset_structure(self):
        """
        Scan the DREAMS dataset to understand its structure.

        Returns:
            Dictionary with dataset information
        """
        logger.info("Scanning DREAMS dataset structure...")

        # Find all EDF files
        edf_files = list(self.input_dir.glob('**/*.edf'))
        logger.info(f"Found {len(edf_files)} EDF files")

        # Find annotation files (various formats)
        txt_files = list(self.input_dir.glob('**/*.txt'))
        csv_files = list(self.input_dir.glob('**/*.csv'))
        xml_files = list(self.input_dir.glob('**/*.xml'))

        logger.info(f"Found {len(txt_files)} TXT files")
        logger.info(f"Found {len(csv_files)} CSV files")
        logger.info(f"Found {len(xml_files)} XML files")

        # Organize by subdataset if directory structure exists
        dataset_info = {
            'edf_files': [str(f) for f in edf_files],
            'annotation_files': {
                'txt': [str(f) for f in txt_files],
                'csv': [str(f) for f in csv_files],
                'xml': [str(f) for f in xml_files]
            },
            'total_recordings': len(edf_files)
        }

        # Print file structure
        if edf_files:
            logger.info("\nSample EDF files:")
            for f in edf_files[:5]:
                logger.info(f"  {f.relative_to(self.input_dir)}")

        return dataset_info

    def convert_edf_to_hdf5(self, resample_rate=256, num_threads=4):
        """
        Convert EDF files to HDF5 format using the existing converter.

        Args:
            resample_rate: Target sampling rate in Hz
            num_threads: Number of parallel threads for conversion
        """
        logger.info(f"\nConverting EDF files to HDF5 format...")
        logger.info(f"Input directory: {self.input_dir}")
        logger.info(f"Output directory: {self.output_dir / 'hdf5'}")
        logger.info(f"Resample rate: {resample_rate} Hz")

        # Create HDF5 output directory
        hdf5_dir = self.output_dir / 'hdf5'
        hdf5_dir.mkdir(parents=True, exist_ok=True)

        # Use existing converter
        converter = EDFToHDF5Converter(
            root_dir=str(self.input_dir),
            target_dir=str(hdf5_dir),
            resample_rate=resample_rate,
            num_threads=num_threads
        )

        # Convert files
        logger.info(f"Found {len(converter.file_locations[0])} EDF files to convert")
        converter.convert_all()

        logger.success(f"Conversion complete! HDF5 files saved to: {hdf5_dir}")

    def create_dataset_splits(self, train_ratio=0.7, val_ratio=0.15, test_ratio=0.15):
        """
        Create train/val/test splits for the DREAMS dataset.

        Args:
            train_ratio: Proportion of data for training
            val_ratio: Proportion of data for validation
            test_ratio: Proportion of data for testing
        """
        logger.info("\nCreating dataset splits...")

        # Get all HDF5 files
        hdf5_dir = self.output_dir / 'hdf5'
        if not hdf5_dir.exists():
            logger.warning("HDF5 directory not found. Please run conversion first.")
            return

        hdf5_files = list(hdf5_dir.glob('**/*.hdf5')) + list(hdf5_dir.glob('**/*.h5'))

        if not hdf5_files:
            logger.warning("No HDF5 files found.")
            return

        logger.info(f"Found {len(hdf5_files)} HDF5 files")

        # Shuffle and split
        import numpy as np
        np.random.seed(42)
        indices = np.random.permutation(len(hdf5_files))

        n_train = int(len(hdf5_files) * train_ratio)
        n_val = int(len(hdf5_files) * val_ratio)

        train_indices = indices[:n_train]
        val_indices = indices[n_train:n_train + n_val]
        test_indices = indices[n_train + n_val:]

        # Create split dictionary
        splits = {
            'train': [str(hdf5_files[i].relative_to(hdf5_dir)) for i in train_indices],
            'val': [str(hdf5_files[i].relative_to(hdf5_dir)) for i in val_indices],
            'test': [str(hdf5_files[i].relative_to(hdf5_dir)) for i in test_indices]
        }

        # Save splits
        splits_path = self.output_dir / 'dataset_splits.json'
        with open(splits_path, 'w') as f:
            json.dump(splits, f, indent=2)

        logger.success(f"Dataset splits saved to: {splits_path}")
        logger.info(f"  Train: {len(splits['train'])} files ({train_ratio * 100:.0f}%)")
        logger.info(f"  Val:   {len(splits['val'])} files ({val_ratio * 100:.0f}%)")
        logger.info(f"  Test:  {len(splits['test'])} files ({test_ratio * 100:.0f}%)")

    def create_summary_report(self):
        """Create a summary report of the processed dataset."""
        logger.info("\n" + "=" * 60)
        logger.info("DREAMS Dataset Processing Summary")
        logger.info("=" * 60)

        # Check what files exist
        hdf5_dir = self.output_dir / 'hdf5'
        splits_file = self.output_dir / 'dataset_splits.json'

        if hdf5_dir.exists():
            hdf5_files = list(hdf5_dir.glob('**/*.hdf5')) + list(hdf5_dir.glob('**/*.h5'))
            logger.info(f"\nProcessed files: {len(hdf5_files)} HDF5 files")
            logger.info(f"Location: {hdf5_dir}")
        else:
            logger.warning("\nNo HDF5 files found. Conversion may not have completed.")

        if splits_file.exists():
            with open(splits_file, 'r') as f:
                splits = json.load(f)
            logger.info(f"\nDataset splits:")
            logger.info(f"  Train: {len(splits['train'])} files")
            logger.info(f"  Val:   {len(splits['val'])} files")
            logger.info(f"  Test:  {len(splits['test'])} files")
        else:
            logger.warning("\nDataset splits not created yet.")

        logger.info("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Process DREAMS dataset for SleepFM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Scan dataset structure
    python process_dreams_data.py --input_dir ./data/dreams --output_dir ./data/dreams_processed --scan_only

    # Convert EDF to HDF5
    python process_dreams_data.py --input_dir ./data/dreams --output_dir ./data/dreams_processed --convert

    # Create dataset splits
    python process_dreams_data.py --input_dir ./data/dreams --output_dir ./data/dreams_processed --create_splits

    # Full processing pipeline
    python process_dreams_data.py --input_dir ./data/dreams --output_dir ./data/dreams_processed --convert --create_splits
        """
    )

    parser.add_argument(
        '--input_dir',
        type=str,
        required=True,
        help='Input directory containing downloaded DREAMS dataset'
    )

    parser.add_argument(
        '--output_dir',
        type=str,
        required=True,
        help='Output directory for processed files'
    )

    parser.add_argument(
        '--resample_rate',
        type=int,
        default=256,
        help='Target sampling rate in Hz (default: 256)'
    )

    parser.add_argument(
        '--num_threads',
        type=int,
        default=4,
        help='Number of parallel threads for conversion (default: 4)'
    )

    parser.add_argument(
        '--scan_only',
        action='store_true',
        help='Only scan dataset structure without processing'
    )

    parser.add_argument(
        '--convert',
        action='store_true',
        help='Convert EDF files to HDF5 format'
    )

    parser.add_argument(
        '--create_splits',
        action='store_true',
        help='Create train/val/test splits'
    )

    parser.add_argument(
        '--train_ratio',
        type=float,
        default=0.7,
        help='Training set ratio (default: 0.7)'
    )

    parser.add_argument(
        '--val_ratio',
        type=float,
        default=0.15,
        help='Validation set ratio (default: 0.15)'
    )

    args = parser.parse_args()

    # Create processor
    processor = DREAMSDataProcessor(args.input_dir, args.output_dir)

    # Scan dataset
    dataset_info = processor.scan_dataset_structure()

    if args.scan_only:
        logger.info("\nScan complete. Use --convert to process files.")
        return

    # Convert EDF to HDF5
    if args.convert:
        processor.convert_edf_to_hdf5(
            resample_rate=args.resample_rate,
            num_threads=args.num_threads
        )

    # Create splits
    if args.create_splits:
        processor.create_dataset_splits(
            train_ratio=args.train_ratio,
            val_ratio=args.val_ratio,
            test_ratio=1.0 - args.train_ratio - args.val_ratio
        )

    # Create summary
    processor.create_summary_report()

    logger.success("\nProcessing complete!")


if __name__ == '__main__':
    main()

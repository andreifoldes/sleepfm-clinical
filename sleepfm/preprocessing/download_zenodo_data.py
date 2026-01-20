#!/usr/bin/env python3
"""
Download DREAMS dataset from Zenodo.

This script downloads the DREAMS Databases and Assessment Algorithm dataset
from Zenodo (record 2650142) using the zenodo_get package. The dataset contains
polysomnographic recordings in EDF format from healthy subjects and patients
with various pathologies.

Usage:
    python download_zenodo_data.py --output_dir ./data/dreams --record_id 2650142
"""

import os
import argparse
import subprocess
import sys
import json
from pathlib import Path
from loguru import logger
import requests


class ZenodoDownloader:
    """Downloads datasets from Zenodo using zenodo_get."""

    def __init__(self, record_id, output_dir):
        """
        Initialize the Zenodo downloader.

        Args:
            record_id: Zenodo record ID (e.g., 2650142 for DREAMS dataset)
            output_dir: Directory to save downloaded files
        """
        self.record_id = record_id
        self.output_dir = Path(output_dir)
        self.api_url = f"https://zenodo.org/api/records/{record_id}"

    def check_zenodo_get_installed(self):
        """Check if zenodo_get is installed."""
        try:
            result = subprocess.run(
                ['zenodo_get', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    def get_record_metadata(self):
        """Fetch metadata for the Zenodo record."""
        logger.info(f"Fetching metadata for Zenodo record {self.record_id}...")
        try:
            response = requests.get(self.api_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f"Could not fetch metadata: {e}")
            return None

    def download_dataset(self, file_patterns=None, continue_on_error=True, verify_md5=True):
        """
        Download all files from the Zenodo record using zenodo_get.

        Args:
            file_patterns: Optional list of file patterns to filter downloads
                          (e.g., ['*.edf', '*.txt']). If None, downloads all files.
            continue_on_error: Continue downloading even if some files fail
            verify_md5: Verify MD5 checksums after download
        """
        # Check if zenodo_get is installed
        if not self.check_zenodo_get_installed():
            logger.error("zenodo_get is not installed!")
            logger.info("Please install it with: pip install zenodo-get")
            logger.info("Or use: python -m pip install zenodo-get")
            sys.exit(1)

        # Get and display metadata
        metadata = self.get_record_metadata()
        if metadata:
            logger.info(f"\nDataset: {metadata['metadata']['title']}")
            logger.info(f"Description: {metadata['metadata']['description'][:200]}...")
            logger.info(f"DOI: {metadata['doi']}")
            logger.info(f"Number of files: {len(metadata['files'])}\n")

            # Save metadata
            self.output_dir.mkdir(parents=True, exist_ok=True)
            metadata_path = self.output_dir / 'metadata.json'
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            logger.info(f"Saved metadata to {metadata_path}\n")

        # Prepare zenodo_get command
        cmd = ['zenodo_get', self.record_id]

        # Add file patterns filter if specified
        if file_patterns:
            pattern_str = ','.join(file_patterns)
            cmd.extend(['-w', pattern_str])
            logger.info(f"Filtering files with patterns: {pattern_str}")

        # Add continue on error flag
        if continue_on_error:
            cmd.append('-e')

        # Add MD5 verification flag
        if verify_md5:
            cmd.append('-m')

        # Add output directory
        cmd.extend(['-o', str(self.output_dir)])

        # Log the command
        logger.info(f"Running: {' '.join(cmd)}\n")

        # Run zenodo_get
        try:
            result = subprocess.run(
                cmd,
                check=True,
                text=True,
                cwd=str(self.output_dir.parent)
            )

            logger.success(f"\nDownload complete! Files saved to: {self.output_dir}")

        except subprocess.CalledProcessError as e:
            logger.error(f"Download failed with exit code {e.returncode}")
            if not continue_on_error:
                sys.exit(1)
        except KeyboardInterrupt:
            logger.warning("\nDownload interrupted by user")
            sys.exit(1)

    def get_file_list(self):
        """Get a list of all files in the Zenodo record."""
        metadata = self.get_record_metadata()
        if metadata:
            return [f['key'] for f in metadata['files']]
        else:
            logger.error("Could not fetch file list")
            return []


def main():
    parser = argparse.ArgumentParser(
        description='Download DREAMS dataset from Zenodo using zenodo_get',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Download entire DREAMS dataset
    python download_zenodo_data.py --output_dir ./data/dreams

    # Download only EDF files
    python download_zenodo_data.py --output_dir ./data/dreams --patterns "*.edf"

    # Download specific file types
    python download_zenodo_data.py --output_dir ./data/dreams --patterns "*.edf" "*.txt"

    # List available files without downloading
    python download_zenodo_data.py --output_dir ./data/dreams --list_only

    # Download without MD5 verification (faster but less safe)
    python download_zenodo_data.py --output_dir ./data/dreams --no_verify_md5

Note:
    This script requires zenodo_get to be installed:
        pip install zenodo-get
        """
    )

    parser.add_argument(
        '--record_id',
        type=str,
        default='2650142',
        help='Zenodo record ID (default: 2650142 for DREAMS dataset)'
    )

    parser.add_argument(
        '--output_dir',
        type=str,
        required=True,
        help='Output directory for downloaded files'
    )

    parser.add_argument(
        '--patterns',
        type=str,
        nargs='+',
        help='File patterns to download (e.g., *.edf *.txt). Downloads all if not specified.'
    )

    parser.add_argument(
        '--list_only',
        action='store_true',
        help='Only list available files without downloading'
    )

    parser.add_argument(
        '--no_verify_md5',
        action='store_true',
        help='Skip MD5 checksum verification (faster but less safe)'
    )

    parser.add_argument(
        '--stop_on_error',
        action='store_true',
        help='Stop downloading if any file fails (default: continue on error)'
    )

    args = parser.parse_args()

    # Create downloader
    downloader = ZenodoDownloader(args.record_id, args.output_dir)

    if args.list_only:
        # Just list files
        logger.info(f"Files available in Zenodo record {args.record_id}:")
        files = downloader.get_file_list()
        if files:
            for i, filename in enumerate(files, 1):
                print(f"{i:3d}. {filename}")
        else:
            logger.error("Could not retrieve file list. Check your internet connection.")
    else:
        # Download dataset
        downloader.download_dataset(
            file_patterns=args.patterns,
            continue_on_error=not args.stop_on_error,
            verify_md5=not args.no_verify_md5
        )


if __name__ == '__main__':
    main()

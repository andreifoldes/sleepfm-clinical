#!/usr/bin/env python3
"""
Download DREAMS dataset from Zenodo.

This script downloads the DREAMS Databases and Assessment Algorithm dataset
from Zenodo (record 2650142). The dataset contains polysomnographic recordings
in EDF format from healthy subjects and patients with various pathologies.

Usage:
    python download_zenodo_data.py --output_dir ./data/dreams --record_id 2650142
"""

import os
import argparse
import requests
from tqdm import tqdm
import json
from pathlib import Path
from loguru import logger


class ZenodoDownloader:
    """Downloads datasets from Zenodo using their API."""

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

    def get_record_metadata(self):
        """Fetch metadata for the Zenodo record."""
        logger.info(f"Fetching metadata for Zenodo record {self.record_id}...")
        response = requests.get(self.api_url)

        if response.status_code != 200:
            raise Exception(f"Failed to fetch metadata: HTTP {response.status_code}")

        return response.json()

    def download_file(self, url, filepath, file_size=None):
        """
        Download a file with progress bar.

        Args:
            url: URL to download from
            filepath: Path to save the file
            file_size: Expected file size in bytes (for progress bar)
        """
        # Create parent directory if it doesn't exist
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Skip if file already exists
        if filepath.exists():
            logger.info(f"File already exists, skipping: {filepath.name}")
            return

        logger.info(f"Downloading {filepath.name}...")

        # Stream the download with progress bar
        response = requests.get(url, stream=True)
        response.raise_for_status()

        # Get file size from response if not provided
        if file_size is None:
            file_size = int(response.headers.get('content-length', 0))

        with open(filepath, 'wb') as f, tqdm(
            total=file_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
            desc=filepath.name
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    pbar.update(len(chunk))

        logger.success(f"Downloaded: {filepath.name}")

    def download_dataset(self, file_patterns=None):
        """
        Download all files from the Zenodo record.

        Args:
            file_patterns: Optional list of file patterns to filter downloads
                          (e.g., ['*.edf', '*.txt']). If None, downloads all files.
        """
        # Get metadata
        metadata = self.get_record_metadata()

        # Save metadata
        self.output_dir.mkdir(parents=True, exist_ok=True)
        metadata_path = self.output_dir / 'metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved metadata to {metadata_path}")

        # Print dataset information
        logger.info(f"\nDataset: {metadata['metadata']['title']}")
        logger.info(f"Description: {metadata['metadata']['description'][:200]}...")
        logger.info(f"DOI: {metadata['doi']}")
        logger.info(f"Number of files: {len(metadata['files'])}\n")

        # Download files
        for file_info in metadata['files']:
            filename = file_info['key']
            file_url = file_info['links']['self']
            file_size = file_info['size']

            # Apply file pattern filter if specified
            if file_patterns:
                if not any(Path(filename).match(pattern) for pattern in file_patterns):
                    logger.debug(f"Skipping {filename} (doesn't match patterns)")
                    continue

            filepath = self.output_dir / filename
            self.download_file(file_url, filepath, file_size)

        logger.success(f"\nDownload complete! Files saved to: {self.output_dir}")

    def get_file_list(self):
        """Get a list of all files in the Zenodo record."""
        metadata = self.get_record_metadata()
        return [f['key'] for f in metadata['files']]


def main():
    parser = argparse.ArgumentParser(
        description='Download DREAMS dataset from Zenodo',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Download entire DREAMS dataset
    python download_zenodo_data.py --output_dir ./data/dreams

    # Download only EDF files
    python download_zenodo_data.py --output_dir ./data/dreams --patterns "*.edf"

    # List available files
    python download_zenodo_data.py --output_dir ./data/dreams --list_only
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

    args = parser.parse_args()

    # Create downloader
    downloader = ZenodoDownloader(args.record_id, args.output_dir)

    if args.list_only:
        # Just list files
        logger.info(f"Files available in Zenodo record {args.record_id}:")
        files = downloader.get_file_list()
        for i, filename in enumerate(files, 1):
            print(f"{i:3d}. {filename}")
    else:
        # Download dataset
        downloader.download_dataset(file_patterns=args.patterns)


if __name__ == '__main__':
    main()

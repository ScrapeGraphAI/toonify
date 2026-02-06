"""Kaggle dataset integration for TOON.

This module provides utilities for downloading Kaggle datasets and parsing
Croissant (ML Commons) metadata, making it easy to convert dataset files
directly to TOON format.

Example:
    >>> from toon.kaggle import download_dataset, parse_croissant
    >>> files = download_dataset("username/dataset-name", "/tmp/data")
    >>> # Or parse Croissant metadata to understand dataset structure
    >>> info = parse_croissant(metadata_dict)
"""

from __future__ import annotations

import csv
import io
import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Optional


def is_kaggle_slug(s: str) -> bool:
    """Check if string is a valid Kaggle dataset slug.

    Args:
        s: String to check

    Returns:
        True if string matches pattern 'username/dataset-name'

    Example:
        >>> is_kaggle_slug("username/my-dataset")
        True
        >>> is_kaggle_slug("/path/to/file.csv")
        False
    """
    import os
    return bool(re.match(r"^[\w-]+/[\w-]+$", s)) and not os.path.exists(s)


def download_dataset(
    slug: str,
    output_dir: Optional[str] = None,
    unzip: bool = True
) -> list[Path]:
    """Download a Kaggle dataset.

    Requires the Kaggle CLI to be installed and configured with API credentials.
    See: https://github.com/Kaggle/kaggle-api#api-credentials

    Args:
        slug: Kaggle dataset slug (e.g., 'username/dataset-name')
        output_dir: Directory to download to (default: temp directory)
        unzip: Whether to unzip the downloaded archive (default: True)

    Returns:
        List of paths to downloaded/extracted files

    Raises:
        RuntimeError: If Kaggle CLI is not installed or download fails
        FileNotFoundError: If no files are found after download

    Example:
        >>> files = download_dataset("youssefelebiary/global-air-quality-2025")
        >>> csv_files = [f for f in files if f.suffix == '.csv']
    """
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="toon_kaggle_")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    cmd = ["kaggle", "datasets", "download", "-d", slug, "-p", str(output_path)]
    if unzip:
        cmd.append("--unzip")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        raise RuntimeError(
            "Kaggle CLI not found. Install with: pip install kaggle\n"
            "Then configure credentials: https://github.com/Kaggle/kaggle-api#api-credentials"
        )

    if result.returncode != 0:
        raise RuntimeError(f"Kaggle download failed: {result.stderr}")

    files = list(output_path.rglob("*"))
    files = [f for f in files if f.is_file()]

    if not files:
        raise FileNotFoundError(f"No files found after downloading {slug}")

    return files


def find_best_csv(files: list[Path]) -> Optional[Path]:
    """Find the best CSV file from a list of files.

    Heuristics:
    - Prefers files with 'all', 'full', 'combined', or 'main' in the name
    - Falls back to the largest CSV file

    Args:
        files: List of file paths

    Returns:
        Path to the best CSV file, or None if no CSVs found

    Example:
        >>> files = list(Path("/data").rglob("*"))
        >>> best = find_best_csv(files)
    """
    csv_files = [f for f in files if f.suffix.lower() == ".csv"]

    if not csv_files:
        return None

    # Look for common "main" file patterns
    main_patterns = ["all", "full", "combined", "main", "complete"]
    for pattern in main_patterns:
        for f in csv_files:
            if pattern in f.stem.lower():
                return f

    # Fall back to largest file
    return max(csv_files, key=lambda f: f.stat().st_size)


def csv_to_records(csv_content: str) -> list[dict[str, Any]]:
    """Convert CSV string to list of dictionaries.

    Args:
        csv_content: CSV data as string

    Returns:
        List of dictionaries, one per row

    Example:
        >>> data = csv_to_records("name,age\\nAlice,30\\nBob,25")
        >>> data[0]
        {'name': 'Alice', 'age': '30'}
    """
    reader = csv.DictReader(io.StringIO(csv_content))
    return list(reader)


def parse_croissant(metadata: dict[str, Any]) -> dict[str, Any]:
    """Parse Croissant (ML Commons) JSON-LD metadata.

    Croissant is the ML Commons standard for dataset documentation.
    See: https://mlcommons.org/croissant/

    Args:
        metadata: Parsed Croissant JSON-LD document

    Returns:
        Dictionary with:
        - name: Dataset name
        - description: Dataset description
        - files: List of file info dicts with name, url, contained_in
        - schema: Dict mapping table names to field definitions
        - kaggle_slug: Kaggle dataset slug if detectable from URLs

    Example:
        >>> with open("metadata.json") as f:
        ...     metadata = json.load(f)
        >>> info = parse_croissant(metadata)
        >>> print(info['name'])
        'Global Air Quality Dataset'
    """
    info: dict[str, Any] = {
        "name": metadata.get("name", "Unknown"),
        "description": metadata.get("description", ""),
        "files": [],
        "schema": {},
        "kaggle_slug": None,
    }

    # Extract file distribution
    for dist in metadata.get("distribution", []):
        file_info = {
            "name": dist.get("name"),
            "url": dist.get("contentUrl"),
            "encoding": dist.get("encodingFormat"),
            "contained_in": dist.get("containedIn", {}).get("@id") if isinstance(
                dist.get("containedIn"), dict
            ) else dist.get("containedIn"),
        }
        info["files"].append(file_info)

        # Try to extract Kaggle slug from URL
        url = dist.get("contentUrl", "")
        if "kaggle.com" in url and info["kaggle_slug"] is None:
            match = re.search(r"datasets/download/([^?]+)", url)
            if match:
                info["kaggle_slug"] = match.group(1)

    # Extract schema from recordSet
    for record_set in metadata.get("recordSet", []):
        fields = []
        for field in record_set.get("field", []):
            field_name = field.get("name")
            if field_name:
                data_types = field.get("dataType", ["unknown"])
                type_str = data_types[0] if data_types else "unknown"
                # Clean up schema.org prefixes
                type_str = type_str.replace("sc:", "").replace("https://schema.org/", "")

                fields.append({
                    "name": field_name,
                    "type": type_str,
                    "description": field.get("description", ""),
                })

        if fields:
            table_name = record_set.get("name", "default")
            info["schema"][table_name] = fields

    return info


def croissant_to_summary(info: dict[str, Any]) -> str:
    """Generate a human-readable summary from parsed Croissant metadata.

    Args:
        info: Parsed Croissant info from parse_croissant()

    Returns:
        Formatted summary string suitable for display or LLM context

    Example:
        >>> info = parse_croissant(metadata)
        >>> print(croissant_to_summary(info))
        # Dataset: Global Air Quality
        # Schema:
        #   data.csv: Date:Date, City:Text, AQI:Float
    """
    lines = [
        f"# Dataset: {info['name']}",
        "# Schema:",
    ]

    for table, fields in info["schema"].items():
        field_strs = [f"{f['name']}:{f['type']}" for f in fields if f["name"]]
        if field_strs:
            lines.append(f"#   {table}: {', '.join(field_strs)}")

    if info["kaggle_slug"]:
        lines.extend([
            "#",
            "# To download and convert this dataset:",
            f"#   toon {info['kaggle_slug']} --kaggle",
        ])

    return "\n".join(lines)

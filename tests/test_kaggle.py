"""Tests for Kaggle integration module."""

import pytest
from toon.kaggle import (
    is_kaggle_slug,
    csv_to_records,
    parse_croissant,
    croissant_to_summary,
    find_best_csv,
)
from pathlib import Path
import tempfile


class TestIsKaggleSlug:
    """Tests for is_kaggle_slug function."""

    def test_valid_slug(self):
        """Test valid Kaggle slugs."""
        assert is_kaggle_slug("username/dataset-name") is True
        assert is_kaggle_slug("user123/my-dataset") is True
        assert is_kaggle_slug("org-name/dataset_v2") is True

    def test_invalid_slug(self):
        """Test invalid Kaggle slugs."""
        assert is_kaggle_slug("not-a-slug") is False
        assert is_kaggle_slug("username/dataset/extra") is False
        assert is_kaggle_slug("") is False
        assert is_kaggle_slug("/dataset") is False


class TestCsvToRecords:
    """Tests for csv_to_records function."""

    def test_basic_csv(self):
        """Test basic CSV conversion."""
        csv_data = "name,age,city\nAlice,30,NYC\nBob,25,LA"
        result = csv_to_records(csv_data)

        assert len(result) == 2
        assert result[0] == {"name": "Alice", "age": "30", "city": "NYC"}
        assert result[1] == {"name": "Bob", "age": "25", "city": "LA"}

    def test_empty_csv(self):
        """Test empty CSV (headers only)."""
        csv_data = "name,age\n"
        result = csv_to_records(csv_data)
        assert result == []

    def test_csv_with_quotes(self):
        """Test CSV with quoted fields."""
        csv_data = 'name,description\nAlice,"Hello, World"\nBob,"Line1\nLine2"'
        result = csv_to_records(csv_data)

        assert len(result) == 2
        assert result[0]["description"] == "Hello, World"


class TestParseCroissant:
    """Tests for parse_croissant function."""

    def test_basic_metadata(self):
        """Test parsing basic Croissant metadata."""
        metadata = {
            "name": "Test Dataset",
            "description": "A test dataset",
            "distribution": [
                {
                    "name": "data.csv",
                    "encodingFormat": "text/csv",
                    "contentUrl": "https://example.com/data.csv",
                }
            ],
            "recordSet": [
                {
                    "name": "data.csv",
                    "field": [
                        {"name": "id", "dataType": ["sc:Integer"]},
                        {"name": "value", "dataType": ["sc:Float"]},
                    ],
                }
            ],
        }

        result = parse_croissant(metadata)

        assert result["name"] == "Test Dataset"
        assert result["description"] == "A test dataset"
        assert len(result["files"]) == 1
        assert result["files"][0]["name"] == "data.csv"
        assert len(result["schema"]["data.csv"]) == 2
        assert result["schema"]["data.csv"][0]["name"] == "id"
        assert result["schema"]["data.csv"][0]["type"] == "Integer"

    def test_kaggle_url_extraction(self):
        """Test Kaggle slug extraction from URL."""
        metadata = {
            "name": "Kaggle Dataset",
            "distribution": [
                {
                    "name": "archive.zip",
                    "contentUrl": "https://www.kaggle.com/api/v1/datasets/download/user/dataset?version=1",
                }
            ],
            "recordSet": [],
        }

        result = parse_croissant(metadata)
        assert result["kaggle_slug"] == "user/dataset"

    def test_empty_metadata(self):
        """Test parsing empty metadata."""
        result = parse_croissant({})

        assert result["name"] == "Unknown"
        assert result["description"] == ""
        assert result["files"] == []
        assert result["schema"] == {}


class TestCroissantToSummary:
    """Tests for croissant_to_summary function."""

    def test_summary_output(self):
        """Test summary string generation."""
        info = {
            "name": "Air Quality Dataset",
            "schema": {
                "data.csv": [
                    {"name": "Date", "type": "Date"},
                    {"name": "AQI", "type": "Float"},
                ]
            },
            "kaggle_slug": "user/air-quality",
        }

        result = croissant_to_summary(info)

        assert "# Dataset: Air Quality Dataset" in result
        assert "Date:Date" in result
        assert "AQI:Float" in result
        assert "toon user/air-quality --kaggle" in result


class TestFindBestCsv:
    """Tests for find_best_csv function."""

    def test_finds_csv(self):
        """Test finding CSV in file list."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            csv1 = Path(tmpdir) / "data.csv"
            csv2 = Path(tmpdir) / "all_data.csv"
            txt = Path(tmpdir) / "readme.txt"

            csv1.write_text("a,b\n1,2")
            csv2.write_text("a,b,c\n1,2,3\n4,5,6")  # Larger
            txt.write_text("readme")

            files = [csv1, csv2, txt]
            result = find_best_csv(files)

            # Should prefer "all_data.csv" due to "all" in name
            assert result == csv2

    def test_no_csv(self):
        """Test when no CSV files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            txt = Path(tmpdir) / "readme.txt"
            txt.write_text("readme")

            result = find_best_csv([txt])
            assert result is None

    def test_prefers_main_patterns(self):
        """Test preference for files with main/full/combined in name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Use "big" instead of "small" - "small" contains "all"!
            big = Path(tmpdir) / "big.csv"
            combined = Path(tmpdir) / "combined.csv"

            # Make big.csv actually larger in bytes
            big.write_text("a,b\n" + "1,2\n" * 100)
            combined.write_text("a,b\n1,2")

            files = [big, combined]
            result = find_best_csv(files)

            # Should prefer "combined" despite being smaller
            assert result == combined

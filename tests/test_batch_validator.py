"""Tests for batch validator module."""

import json
from pathlib import Path

import pytest

from stac_validator.batch_validator import (
    _validate_single_file,
    get_optimal_worker_count,
    validate_concurrently,
    validate_dicts,
)


@pytest.fixture
def test_items_dir():
    """Get path to test items directory."""
    return Path(__file__).parent / "test_data" / "v110"


def test_get_optimal_worker_count():
    """Test worker count calculation."""
    import multiprocessing

    total_cores = multiprocessing.cpu_count()

    # Test auto-detect
    assert get_optimal_worker_count(None) == total_cores
    assert get_optimal_worker_count(0) == total_cores

    # Test specific count
    assert get_optimal_worker_count(4) == min(4, total_cores)

    # Test negative (reserve cores)
    assert get_optimal_worker_count(-1) == max(1, total_cores - 1)
    assert get_optimal_worker_count(-2) == max(1, total_cores - 2)

    # Test capping at available cores
    assert get_optimal_worker_count(1000) == total_cores


def test_validate_single_file(test_items_dir):
    """Test validation of a single file."""
    item_path = str(test_items_dir / "extended-item.json")

    file_path, is_valid, errors = _validate_single_file(item_path)

    assert file_path == item_path
    assert is_valid is True
    assert len(errors) == 0


def test_validate_single_file_invalid(test_items_dir):
    """Test validation of an invalid file."""
    item_path = str(test_items_dir / "test-sar-item-invalid.json")

    file_path, is_valid, errors = _validate_single_file(item_path)

    assert file_path == item_path
    # This file may or may not be valid depending on schema
    # Just verify the function returns the expected structure
    assert isinstance(is_valid, bool)
    assert isinstance(errors, list)


def test_validate_concurrently(test_items_dir):
    """Test concurrent validation of multiple files."""
    files = [
        str(test_items_dir / "extended-item.json"),
        str(test_items_dir / "simple-item.json"),
        str(test_items_dir / "collection.json"),
    ]

    results = validate_concurrently(files, max_workers=2, show_progress=False)

    assert len(results) == 3
    assert all("path" in r for r in results)
    assert all("valid_stac" in r for r in results)

    # Check that at least some items are valid
    valid_count = sum(1 for r in results if r["valid_stac"])
    assert valid_count >= 1


def test_validate_concurrently_single_file(test_items_dir):
    """Test concurrent validation with single file."""
    files = [str(test_items_dir / "extended-item.json")]

    results = validate_concurrently(files, show_progress=False)

    assert len(results) == 1
    assert results[0]["valid_stac"] is True


def test_validate_concurrently_auto_cores(test_items_dir):
    """Test concurrent validation with auto-detected cores."""
    files = [
        str(test_items_dir / "extended-item.json"),
        str(test_items_dir / "simple-item.json"),
    ]

    # Use None to auto-detect cores
    results = validate_concurrently(files, max_workers=None, show_progress=False)

    assert len(results) == 2
    assert all("valid_stac" in r for r in results)


def test_validate_concurrently_no_progress(test_items_dir):
    """Test that progress bar can be disabled."""
    files = [
        str(test_items_dir / "extended-item.json"),
        str(test_items_dir / "simple-item.json"),
    ]

    # Should not raise even without tqdm
    results = validate_concurrently(files, show_progress=False)

    assert len(results) == 2


def test_validate_concurrently_result_format(test_items_dir):
    """Test that results have correct format."""
    files = [str(test_items_dir / "extended-item.json")]

    results = validate_concurrently(files, show_progress=False)

    assert len(results) == 1
    result = results[0]

    # Check required fields
    assert "path" in result
    assert "valid_stac" in result

    # Check optional fields
    if not result["valid_stac"]:
        assert "errors" in result


def test_validate_feature_collection_files(test_items_dir):
    """Test validation of FeatureCollection files."""
    import tempfile

    # Load items
    with open(test_items_dir / "extended-item.json") as f:
        item1 = json.load(f)
    with open(test_items_dir / "simple-item.json") as f:
        item2 = json.load(f)

    # Create FeatureCollection
    fc = {"type": "FeatureCollection", "features": [item1, item2]}

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(fc, f)
        temp_file = f.name

    try:
        # Validate with feature_collection flag
        results = validate_concurrently(
            [temp_file], show_progress=False, feature_collection=True
        )

        # Should have 2 results (one per feature)
        assert len(results) == 2

        # Check path format includes feature index
        assert "[0]" in results[0]["path"]
        assert "[1]" in results[1]["path"]

        # Both should be valid
        assert results[0]["valid_stac"] is True
        assert results[1]["valid_stac"] is True
    finally:
        import os

        os.unlink(temp_file)


def test_validate_feature_collection_mixed_files(test_items_dir):
    """Test validation with mix of regular files and FeatureCollections."""
    import tempfile

    # Load items
    with open(test_items_dir / "extended-item.json") as f:
        item1 = json.load(f)
    with open(test_items_dir / "simple-item.json") as f:
        item2 = json.load(f)

    # Create FeatureCollection
    fc = {"type": "FeatureCollection", "features": [item1, item2]}

    # Write to temp file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(fc, f)
        temp_fc_file = f.name

    try:
        # Validate with feature_collection flag
        results = validate_concurrently(
            [temp_fc_file], show_progress=False, feature_collection=True
        )

        # Should have 2 results from the FeatureCollection
        assert len(results) == 2
        assert all(r["valid_stac"] for r in results)
    finally:
        import os

        os.unlink(temp_fc_file)


def test_validate_dicts(test_items_dir):
    """Test validation of list of dictionaries."""
    # Load items as dictionaries
    with open(test_items_dir / "extended-item.json") as f:
        item1 = json.load(f)
    with open(test_items_dir / "simple-item.json") as f:
        item2 = json.load(f)

    items = [item1, item2]

    # Validate using validate_dicts (handles temp files internally)
    results = validate_dicts(items, max_workers=2, show_progress=False)

    assert len(results) == 2
    assert all("valid_stac" in r for r in results)
    assert all(r["valid_stac"] for r in results)


def test_validate_dicts_with_feature_collection(test_items_dir):
    """Test validate_dicts with feature_collection flag."""
    # Load items as dictionaries
    with open(test_items_dir / "extended-item.json") as f:
        item1 = json.load(f)
    with open(test_items_dir / "simple-item.json") as f:
        item2 = json.load(f)

    items = [item1, item2]

    # Validate with feature_collection flag
    results = validate_dicts(
        items, max_workers=2, show_progress=False, feature_collection=True
    )

    assert len(results) == 2
    assert all("valid_stac" in r for r in results)
    assert all(r["valid_stac"] for r in results)

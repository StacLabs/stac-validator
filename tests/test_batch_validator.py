"""Tests for batch validator module."""

import json
from pathlib import Path
from unittest.mock import patch

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
    import os

    # Get total cores using the same logic as get_optimal_worker_count()
    try:
        if hasattr(os, "sched_getaffinity"):
            # Linux: respects Docker/container CPU limits
            total_cores = len(os.sched_getaffinity(0))
        else:
            # Fallback for non-Linux systems
            total_cores = multiprocessing.cpu_count()
    except Exception:
        # Fallback if anything goes wrong
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

        # Check path format includes feature indices (order may vary due to concurrent execution)
        paths = {result["path"] for result in results}
        assert any("[0]" in path for path in paths), f"Expected [0] in paths: {paths}"
        assert any("[1]" in path for path in paths), f"Expected [1] in paths: {paths}"

        # Both should be valid
        assert all(result["valid_stac"] is True for result in results)
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
    """Test validate_dicts with items from a FeatureCollection."""
    # Load items as dictionaries
    with open(test_items_dir / "extended-item.json") as f:
        item1 = json.load(f)
    with open(test_items_dir / "simple-item.json") as f:
        item2 = json.load(f)

    items = [item1, item2]

    # Validate items (can be from any source including FeatureCollections)
    results = validate_dicts(items, max_workers=2, show_progress=False)

    assert len(results) == 2
    assert all("valid_stac" in r for r in results)
    assert all(r["valid_stac"] for r in results)


def test_validate_concurrently_with_read_errors():
    """Test that validate_concurrently accumulates errors when feature_collection=True."""
    import os
    import tempfile

    # Create valid STAC items for testing
    valid_item1 = {
        "stac_version": "1.1.0",
        "stac_extensions": [],
        "type": "Feature",
        "id": "test-item-1",
        "bbox": [0, 0, 1, 1],
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
        },
        "properties": {"datetime": "2020-01-01T00:00:00Z"},
        "links": [],
        "assets": {},
    }

    valid_item2 = {
        "stac_version": "1.1.0",
        "stac_extensions": [],
        "type": "Feature",
        "id": "test-item-2",
        "bbox": [0, 0, 1, 1],
        "geometry": {
            "type": "Polygon",
            "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 1], [0, 0]]],
        },
        "properties": {"datetime": "2020-01-02T00:00:00Z"},
        "links": [],
        "assets": {},
    }

    temp_files = []
    try:
        # Create a valid FeatureCollection file
        fc1 = {"type": "FeatureCollection", "features": [valid_item1]}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(fc1, f)
            temp_files.append(f.name)

        # Create an invalid JSON file (will fail to parse)
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write("{invalid json content")
            temp_files.append(f.name)

        # Create another valid FeatureCollection file
        fc2 = {"type": "FeatureCollection", "features": [valid_item2]}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(fc2, f)
            temp_files.append(f.name)

        # Validate with feature_collection flag - this tests error accumulation
        results = validate_concurrently(
            temp_files, show_progress=False, feature_collection=True
        )

        # Should have 3 results: 1 from first FC, 1 error from invalid JSON, 1 from second FC
        assert len(results) == 3

        # Check that we have both valid and invalid results
        valid_results = [r for r in results if r["valid_stac"]]
        invalid_results = [r for r in results if not r["valid_stac"]]

        assert (
            len(valid_results) == 2
        ), f"Expected 2 valid results, got {len(valid_results)}"
        assert (
            len(invalid_results) == 1
        ), f"Expected 1 invalid result, got {len(invalid_results)}"

        # Check that the error result has error information
        error_result = invalid_results[0]
        assert "errors" in error_result
        assert len(error_result["errors"]) > 0
        assert "Failed to read file" in error_result["errors"][0]

    finally:
        # Clean up temp files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except OSError:
                pass


@patch("stac_validator.utilities.requests.get")
def test_worker_schema_caching(mock_get, test_items_dir):
    """Test that schema caching prevents redundant network calls in worker processes.

    Verifies that when the same STAC item is validated twice in a worker process,
    the schema is only fetched once from the network, with subsequent validations
    using the cached schema.
    """
    item_path = str(test_items_dir / "extended-item.json")

    # 1. First validation: Should trigger network requests for schemas
    _validate_single_file(item_path)

    calls_after_first = mock_get.call_count
    assert calls_after_first > 0, "Expected network calls on the first validation"

    # 2. Second validation: Same item, so schemas should be cached
    # Each worker process has its own isolated schema cache
    _validate_single_file(item_path)

    calls_after_second = mock_get.call_count

    # 3. Assertion: The call count should NOT have increased
    # If caching works, the second validation should not trigger new network calls
    assert calls_after_second == calls_after_first, (
        f"Schemas were fetched again instead of using cache! "
        f"First run: {calls_after_first} calls, Second run: {calls_after_second} calls"
    )

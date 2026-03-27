"""Tests for FastAPI validator module."""

import json
import pytest
from pathlib import Path

from stac_validator.fastapi_validator import (
    validate_item,
    validate_items_batch,
    validate_feature_collection,
    ValidationResult,
    BatchValidationResponse,
    get_optimal_worker_count,
)


@pytest.fixture
def test_items_dir():
    """Get path to test items directory."""
    return Path(__file__).parent / "test_data" / "v110"


@pytest.fixture
def valid_item(test_items_dir):
    """Load a valid STAC item."""
    with open(test_items_dir / "extended-item.json") as f:
        return json.load(f)


@pytest.fixture
def valid_item2(test_items_dir):
    """Load another valid STAC item."""
    with open(test_items_dir / "simple-item.json") as f:
        return json.load(f)


@pytest.fixture
def feature_collection(valid_item, valid_item2):
    """Create a FeatureCollection from items."""
    return {
        "type": "FeatureCollection",
        "features": [valid_item, valid_item2]
    }


def test_validate_item_valid(valid_item):
    """Test validation of a valid item."""
    result = validate_item(valid_item)
    
    assert isinstance(result, ValidationResult)
    assert result.valid is True
    assert len(result.errors) == 0


def test_validate_item_with_extensions(valid_item):
    """Test validation with extension validation enabled."""
    result = validate_item(
        valid_item,
        validate_extensions=True,
        validate_links=False,
        validate_assets=False,
    )
    
    assert isinstance(result, ValidationResult)
    assert result.valid is True


def test_validate_item_missing_version():
    """Test validation of item missing stac_version."""
    invalid_item = {
        "type": "Feature",
        "geometry": {},
        "properties": {},
    }
    
    result = validate_item(invalid_item)
    
    assert result.valid is False
    assert len(result.errors) > 0
    assert "stac_version" in result.errors[0].lower()


def test_validate_items_batch(valid_item, valid_item2):
    """Test batch validation of multiple items."""
    items = [valid_item, valid_item2]
    
    result = validate_items_batch(items)
    
    assert isinstance(result, BatchValidationResponse)
    assert result.total == 2
    assert result.valid_count >= 1
    assert result.invalid_count <= 1
    assert len(result.results) == 2


def test_validate_items_batch_with_options(valid_item, valid_item2):
    """Test batch validation with validation options."""
    items = [valid_item, valid_item2]
    
    result = validate_items_batch(
        items,
        validate_extensions=True,
        validate_links=False,
        validate_assets=False,
    )
    
    assert isinstance(result, BatchValidationResponse)
    assert result.total == 2


def test_validate_items_batch_empty():
    """Test batch validation with empty list."""
    result = validate_items_batch([])
    
    assert result.total == 0
    assert result.valid_count == 0
    assert result.invalid_count == 0
    assert len(result.results) == 0


def test_validate_items_batch_mixed_valid_invalid(valid_item):
    """Test batch validation with mix of valid and invalid items."""
    invalid_item = {
        "type": "Feature",
        "geometry": {},
        "properties": {},
    }
    
    items = [valid_item, invalid_item]
    result = validate_items_batch(items)
    
    assert result.total == 2
    assert result.valid_count >= 1
    assert result.invalid_count >= 1
    assert len(result.results) == 2


def test_validate_feature_collection(feature_collection):
    """Test validation of a FeatureCollection."""
    result = validate_feature_collection(feature_collection)
    
    assert isinstance(result, BatchValidationResponse)
    assert result.total == 2
    assert result.valid_count >= 1


def test_validate_feature_collection_with_options(feature_collection):
    """Test FeatureCollection validation with options."""
    result = validate_feature_collection(
        feature_collection,
        validate_extensions=True,
        validate_links=False,
        validate_assets=False,
    )
    
    assert isinstance(result, BatchValidationResponse)
    assert result.total == 2


def test_validate_feature_collection_invalid_features():
    """Test FeatureCollection with invalid features field."""
    invalid_fc = {
        "type": "FeatureCollection",
        "features": "not a list"
    }
    
    result = validate_feature_collection(invalid_fc)
    
    assert result.total == 0
    assert result.invalid_count == 1


def test_validate_feature_collection_missing_features():
    """Test FeatureCollection with missing features field."""
    invalid_fc = {
        "type": "FeatureCollection",
    }
    
    result = validate_feature_collection(invalid_fc)
    
    assert result.total == 0
    assert result.valid_count == 0


def test_validation_result_model(valid_item):
    """Test ValidationResult Pydantic model."""
    result = validate_item(valid_item)
    
    # Should be serializable to dict
    result_dict = result.dict()
    assert "valid" in result_dict
    assert "errors" in result_dict
    assert "warnings" in result_dict


def test_batch_validation_response_model(valid_item, valid_item2):
    """Test BatchValidationResponse Pydantic model."""
    result = validate_items_batch([valid_item, valid_item2])
    
    # Should be serializable to dict
    result_dict = result.dict()
    assert "total" in result_dict
    assert "valid_count" in result_dict
    assert "invalid_count" in result_dict
    assert "results" in result_dict


def test_get_optimal_worker_count():
    """Test worker count calculation in fastapi_validator."""
    import multiprocessing
    
    total_cores = multiprocessing.cpu_count()
    
    assert get_optimal_worker_count(None) == total_cores
    assert get_optimal_worker_count(0) == total_cores
    assert get_optimal_worker_count(4) == min(4, total_cores)
    assert get_optimal_worker_count(-1) == max(1, total_cores - 1)

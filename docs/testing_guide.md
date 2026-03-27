# Testing Guide

This document describes the test suite for the STAC validator, including batch validation and FastAPI integration.

## Running Tests

### Run all tests
```bash
pytest
```

### Run specific test file
```bash
pytest tests/test_batch_validator.py -v
pytest tests/test_fastapi_validator.py -v
```

### Run specific test
```bash
pytest tests/test_batch_validator.py::test_validate_concurrently -v
```

### Run with coverage
```bash
pytest --cov=stac_validator tests/
```

## Test Structure

### Batch Validator Tests (`tests/test_batch_validator.py`)

Tests for the multiprocessing batch validation functionality.

**Tests:**
- `test_get_optimal_worker_count()` - Verify CPU core detection
- `test_validate_single_file()` - Single file validation
- `test_validate_single_file_invalid()` - Invalid file handling
- `test_validate_concurrently()` - Concurrent validation of multiple files
- `test_validate_concurrently_single_file()` - Single file in concurrent mode
- `test_validate_concurrently_auto_cores()` - Auto-detection of available cores
- `test_validate_concurrently_no_progress()` - Progress bar disabled
- `test_validate_concurrently_result_format()` - Result format validation

**Coverage:**
- Worker count calculation (None, 0, positive, negative)
- Single and batch file validation
- Core auto-detection
- Progress bar handling
- Result structure

### FastAPI Validator Tests (`tests/test_fastapi_validator.py`)

Tests for the FastAPI integration and validation functions.

**Tests:**
- `test_validate_item_valid()` - Valid item validation
- `test_validate_item_with_extensions()` - Item validation with extension checks
- `test_validate_item_missing_version()` - Missing stac_version handling
- `test_validate_items_batch()` - Batch item validation
- `test_validate_items_batch_with_options()` - Batch with validation options
- `test_validate_items_batch_empty()` - Empty batch handling
- `test_validate_items_batch_mixed_valid_invalid()` - Mixed valid/invalid items
- `test_validate_feature_collection()` - FeatureCollection validation
- `test_validate_feature_collection_with_options()` - FeatureCollection with options
- `test_validate_feature_collection_invalid_features()` - Invalid features field
- `test_validate_feature_collection_missing_features()` - Missing features field
- `test_validation_result_model()` - ValidationResult Pydantic model
- `test_batch_validation_response_model()` - BatchValidationResponse model
- `test_get_optimal_worker_count()` - Worker count in FastAPI validator

**Coverage:**
- Single item validation
- Batch validation
- FeatureCollection validation
- Validation options (extensions, links, assets)
- Error handling
- Pydantic model serialization
- Worker count calculation

## Test Data

Tests use STAC items from `tests/test_data/v110/`:
- `extended-item.json` - Valid item with multiple extensions
- `simple-item.json` - Simple valid item
- `collection.json` - Valid collection
- `test-sar-item-invalid.json` - Invalid item for error testing

## Fixtures

### Batch Validator Fixtures
- `test_items_dir` - Path to test data directory

### FastAPI Validator Fixtures
- `test_items_dir` - Path to test data directory
- `valid_item` - Loaded extended-item.json
- `valid_item2` - Loaded simple-item.json
- `feature_collection` - FeatureCollection from two items

## Running Tests in CI/CD

### GitHub Actions Example
```yaml
- name: Run tests
  run: |
    pip install -e ".[dev]"
    pytest tests/ -v --cov=stac_validator
```

### Pre-commit Hook
```yaml
- repo: local
  hooks:
    - id: pytest
      name: pytest
      entry: pytest
      language: system
      types: [python]
      stages: [commit]
```

## Test Coverage Goals

Current coverage:
- Batch validator: 100% of public API
- FastAPI validator: 100% of public API
- Worker count calculation: 100%

## Adding New Tests

When adding new functionality:

1. Create test in appropriate file (`test_batch_validator.py` or `test_fastapi_validator.py`)
2. Use descriptive test names: `test_<function>_<scenario>()`
3. Use fixtures for common setup
4. Test both success and failure cases
5. Verify result format/structure
6. Run tests: `pytest tests/ -v`

Example:
```python
def test_new_feature_success(valid_item):
    """Test new feature with valid input."""
    result = new_function(valid_item)
    
    assert result is not None
    assert result.valid is True

def test_new_feature_error(invalid_item):
    """Test new feature with invalid input."""
    result = new_function(invalid_item)
    
    assert result.valid is False
    assert len(result.errors) > 0
```

## Troubleshooting

### Tests fail with "No such file or directory"
- Ensure you're running pytest from the project root
- Check that test data files exist in `tests/test_data/v110/`

### Multiprocessing tests hang
- May occur on some systems; try running with `-n 1` (single process)
- Or use `pytest -x` to stop on first failure

### Pydantic deprecation warnings
- These are expected with Pydantic v2
- Use `model_dump()` instead of `dict()` for new code

## Performance

Test execution time:
- Batch validator tests: ~11 seconds (includes multiprocessing overhead)
- FastAPI validator tests: ~1 second
- Total: ~12 seconds

Tests use `show_progress=False` and `max_workers=2` to keep execution fast.

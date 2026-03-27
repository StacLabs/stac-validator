"""FastAPI integration for STAC validation."""

import multiprocessing
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

from .utilities import fetch_and_parse_file, validate_stac_version_field
from .validate import StacValidate


def get_optimal_worker_count(max_workers: Optional[int] = None) -> int:
    """
    Get the optimal number of worker processes.
    
    Detects available CPU cores, accounting for containerized environments.
    Falls back to os.sched_getaffinity() on Linux for Docker/container support.
    
    Args:
        max_workers: Number of workers to use. Options:
            - None or 0: Use all available cores (default)
            - Positive int: Use that many cores (capped at available)
            - Negative int: Use all cores minus that many (e.g., -1 reserves 1 core for OS)
        
    Returns:
        Optimal number of worker processes
        
    Note:
        In containerized environments (Docker, ECS), this uses os.sched_getaffinity()
        on Linux to detect the actual cores allocated to the container, rather than
        the host machine's total cores.
    """
    import os
    
    # Try to get container-aware core count on Linux
    try:
        if hasattr(os, 'sched_getaffinity'):
            # Linux: respects Docker/container CPU limits
            total_cores = len(os.sched_getaffinity(0))
        else:
            # Fallback for non-Linux systems
            total_cores = multiprocessing.cpu_count()
    except Exception:
        # Fallback if anything goes wrong
        total_cores = multiprocessing.cpu_count()
    
    if max_workers is None or max_workers == 0:
        return total_cores
    elif max_workers < 0:
        return max(1, total_cores + max_workers)
    else:
        return min(max_workers, total_cores)


class ValidationResult(BaseModel):
    """Result of validating a single STAC item."""
    valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class BatchValidationRequest(BaseModel):
    """Request body for batch validation."""
    items: List[Dict[str, Any]]
    validate_extensions: bool = True
    validate_links: bool = False
    validate_assets: bool = False


class FeatureCollectionValidationRequest(BaseModel):
    """Request body for FeatureCollection validation."""
    type: str = "FeatureCollection"
    features: List[Dict[str, Any]]
    validate_extensions: bool = True
    validate_links: bool = False
    validate_assets: bool = False


class BatchValidationResponse(BaseModel):
    """Response from batch validation."""
    total: int
    valid_count: int
    invalid_count: int
    results: List[Dict[str, Any]]


def validate_item(
    item: Dict[str, Any],
    validate_extensions: bool = True,
    validate_links: bool = False,
    validate_assets: bool = False,
) -> ValidationResult:
    """
    Validate a single STAC item dictionary.
    
    Args:
        item: STAC item dictionary to validate
        validate_extensions: Whether to validate extensions
        validate_links: Whether to validate links
        validate_assets: Whether to validate assets
        
    Returns:
        ValidationResult with validation status and any errors
    """
    errors = []
    warnings = []
    
    try:
        # 1. Validate version
        is_valid_version, err_type, err_msg = validate_stac_version_field(item)
        if not is_valid_version:
            return ValidationResult(
                valid=False,
                errors=[f"{err_type}: {err_msg}"]
            )
        
        # 2. Use StacValidate for comprehensive validation
        # Create a temporary validator with the item dictionary
        validator = StacValidate(item)
        
        # Set validation options
        if not validate_extensions:
            validator.extensions = False
        if validate_links:
            validator.links = True
        if validate_assets:
            validator.assets = True
        
        # Run validation
        validator.run()
        
        # Parse results
        if validator.message:
            try:
                messages = validator.message
                if isinstance(messages, list) and len(messages) > 0:
                    msg_obj = messages[0]
                    if not msg_obj.get("valid_stac", False):
                        if "errors" in msg_obj:
                            errors.extend(msg_obj["errors"])
            except (KeyError, IndexError, TypeError):
                if validator.message:
                    errors.append(str(validator.message))
        
    except Exception as e:
        return ValidationResult(
            valid=False,
            errors=[f"Validation error: {str(e)}"]
        )
    
    is_valid = len(errors) == 0
    return ValidationResult(
        valid=is_valid,
        errors=errors,
        warnings=warnings
    )


def validate_items_batch(
    items: List[Dict[str, Any]],
    validate_extensions: bool = True,
    validate_links: bool = False,
    validate_assets: bool = False,
) -> BatchValidationResponse:
    """
    Validate a batch of STAC items.
    
    Args:
        items: List of STAC item dictionaries to validate
        validate_extensions: Whether to validate extensions
        validate_links: Whether to validate links
        validate_assets: Whether to validate assets
        
    Returns:
        BatchValidationResponse with overall statistics and per-item results
    """
    results = []
    valid_count = 0
    
    for item in items:
        result = validate_item(
            item,
            validate_extensions=validate_extensions,
            validate_links=validate_links,
            validate_assets=validate_assets,
        )
        
        result_dict = {
            "valid": result.valid,
            "errors": result.errors,
        }
        if result.warnings:
            result_dict["warnings"] = result.warnings
        
        results.append(result_dict)
        
        if result.valid:
            valid_count += 1
    
    return BatchValidationResponse(
        total=len(items),
        valid_count=valid_count,
        invalid_count=len(items) - valid_count,
        results=results
    )


def validate_feature_collection(
    feature_collection: Dict[str, Any],
    validate_extensions: bool = True,
    validate_links: bool = False,
    validate_assets: bool = False,
) -> BatchValidationResponse:
    """
    Validate a GeoJSON FeatureCollection of STAC items.
    
    Args:
        feature_collection: GeoJSON FeatureCollection with STAC items as features
        validate_extensions: Whether to validate extensions
        validate_links: Whether to validate links
        validate_assets: Whether to validate assets
        
    Returns:
        BatchValidationResponse with overall statistics and per-feature results
    """
    # Extract features from FeatureCollection
    features = feature_collection.get("features", [])
    
    if not isinstance(features, list):
        return BatchValidationResponse(
            total=0,
            valid_count=0,
            invalid_count=1,
            results=[{"valid": False, "errors": ["'features' must be a list"]}]
        )
    
    # Validate all features as items
    return validate_items_batch(
        features,
        validate_extensions=validate_extensions,
        validate_links=validate_links,
        validate_assets=validate_assets,
    )

"""
Example FastAPI integration for STAC validation.

This example shows how to integrate the STAC validator into a FastAPI application
for validating items as they're posted to your STAC API endpoints.

Usage:
    pip install fastapi uvicorn stac-validator
    uvicorn examples.fastapi_integration:app --reload
    
Then POST to:
    http://localhost:8000/collections/my-collection/items
    http://localhost:8000/validate/item
    http://localhost:8000/validate/batch
"""

from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

from stac_validator.fastapi_validator import (
    validate_item,
    validate_items_batch,
    validate_feature_collection,
    ValidationResult,
    BatchValidationRequest,
    BatchValidationResponse,
    FeatureCollectionValidationRequest,
)


app = FastAPI(
    title="STAC Validator API",
    description="Validate STAC items via REST API",
    version="1.0.0"
)


class ItemResponse(BaseModel):
    """Response after posting an item."""
    id: str
    valid: bool
    validation: ValidationResult


class CollectionItemsRequest(BaseModel):
    """Request body for posting items to a collection."""
    items: List[Dict[str, Any]]


class CollectionItemsResponse(BaseModel):
    """Response after posting items to a collection."""
    collection_id: str
    total_items: int
    valid_items: int
    invalid_items: int
    results: List[Dict[str, Any]]


# ============================================================================
# Single Item Validation Endpoint
# ============================================================================

@app.post(
    "/validate/item",
    response_model=ValidationResult,
    summary="Validate a single STAC item",
    tags=["Validation"]
)
async def validate_single_item(
    item: Dict[str, Any],
    validate_extensions: bool = True,
    validate_links: bool = False,
    validate_assets: bool = False,
):
    """
    Validate a single STAC item.
    
    **Parameters:**
    - `item`: STAC item dictionary
    - `validate_extensions`: Whether to validate declared extensions (default: true)
    - `validate_links`: Whether to validate links (default: false)
    - `validate_assets`: Whether to validate assets (default: false)
    
    **Returns:**
    - `valid`: Whether the item is valid
    - `errors`: List of validation errors (if any)
    - `warnings`: List of validation warnings (if any)
    """
    result = validate_item(
        item,
        validate_extensions=validate_extensions,
        validate_links=validate_links,
        validate_assets=validate_assets,
    )
    return result


# ============================================================================
# Batch Validation Endpoint
# ============================================================================

@app.post(
    "/validate/batch",
    response_model=BatchValidationResponse,
    summary="Validate multiple STAC items",
    tags=["Validation"]
)
async def validate_batch(
    request: BatchValidationRequest,
):
    """
    Validate a batch of STAC items.
    
    **Request Body:**
    ```json
    {
        "items": [
            { "type": "Feature", "stac_version": "1.1.0", ... },
            { "type": "Feature", "stac_version": "1.1.0", ... }
        ],
        "validate_extensions": true,
        "validate_links": false,
        "validate_assets": false
    }
    ```
    
    **Returns:**
    - `total`: Total number of items validated
    - `valid_count`: Number of valid items
    - `invalid_count`: Number of invalid items
    - `results`: Per-item validation results
    """
    response = validate_items_batch(
        request.items,
        validate_extensions=request.validate_extensions,
        validate_links=request.validate_links,
        validate_assets=request.validate_assets,
    )
    return response


@app.post(
    "/validate/feature-collection",
    response_model=BatchValidationResponse,
    summary="Validate a GeoJSON FeatureCollection of STAC items",
    tags=["Validation"]
)
async def validate_feature_collection_endpoint(
    request: FeatureCollectionValidationRequest,
):
    """
    Validate a GeoJSON FeatureCollection containing STAC items.
    
    **Request Body:**
    ```json
    {
        "type": "FeatureCollection",
        "features": [
            { "type": "Feature", "stac_version": "1.1.0", ... },
            { "type": "Feature", "stac_version": "1.1.0", ... }
        ],
        "validate_extensions": true,
        "validate_links": false,
        "validate_assets": false
    }
    ```
    
    **Returns:**
    - `total`: Total number of features validated
    - `valid_count`: Number of valid features
    - `invalid_count`: Number of invalid features
    - `results`: Per-feature validation results
    """
    response = validate_feature_collection(
        request.dict(),
        validate_extensions=request.validate_extensions,
        validate_links=request.validate_links,
        validate_assets=request.validate_assets,
    )
    return response


# ============================================================================
# STAC API Endpoints - Collection Items
# ============================================================================

@app.post(
    "/collections/{collection_id}/items",
    response_model=CollectionItemsResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Post items to a collection with validation",
    tags=["Collections"]
)
async def post_collection_items(
    collection_id: str,
    request: CollectionItemsRequest,
    validate_extensions: bool = True,
    validate_links: bool = False,
    validate_assets: bool = False,
):
    """
    Post items to a collection with automatic validation.
    
    This endpoint validates all items before accepting them. If any items
    are invalid, the entire request is rejected with a 400 error.
    
    **Path Parameters:**
    - `collection_id`: ID of the collection
    
    **Query Parameters:**
    - `validate_extensions`: Whether to validate extensions (default: true)
    - `validate_links`: Whether to validate links (default: false)
    - `validate_assets`: Whether to validate assets (default: false)
    
    **Request Body:**
    ```json
    {
        "items": [
            { "type": "Feature", "stac_version": "1.1.0", ... },
            { "type": "Feature", "stac_version": "1.1.0", ... }
        ]
    }
    ```
    
    **Returns:**
    - `collection_id`: The collection ID
    - `total_items`: Total items posted
    - `valid_items`: Number of valid items
    - `invalid_items`: Number of invalid items
    - `results`: Per-item validation results
    
    **Errors:**
    - `400 Bad Request`: If any items are invalid
    - `422 Unprocessable Entity`: If request body is malformed
    """
    # Validate all items
    validation_response = validate_items_batch(
        request.items,
        validate_extensions=validate_extensions,
        validate_links=validate_links,
        validate_assets=validate_assets,
    )
    
    # Reject if any items are invalid
    if validation_response.invalid_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"{validation_response.invalid_count} item(s) failed validation",
                "total": validation_response.total,
                "valid_count": validation_response.valid_count,
                "invalid_count": validation_response.invalid_count,
                "results": validation_response.results,
            }
        )
    
    # All items are valid - in a real application, you would now:
    # 1. Store items in database
    # 2. Index in search engine
    # 3. Update collection metadata
    # For this example, we just return success
    
    return CollectionItemsResponse(
        collection_id=collection_id,
        total_items=validation_response.total,
        valid_items=validation_response.valid_count,
        invalid_items=validation_response.invalid_count,
        results=validation_response.results,
    )


# ============================================================================
# Health Check
# ============================================================================

@app.get(
    "/health",
    summary="Health check",
    tags=["Health"]
)
async def health_check():
    """Check if the validation service is running."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

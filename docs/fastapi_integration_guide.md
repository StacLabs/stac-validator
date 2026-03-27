# FastAPI Integration Guide

This guide shows how to integrate STAC validation into your FastAPI application, particularly for POST endpoints like `/collections/{collectionId}/items`.

## Quick Start

### 1. Install Dependencies

```bash
pip install stac-validator fastapi uvicorn
```

### 2. Import Validation Functions

```python
from fastapi import FastAPI
from stac_validator.fastapi_validator import (
    validate_item,
    validate_items_batch,
    ValidationResult,
    BatchValidationResponse,
)
```

### 3. Add Validation to Your Endpoints

#### Single Item Validation

```python
from fastapi import FastAPI
from stac_validator.fastapi_validator import validate_item

app = FastAPI()

@app.post("/items")
async def create_item(item: dict):
    """Create a STAC item with validation."""
    result = validate_item(item)
    
    if not result.valid:
        raise HTTPException(
            status_code=400,
            detail={"errors": result.errors}
        )
    
    # Item is valid - store it
    return {"id": item["id"], "valid": True}
```

#### Batch Item Validation

```python
from fastapi import FastAPI, HTTPException
from stac_validator.fastapi_validator import validate_items_batch

app = FastAPI()

@app.post("/collections/{collection_id}/items")
async def post_collection_items(collection_id: str, request: dict):
    """Post multiple items to a collection with validation."""
    items = request.get("items", [])
    
    # Validate all items
    result = validate_items_batch(items)
    
    if result.invalid_count > 0:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"{result.invalid_count} item(s) failed validation",
                "results": result.results
            }
        )
    
    # All items valid - store them
    return {
        "collection_id": collection_id,
        "total": result.total,
        "valid": result.valid_count,
        "invalid": result.invalid_count
    }
```

## Real-World Example: STAC FastAPI Integration

Here's how to integrate with a STAC FastAPI application:

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any

from stac_validator.fastapi_validator import (
    validate_item,
    validate_items_batch,
)

app = FastAPI(title="My STAC API")

class ItemsRequest(BaseModel):
    items: List[Dict[str, Any]]

@app.post(
    "/collections/{collection_id}/items",
    status_code=status.HTTP_201_CREATED
)
async def post_items(collection_id: str, request: ItemsRequest):
    """
    POST items to a collection.
    
    Validates all items before accepting them.
    Returns 400 if any items are invalid.
    """
    # Validate all items
    validation = validate_items_batch(
        request.items,
        validate_extensions=True,
        validate_links=False,
        validate_assets=False,
    )
    
    # Reject if any are invalid
    if validation.invalid_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": f"{validation.invalid_count} item(s) failed validation",
                "results": validation.results
            }
        )
    
    # All valid - store in database
    # db.items.insert_many(request.items)
    
    return {
        "collection_id": collection_id,
        "total_items": validation.total,
        "valid_items": validation.valid_count,
        "message": "All items accepted"
    }
```

## Validation Options

The `validate_item()` and `validate_items_batch()` functions accept these parameters:

- **`validate_extensions`** (bool, default: True)
  - Validate declared STAC extensions
  
- **`validate_links`** (bool, default: False)
  - Validate link objects (href, rel, type, etc.)
  
- **`validate_assets`** (bool, default: False)
  - Validate asset objects (href, type, roles, etc.)

Example:

```python
result = validate_item(
    item,
    validate_extensions=True,
    validate_links=True,
    validate_assets=True,
)
```

## Response Format

### Single Item Validation

```python
ValidationResult(
    valid: bool,
    errors: List[str],
    warnings: List[str]
)
```

Example response:

```json
{
    "valid": false,
    "errors": [
        "Core Schema validation failed: '2020-12-15T01:48:13.725Z' is not of types 'boolean', 'object'"
    ],
    "warnings": []
}
```

### Batch Validation

```python
BatchValidationResponse(
    total: int,
    valid_count: int,
    invalid_count: int,
    results: List[Dict[str, Any]]
)
```

Example response:

```json
{
    "total": 100,
    "valid_count": 98,
    "invalid_count": 2,
    "results": [
        {
            "valid": true,
            "errors": []
        },
        {
            "valid": false,
            "errors": ["Missing stac_version field"]
        },
        ...
    ]
}
```

## Error Handling

### Fail-Fast Pattern (Recommended for APIs)

Reject the entire request if any item is invalid:

```python
@app.post("/collections/{collection_id}/items")
async def post_items(collection_id: str, request: ItemsRequest):
    validation = validate_items_batch(request.items)
    
    if validation.invalid_count > 0:
        raise HTTPException(
            status_code=400,
            detail={
                "message": f"{validation.invalid_count} item(s) invalid",
                "results": validation.results
            }
        )
    
    # Store all items
    return {"status": "accepted"}
```

### Partial Accept Pattern

Accept valid items and return errors for invalid ones:

```python
@app.post("/collections/{collection_id}/items")
async def post_items(collection_id: str, request: ItemsRequest):
    validation = validate_items_batch(request.items)
    
    # Store valid items
    valid_items = [
        item for item, result in zip(request.items, validation.results)
        if result["valid"]
    ]
    # db.items.insert_many(valid_items)
    
    return {
        "accepted": len(valid_items),
        "rejected": validation.invalid_count,
        "results": validation.results
    }
```

## Performance Considerations

### Schema Caching

The validator automatically caches downloaded schemas in memory. Each FastAPI worker process maintains its own cache.

For high-throughput scenarios:

```python
from stac_validator.utilities import set_schema_cache_size

# At application startup
@app.on_event("startup")
async def startup():
    # Increase cache size for high-throughput validation
    set_schema_cache_size(256)
```

### Async Validation

The validation functions are CPU-bound and synchronous. For very high throughput, use `asyncio.to_thread()`:

```python
import asyncio
from fastapi import FastAPI

app = FastAPI()

@app.post("/collections/{collection_id}/items")
async def post_items(collection_id: str, request: ItemsRequest):
    # Run validation in thread pool to avoid blocking event loop
    validation = await asyncio.to_thread(
        validate_items_batch,
        request.items
    )
    
    if validation.invalid_count > 0:
        raise HTTPException(status_code=400, detail=validation.results)
    
    return {"status": "accepted"}
```

### Batch Processing

For ingesting millions of items, use the CLI batch validator instead:

```bash
stac-validator batch /path/to/items/*.json --cores 8
```

Then import valid items into your database.

## Complete Example

See `examples/fastapi_integration.py` for a complete working example with:

- Single item validation endpoint
- Batch validation endpoint
- Collection items POST endpoint
- Health check endpoint
- Full error handling

Run it:

```bash
uvicorn examples.fastapi_integration:app --reload
```

Then test:

```bash
# Validate single item
curl -X POST http://localhost:8000/validate/item \
  -H "Content-Type: application/json" \
  -d @item.json

# Validate batch
curl -X POST http://localhost:8000/validate/batch \
  -H "Content-Type: application/json" \
  -d '{"items": [...]}'

# Post to collection
curl -X POST http://localhost:8000/collections/my-collection/items \
  -H "Content-Type: application/json" \
  -d '{"items": [...]}'
```

## Integration with stac-fastapi

If you're using [stac-fastapi](https://github.com/stac-utils/stac-fastapi), you can add validation as middleware or in your item creation endpoints:

```python
from stac_fastapi.api.app import StacApi
from stac_validator.fastapi_validator import validate_item

# In your item creation handler
async def create_item(item: dict):
    # Validate first
    result = validate_item(item)
    if not result.valid:
        raise HTTPException(status_code=400, detail=result.errors)
    
    # Then create via stac-fastapi
    return await super().create_item(item)
```

## Troubleshooting

### "stac_version field is missing"

Items must include a valid `stac_version` field:

```json
{
    "type": "Feature",
    "stac_version": "1.1.0",
    "stac_extensions": [],
    ...
}
```

### "Unknown format: duration"

Some extension schemas use custom formats that aren't fully supported. This is a known limitation. The item is still valid according to the STAC spec.

### Slow Validation

- Increase schema cache size: `set_schema_cache_size(512)`
- Use `asyncio.to_thread()` to avoid blocking the event loop
- For batch operations, use the CLI validator instead of the API

## Support

For issues or questions, see:
- [STAC Validator GitHub](https://github.com/stac-utils/stac-validator)
- [STAC Specification](https://stacspec.org)
- [stac-fastapi Documentation](https://stac-utils.github.io/stac-fastapi/)

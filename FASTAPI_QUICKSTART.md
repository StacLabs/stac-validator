# FastAPI STAC Validator - Quick Start

## Usage Patterns

### Installation

```bash
pip install stac-validator fastapi uvicorn
```

### Pattern 1: List of Items

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any

from stac_validator.fastapi_validator import validate_items_batch

app = FastAPI()

class ItemsRequest(BaseModel):
    items: List[Dict[str, Any]]

@app.post("/collections/{collection_id}/items", status_code=201)
async def post_collection_items(collection_id: str, request: ItemsRequest):
    """POST items to a collection with validation."""
    validation = validate_items_batch(request.items)
    
    if validation.invalid_count > 0:
        raise HTTPException(
            status_code=400,
            detail={"errors": validation.results}
        )
    
    return {"collection_id": collection_id, "accepted": validation.total}
```

### Pattern 2: GeoJSON FeatureCollection (More Common)

```python
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Dict, Any

from stac_validator.fastapi_validator import validate_feature_collection

app = FastAPI()

class FeatureCollectionRequest(BaseModel):
    type: str = "FeatureCollection"
    features: List[Dict[str, Any]]

@app.post("/collections/{collection_id}/items", status_code=201)
async def post_collection_items(collection_id: str, request: FeatureCollectionRequest):
    """POST a FeatureCollection of items to a collection with validation."""
    validation = validate_feature_collection(request.dict())
    
    if validation.invalid_count > 0:
        raise HTTPException(
            status_code=400,
            detail={"errors": validation.results}
        )
    
    return {"collection_id": collection_id, "accepted": validation.total}
```

### Single Item Validation

```python
from stac_validator.fastapi_validator import validate_item

@app.post("/items")
async def create_item(item: dict):
    """Create a single STAC item with validation."""
    result = validate_item(item)
    
    if not result.valid:
        raise HTTPException(
            status_code=400,
            detail={"errors": result.errors}
        )
    
    # Item is valid - store it
    return {"id": item["id"], "valid": True}
```

### CLI Batch Validation with FeatureCollections

The `stac-validator batch` command also supports validating FeatureCollections:

```bash
# Validate individual files
stac-validator batch item1.json item2.json item3.json

# Validate FeatureCollections (extracts and validates each feature)
stac-validator batch collection.json --feature-collection

# With custom cores
stac-validator batch collection.json --feature-collection --cores 8
```

**Output with FeatureCollection:**
```json
[
    {
        "path": "collection.json[0]",
        "valid_stac": true
    },
    {
        "path": "collection.json[1]",
        "valid_stac": true
    }
]
```

The `[0]`, `[1]` notation shows which feature in the FeatureCollection each result corresponds to.

### Validation Options

```python
# Validate with all options enabled
validation = validate_items_batch(
    items,
    validate_extensions=True,  # Check declared extensions
    validate_links=True,       # Check link objects
    validate_assets=True,      # Check asset objects
)
```

### Auto-Detect CPU Cores

The validator automatically detects available CPU cores - no configuration needed:

```python
from stac_validator.batch_validator import get_optimal_worker_count

# Auto-detect available cores
workers = get_optimal_worker_count()  # Returns all available cores

# Or specify custom core usage:
workers = get_optimal_worker_count(4)      # Use exactly 4 cores
workers = get_optimal_worker_count(-1)     # Use all cores minus 1
workers = get_optimal_worker_count(None)   # Use all cores (default)
```

In FastAPI, just let it auto-detect:

```python
@app.post("/collections/{collection_id}/items")
async def post_items(collection_id: str, request: FeatureCollectionRequest):
    # Automatically uses all available CPU cores
    validation = validate_feature_collection(request.dict())
    # ...
```

### Response Format

**Success (all items valid):**
```json
{
    "collection_id": "my-collection",
    "total_items": 100,
    "valid_items": 100,
    "message": "All items accepted"
}
```

**Error (some items invalid):**
```json
{
    "detail": {
        "message": "2 item(s) failed validation",
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
}
```

### Performance Tips

1. **Increase schema cache for high throughput:**
   ```python
   from stac_validator.utilities import set_schema_cache_size
   
   @app.on_event("startup")
   async def startup():
       set_schema_cache_size(256)  # Default is 16
   ```

2. **Use async thread pool for CPU-bound validation:**
   ```python
   import asyncio
   
   @app.post("/collections/{collection_id}/items")
   async def post_items(collection_id: str, request: ItemsRequest):
       # Run validation in thread pool
       validation = await asyncio.to_thread(
           validate_items_batch,
           request.items
       )
       # ... rest of handler
   ```

3. **For millions of items, use CLI batch validator:**
   ```bash
   stac-validator batch /path/to/items/*.json --cores 8
   ```

### Complete Working Example

See `examples/fastapi_integration.py` for a full example with:
- Single item validation endpoint
- Batch validation endpoint  
- Collection items POST endpoint
- Health check endpoint
- Full error handling

Run it:
```bash
uvicorn examples.fastapi_integration:app --reload
```

Test it:
```bash
# Validate single item
curl -X POST http://localhost:8000/validate/item \
  -H "Content-Type: application/json" \
  -d @item.json

# Post to collection
curl -X POST http://localhost:8000/collections/my-collection/items \
  -H "Content-Type: application/json" \
  -d '{"items": [...]}'
```

### Integration with stac-fastapi

If using [stac-fastapi](https://github.com/stac-utils/stac-fastapi):

```python
from stac_fastapi.api.app import StacApi
from stac_validator.fastapi_validator import validate_item

class MyItemsClient(ItemsBaseClient):
    async def create_item(self, item: dict, **kwargs):
        # Validate first
        result = validate_item(item)
        if not result.valid:
            raise HTTPException(status_code=400, detail=result.errors)
        
        # Then create via stac-fastapi
        return await super().create_item(item, **kwargs)
```

### Available Functions

**Single Item:**
```python
from stac_validator.fastapi_validator import validate_item

result = validate_item(
    item: Dict[str, Any],
    validate_extensions: bool = True,
    validate_links: bool = False,
    validate_assets: bool = False,
) -> ValidationResult
```

**Batch Items:**
```python
from stac_validator.fastapi_validator import validate_items_batch

result = validate_items_batch(
    items: List[Dict[str, Any]],
    validate_extensions: bool = True,
    validate_links: bool = False,
    validate_assets: bool = False,
) -> BatchValidationResponse
```

### Response Models

```python
class ValidationResult(BaseModel):
    valid: bool
    errors: List[str]
    warnings: List[str]

class BatchValidationResponse(BaseModel):
    total: int
    valid_count: int
    invalid_count: int
    results: List[Dict[str, Any]]
```

### Troubleshooting

**"stac_version field is missing"**
- Items must include `"stac_version": "1.1.0"` (or other valid version)

**"Unknown format: duration"**
- Some extension schemas use custom formats. Item is still valid per STAC spec.

**Slow validation**
- Increase cache size: `set_schema_cache_size(512)`
- Use `asyncio.to_thread()` to avoid blocking event loop
- For bulk operations, use CLI batch validator

### Full Documentation

See `docs/fastapi_integration_guide.md` for comprehensive documentation including:
- Detailed integration examples
- Error handling patterns
- Performance optimization
- Troubleshooting guide
- stac-fastapi integration details

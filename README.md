# SpatioTemporal Asset Catalog Validator

<!-- markdownlint-disable MD033 MD041 -->

<p align="left">
  <img src="https://raw.githubusercontent.com/stac-utils/stac-validator/main/assets/stac-validator.png" width=560>
</p>

[![PyPI Downloads](https://static.pepy.tech/personalized-badge/stac-validator?period=total&units=NONE&left_color=GREY&right_color=BLUE&left_text=downloads)](https://pepy.tech/projects/stac-validator)
  [![GitHub contributors](https://img.shields.io/github/contributors/stac-utils/stac-validator?color=blue)](https://github.com/stac-utils/stac-validator/graphs/contributors)
  [![GitHub stars](https://img.shields.io/github/stars/stac-utils/stac-validator.svg?color=blue)](https://github.com/stac-utils/stac-validator/stargazers)
  [![GitHub forks](https://img.shields.io/github/forks/stac-utils/stac-validator.svg?color=blue)](https://github.com/stac-utils/stac-validator/network/members)
   [![PyPI version](https://img.shields.io/pypi/v/stac-validator.svg?color=blue)](https://pypi.org/project/stac-validator/)
  [![STAC](https://img.shields.io/badge/STAC-1.1.0-blue.svg)](https://github.com/radiantearth/stac-spec/tree/v1.1.0)

## Table of Contents

- [Overview](#overview)
- [Documentation](#documentation)
- [Requirements](#requirements)
- [Installation](#install)
- [Supported STAC Versions](#versions-supported)
- [Usage](#usage)
  - [CLI](#cli)
    - [Legacy Validation](#legacy-validation)
  - [Batch Validation](#batch-validation)
  - [Python](#python)
- [Schema Cache Settings](#schema-cache-settings)
- [Performance Benchmarking](#performance-benchmarking)
- [Examples](#additional-examples)
  - [Core Validation](#--core)
  - [Custom Schema](#--custom)
  - [Extensions Validation](#--extensions)
  - [Recursive Validation](#--recursive)
  - [Item Collection Validation](#--item-collection)
  - [Using Headers](#--header)
  - [Schema Mapping](#--schema-map)
  - [Schema Config](#--schema-config)
  - [Pydantic Validation](#--pydantic)
- [Deployment](#deployment)
  - [Docker](#docker)
  - [AWS (CDK)](#aws-cdk)
- [Testing](#testing)
- [Related Projects](#related-projects)
- [Sponsors and Supporters](#sponsors-and-supporters)
- [Contributing](#contributing)
- [License](#license)

## Overview

STAC Validator is a tool to validate [STAC (SpatioTemporal Asset Catalog)](https://github.com/radiantearth/stac-spec) json files against the official STAC specification. It provides both a command-line interface and a Python API for validating STAC objects.

## Documentation

For detailed documentation, please visit our [GitHub Pages documentation site](https://stac-utils.github.io/stac-validator/).

## Validate STAC json files against the [STAC spec](https://github.com/radiantearth/stac-spec).

```bash
$ stac-validator https://raw.githubusercontent.com/radiantearth/stac-spec/master/examples/extended-item.json
```

```bash
[
    {
        "version": "1.0.0",
        "path": "https://raw.githubusercontent.com/radiantearth/stac-spec/master/examples/extended-item.json",
        "schema": [
            "https://stac-extensions.github.io/eo/v1.0.0/schema.json",
            "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
            "https://stac-extensions.github.io/scientific/v1.0.0/schema.json",
            "https://stac-extensions.github.io/view/v1.0.0/schema.json",
            "https://stac-extensions.github.io/remote-data/v1.0.0/schema.json",
            "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/item.json"
        ],
        "valid_stac": true,
        "asset_type": "ITEM",
        "validation_method": "default"
    }
]
```

## Requirements

- Python 3.8+
  - Requests
  - Click
  - Jsonschema

## Related Projects

Note: Stac-validator is also used in stac-check which adds linting messages based on the official STAC best practices document.  
https://github.com/stac-utils/stac-check

## Install

### Installation from PyPi

```bash
$ pip install stac-validator
```

### Installation from Repo

```bash
$ pip install .
```

or for local development

```bash
$ pip install -e '.[dev]'
```

The [Makefile](./Makefile) has convenience commands if Make is installed.

```bash
$ make help
```

## Versions supported

| STAC         |
| ------------ |
| 0.8.0        |
| 0.8.1        |
| 0.9.0        |
| 1.0.0-beta.1 |
| 1.0.0-beta.2 |
| 1.0.0-rc.1   |
| 1.0.0-rc.2   |
| 1.0.0-rc.3   |
| 1.0.0-rc.4   |
| 1.0.0        |
| 1.1.0-beta.1 |
| 1.1.0        |

## Usage

### CLI

**Basic Usage**

```bash
$ stac-validator --help
```

```bash
Usage: stac-validator [OPTIONS] COMMAND [ARGS]...

  STAC Validator - Validate STAC files against the STAC specification.

  Usage:
    stac-validator validate <file> [options]
    stac-validator batch <files> [options]
    stac-validator batch <file> --item-collection [options]
      

Options:
  --help  Show this message and exit.

Commands:
  batch     Validate multiple STAC files concurrently using all available...
  validate  Main function for the `stac-validator` command line tool.
```

**Validate Command**

```bash
$ stac-validator validate --help
```

```bash
Usage: stac-validator validate [OPTIONS] STAC_FILE

  Validate a STAC file against the STAC specification.

  Prints validation results to the console as JSON. Exits with status code 0
  if valid, 1 if invalid.

Options:
  --core                          Validate core stac object only without
                                  extensions.
  --extensions                    Validate extensions only.
  --links                         Additionally validate links. Only works with
                                  default mode.
  --assets                        Additionally validate assets. Only works
                                  with default mode.
  -c, --custom TEXT               Validate against a custom schema (local
                                  filepath or remote schema).
  -sc, --schema-config TEXT       Validate against a custom schema config
                                  (local filepath or remote schema config).
  -s, --schema-map <TEXT TEXT>...
                                  Schema path to replaced by (local) schema
                                  path during validation. Can be used multiple
                                  times.
  -r, --recursive                 Recursively validate all related stac
                                  objects.
  -m, --max-depth INTEGER         Maximum depth to traverse when recursing.
                                  Omit this argument to get full recursion.
                                  Ignored if `recursive == False`.
  --collections                   Validate /collections response.
  --item-collection               Validate item collection response. Can be
                                  combined with --pages. Defaults to one page.
  --no-assets-urls                Disables the opening of href links when
                                  validating assets (enabled by default).
  --header <TEXT TEXT>...         HTTP header to include in the requests. Can
                                  be used multiple times.
  -p, --pages INTEGER             Maximum number of pages to validate via
                                  --item-collection. Defaults to one page.
  -t, --trace-recursion           Enables verbose output for recursive mode.
  --no_output                     Do not print output to console.
  --log_file TEXT                 Save full recursive output to log file
                                  (local filepath).
  --pydantic                      Validate using stac-pydantic models for
                                  enhanced type checking and validation.
  --verbose                       Enable verbose output. This will output
                                  additional information during validation.
  --schema-cache-size INTEGER     Max number of schema entries to cache in
                                  memory. Use 0 to disable schema caching.
                                  Defaults to 16.
  --help                          Show this message and exit.
```

**Batch Command**

```bash
$ stac-validator batch --help
```

```bash
Usage: stac-validator batch [OPTIONS] FILES...

  Validate multiple STAC files concurrently using all available CPU cores.

  This command uses multiprocessing to validate STAC files in parallel,
  bypassing Python's Global Interpreter Lock (GIL) for maximum performance.
  Each CPU core gets its own schema cache, which is warmed up on the first
  file and reused for subsequent files.

  Examples:

      # Validate all JSON files in a directory
      $ stac-validator batch *.json

      # Validate specific files
      $ stac-validator batch file1.json file2.json file3.json

      # Validate a GeoJSON FeatureCollection (validates each feature individually)
      $ stac-validator batch --item-collection sample_data/sentinel-cogs_0_100.json

      # Use only 4 cores
      $ stac-validator batch *.json --cores 4

      # Disable progress bar
      $ stac-validator batch *.json --no-progress

Options:
  --cores INTEGER       Number of CPU cores to use for parallel validation.
                        Defaults to all available cores.
  --no-progress         Disable progress bar during validation.
  --no-output           Do not print output to console.
  --item-collection  Treat files as GeoJSON FeatureCollections and validate
                        each feature individually.
  --verbose             Show full JSON output for all items. By default, only
                        invalid items are shown.
  --schema-cache-size INTEGER  Max number of schema entries to cache
                             per worker process. Use 0 to disable
                             schema caching. Defaults to 16.
  --batch-size INTEGER         Batch size for chunked processing. Larger
                               batches use more memory but may be faster.
                               Defaults to 2000.
  --help                Show this message and exit.
```

#### Legacy Validation

The `validate` command is the main legacy validation tool with comprehensive options:

```bash
# Basic single file validation
$ stac-validator validate path/to/stac_file.json

# Validate with custom schema
$ stac-validator validate item.json --custom /path/to/schema.json

# Recursively validate all related STAC objects
$ stac-validator validate catalog.json --recursive --max-depth 5

# Validate collections endpoint response
$ stac-validator validate https://example.com/collections --collections

# Validate item collection response
$ stac-validator validate https://example.com/search --item-collection --pages 10

# Validate with extensions and links
$ stac-validator validate item.json --extensions --links --assets
```

**Options include:**
- `--core` - Validate core STAC only (skip extensions)
- `--extensions` - Validate extensions only
- `--links` - Validate link objects
- `--assets` - Validate asset objects
- `--recursive` - Recursively validate related STAC objects
- `--custom` - Validate against custom schema
- `--schema-map` - Replace schema URLs during validation
- `--collections` - Validate /collections endpoint response
- `--item-collection` - Validate item collection responses
- `--pydantic` - Use Pydantic models for validation
- `--schema-cache-size` - Configure schema cache size
- `--batch-size` - Configure batch size for chunked processing (batch command only)
- And more (see `stac-validator validate --help`)

#### Batch Validation

The `batch` command validates multiple STAC files concurrently using multiprocessing to bypass Python's Global Interpreter Lock (GIL). This enables **10-100x performance improvement** over single-threaded validation by utilizing all available CPU cores.

**Architecture:**

- **Multiprocessing:** Each CPU core runs an independent Python process
- **Per-worker schema cache:** Each worker maintains its own LRU cache of downloaded schemas (default 16 per worker)
- **Cache warmup:** First file on each worker downloads schemas, subsequent files use cached copies
- **Configurable cache:** Use `--schema-cache-size` to adjust cache size per worker (0 = disabled)
- **Linear scaling:** Performance scales linearly with available cores (e.g., 8 cores = ~8x faster)
- **Container-aware:** Automatically detects Docker/ECS CPU limits via `os.sched_getaffinity()`

**Basic Usage**

```bash
# Validate all JSON files in current directory
$ stac-validator batch *.json

# Validate specific files
$ stac-validator batch item1.json item2.json item3.json

# Validate a FeatureCollection (extracts and validates each feature)
$ stac-validator batch collection.json --item-collection
```

**Options**

```bash
# Use specific number of cores
$ stac-validator batch *.json --cores 4

# Reserve cores for OS (useful on local machines)
$ stac-validator batch *.json --cores -1  # Uses all cores minus 1

# Disable progress bar (for CI/CD environments)
$ stac-validator batch *.json --no-progress

# Suppress JSON output (show only summary)
$ stac-validator batch *.json --no-output

# Configure schema cache size per worker (default: 16 schemas per worker)
$ stac-validator batch *.json --schema-cache-size 32

# Disable schema caching entirely
$ stac-validator batch *.json --schema-cache-size 0

# Configure batch size for chunked processing (default: 2000 items per chunk)
$ stac-validator batch *.json --batch-size 5000

# Use larger batch size for faster processing (uses more memory)
$ stac-validator batch collection.json --item-collection --batch-size 10000

# Use smaller batch size for memory-constrained environments
$ stac-validator batch *.json --batch-size 500
```

**Batch Size Configuration**

The `--batch-size` option controls how many items are processed in each chunk. This affects memory usage and performance:

- **Default (2000):** Balanced memory usage and performance for most systems
- **Larger values (5000-10000):** Faster processing on systems with abundant memory; reduces overhead from creating multiple worker pools
- **Smaller values (500-1000):** Lower memory footprint; useful on memory-constrained systems or when validating very large items

**How It Works**

1. **Startup:** Detects available CPU cores (respects Docker limits)
2. **Distribution:** Distributes files across worker processes
3. **Validation:** Each worker validates files independently
4. **Schema Caching:** Each worker maintains its own LRU cache (default 16 schemas per worker)
   - First file on a worker: schemas are fetched and cached
   - Subsequent files: schemas are reused from cache (no network/disk I/O)
   - Total memory: up to `cores × schema_cache_size` schemas in memory
5. **Results:** Aggregates results and displays summary statistics

**Example Output**

```bash
$ stac-validator batch --item-collection sample_data/sentinel-cogs_0_100.json
[
    {
        "path": "sample_data/sentinel-cogs_0_100.json[0]",
        "valid_stac": false,
        "errors": [
            "'eo:bands' does not match any of the regexes: '^(?!eo:)'. Error is in properties "
        ]
    }
]

Validation Summary:
  Total files: 100
  CPU cores used: 16
  ✅ Valid: 99
  ❌ Invalid: 1

Failed validations:
  sample_data/sentinel-cogs_0_100.json[0]
    - 'eo:bands' does not match any of the regexes: '^(?!eo:)'. Error is in properties 

Validation completed in 1.10s
```

**Performance Characteristics**

| Scenario | Single-threaded | Batch (8 cores) | Speedup |
|----------|-----------------|-----------------|---------|
| 100 items | ~5 seconds | ~1 second | 5x |
| 1000 items | ~50 seconds | ~6 seconds | 8x |
| 10000 items | ~500 seconds | ~60 seconds | 8x |

*Times vary based on schema complexity and network latency for first download*

**Python API**

```python
from stac_validator.batch_validator import validate_concurrently

# Validate files
results = validate_concurrently(
    ["item1.json", "item2.json", "item3.json"],
    max_workers=None,  # Auto-detect cores
    show_progress=True
)

# Validate FeatureCollections
results = validate_concurrently(
    ["collection.json"],
    feature_collection=True,
    max_workers=8
)

# Process results
for result in results:
    if result["valid_stac"]:
        print(f"✅ {result['path']}")
    else:
        print(f"❌ {result['path']}")
        for error in result.get("errors", []):
            print(f"   - {error}")
```

**Use Cases**

- **Bulk ingestion:** Validate thousands of STAC items from ESA, Copernicus, or other catalogs
- **CI/CD pipelines:** Validate entire dataset collections in GitHub Actions or AWS CodePipeline
- **Data quality checks:** Periodically validate all items in a STAC catalog
- **Migration validation:** Verify all items when upgrading STAC versions
- **API preprocessing:** Validate incoming FeatureCollections before storage (see FastAPI integration)

### Python

**Single File Validation**

```python
from stac_validator import stac_validator

# Remote source
stac = stac_validator.StacValidate("https://raw.githubusercontent.com/stac-utils/pystac/main/tests/data-files/examples/0.9.0/collection-spec/examples/landsat-collection.json")
stac.run()
print(stac.message)

# Local file
stac = stac_validator.StacValidate("tests/test_data/1beta1/sentinel2.json", extensions=True)
stac.run()
print(stac.message)
```

**Dictionary Validation**

```python
from stac_validator import stac_validator

stac = stac_validator.StacValidate()
stac.validate_dict(item_dict)
print(stac.message)
```

**Batch Validation - List of Dictionaries**

For validating dictionaries directly without managing temp files, use `validate_dicts()`:

```python
from stac_validator.batch_validator import validate_dicts

items = [
    {"type": "Feature", "stac_version": "1.1.0", ...},
    {"type": "Feature", "stac_version": "1.1.0", ...},
    {"type": "Feature", "stac_version": "1.1.0", ...},
]

# Validate all items concurrently (temp files handled internally)
results = validate_dicts(items, max_workers=None, show_progress=True)

print(f"Total: {len(results)}")
print(f"Valid: {sum(1 for r in results if r['valid_stac'])}")
print(f"Invalid: {sum(1 for r in results if not r['valid_stac'])}")

# Process results
for result in results:
    if result["valid_stac"]:
        print(f"✅ Valid")
    else:
        print(f"❌ Invalid: {result.get('errors', [])}")
```

**Parameters:**
- `items` - List of STAC item dictionaries
- `max_workers` - CPU cores to use (None = auto-detect, positive int = specific cores, negative int = all minus N)
- `show_progress` - Display progress bar (default: True)
- `chunk_size` - Number of items to process at a time to bound disk and memory usage (default: 1000)

**Batch Validation - FeatureCollection (Concurrent with Multiprocessing)**

For FeatureCollection validation with multiprocessing, use `validate_concurrently()` with `feature_collection=True`:

```python
from stac_validator.batch_validator import validate_concurrently

# Validate FeatureCollection files directly (10-100x faster for large collections)
results = validate_concurrently(
    ["collection1.json", "collection2.json"],
    feature_collection=True,  # Expand and validate each feature
    max_workers=None  # Auto-detect cores
)

print(f"Total features: {len(results)}")
print(f"Valid: {sum(1 for r in results if r['valid_stac'])}")
print(f"Invalid: {sum(1 for r in results if not r['valid_stac'])}")

# Process results
for result in results:
    if result["valid_stac"]:
        print(f"✅ Feature valid")
    else:
        print(f"❌ Feature invalid: {result.get('errors', [])}")
```

**Batch Validation - Multiple Files**

```python
from stac_validator.batch_validator import validate_concurrently

files = [
    "item1.json",
    "item2.json",
    "item3.json",
]

# Validate files concurrently using all available CPU cores
results = validate_concurrently(
    files,
    max_workers=None,  # Auto-detect cores
    show_progress=True
)

# Process results
for result in results:
    if result["valid_stac"]:
        print(f"✅ {result['path']}")
    else:
        print(f"❌ {result['path']}: {result.get('errors', [])}")
```

**Batch Validation - FeatureCollection Files**

```python
from stac_validator.batch_validator import validate_concurrently

files = ["collection1.json", "collection2.json"]

# Validate FeatureCollections by extracting and validating each feature
results = validate_concurrently(
    files,
    feature_collection=True,
    max_workers=8
)

# Results show feature index: "collection1.json[0]", "collection1.json[1]", etc.
for result in results:
    print(f"{result['path']}: {'✅' if result['valid_stac'] else '❌'}")
```

**Item Collection Validation**

```python
from stac_validator import stac_validator

stac = stac_validator.StacValidate()
stac.validate_item_collection_dict(item_collection_dict)
print(stac.message)
```

**Configure Schema Cache Size**

```python
from stac_validator import stac_validator
from stac_validator.utilities import set_schema_cache_size

# Set once at app startup (process-wide)
set_schema_cache_size(16)  # use 0 to disable caching

stac = stac_validator.StacValidate()
stac.validate_dict(dictionary)
print(stac.message)
```


### Schema Cache Settings

- Default schema cache size is 16 entries.
- Use `--schema-cache-size` in the CLI or `set_schema_cache_size(...)` in Python to override it.
- Use `0` to disable schema caching.

Use `set_schema_cache_size` once at application startup:

```python
from stac_validator.utilities import set_schema_cache_size

# Examples:
set_schema_cache_size(16)  # small cache for low-memory deployments
set_schema_cache_size(64)  # moderate cache for long-running services
set_schema_cache_size(0)   # disable schema caching
```

Notes:
- `StacValidate()` and `validate_dict()` do not accept a cache-size parameter.
- Changing cache size at runtime replaces the cache instance and drops existing cached entries.
- In multi-worker deployments, configure cache size in each worker process.

## Performance Benchmarking

A benchmark script is included to compare the performance of batch validation vs legacy item-collection validation. This is useful for understanding the performance improvements of the multiprocessing batch validator.

### Running the Benchmark

```bash
# Test with 10,000 items (default)
python benchmark_validation.py

# Test with custom number of items
python benchmark_validation.py --items 5000
python benchmark_validation.py --items 50000

# Run only batch validation (skip slow legacy validation)
python benchmark_validation.py --items 10000 --batch-only

# Run only legacy validation
python benchmark_validation.py --items 10000 --legacy-only

# View all options
python benchmark_validation.py --help
```

### Example Output

```
======================================================================
BENCHMARK RESULTS
======================================================================
Items tested: 10000

Batch Validation (multiprocessing):
  Time: 49.02s
  ✅ Valid: 6666
  ❌ Invalid: 3334

Legacy Validation (single-threaded):
  Time: 187.31s
  ✅ Valid: 6666
  ❌ Invalid: 3334

======================================================================
Speedup: 3.8x faster with batch validation
Time saved: 138.29s
```

### Interpreting Results

- **Speedup Factor**: Shows how many times faster batch validation is compared to legacy validation
- **Time Saved**: The absolute time difference in seconds
- **CPU Cores Used**: Number of CPU cores utilized by batch validation (typically all available cores)

The batch validator's multiprocessing approach provides significant performance improvements, especially for large datasets. The speedup factor varies based on:
- Number of CPU cores available
- Size of the dataset
- Complexity of validation (extensions, custom schemas, etc.)

## Deployment

### Docker

The validator can run using docker containers.

```bash
$ docker build -t stac-validator .
$ docker run stac-validator https://raw.githubusercontent.com/stac-extensions/projection/main/examples/item.json
```

```bash
[
    {
        "version": "1.0.0",
        "path": "https://raw.githubusercontent.com/stac-extensions/projection/main/examples/item.json",
        "schema": [
            "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
            "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/item.json"
        ],
        "valid_stac": true,
        "asset_type": "ITEM",
        "validation_method": "default"
    }
]
```

### AWS (CDK)

An example [AWS CDK](https://aws.amazon.com/cdk/) deployment is available in [cdk-deployment](./cdk-deployment/README.md)

```bash
$ cd cdk-deployment
$ cdk diff
```

## Testing

```bash
$ make test
# or
$ pytest -v
```

See the [tests](./tests/test_stac_validator.py) files for examples on different usages.

## Additional Examples

### --core

```bash
$ stac-validator https://raw.githubusercontent.com/radiantearth/stac-spec/master/examples/extended-item.json --core
```

```bash
[
    {
        "version": "1.0.0",
        "path": "https://raw.githubusercontent.com/radiantearth/stac-spec/master/examples/extended-item.json",
        "schema": [
            "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/item.json"
        ],
        "valid_stac": true,
        "asset_type": "ITEM",
        "validation_method": "core"
    }
]
```

### --custom

```bash
$ stac-validator https://radarstac.s3.amazonaws.com/stac/catalog.json --custom https://cdn.staclint.com/v0.7.0/catalog.json
```

```bash
[
    {
        "version": "0.7.0",
        "path": "https://radarstac.s3.amazonaws.com/stac/catalog.json",
        "schema": [
            "https://cdn.staclint.com/v0.7.0/catalog.json"
        ],
        "asset_type": "CATALOG",
        "validation_method": "custom",
        "valid_stac": true
    }
]
```

### --extensions

```bash
$ stac-validator https://raw.githubusercontent.com/radiantearth/stac-spec/master/examples/extended-item.json --extensions
```

```bash
[
    {
        "version": "1.0.0",
        "path": "https://raw.githubusercontent.com/radiantearth/stac-spec/master/examples/extended-item.json",
        "schema": [
            "https://stac-extensions.github.io/eo/v1.0.0/schema.json",
            "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
            "https://stac-extensions.github.io/scientific/v1.0.0/schema.json",
            "https://stac-extensions.github.io/view/v1.0.0/schema.json",
            "https://stac-extensions.github.io/remote-data/v1.0.0/schema.json"
        ],
        "valid_stac": true,
        "asset_type": "ITEM",
        "validation_method": "extensions"
    }
]
```

### --recursive

```bash
$ stac-validator https://spot-canada-ortho.s3.amazonaws.com/catalog.json --recursive --max-depth 1 --trace-recursion
```

```bash
[
    {
        "version": "0.8.1",
        "path": "https://canada-spot-ortho.s3.amazonaws.com/canada_spot_orthoimages/canada_spot4_orthoimages/collection.json",
        "schema": "https://cdn.staclint.com/v0.8.1/collection.json",
        "asset_type": "COLLECTION",
        "validation_method": "recursive",
        "valid_stac": true
    },
    {
        "version": "0.8.1",
        "path": "https://canada-spot-ortho.s3.amazonaws.com/canada_spot_orthoimages/canada_spot5_orthoimages/collection.json",
        "schema": "https://cdn.staclint.com/v0.8.1/collection.json",
        "asset_type": "COLLECTION",
        "validation_method": "recursive",
        "valid_stac": true
    },
    {
        "version": "0.8.1",
        "path": "https://spot-canada-ortho.s3.amazonaws.com/catalog.json",
        "schema": "https://cdn.staclint.com/v0.8.1/catalog.json",
        "asset_type": "CATALOG",
        "validation_method": "recursive",
        "valid_stac": true
    }
]
```

### --item-collection

```bash
$ stac-validator https://earth-search.aws.element84.com/v0/collections/sentinel-s2-l2a/items --item-collection --pages 2
```

### --header

```bash
$ stac-validator https://stac-catalog.eu/collections/sentinel-s2-l2a/items --header x-api-key $MY_API_KEY --header foo bar
```

### --schema-map

Schema map allows stac-validator to replace a schema in a STAC json by a schema from another URL or local schema file.
This is especially useful when developing a schema and testing validation against your local copy of the schema.

```bash
$ stac-validator https://raw.githubusercontent.com/radiantearth/stac-spec/v1.0.0/examples/extended-item.json --extensions --schema-map https://stac-extensions.github.io/projection/v1.0.0/schema.json "tests/test_data/schema/v1.0.0/projection.json"
```

```bash
[
    {
        "version": "1.0.0",
        "path": "https://raw.githubusercontent.com/radiantearth/stac-spec/v1.0.0/examples/extended-item.json",
        "schema": [
            "https://stac-extensions.github.io/eo/v1.0.0/schema.json",
            "tests/test_data/schema/v1.0.0/projection.json",
            "https://stac-extensions.github.io/scientific/v1.0.0/schema.json",
            "https://stac-extensions.github.io/view/v1.0.0/schema.json",
            "https://stac-extensions.github.io/remote-data/v1.0.0/schema.json"
        ],
        "valid_stac": true,
        "asset_type": "ITEM",
        "validation_method": "extensions"
    }
]
```

This option is also capable of replacing URLs to subschemas:

```bash
$ stac-validator tests/test_data/v100/extended-item-local.json --custom tests/test_data/schema/v1.0.0/item_with_unreachable_url.json --schema-map https://geojson-wrong-url.org/schema/Feature.json https://geojson.org/schema/Feature.json --schema-map https://geojson-wrong-url.org/schema/Geometry.json https://geojson.org/schema/Geometry.json
```

```bash
[
    {
        "version": "1.0.0",
        "path": "tests/test_data/v100/extended-item-local.json",
        "schema": [
            "tests/test_data/schema/v1.0.0/item_with_unreachable_url.json"
        ],
        "valid_stac": true,
        "asset_type": "ITEM",
        "validation_method": "custom"
    }
]
```

### --schema-config

The `--schema-config` option allows you to specify a YAML or JSON configuration file that maps remote schema URLs to local file paths. This is useful when you need to validate against multiple local schemas and want to avoid using multiple `--schema-map` arguments.

Example schema config file (YAML):
```yaml
schemas:
  "https://schemas.stacspec.org/v1.0.0/collection-spec/json-schema/collection.json": "local_schemas/v1.0.0/collection.json"
  "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/item.json": "local_schemas/v1.0.0/item.json"
  "https://stac-extensions.github.io/eo/v1.0.0/schema.json": "local_schemas/v1.0.0/eo.json"
```

Usage:
```bash
$ stac-validator https://raw.githubusercontent.com/radiantearth/stac-spec/v1.0.0/examples/extended-item.json --schema-config path/to/schema_config.yaml
```

The paths in the config file can be absolute or relative to the config file's location.

### --pydantic

The `--pydantic` option provides enhanced validation using stac-pydantic models, which offer stronger type checking and more detailed error messages. To use this feature, you need to install the optional dependency:

```bash
$ pip install stac-validator[pydantic]
```

Then you can validate your STAC objects using Pydantic models:

```bash
$ stac-validator https://raw.githubusercontent.com/radiantearth/stac-spec/master/examples/extended-item.json --pydantic
```

```bash
[
    {
        "version": "1.0.0",
        "path": "https://raw.githubusercontent.com/radiantearth/stac-spec/master/examples/extended-item.json",
        "schema": [
            "stac-pydantic Item model"
        ],
        "valid_stac": true,
        "asset_type": "ITEM",
        "validation_method": "pydantic",
        "extension_schemas": [
            "https://stac-extensions.github.io/eo/v1.0.0/schema.json",
            "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
            "https://stac-extensions.github.io/scientific/v1.0.0/schema.json",
            "https://stac-extensions.github.io/view/v1.0.0/schema.json",
            "https://stac-extensions.github.io/remote-data/v1.0.0/schema.json"
        ],
        "model_validation": "passed"
    }
]
```

## Sponsors and Supporters

The following organizations have contributed time and/or funding to support the development of this project:
- [Healy Hyperspatial](https://healy-hyperspatial.github.io/)
- [Radiant Earth Foundation](https://radiant.earth/)
- [Sparkgeo](https://sparkgeo.com/)
- [CloudFerro](https://cloudferro.com/)

<p align="left">
  <a href="https://healy-hyperspatial.github.io/"><img src="https://raw.githubusercontent.com/stac-utils/stac-fastapi-elasticsearch-opensearch/refs/heads/main/assets/hh-logo-blue.png" alt="Healy Hyperspatial" height="100" hspace="20"></a>
  <a href="https://radiant.earth/"><img src="assets/radiant-earth.webp" alt="Radiant Earth Foundation" height="100" hspace="20"></a>
  <a href="https://sparkgeo.com/"><img src="assets/sparkgeo_logo.jpeg" alt="Sparkgeo" height="100" hspace="20"></a>
  <a href="https://cloudferro.com/"><img src="assets/cloudferro-logo.png" alt="CloudFerro" height="110" hspace="20"></a>
</p>


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0.

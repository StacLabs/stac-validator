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
  - [Python](#python)
- [Schema Cache Settings](#schema-cache-settings)
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
Usage: stac-validator [OPTIONS] STAC_FILE

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
  --pydantic                      Validate using stac-pydantic models for enhanced
                                  type checking and validation.
    --schema-cache-size INTEGER     Max number of schema entries to cache in
                                                                    memory. Use 0 to disable schema caching.
  --schema-config TEXT            Path to a YAML or JSON schema config file.
  --verbose                       Enable verbose output. This will output
                                  additional information during validation.
  --help                          Show this message and exit.
```

### Python

**Remote source**

```python
from stac_validator import stac_validator

stac = stac_validator.StacValidate("https://raw.githubusercontent.com/stac-utils/pystac/main/tests/data-files/examples/0.9.0/collection-spec/examples/landsat-collection.json")
stac.run()
print(stac.message)
```
```python
[
    {
        "version": "0.9.0",
        "path": "https://raw.githubusercontent.com/stac-utils/pystac/main/tests/data-files/examples/0.9.0/collection-spec/examples/landsat-collection.json",
        "schema": [
            "https://cdn.staclint.com/v0.9.0/collection.json"
        ],
        "valid_stac": true,
        "asset_type": "COLLECTION",
        "validation_method": "default"
    }
]
```

**Local file**

```python
from stac_validator import stac_validator

stac = stac_validator.StacValidate("tests/test_data/1beta1/sentinel2.json", extensions=True)
stac.run()
print(stac.message)
```
```python
[
    {
        "version": "1.0.0-beta.1",
        "path": "tests/test_data/1beta1/sentinel2.json",
        "schema": [
            "https://cdn.staclint.com/v1.0.0-beta.1/collection.json"
        ],
        "valid_stac": true,
        "asset_type": "COLLECTION",
        "validation_method": "extensions"
    }
]
```

**Dictionary**

```python
from stac_validator import stac_validator

stac = stac_validator.StacValidate()
stac.validate_dict(dictionary)
print(stac.message)
```

Set schema cache size
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

Schema caching is process-wide and configured separately from `StacValidate` instantiation.

The default is 256.

That comes from utilities.py, where `DEFAULT_SCHEMA_CACHE_SIZE = 256`.

For the README, I would state it plainly in the new cache section:

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



**Item Collection**

```python
from stac_validator import stac_validator

stac = stac_validator.StacValidate()
stac.validate_item_collection_dict(item_collection_dict)
print(stac.message)
```

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

<p align="left">
  <a href="https://healy-hyperspatial.github.io/"><img src="https://raw.githubusercontent.com/stac-utils/stac-fastapi-elasticsearch-opensearch/refs/heads/main/assets/hh-logo-blue.png" alt="Healy Hyperspatial" height="100" hspace="20"></a>
  <a href="https://radiant.earth/"><img src="assets/radiant-earth.webp" alt="Radiant Earth Foundation" height="100" hspace="20"></a>
  <a href="https://sparkgeo.com/"><img src="assets/sparkgeo_logo.jpeg" alt="Sparkgeo" height="100" hspace="20"></a>
</p>


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache License 2.0.

# STAC Validator Change Log

All notable changes to this project will be documented in this file.

The format is (loosely) based on [Keep a Changelog](http://keepachangelog.com/) and this project adheres to [Semantic Versioning](http://semver.org/).

## [Unreleased]

### Added

### Changed

### Fixed

### Removed

### Updated

## [v4.1.0] - 2026-04-01

### Added

- Added benchmark_validation.py script for comparing batch vs legacy validation performance [#274](https://github.com/stac-utils/stac-validator/pull/274)

- Added `--batch-size` option to `batch` command for configurable chunk processing (default: 2000) [#274](https://github.com/stac-utils/stac-validator/pull/274)


### Changed

- Implemented compiled validator caching using `@functools.lru_cache` to avoid recompiling JSON schemas [#274](https://github.com/stac-utils/stac-validator/pull/274)

- Implemented direct dictionary passing to worker processes via pickle instead of temp file I/O [#274](https://github.com/stac-utils/stac-validator/pull/274)

- Implemented pre-warming of schema cache before forking worker processes via Copy-on-Write [#274](https://github.com/stac-utils/stac-validator/pull/274)

- Allow both `--feature-collection` and `--item-collection` in `batch` and `validate` command interface [#274](https://github.com/stac-utils/stac-validator/pull/274)

- Updated batch command output format to match validate command, including all fields: version, path, schema, error_type, error_message, failed_schema, recommendation [#274](https://github.com/stac-utils/stac-validator/pull/274)

- Unified validator cache control with `--schema-cache-size` option to control both fetch/parse and compiled validator caching [#274](https://github.com/stac-utils/stac-validator/pull/274)

- Added input validation for `--batch-size` option (minimum value: 1) [#274](https://github.com/stac-utils/stac-validator/pull/274)

### Fixed

- Fixed batch command error grouping to work with new validation message format [#274](https://github.com/stac-utils/stac-validator/pull/274)

- Fixed validator cache to respect runtime `--schema-cache-size` changes via dynamic cache builder [#274](https://github.com/stac-utils/stac-validator/pull/274)

## [v4.0.1] - 2026-03-31

### Updated

- Added special message about collection link missing from STAC items [#272](https://github.com/stac-utils/stac-validator/pull/272)

### Fixed

- Fixed concurrency issue with using set schema size from core validator [#272](https://github.com/stac-utils/stac-validator/pull/272)

## [v4.0.0] - 2026-03-30

### Added

- **Batch Validation with Multiprocessing:** New `stac-validator batch` command for concurrent validation of multiple STAC files using all available CPU cores. Provides 10-100x performance improvement over single-threaded validation.
  - Auto-detection of available CPU cores with Docker/container awareness via `os.sched_getaffinity()`
  - Per-worker schema caching with LRU eviction for optimal memory usage (configurable via `--schema-cache-size`, default 16 schemas per worker)
  - Optional `--cores` flag for manual core specification (supports negative values to reserve cores for OS)
  - Optional `--feature-collection` flag to validate GeoJSON FeatureCollections by extracting and validating each feature individually
  - Optional `--schema-cache-size` flag to configure schema cache size per worker or disable caching entirely
  - Progress bar with `tqdm` (can be disabled with `--no-progress`)
  - JSON output with validation summary statistics

- **Python API for Batch Validation:** New functions in `stac_validator.batch_validator` module
  - `validate_concurrently()` - Validate files with multiprocessing
  - `validate_dicts()` - Validate list of STAC item dictionaries (handles temp files internally)
  - `get_optimal_worker_count()` - Auto-detect CPU cores with Docker awareness

- **Comprehensive Test Suite:** 16 new tests covering batch validation
  - 12 batch validator tests (worker count, concurrency, FeatureCollections, dict validation)
  - 4 CLI sys_exit tests (new subcommand structure)

- **Documentation:**
  - First-class README section on batch validation with architecture, usage, and examples
  - Batch Validation as top-level section in Table of Contents
  - Python API examples for `validate_concurrently()` and `validate_dicts()`

### Changed

- **CLI Structure:** Refactored CLI to use explicit subcommands for clarity
  - Old style: `stac-validator <file>` → New style: `stac-validator validate <file>`
  - New batch command: `stac-validator batch <files> [options]`
  - Updated all tests to use new subcommand structure
  - Updated help text to document both validate and batch commands

## [v3.11.0] - 2026-03-27

### Added 

- Added a new CLI option --schema-cache-size to control the in-memory schema cache size at runtime.
- Added support for setting schema cache size to 0 to disable schema caching for low-memory environments.

### Changed 

- Refactored schema caching to support runtime cache reconfiguration while preserving cache inspection and clearing behavior.
- Added test coverage for:
  - runtime schema cache size reconfiguration
  - zero-size cache behavior
  - negative cache size validation
  - CLI acceptance of --schema-cache-size


## [v3.10.2] - 2025-11-16

### Fixed
- Added validation for STAC version format to provide clear error messages when stac_version field is missing, empty, or incorrectly formatted (e.g., "1.1" instead of "1.1.0"). [#268](https://github.com/stac-utils/stac-validator/pull/268)

### Changed
- Migrated from `setup.py` to modern `pyproject.toml` packaging (PEP 621), removing legacy `requirements-dev.txt` file. [#268](https://github.com/stac-utils/stac-validator/pull/268)

## [v3.10.1] - 2025-07-26

### Fixed
- Reverted path cleaning changes that removed `./` prefix from relative paths, which was causing compatibility issues with tools like stac-check. The validator now correctly preserves the `./` prefix for relative paths in the current directory. [#266](https://github.com/stac-utils/stac-validator/pull/266)

## [v3.10.0] - 2025-07-20

### Added
- Added detailed recursive validation summary showing validation counts by STAC object type (Catalog, Collection, etc.) [#265](https://github.com/stac-utils/stac-validator/pull/265)
- Added validation duration timing that shows total processing time in a human-readable format [#265](https://github.com/stac-utils/stac-validator/pull/265)
- Added support for pydantic validation in recursive mode with proper schema reporting [#265](https://github.com/stac-utils/stac-validator/pull/265)

### Changed
- Standardized summary output formatting across all validation modes for consistency [#265](https://github.com/stac-utils/stac-validator/pull/265)

## [v3.9.3] - 2025-06-28

### Changed
- Improved path resolution in recursive validation to handle relative paths more reliably, especially in GitHub repository structures [#264](https://github.com/stac-utils/stac-validator/pull/264)

### Fixed
- Fixed issue where validator would get confused by repository structure when validating catalogs with relative paths [#264](https://github.com/stac-utils/stac-validator/pull/264)
- Cleaned up path output by removing unnecessary `./` components from displayed paths [#264](https://github.com/stac-utils/stac-validator/pull/264)

### Removed

## [v3.9.2] - 2025-06-18

### Fixed
- Fixed missing item id in the url path with --item-collection output [#263](https://github.com/stac-utils/stac-validator/pull/263)

## [v3.9.1] - 2025-06-13

### Added
- `failed_schema` field to error messages for easier error handling [#260](https://github.com/stac-utils/stac-validator/pull/260)
- `recommendation` field to --verbose mode [#260](https://github.com/stac-utils/stac-validator/pull/260)

## [v3.9.0] - 2025-06-13

### Added
- Added separate `recommendation` field in error messages when running in non-verbose mode [#257](https://github.com/stac-utils/stac-validator/pull/257)
- Verbose error messages for JSONSchemaValidationErrors [#257](https://github.com/stac-utils/stac-validator/pull/257)

### Changed
- Changed --verbose for recursive mode to --trace-recursive to make way for more comprehensive error messaging [#257](https://github.com/stac-utils/stac-validator/pull/257)

## [v3.8.1] - 2025-06-04

### Fixed
- Fixed the pydantic extra dependency in setup.py to properly install stac-pydantic when using `pip install stac-validator[pydantic]` [#254](https://github.com/stac-utils/stac-validator/pull/254)

## [v3.8.0] - 2025-06-03

### Added

- Added `--schema-config` option to specify a YAML or JSON configuration file that maps remote schema URLs to local file paths, making it easier to validate against multiple local schemas, allowing offline validation and improved performance [#253](https://github.com/stac-utils/stac-validator/pull/253)

## [v3.7.0] - 2025-05-30

### Added

- Added a comprehensive Table of Contents to README.md [#247](https://github.com/stac-utils/stac-validator/pull/247)
- Added Sponsors and Supporters section to README.md with organizational logos and acknowledgments [#247](https://github.com/stac-utils/stac-validator/pull/247)
- Added `--pydantic` option for validating STAC objects using stac-pydantic models, providing enhanced type checking and validation [#249](https://github.com/stac-utils/stac-validator/pull/249)
- Added optional dependency for stac-pydantic that can be installed with `pip install stac-validator[pydantic]` [#249](https://github.com/stac-utils/stac-validator/pull/249)
- Added GitHub Actions workflow for automatically building and deploying documentation to GitHub Pages [#250](https://github.com/stac-utils/stac-validator/pull/250)

### Changed

- Reformatted and restructured the README.md for improved readability and organization [#247](https://github.com/stac-utils/stac-validator/pull/247)
- Migrated documentation from Read the Docs to GitHub Pages for better integration with the repository [#250](https://github.com/stac-utils/stac-validator/pull/250)
- Updated documentation system to use Sphinx with MyST parser for improved Markdown support [#250](https://github.com/stac-utils/stac-validator/pull/250)
- Enhanced documentation to include content directly from README.md for consistency [#250](https://github.com/stac-utils/stac-validator/pull/250)

## [v3.6.0] - 2025-03-25

### Added

- If a validation error occurs in recursive mode only show the invalid items unless verbose mode is on. [#243](https://github.com/stac-utils/stac-validator/pull/243)
- Added ability to validate extensions of Collections [#243](https://github.com/stac-utils/stac-validator/pull/243)
- Improve error reporting through use of [best_match](https://python-jsonschema.readthedocs.io/en/stable/errors/#best-match-and-relevance) [#243](https://github.com/stac-utils/stac-validator/pull/243)
- Add `schema-map` option similar to [stac-node-validator SchemaMap](https://github.com/stac-utils/stac-node-validator?tab=readme-ov-file#usage) to allow validation against local copies of schemas. [#243](https://github.com/stac-utils/stac-validator/pull/243)

## [v3.5.0] - 2025-01-10

### Added

- Added publish.yml to automatically publish new releases to PyPI [#236](https://github.com/stac-utils/stac-validator/pull/236)
- Configure whether to open URLs when validating assets [#238](https://github.com/stac-utils/stac-validator/pull/238)
- Allow to provide HTTP headers [#239](https://github.com/stac-utils/stac-validator/pull/239)

### Changed

- Switched to the referencing library for dynamic JSON schema validation and reference resolution [#241](https://github.com/stac-utils/stac-validator/pull/241)

## [v3.4.0] - 2024-10-08

### Added

- Added ability to validate response from a /collections endpoint [#220](https://github.com/stac-utils/stac-validator/issues/220)
- Added mypy to pre-commit config ([#229](https://github.com/stac-utils/stac-validator/pull/224))
- Support for stac spec version 1.1.0 [#235](https://github.com/stac-utils/stac-validator/pull/235)

## [v3.3.2] - 2023-11-17

### Added

- Docstrings ([#224](https://github.com/stac-utils/stac-validator/pull/224))

### Changed

- Development dependencies removed from runtime dependency list
  ([#228](https://github.com/stac-utils/stac-check/pull/109))
- Remove jsonschema RefResolver ([#228](https://github.com/stac-utils/stac-check/pull/109)

## [v3.3.1] - 2022-12-16

### Fixed

- Moved --verbose messaging for --recursive as --verbose was printing out the wrong messages https://github.com/stac-utils/stac-validator/pull/222

## [v3.3.0] - 2022-11-28

### Added

- Added --item-collection to validate local and remote item collections https://github.com/stac-utils/stac-validator/pull/219
- Added --pages to validate additional items retrieved via pagination links https://github.com/stac-utils/stac-validator/pull/219

## [v3.2.0] - 2022-09-20

### Added

- Added ability to check local schemas in item extensions https://github.com/stac-utils/stac-validator/pull/215
- Added an example on validating a dictionary https://github.com/stac-utils/stac-validator/pull/215

### Changed

- Changed 'ValidationError' error type to 'JSONSchemaValidationError' https://github.com/stac-utils/stac-validator/pull/213

## [v3.1.0] - 2022-04-28

### Added

- Added update stac version message to cli output https://github.com/stac-utils/stac-validator/pull/211

### Fixed

- Reordered exception handlers to avoid unreachable code https://github.com/stac-utils/stac-validator/pull/203/
- Details about invalid items are shown in the message when in recursive mode https://github.com/stac-utils/stac-validator/pull/202/
- Dockerfile - change cli command from stac_validator to stac-validator https://github.com/stac-utils/stac-validator/pull/201/
- Items with no assets key can still be valid https://github.com/stac-utils/stac-validator/pull/206
- Top-level `is_valid` flag for recursive JSONSchema exceptions https://github.com/stac-utils/stac-validator/pull/208

### Removed

- Stac-check linting as it creates a circular dependency https://github.com/stac-utils/stac-validator/pull/209
- Remove v0.7.0 test data and v0.7.0 local tests https://github.com/stac-utils/stac-validator/pull/210
- Removed pystac from dependencies https://github.com/stac-utils/stac-validator/pull/210

## [v3.0.0] - 2022-03-11

### Added

- A note about full recursion to the `--max-depth` help text

### Fixed

- Item messages are now included even if `max_depth is None`
- Exit with non-zero code when validation fails

### Removed

- References to Python 3.6

## [v2.5.0] - 2022-03-10

### Changed

- Split the `--recursive` option into a `--recursive` flag and a `--max-depth` option
- Renamed the entry point from `stac_validator` to `stac-validator`

## [v2.4.3] - 2022-03-10

### Changed

- Add schema caching

## [v2.4.2] - 2022-03-02

### Changed

- Loosen pystac version dependency

## [v2.4.1] - 2022-03-02

### Changed

- Loosen stac-check version dependency

## [v2.4.0] - 2022-02-02

### Added

- Linting option in cli to display stac-check generated information

## [v2.3.0] - 2021-08-31 - 2021-11-28

### Added

- Added --links option to validate links on format and a valid response
- Added --assets option to validate assets on format and and a valid response
- Added test_links.py
- Added v1.0.0 STAC examples from radiant earth github
- Added v1.0.0 examples to tests

### Changed

- Upgraded pystac to 1.1.0 from 0.5.6
- Moved tests for cli options out of test_stac_validator into individual files
- Moved utilities to utilities.py
- Moved backend to validate.py

## [v2.2.0] - 2021-05-25

### Added

- Added Support for STAC 1.0.0
- Added more tests for STAC 1.0.0-rc.4
- Option to pass stac dictionary into validator in python with new stac_dict method

### Changed

- Moved std out to cli so that it doesn't display in pure python applications
- Added Pypi badges to readme

## [v2.1.0] - 2021-05-06

### Added

- Added more tests for STAC 1.0.0-rc.3
- Added basic support for rc.4
- Add system exit code to CLI. see #144

### Changed

- Modified how Lambda CDK is built

## [v2.0.0] - 2021-04-28

### Added

- Stac versions from 0.8.0 --> 1.0.0-rc.3 are now supported.
- Version is detected automatically.
- Default validation attempts to validate a core Stac object as well as any extensions.
- Recursion which was previously handled by Pystac is now done natively with both a depth option to limit the time it takes to validate and a verbose option to display output as individual objects are being validated one by one.
- Added AWS CDK deployment example.
- Added FastAPI routing to CDK deployment.

### Changed

- Pystac is now only being used to identify stac objects. Jsonschema is being used for all other validation.
- The cli library was changed from Docopt to Click.
- Custom validation was updated to allow for local schemas.

### Removed

- The force, legacy, version, and update methods were removed.
- stac versions where a `stac_version` field is not present are
  no longer supported.

## [v1.0.1] - 2020-09-01

### Added

- The ability (--update) to update a STAC object. This is based on migrate from pystac. It doesn't always work. Frequently it does. Presently it tries to update to version 1.0.0-beta.2
- A function to display what has changed via --update. This is represented in the logs as diff.
- A --force option. This updates the stac_version to v0.9.0 and adds an id field as older STAC versions seem to be missing this sometimes. This seems to be especially effective with objects as old as 0.6.0 and 0.6.1
- An option (--version) to specify and set a specific version to validate against.
- The --extension option. This uses pystac validation to validate against various extension schemas.
- The ExtensionError, as inputing a bad value for extension caused validation in pystac to be bypassed.
- The VersionError, as inputing a bad value for version was causing validation in pystac to be bypassed as well.
- The --recursive option. This uses validate_all from pystac to recursively search the links from a catalog or collection.
- The ability (--core) to validate against the core only. This is provided by pystac.
- (--legacy). This validates agains schemas from v0.4.0 to v1.0.0-beta.1 Legacy must be accompanied by --version.
- valid_versions for --legacy are: 'v0.4.0', 'v0.4.1', 'v0.5.0', 'v0.5.1', 'v0.5.2', 'v0.6.0', 'v0.6.0-rc1',
  'v0.6.0-rc2', 'v0.6.1', 'v0.6.2', 'v0.7.0', 'v0.8.0', 'v0.8.0-rc1', 'v0.8.1', 'v0.9.0',
  'v0.9.0-rc1', 'v0.9.0-rc2', and 'v1.0.0-beta.1'
- (--custom). Validate against a custom schema
- Tests to explore new functionality.

### Changed

- Updated core validation to use validation from pystac instead of jsonchema.
- With the newest version - 1.0.0-beta.2 - items will run through jsonchema validation before the PySTAC validation. The reason for this is that jsonschema will give more informative error messages. This should be addressed better in the future. This is not the case with the --recursive option as time can be a concern here with larger collections.
- Logging. Various additions were made here depending on the options selected. This was done to help assist people to update their STAC collections.

[Unreleased]: https://github.com/sparkgeo/stac-validator/compare/v4.1.0..main
[v4.1.0]: https://github.com/sparkgeo/stac-validator/compare/v4.0.1..v4.1.0
[v4.0.1]: https://github.com/sparkgeo/stac-validator/compare/v4.0.0..v4.0.1
[v4.0.0]: https://github.com/sparkgeo/stac-validator/compare/v3.11.0..v4.0.0
[v3.11.0]: https://github.com/sparkgeo/stac-validator/compare/v3.10.2..v3.11.0
[v3.10.2]: https://github.com/sparkgeo/stac-validator/compare/v3.10.1..v3.10.2
[v3.10.1]: https://github.com/sparkgeo/stac-validator/compare/v3.10.0..v3.10.1
[v3.10.0]: https://github.com/sparkgeo/stac-validator/compare/v3.9.3..v3.10.0
[v3.9.3]: https://github.com/sparkgeo/stac-validator/compare/v3.9.2..v3.9.3
[v3.9.2]: https://github.com/sparkgeo/stac-validator/compare/v3.9.1..v3.9.2
[v3.9.1]: https://github.com/sparkgeo/stac-validator/compare/v3.9.0..v3.9.1
[v3.9.0]: https://github.com/sparkgeo/stac-validator/compare/v3.8.1..v3.9.0
[v3.8.1]: https://github.com/sparkgeo/stac-validator/compare/v3.8.0..v3.8.1
[v3.8.0]: https://github.com/sparkgeo/stac-validator/compare/v3.7.0..v3.8.0
[v3.7.0]: https://github.com/sparkgeo/stac-validator/compare/v3.6.0..v3.7.0
[v3.6.0]: https://github.com/sparkgeo/stac-validator/compare/v3.5.0..v3.6.0
[v3.5.0]: https://github.com/sparkgeo/stac-validator/compare/v3.4.0..v3.5.0
[v3.4.0]: https://github.com/sparkgeo/stac-validator/compare/v3.3.2..v3.4.0
[v3.3.2]: https://github.com/sparkgeo/stac-validator/compare/v3.3.1..v3.3.2
[v3.3.1]: https://github.com/sparkgeo/stac-validator/compare/v3.3.0..v3.3.1
[v3.3.0]: https://github.com/sparkgeo/stac-validator/compare/v3.2.0..v3.3.0
[v3.2.0]: https://github.com/sparkgeo/stac-validator/compare/v3.1.0..v3.2.0
[v3.1.0]: https://github.com/sparkgeo/stac-validator/compare/v3.0.0..v3.1.0
[v3.0.0]: https://github.com/sparkgeo/stac-validator/compare/v2.5.0..v3.0.0
[v2.5.0]: https://github.com/sparkgeo/stac-validator/compare/v2.4.3..v2.5.0
[v2.4.3]: https://github.com/sparkgeo/stac-validator/compare/v2.3.0..v2.4.0
[v2.4.2]: https://github.com/sparkgeo/stac-validator/compare/v2.4.1..v2.4.2
[v2.4.1]: https://github.com/sparkgeo/stac-validator/compare/v2.4.0..v2.4.1
[v2.4.0]: https://github.com/sparkgeo/stac-validator/compare/v2.3.0..v2.4.0
[v2.3.0]: https://github.com/sparkgeo/stac-validator/compare/v2.2.0..v2.3.0
[v2.2.0]: https://github.com/sparkgeo/stac-validator/compare/v2.1.0..v2.2.0
[v2.1.0]: https://github.com/sparkgeo/stac-validator/compare/v2.0.0..v2.1.0
[v2.0.0]: https://github.com/sparkgeo/stac-validator/compare/v1.0.1..v2.0.0
[v1.0.1]: https://github.com/sparkgeo/stac-validator/compare/v0.5.0..v1.0.1
[v0.5.0]: https://github.com/sparkgeo/stac-validator/compare/v0.1.3..v0.5.0
[v0.1.3]: https://github.com/sparkgeo/stac-validator/compare/v0.1.1..v0.1.3
[v0.1.1]: https://github.com/sparkgeo/stac-validator/compare/v0.1.0..v0.1.1
[v0.1.0]: https://github.com/sparkgeo/stac-validator/releases/tag/v0.1.0

"""Concurrent batch validation of STAC files using multiprocessing."""

import concurrent.futures
import json
import multiprocessing
from itertools import islice
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .utilities import _build_cached_validator
from .validate import StacValidate


def _warm_schema_cache() -> None:
    """
    Pre-warm the schema cache before forking worker processes.

    This function loads and compiles core STAC schemas in the main process.
    When ProcessPoolExecutor forks child processes, they inherit the parent's
    memory via Copy-on-Write (CoW), so all workers get a fully-warmed cache
    without making any network requests.

    Core schemas warmed:
    - STAC Item (v1.0.0)
    - STAC Collection (v1.0.0)
    - STAC Catalog (v1.0.0)
    """
    try:
        # Core STAC schema URLs that are commonly used
        core_schemas = [
            "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/item.json",
            "https://schemas.stacspec.org/v1.0.0/collection-spec/v1.0.0/collection.json",
            "https://schemas.stacspec.org/v1.0.0/catalog-spec/v1.0.0/catalog.json",
        ]

        from .utilities import fetch_and_parse_schema

        # Fetch and parse each schema to populate the cache
        for schema_url in core_schemas:
            try:
                schema = fetch_and_parse_schema(schema_url)
                # Convert to JSON string and cache via _build_cached_validator
                schema_json = json.dumps(schema, sort_keys=True, separators=(",", ":"))
                _build_cached_validator(schema_json)
            except Exception:
                # If a schema fails to load, continue with others
                # This ensures partial cache warming even if some schemas are unavailable
                pass
    except Exception:
        # If cache warming fails entirely, continue without it
        # The validators will still work, just without the pre-warmed cache
        pass


def get_optimal_worker_count(max_workers: Optional[int] = None) -> int:
    """
    Get the optimal number of worker processes.

    Detects available CPU cores, accounting for containerized environments.
    Falls back to os.sched_getaffinity() on Linux for Docker/container support.

    Args:
        max_workers: Maximum number of workers to use. Options:
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
    import os as os_module

    # Try to get container-aware core count on Linux
    try:
        if hasattr(os_module, "sched_getaffinity"):
            # Linux: respects Docker/container CPU limits
            total_cores = len(os_module.sched_getaffinity(0))
        else:
            # Fallback for non-Linux systems
            total_cores = multiprocessing.cpu_count()
    except Exception:
        # Fallback if anything goes wrong
        total_cores = multiprocessing.cpu_count()

    if max_workers is None or max_workers == 0:
        # Use all available cores
        return total_cores
    elif max_workers < 0:
        # Use all cores minus the specified amount (useful for reserving cores for OS)
        return max(1, total_cores + max_workers)
    else:
        # Use the specified number, but cap at available cores
        return min(max_workers, total_cores)


def _validate_single_file(file_path: str) -> Tuple[str, bool, List[str]]:
    """
    Worker function that runs on an individual CPU core.
    Validates a single STAC file and returns results.

    Each worker process has its own isolated schema cache for optimal performance.

    Args:
        file_path: Path to the STAC JSON file to validate.

    Returns:
        Tuple of (file_path, is_valid, list_of_errors)
    """
    errors = []

    try:
        # Use StacValidate for comprehensive validation (includes version check, core, and extensions)
        # Each worker process has its own isolated schema cache (no need to reconfigure)
        validator = StacValidate(file_path)
        validator.run()

        # Collect errors from validation
        # validator.message is a list of result objects
        if validator.message:
            try:
                messages = validator.message
                if isinstance(messages, list) and len(messages) > 0:
                    msg_obj = messages[0]
                    if not msg_obj.get("valid_stac", False):
                        # Try multiple error field names
                        if "errors" in msg_obj:
                            errors.extend(msg_obj["errors"])
                        elif "error_message" in msg_obj:
                            errors.append(msg_obj["error_message"])
                        else:
                            errors.append(
                                f"{msg_obj.get('error_type', 'ValidationError')}"
                            )
            except (KeyError, IndexError, TypeError):
                # If we can't parse, just use the raw message
                if validator.message:
                    errors.append(str(validator.message))

    except Exception as e:
        # Catch any exception including StacValidate instantiation failures
        # This prevents UnboundLocalError if validator creation fails
        return file_path, False, [f"Critical error processing file: {str(e)}"]

    is_valid = len(errors) == 0
    return file_path, is_valid, errors


def _validate_dict(
    item_dict: Dict[str, Any], source_path: str
) -> Tuple[str, bool, List[str]]:
    """
    Worker function that validates a STAC item dictionary directly (no temp files).

    This function receives pickled dictionaries from the main process, avoiding
    expensive disk I/O. Each worker process has its own isolated schema cache.

    Args:
        item_dict: Dictionary representation of a STAC item to validate.
        source_path: Display path for result reporting (e.g., "file.json[0]").

    Returns:
        Tuple of (source_path, is_valid, list_of_errors)
    """
    errors = []

    try:
        # Validate the dictionary directly without writing to disk
        # StacValidate can accept a dict via validate_dict() method
        validator = StacValidate()
        validator.stac_content = item_dict

        # Set STAC version from item
        validator.version = item_dict.get("stac_version", "1.0.0")

        # Run validation on the dictionary
        validator.validate_dict(item_dict)

        # Collect errors from validation
        if validator.message:
            try:
                messages = validator.message
                if isinstance(messages, list) and len(messages) > 0:
                    msg_obj = messages[0]
                    if not msg_obj.get("valid_stac", False):
                        # Try multiple error field names
                        if "errors" in msg_obj:
                            errors.extend(msg_obj["errors"])
                        elif "error_message" in msg_obj:
                            errors.append(msg_obj["error_message"])
                        else:
                            errors.append(
                                f"{msg_obj.get('error_type', 'ValidationError')}"
                            )
            except (KeyError, IndexError, TypeError):
                # If we can't parse, just use the raw message
                if validator.message:
                    errors.append(str(validator.message))

    except Exception as e:
        # Catch any exception during validation
        return source_path, False, [f"Critical error processing item: {str(e)}"]

    is_valid = len(errors) == 0
    return source_path, is_valid, errors


def validate_concurrently(
    file_paths: List[str],
    max_workers: Optional[int] = None,
    show_progress: bool = True,
    feature_collection: bool = False,
    batch_size: int = 2000,
) -> List[Dict[str, Any]]:
    """
    Validates a list of STAC files concurrently using available CPU cores.

    Uses ProcessPoolExecutor to bypass Python's GIL by creating separate Python
    processes for each worker. Pre-warms the schema cache in the main process
    before forking, so all workers inherit a fully-populated cache via Copy-on-Write.

    Args:
        file_paths: List of paths to STAC JSON files or FeatureCollections.
        max_workers: Number of CPU cores to use. Options:
            - None or 0: Use all available cores (default)
            - Positive int: Use that many cores (capped at available)
            - Negative int: Use all cores minus that many (e.g., -1 = all cores - 1)
        show_progress: Whether to display a progress bar (requires tqdm).
        feature_collection: If True, treat files as FeatureCollections and validate each feature.
        batch_size: Number of items to process at a time to bound memory usage (default: 2000).

    Returns:
        List of result dictionaries with keys: path, valid_stac, errors
    """
    # Pre-warm the schema cache in the main process before forking workers
    # This leverages Copy-on-Write so all workers inherit the warmed cache
    _warm_schema_cache()

    # If feature_collection mode, extract features and delegate to validate_dicts
    # for memory-safe chunked processing
    if feature_collection:
        error_results: List[Dict[str, Any]] = []

        def item_iter() -> Iterable[Dict[str, Any]]:
            """
            Lazily iterate over all items (features or standalone objects)
            from the provided file_paths, annotating each with source
            metadata. Any file-level read/parse errors are recorded in
            error_results and skipped.
            """
            for file_path in file_paths:
                try:
                    with open(file_path, "r") as f:
                        data = json.load(f)

                    # Check if it's a FeatureCollection
                    if (
                        isinstance(data, dict)
                        and data.get("type") == "FeatureCollection"
                    ):
                        features = data.get("features", [])
                        for idx, feature in enumerate(features):
                            # Attach source info for result display
                            feature["__source_file__"] = file_path
                            feature["__feature_index__"] = idx
                            yield feature
                    else:
                        # Regular file, treat as single item
                        data["__source_file__"] = file_path
                        data["__feature_index__"] = None
                        yield data

                except Exception as e:
                    # Accumulate error for this file and continue processing others
                    error_results.append(
                        {
                            "path": file_path,
                            "valid_stac": False,
                            "errors": [f"Failed to read file: {str(e)}"],
                        }
                    )

        # Delegate to validate_dicts for chunked, memory-safe processing
        validation_results = validate_dicts(
            item_iter(),
            max_workers=max_workers,
            show_progress=show_progress,
            chunk_size=batch_size,
        )

        # Combine error results with validation results
        return error_results + validation_results

    # Standard file path validation (no FeatureCollection expansion)
    results: List[Dict[str, Any]] = []

    try:
        from tqdm import tqdm

        has_tqdm = True
    except ImportError:
        has_tqdm = False
        show_progress = False

    optimal_workers = get_optimal_worker_count(max_workers)

    if not file_paths:
        return results

    try:
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=optimal_workers
        ) as executor:

            # Submit all tasks to the pool
            future_to_file = {
                executor.submit(_validate_single_file, path): path
                for path in file_paths
            }

            # Wrap the as_completed iterator with tqdm for a nice progress bar
            iterator = concurrent.futures.as_completed(future_to_file)
            if show_progress and has_tqdm:
                iterator = tqdm(  # type: ignore
                    iterator,
                    total=len(file_paths),
                    desc="Validating STAC Items",
                )

            # Collect results as they finish
            for future in iterator:
                file_path, is_valid, errors = future.result()

                result = {
                    "path": file_path,
                    "valid_stac": is_valid,
                }

                if errors:
                    result["errors"] = errors

                results.append(result)

    finally:
        pass

    return results


def _chunked_iterable(iterable: Iterable, size: int):
    """Yield successive n-sized chunks from an iterable."""
    it = iter(iterable)
    while True:
        chunk = list(islice(it, size))
        if not chunk:
            break
        yield chunk


def validate_dicts(
    items: Iterable[Dict[str, Any]],
    max_workers: Optional[int] = None,
    show_progress: bool = True,
    chunk_size: int = 2000,
) -> List[Dict[str, Any]]:
    """
    Validate an iterable of STAC item dictionaries concurrently.

    Passes dictionaries directly to worker processes via pickle (memory-based),
    avoiding expensive disk I/O. Pre-warms the schema cache in the main process
    before forking, so all workers inherit a fully-populated cache via Copy-on-Write.
    Processes items in bounded chunks to prevent out-of-memory errors.

    Args:
        items: Iterable of STAC item dictionaries to validate
        max_workers: Maximum number of worker processes. Options:
            - None or 0: Use all available cores (default)
            - Positive int: Use that many cores (capped at available)
            - Negative int: Use all cores minus that many
        show_progress: Whether to show progress bar (default: True)
        chunk_size: Number of items to process at a time to bound memory usage.

    Returns:
        List of validation results with path, valid_stac, and errors (if any)
    """
    # Pre-warm the schema cache in the main process before forking workers
    # This leverages Copy-on-Write so all workers inherit the warmed cache
    _warm_schema_cache()

    all_results = []

    try:
        from tqdm import tqdm

        has_tqdm = True
    except ImportError:
        has_tqdm = False
        show_progress = False

    optimal_workers = get_optimal_worker_count(max_workers)

    # Process items in bounded chunks to protect memory
    for chunk in _chunked_iterable(items, chunk_size):
        chunk_list = list(chunk)
        if not chunk_list:
            continue

        try:
            with concurrent.futures.ProcessPoolExecutor(
                max_workers=optimal_workers
            ) as executor:
                # Submit all items in chunk to the pool
                # Pass dictionaries directly via pickle (no temp files)
                future_to_item = {}
                for idx, item in enumerate(chunk_list):
                    # Extract source metadata if present
                    source_file = item.get("__source_file__")
                    feature_index = item.get("__feature_index__")

                    # Create display path for results
                    if source_file is not None:
                        display_path = (
                            f"{source_file}[{feature_index}]"
                            if feature_index is not None
                            else source_file
                        )
                    else:
                        display_path = f"item-{idx}"

                    # Create payload without internal metadata keys
                    payload = {
                        k: v
                        for k, v in item.items()
                        if k not in ("__source_file__", "__feature_index__")
                    }

                    # Submit to worker - dictionary is pickled automatically
                    future = executor.submit(_validate_dict, payload, display_path)
                    future_to_item[future] = (display_path, idx)

                # Wrap iterator with tqdm for progress bar
                iterator = concurrent.futures.as_completed(future_to_item)
                if show_progress and has_tqdm:
                    iterator = tqdm(  # type: ignore
                        iterator,
                        total=len(chunk_list),
                        desc="Validating Items",
                        unit="item",
                    )

                # Collect results as they finish
                for future in iterator:
                    display_path, idx = future_to_item[future]
                    source_path, is_valid, errors = future.result()

                    result = {
                        "path": source_path,
                        "valid_stac": is_valid,
                    }

                    if errors:
                        result["errors"] = errors

                    all_results.append(result)

        except Exception as e:
            # If chunk processing fails, record error for all items in chunk
            for idx, item in enumerate(chunk_list):
                source_file = item.get("__source_file__")
                feature_index = item.get("__feature_index__")

                if source_file is not None:
                    display_path = (
                        f"{source_file}[{feature_index}]"
                        if feature_index is not None
                        else source_file
                    )
                else:
                    display_path = f"item-{idx}"

                all_results.append(
                    {
                        "path": display_path,
                        "valid_stac": False,
                        "errors": [f"Chunk processing error: {str(e)}"],
                    }
                )

    return all_results

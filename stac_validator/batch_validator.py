"""Concurrent batch validation of STAC files using multiprocessing."""

import concurrent.futures
import json
import multiprocessing
import os
import tempfile
from itertools import islice
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .validate import StacValidate


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
    import os

    # Try to get container-aware core count on Linux
    try:
        if hasattr(os, "sched_getaffinity"):
            # Linux: respects Docker/container CPU limits
            total_cores = len(os.sched_getaffinity(0))
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

    Args:
        file_path: Path to the STAC JSON file to validate.

    Returns:
        Tuple of (file_path, is_valid, list_of_errors)
    """
    errors = []

    try:
        # Use StacValidate for comprehensive validation (includes version check, core, and extensions)
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
        return file_path, False, [f"Critical error processing file: {str(e)}"]

    is_valid = len(errors) == 0
    return file_path, is_valid, errors


def validate_concurrently(
    file_paths: List[str],
    max_workers: Optional[int] = None,
    show_progress: bool = True,
    feature_collection: bool = False,
) -> List[Dict[str, Any]]:
    """
    Validates a list of STAC files concurrently using available CPU cores.

    Uses ProcessPoolExecutor to bypass Python's GIL by creating separate Python
    processes for each worker. Each core gets its own schema cache, which is
    warmed up on the first file and then reused for subsequent files.

    Args:
        file_paths: List of paths to STAC JSON files or FeatureCollections.
        max_workers: Number of CPU cores to use. Options:
            - None or 0: Use all available cores (default)
            - Positive int: Use that many cores (capped at available)
            - Negative int: Use all cores minus that many (e.g., -1 = all cores - 1)
        show_progress: Whether to display a progress bar (requires tqdm).
        feature_collection: If True, treat files as FeatureCollections and validate each feature.

    Returns:
        List of result dictionaries with keys: path, valid_stac, errors
    """
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
    chunk_size: int = 1000,
) -> List[Dict[str, Any]]:
    """
    Validate an iterable of STAC item dictionaries concurrently.

    Internally writes dictionaries to temporary files in bounded chunks for
    concurrent validation, preventing both out-of-memory (OOM) errors and
    disk/inode exhaustion in containerized environments.

    Args:
        items: Iterable of STAC item dictionaries to validate
        max_workers: Maximum number of worker processes. Options:
            - None or 0: Use all available cores (default)
            - Positive int: Use that many cores (capped at available)
            - Negative int: Use all cores minus that many
        show_progress: Whether to show progress bar (default: True)
        chunk_size: Number of items to process at a time to bound disk and memory usage.

    Returns:
        List of validation results with path, valid_stac, and errors (if any)
    """
    all_results = []

    # Process items in bounded chunks to protect memory and /tmp disk space
    for chunk in _chunked_iterable(items, chunk_size):
        temp_files = []
        temp_file_to_source = (
            {}
        )  # Map temp file paths to source info for result display
        try:
            # Write this specific chunk to temporary files
            for item in chunk:
                # Extract source metadata if present (from validate_concurrently)
                # Use .get() to avoid mutating the input dictionary
                source_file = item.get("__source_file__")
                feature_index = item.get("__feature_index__")

                # Create a payload without internal metadata keys to avoid mutating input
                payload = {
                    k: v
                    for k, v in item.items()
                    if k not in ("__source_file__", "__feature_index__")
                }

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".json", delete=False
                ) as f:
                    json.dump(payload, f)
                    tmp_path = f.name
                    temp_files.append(tmp_path)

                    # Store source info for result mapping
                    if source_file is not None:
                        display_path = (
                            f"{source_file}[{feature_index}]"
                            if feature_index is not None
                            else source_file
                        )
                        temp_file_to_source[tmp_path] = display_path

            # Validate the chunk concurrently
            chunk_results = validate_concurrently(
                temp_files,
                max_workers=max_workers,
                show_progress=show_progress,
                feature_collection=False,  # Already expanded, no need to re-process
            )

            # Map results back to original source paths if available
            for result in chunk_results:
                result_path = result["path"]
                if result_path in temp_file_to_source:
                    result["path"] = temp_file_to_source[result_path]

            all_results.extend(chunk_results)

        finally:
            # Strictly clean up temporary files before moving to the next chunk
            for temp_file in temp_files:
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass

    return all_results

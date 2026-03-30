"""Concurrent batch validation of STAC files using multiprocessing."""

import concurrent.futures
import json
import multiprocessing
import os
import tempfile
from typing import Any, Dict, List, Optional, Tuple

from .utilities import fetch_and_parse_file, validate_stac_version_field
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
        # Load the file
        stac_content = fetch_and_parse_file(file_path)

        # 1. Validate version
        is_valid_version, err_type, err_msg = validate_stac_version_field(stac_content)
        if not is_valid_version:
            return file_path, False, [f"{err_type}: {err_msg}"]

        # 2. Use existing StacValidate for comprehensive validation
        validator = StacValidate(file_path, extensions=True)
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
    results = []
    temp_files_to_cleanup = []
    path_mapping = (
        {}
    )  # Maps actual file paths (including temp files) to their display paths

    try:
        from tqdm import tqdm

        has_tqdm = True
    except ImportError:
        has_tqdm = False
        show_progress = False

    optimal_workers = get_optimal_worker_count(max_workers)

    try:
        # Step 1: Prepare the tasks
        if feature_collection:
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

                        # Create temporary files for each feature so workers can process them
                        for idx, feature in enumerate(features):
                            with tempfile.NamedTemporaryFile(
                                mode="w", suffix=".json", delete=False
                            ) as tmp:
                                json.dump(feature, tmp)
                                tmp_path = tmp.name

                            temp_files_to_cleanup.append(tmp_path)
                            display_path = f"{file_path}[{idx}]"
                            path_mapping[tmp_path] = display_path
                    else:
                        # Regular file, process as-is
                        path_mapping[file_path] = file_path

                except Exception as e:
                    results.append(
                        {
                            "path": file_path,
                            "valid_stac": False,
                            "errors": [f"Failed to read file: {str(e)}"],
                        }
                    )
                    continue
        else:
            for file_path in file_paths:
                path_mapping[file_path] = file_path

        tasks_to_run = list(path_mapping.keys())
        if not tasks_to_run:
            return results

        # Step 2: ProcessPoolExecutor bypasses the GIL by creating separate Python processes
        with concurrent.futures.ProcessPoolExecutor(
            max_workers=optimal_workers
        ) as executor:

            # Submit all tasks to the pool
            future_to_file = {
                executor.submit(_validate_single_file, path): path
                for path in tasks_to_run
            }

            # Wrap the as_completed iterator with tqdm for a nice progress bar
            iterator = concurrent.futures.as_completed(future_to_file)
            if show_progress and has_tqdm:
                iterator = tqdm(  # type: ignore
                    iterator,
                    total=len(tasks_to_run),
                    desc="Validating STAC Items",
                )

            # Step 3: Collect results as they finish
            for future in iterator:
                actual_path, is_valid, errors = future.result()

                # Map the temp file path back to the user-friendly display path
                display_path = path_mapping[actual_path]

                result = {
                    "path": display_path,
                    "valid_stac": is_valid,
                }

                if errors:
                    result["errors"] = errors

                results.append(result)

    finally:
        # Step 4: Clean up any temporary files we created for FeatureCollections
        for tmp_path in temp_files_to_cleanup:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    return results


def validate_dicts(
    items: List[Dict[str, Any]],
    max_workers: Optional[int] = None,
    show_progress: bool = True,
    feature_collection: bool = False,
) -> List[Dict[str, Any]]:
    """
    Validate a list of STAC item dictionaries concurrently.

    Internally writes dictionaries to temporary files for concurrent validation,
    eliminating the need for users to manage temp files.

    Args:
        items: List of STAC item dictionaries to validate
        max_workers: Maximum number of worker processes. Options:
            - None or 0: Use all available cores (default)
            - Positive int: Use that many cores (capped at available)
            - Negative int: Use all cores minus that many
        show_progress: Whether to show progress bar (default: True)
        feature_collection: If True, treat items as features from a FeatureCollection

    Returns:
        List of validation results with path, valid_stac, and errors (if any)
    """
    temp_files = []

    try:
        # Write items to temporary files
        for i, item in enumerate(items):
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as f:
                json.dump(item, f)
                temp_files.append(f.name)

        # Validate using concurrent validation
        results = validate_concurrently(
            temp_files,
            max_workers=max_workers,
            show_progress=show_progress,
            feature_collection=feature_collection,
        )

        return results

    finally:
        # Clean up temporary files
        for temp_file in temp_files:
            try:
                os.unlink(temp_file)
            except Exception:
                pass

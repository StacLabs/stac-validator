"""Concurrent batch validation of STAC files using multiprocessing."""

import concurrent.futures
import json
import multiprocessing
from typing import List, Dict, Any, Tuple, Optional

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
                        if "errors" in msg_obj:
                            errors.extend(msg_obj["errors"])
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
    feature_collection: bool = False
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
    
    try:
        from tqdm import tqdm
        has_tqdm = True
    except ImportError:
        has_tqdm = False
        show_progress = False
    
    # Get optimal worker count
    optimal_workers = get_optimal_worker_count(max_workers)
    
    # If feature_collection mode, expand FeatureCollections into individual items
    if feature_collection:
        expanded_files = []
        for file_path in file_paths:
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                
                # Check if it's a FeatureCollection
                if isinstance(data, dict) and data.get("type") == "FeatureCollection":
                    features = data.get("features", [])
                    # Create temporary files for each feature
                    for idx, feature in enumerate(features):
                        # Store feature with reference to original file
                        expanded_files.append({
                            "feature": feature,
                            "source_file": file_path,
                            "feature_index": idx
                        })
                else:
                    # Regular file, process as-is
                    expanded_files.append({
                        "feature": data,
                        "source_file": file_path,
                        "feature_index": None
                    })
            except Exception as e:
                results.append({
                    "path": file_path,
                    "valid_stac": False,
                    "errors": [f"Failed to read file: {str(e)}"]
                })
                continue
        
        # Validate features directly
        for item in expanded_files:
            try:
                feature = item["feature"]
                source_file = item["source_file"]
                feature_index = item["feature_index"]
                
                # Validate the feature/item
                is_valid_version, err_type, err_msg = validate_stac_version_field(feature)
                if not is_valid_version:
                    result_path = f"{source_file}[{feature_index}]" if feature_index is not None else source_file
                    results.append({
                        "path": result_path,
                        "valid_stac": False,
                        "errors": [f"{err_type}: {err_msg}"]
                    })
                    continue
                
                # Use StacValidate for comprehensive validation
                validator = StacValidate(feature)
                validator.run()
                
                # Parse results
                errors = []
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
                
                result_path = f"{source_file}[{feature_index}]" if feature_index is not None else source_file
                results.append({
                    "path": result_path,
                    "valid_stac": len(errors) == 0,
                    "errors": errors if errors else None
                })
                
            except Exception as e:
                result_path = f"{source_file}[{feature_index}]" if feature_index is not None else source_file
                results.append({
                    "path": result_path,
                    "valid_stac": False,
                    "errors": [f"Critical error: {str(e)}"]
                })
        
        return results
    
    # ProcessPoolExecutor bypasses the GIL by creating entirely separate Python processes
    with concurrent.futures.ProcessPoolExecutor(max_workers=optimal_workers) as executor:
        
        # Submit all tasks to the pool
        future_to_file = {
            executor.submit(_validate_single_file, path): path 
            for path in file_paths
        }
        
        # Wrap the as_completed iterator with tqdm for a nice progress bar
        if show_progress and has_tqdm:
            iterator = tqdm(
                concurrent.futures.as_completed(future_to_file), 
                total=len(file_paths), 
                desc="Validating STAC Items"
            )
        else:
            iterator = concurrent.futures.as_completed(future_to_file)
        
        for future in iterator:
            file_path, is_valid, errors = future.result()
            
            result = {
                "path": file_path,
                "valid_stac": is_valid,
            }
            
            if errors:
                result["errors"] = errors
            
            results.append(result)
    
    return results

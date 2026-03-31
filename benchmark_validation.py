#!/usr/bin/env python3
"""
Benchmark script comparing batch validation vs legacy item-collection validation.

Compares:
1. stac-validator batch --feature-collection (multiprocessing)
2. stac-validator validate --item-collection (single-threaded legacy)

Usage:
    python benchmark_validation.py --items 10000
    python benchmark_validation.py --items 1000 --batch-only
    python benchmark_validation.py --items 5000 --legacy-only
"""

import argparse
import copy
import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def generate_test_feature_collection(num_items: int = 10000) -> str:
    """
    Generate a test GeoJSON FeatureCollection with STAC items.
    
    About 2/3 of items will be valid (with collection link) and 1/3 will be invalid
    (missing collection link) to create a realistic mix.
    
    Args:
        num_items: Number of items to generate
        
    Returns:
        Path to the temporary GeoJSON file
    """
    print(f"Generating test FeatureCollection with {num_items} items...")
    
    # Load a sample item
    sample_item_path = Path(__file__).parent / "sample_data" / "sentinel-cogs-test.json"
    if not sample_item_path.exists():
        print(f"Error: Sample item not found at {sample_item_path}")
        sys.exit(1)
    
    with open(sample_item_path) as f:
        sample_item = json.load(f)
    
    # Create a FeatureCollection with a mix of valid and invalid items
    features = []
    valid_count = 0
    invalid_count = 0
    
    for i in range(num_items):
        item = copy.deepcopy(sample_item)
        item["id"] = f"{item.get('id', 'item')}-{i}"
        
        # Make ~2/3 of items valid by adding a collection link
        if i % 3 != 0:  # 2 out of 3 items
            # Add a collection link if it doesn't exist
            if "links" not in item:
                item["links"] = []
            else:
                # Deep copy the links list to avoid modifying the original
                item["links"] = copy.deepcopy(item["links"])
            
            # Check if collection link already exists
            has_collection_link = any(
                link.get("rel") == "collection" for link in item.get("links", [])
            )
            
            if not has_collection_link:
                item["links"].append({
                    "rel": "collection",
                    "href": f"https://example.com/collections/{item.get('collection', 'unknown')}",
                    "type": "application/json"
                })
            valid_count += 1
        else:
            # Keep ~1/3 of items invalid (missing collection link)
            invalid_count += 1
        
        features.append(item)
    
    feature_collection = {
        "type": "FeatureCollection",
        "features": features
    }
    
    # Write to temporary file
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.json',
        delete=False
    )
    json.dump(feature_collection, temp_file)
    temp_file.close()
    
    print(f"Test FeatureCollection created: {temp_file.name}")
    print(f"  Valid items (with collection link): {valid_count}")
    print(f"  Invalid items (missing collection link): {invalid_count}")
    return temp_file.name


def run_batch_validation(file_path: str) -> dict:
    """
    Run batch validation with --feature-collection.
    """
    print("\n" + "="*70)
    print("BENCHMARK 1: stac-validator batch --feature-collection")
    print("="*70)
    
    start_time = time.time()
    
    # Use Popen to capture output AND print it in real-time
    process = subprocess.Popen(
        [
            "stac-validator",
            "batch",
            "--feature-collection",
            file_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    output_lines = []
    # Read output line-by-line as it's generated
    for line in process.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
        output_lines.append(line)
        
    process.wait()
    elapsed = time.time() - start_time
    
    # Parse the output to extract valid/invalid counts
    valid_count = 0
    invalid_count = 0
    
    for line in output_lines:
        if '✅ Valid:' in line:
            try:
                valid_count = int(line.split('✅ Valid:')[1].split()[0])
            except (IndexError, ValueError):
                pass
        elif '❌ Invalid:' in line:
            try:
                invalid_count = int(line.split('❌ Invalid:')[1].split()[0])
            except (IndexError, ValueError):
                pass
    
    return {
        "method": "batch --feature-collection",
        "elapsed": elapsed,
        "exit_code": process.returncode,
        "output": "",
        "valid_count": valid_count,
        "invalid_count": invalid_count
    }


def run_legacy_validation(file_path: str) -> dict:
    """
    Run legacy validation with --item-collection.
    """
    print("\n" + "="*70)
    print("BENCHMARK 2: stac-validator validate --item-collection")
    print("="*70)
    
    start_time = time.time()
    
    # Use Popen to capture output AND print it in real-time
    process = subprocess.Popen(
        [
            "stac-validator",
            "validate",
            "--item-collection",
            file_path
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )
    
    output_lines = []
    # Read output line-by-line as it's generated
    for line in process.stdout:
        sys.stdout.write(line)
        sys.stdout.flush()
        output_lines.append(line)
        
    process.wait()
    elapsed = time.time() - start_time
    
    # Parse output to extract valid/invalid counts
    valid_count = 0
    invalid_count = 0
    
    for line in output_lines:
        if 'Items passed:' in line:
            try:
                passed_part = line.split('Items passed:')[1].strip()
                parts = passed_part.split('/')
                valid_count = int(parts[0].strip())
                total_str = parts[1].split('(')[0].strip()
                total = int(total_str)
                invalid_count = total - valid_count
            except (IndexError, ValueError):
                pass
    
    return {
        "method": "validate --item-collection",
        "elapsed": elapsed,
        "exit_code": process.returncode,
        "output": "",
        "valid_count": valid_count,
        "invalid_count": invalid_count
    }

def main():
    """Run the benchmark comparison."""
    parser = argparse.ArgumentParser(
        description="Benchmark batch validation vs legacy item-collection validation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python benchmark_validation.py --items 10000
  python benchmark_validation.py --items 1000 --batch-only
  python benchmark_validation.py --items 5000 --legacy-only
        """
    )
    parser.add_argument(
        "--items",
        type=int,
        default=10000,
        help="Number of items to test (default: 10000)"
    )
    parser.add_argument(
        "--batch-only",
        action="store_true",
        help="Only run batch validation benchmark"
    )
    parser.add_argument(
        "--legacy-only",
        action="store_true",
        help="Only run legacy validation benchmark"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.batch_only and args.legacy_only:
        print("Error: Cannot specify both --batch-only and --legacy-only")
        sys.exit(1)
    
    if args.items < 1:
        print("Error: --items must be at least 1")
        sys.exit(1)
    
    # Generate test data
    test_file = generate_test_feature_collection(args.items)
    
    try:
        results = {}
        
        # Run batch validation if not legacy-only
        if not args.legacy_only:
            results['batch'] = run_batch_validation(test_file)
        
        # Run legacy validation if not batch-only
        if not args.batch_only:
            results['legacy'] = run_legacy_validation(test_file)
        
        # Print comparison
        print("\n" + "="*70)
        print("BENCHMARK RESULTS")
        print("="*70)
        print(f"Items tested: {args.items}")
        
        if 'batch' in results:
            batch_result = results['batch']
            print(f"\nBatch Validation (multiprocessing):")
            print(f"  Time: {batch_result['elapsed']:.2f}s")
            print(f"  ✅ Valid: {batch_result.get('valid_count', 0)}")
            print(f"  ❌ Invalid: {batch_result.get('invalid_count', 0)}")
        
        if 'legacy' in results:
            legacy_result = results['legacy']
            print(f"\nLegacy Validation (single-threaded):")
            print(f"  Time: {legacy_result['elapsed']:.2f}s")
            print(f"  ✅ Valid: {legacy_result.get('valid_count', 0)}")
            print(f"  ❌ Invalid: {legacy_result.get('invalid_count', 0)}")
        
        # Calculate speedup if both ran
        if 'batch' in results and 'legacy' in results:
            speedup = legacy_result['elapsed'] / batch_result['elapsed']
            print(f"\n{'='*70}")
            print(f"Speedup: {speedup:.1f}x faster with batch validation")
            print(f"Time saved: {legacy_result['elapsed'] - batch_result['elapsed']:.2f}s")
        
    finally:
        # Clean up
        import os
        os.unlink(test_file)
        print(f"\nCleaned up test file: {test_file}")


if __name__ == "__main__":
    main()

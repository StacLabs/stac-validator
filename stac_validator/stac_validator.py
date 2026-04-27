import json
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

import click  # type: ignore

from .batch_validator import validate_concurrently
from .utilities import set_schema_cache_size
from .validate import StacValidate
from .fast_validator import FastValidator


def _print_summary(
    title: str, valid_count: int, total_count: int, obj_type: str = "STAC objects"
) -> None:
    """Helper function to print a consistent summary line.

    Args:
        title (str): Title of the summary section
        valid_count (int): Number of valid items
        total_count (int): Total number of items
        obj_type (str): Type of objects being counted (e.g., 'items', 'collections')
    """
    click.secho()
    click.secho(f"{title}:", bold=True)
    if total_count > 0:
        percentage = (valid_count / total_count) * 100
        click.secho(
            f"  {obj_type.capitalize()} passed: {valid_count}/{total_count} ({percentage:.1f}%)"
        )
    else:
        click.secho(f"  No {obj_type} found to validate")


def format_duration(seconds: float) -> str:
    """Format duration in seconds to a human-readable string.

    Args:
        seconds (float): Duration in seconds

    Returns:
        str: Formatted duration string (e.g., '1m 23.45s' or '456.78ms')
    """
    if seconds < 1.0:
        return f"{seconds * 1000:.2f}ms"
    minutes, seconds = divmod(seconds, 60)
    if minutes > 0:
        return f"{int(minutes)}m {seconds:.2f}s"
    return f"{seconds:.2f}s"


def print_update_message(version: str) -> None:
    """Prints an update message for `stac-validator` based on the version of the
    STAC file being validated.

    Args:
        version (str): The version of the STAC file being validated.

    Returns:
        None
    """
    click.secho()
    if version != "1.1.0":
        click.secho(
            f"Please upgrade from version {version} to version 1.1.0!", fg="red"
        )
    else:
        click.secho("Thanks for using STAC version 1.1.0!", fg="green")
    click.secho()


def item_collection_summary(message: List[Dict[str, Any]]) -> None:
    """Prints a summary of the validation results for an item collection response.

    Args:
        message (List[Dict[str, Any]]): The validation results for the item collection.

    Returns:
        None
    """
    valid_count = sum(1 for item in message if item.get("valid_stac") is True)
    _print_summary("-- Item Collection Summary", valid_count, len(message), "items")


def collections_summary(message: List[Dict[str, Any]]) -> None:
    """Prints a summary of the validation results for a collections response.

    Args:
        message (List[Dict[str, Any]]): The validation results for the collections.

    Returns:
        None
    """
    valid_count = sum(1 for coll in message if coll.get("valid_stac") is True)
    _print_summary("-- Collections Summary", valid_count, len(message), "collections")


def recursive_validation_summary(message: List[Dict[str, Any]]) -> None:
    """Prints a summary of the recursive validation results.

    Args:
        message (List[Dict[str, Any]]): The validation results from recursive validation.

    Returns:
        None
    """
    # Count valid and total objects by type
    type_counts = {}
    total_valid = 0

    for item in message:
        if not isinstance(item, dict):
            continue

        obj_type = item.get("asset_type", "unknown").lower()
        is_valid = item.get("valid_stac", False) is True

        if obj_type not in type_counts:
            type_counts[obj_type] = {"valid": 0, "total": 0}

        type_counts[obj_type]["total"] += 1
        if is_valid:
            type_counts[obj_type]["valid"] += 1
            total_valid += 1

    # Print overall summary
    _print_summary("-- Recursive Validation Summary", total_valid, len(message))

    # Print breakdown by type if there are multiple types
    if len(type_counts) > 1:
        click.secho("\n  Breakdown by type:")
        for obj_type, counts in sorted(type_counts.items()):
            percentage = (
                (counts["valid"] / counts["total"]) * 100 if counts["total"] > 0 else 0
            )
            click.secho(
                f"    {obj_type.capitalize()}: {counts['valid']}/{counts['total']} ({percentage:.1f}%)"
            )


@click.command()
@click.argument("stac_file")
@click.option(
    "--core", is_flag=True, help="Validate core stac object only without extensions."
)
@click.option("--extensions", is_flag=True, help="Validate extensions only.")
@click.option(
    "--links",
    is_flag=True,
    help="Additionally validate links. Only works with default mode.",
)
@click.option(
    "--assets",
    is_flag=True,
    help="Additionally validate assets. Only works with default mode.",
)
@click.option(
    "--custom",
    "-c",
    default="",
    help="Validate against a custom schema (local filepath or remote schema).",
)
@click.option(
    "--schema-config",
    "-sc",
    default="",
    help="Validate against a custom schema config (local filepath or remote schema config).",
)
@click.option(
    "--schema-map",
    "-s",
    type=(str, str),
    multiple=True,
    help="Schema path to replaced by (local) schema path during validation. Can be used multiple times.",
)
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    help="Recursively validate all related stac objects.",
)
@click.option(
    "--max-depth",
    "-m",
    type=int,
    help="Maximum depth to traverse when recursing. Omit this argument to get full recursion. Ignored if `recursive == False`.",
)
@click.option(
    "--collections",
    is_flag=True,
    help="Validate /collections response.",
)
@click.option(
    "--item-collection",
    "--feature-collection",
    is_flag=True,
    help="Validate item collection response. Can be combined with --pages. Defaults to one page.",
)
@click.option(
    "--no-assets-urls",
    is_flag=True,
    help="Disables the opening of href links when validating assets (enabled by default).",
)
@click.option(
    "--header",
    type=(str, str),
    multiple=True,
    help="HTTP header to include in the requests. Can be used multiple times.",
)
@click.option(
    "--pages",
    "-p",
    type=int,
    help="Maximum number of pages to validate via --item-collection. Defaults to one page.",
)
@click.option(
    "-t",
    "--trace-recursion",
    is_flag=True,
    help="Enables verbose output for recursive mode.",
)
@click.option("--no_output", is_flag=True, help="Do not print output to console.")
@click.option(
    "--log_file",
    default="",
    help="Save full recursive output to log file (local filepath).",
)
@click.option(
    "--pydantic",
    is_flag=True,
    help="Validate using stac-pydantic models for enhanced type checking and validation.",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose output. This will output additional information during validation.",
)
@click.option(
    "--schema-cache-size",
    type=int,
    default=None,
    help="Max number of schema entries to cache in memory. Defaults to 16.",
)
def main(
    stac_file: str,
    collections: bool,
    item_collection: bool,
    no_assets_urls: bool,
    header: list,
    pages: int,
    recursive: bool,
    max_depth: int,
    core: bool,
    extensions: bool,
    links: bool,
    assets: bool,
    custom: str,
    schema_config: str,
    schema_map: List[Tuple],
    trace_recursion: bool,
    no_output: bool,
    log_file: str,
    pydantic: bool,
    verbose: bool = False,
    schema_cache_size: Optional[int] = None,
):
    """Validate a STAC file against the STAC specification.

    Prints validation results to the console as JSON.
    Exits with status code 0 if valid, 1 if invalid.
    """
    start_time = time.time()
    valid = True

    if schema_map == ():
        schema_map_dict: Optional[Dict[str, str]] = None
    else:
        schema_map_dict = dict(schema_map)

    if schema_cache_size is not None:
        if schema_cache_size < 0:
            raise click.BadParameter(
                "must be greater than or equal to 0",
                param_hint="--schema-cache-size",
            )
        set_schema_cache_size(schema_cache_size)

    stac = StacValidate(
        stac_file=stac_file,
        collections=collections,
        item_collection=item_collection,
        pages=pages,
        recursive=recursive,
        max_depth=max_depth,
        core=core,
        links=links,
        assets=assets,
        assets_open_urls=not no_assets_urls,
        headers=dict(header),
        extensions=extensions,
        custom=custom,
        schema_config=schema_config,
        schema_map=schema_map_dict,
        trace_recursion=trace_recursion,
        log=log_file,
        pydantic=pydantic,
        verbose=verbose,
        show_progress=True,
    )

    try:
        if not item_collection and not collections:
            valid = stac.run()
        elif collections:
            stac.validate_collections()
        else:
            stac.validate_item_collection()

        message = stac.message
        if "version" in message[0]:
            print_update_message(message[0]["version"])

        if no_output is False:
            click.echo(json.dumps(message, indent=4))

        # Print appropriate summary based on validation mode
        if item_collection:
            item_collection_summary(message)
        elif collections:
            collections_summary(message)
        elif recursive:
            recursive_validation_summary(message)

    finally:
        # Always print the duration, even if validation fails
        duration = time.time() - start_time
        click.secho(
            f"\nValidation completed in {format_duration(duration)}", fg="green"
        )
        click.secho()
    sys.exit(0 if valid else 1)


@click.command()
@click.argument("files", nargs=-1, required=True, type=click.Path(exists=True))
@click.option(
    "--cores",
    type=int,
    default=None,
    help="Number of CPU cores to use for parallel validation. Defaults to all available cores.",
)
@click.option(
    "--no-progress",
    is_flag=True,
    help="Disable progress bar during validation.",
)
@click.option(
    "--no-output",
    is_flag=True,
    help="Do not print output to console.",
)
@click.option(
    "--item-collection",
    "--feature-collection",
    is_flag=True,
    help="Treat files as ItemCollections and validate each item individually.",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Show full JSON output for all items. By default, only invalid items are shown.",
)
@click.option(
    "--schema-cache-size",
    type=int,
    default=16,
    help="Max number of schema entries to cache per worker process. Defaults to 16.",
)
@click.option(
    "--batch-size",
    type=click.IntRange(min=1),
    default=2000,
    help="Batch size for chunked processing. Larger batches use more memory but may be faster. Defaults to 2000.",
)
def batch(
    files: Tuple[str, ...],
    cores: Optional[int],
    no_progress: bool,
    no_output: bool,
    item_collection: bool,
    verbose: bool,
    schema_cache_size: int,
    batch_size: int,
):
    """Validate multiple STAC files concurrently using all available CPU cores.

    This command uses multiprocessing to validate STAC files in parallel,
    bypassing Python's Global Interpreter Lock (GIL) for maximum performance.
    Each CPU core gets its own schema cache, which is warmed up on the first
    file and reused for subsequent files.

    Examples:

        # Validate all JSON files in a directory
        stac-validator batch *.json

        # Validate specific files
        stac-validator batch file1.json file2.json file3.json

        # Use only 4 cores
        stac-validator batch *.json --cores 4

        # Disable progress bar
        stac-validator batch *.json --no-progress
    """
    if not files:
        click.secho("Error: No files provided", fg="red")
        sys.exit(1)

    start_time = time.time()

    try:
        # Configure schema cache size BEFORE spawning workers
        # This ensures all worker processes inherit the configured cache size
        if schema_cache_size != 16:
            set_schema_cache_size(schema_cache_size)

        # Get optimal worker count
        from .batch_validator import get_optimal_worker_count

        optimal_workers = get_optimal_worker_count(cores)

        # Validate concurrently
        results = validate_concurrently(
            list(files),
            max_workers=cores,
            show_progress=not no_progress,
            feature_collection=item_collection,
            batch_size=batch_size,
        )

        # Calculate statistics
        valid_count = sum(1 for r in results if r.get("valid_stac", False))
        invalid_count = len(results) - valid_count

        # Print details of failed validations first (only in non-verbose mode)
        if not no_output and invalid_count > 0 and not verbose:
            click.secho("Failed validations:", fg="red")

            # Group errors by (message, schema) and collect item IDs
            from collections import defaultdict

            error_groups = defaultdict(list)

            for result in results:
                if not result.get("valid_stac", False):
                    # Try to get item ID from result, fallback to path
                    item_id = result.get("item_id", result.get("path", "unknown"))

                    # Handle both old format (errors array) and new format (error_message/failed_schema)
                    if "errors" in result:
                        # Old format: errors array with dict entries
                        for error in result["errors"]:
                            if isinstance(error, dict):
                                error_msg = error.get("message", str(error))
                                error_schema = error.get("schema", "")
                                error_key = (error_msg, error_schema)
                            else:
                                error_key = (str(error), "")
                            error_groups[error_key].append(item_id)
                    elif "error_message" in result:
                        # New format: error_message and failed_schema fields
                        error_msg = result.get("error_message", "")
                        error_schema = result.get("failed_schema", "")
                        error_key = (error_msg, error_schema)
                        error_groups[error_key].append(item_id)

            # Print grouped errors with compact formatting
            for idx, ((error_msg, error_schema), item_ids) in enumerate(
                sorted(error_groups.items())
            ):
                # Add blank line between error sections (but not before the first one)
                if idx > 0:
                    click.secho()

                # Format item IDs compactly (max 5 per line)
                if len(item_ids) <= 5:
                    ids_str = ", ".join(str(id) for id in item_ids)
                    click.secho(f"  [{ids_str}]", fg="red")
                else:
                    # For many items, show first few and count
                    first_few = ", ".join(str(id) for id in item_ids[:5])
                    remaining = len(item_ids) - 5
                    click.secho(f"  [{first_few}, ... +{remaining} more]", fg="red")

                # Display error message
                click.secho(f"    - {error_msg}", fg="yellow")

                # Display schema if available
                if error_schema:
                    click.secho(f"      Schema: {error_schema}", fg="cyan")

        # Print full JSON output in verbose mode
        if not no_output and verbose:
            click.echo(json.dumps(results, indent=4))

        # Print summary at the bottom
        click.secho()
        click.secho("Validation Summary:", bold=True)
        click.secho(f"  Total files: {len(results)}")
        click.secho(f"  CPU cores used: {optimal_workers}")
        click.secho(f"  ✅ Valid: {valid_count}")
        click.secho(f"  ❌ Invalid: {invalid_count}")

        duration = time.time() - start_time
        click.secho()
        click.secho(f"Validation completed in {format_duration(duration)}", fg="green")
        click.secho()

        sys.exit(0 if invalid_count == 0 else 1)

    except Exception as e:
        click.secho(f"Error during batch validation: {e}", fg="red")
        sys.exit(1)


@click.command()
@click.argument("stac_file")
@click.option(
    "--quiet",
    "-q",
    is_flag=True,
    help="Suppress individual item logs.",
)
def fast(stac_file: str, quiet: bool):
    """High-speed validation using fastjsonschema and local caching."""
    fv = FastValidator(stac_file, quiet=quiet)
    fv.run()
    sys.exit(0 if fv.valid else 1)


@click.group()
def cli():
    """STAC Validator - Validate STAC files against the STAC specification.

    \b
    Usage:
      stac-validator validate <file> [options]
      stac-validator batch <files> [options]
      stac-validator batch <file> --feature-collection [options]
      stac-validator fast <file> [options]
    """
    pass


# Register commands
cli.add_command(main, name="validate")
cli.add_command(batch, name="batch")
cli.add_command(fast, name="fast")


if __name__ == "__main__":
    cli()

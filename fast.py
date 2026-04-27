#!/usr/bin/env python3
import json
import os
import sys
import time
import urllib.error
import urllib.request
from typing import Any, Dict, List, Tuple

import click
import fastjsonschema

# --- Caches & Config ---
SCHEMA_CACHE = {}
VALIDATOR_CACHE = {}
LOCAL_SCHEMA_DIR = "local_schemas/.schemas"


def get_local_path_for_uri(uri: str) -> str:
    """Creates a safe local filepath for a cached schema URL."""
    safe_filename = uri.replace("https://", "").replace("http://", "").replace("/", "_")
    return os.path.join(LOCAL_SCHEMA_DIR, safe_filename)


def fetch_schema(uri: str) -> Dict[str, Any]:
    """The Ultimate Handler: RAM -> Disk -> Network -> Disk -> RAM"""

    # 1. RAM Cache
    if uri in SCHEMA_CACHE:
        return SCHEMA_CACHE[uri]

    local_path = get_local_path_for_uri(uri)

    # 2. Disk Cache
    if os.path.exists(local_path):
        try:
            with open(local_path, "r") as f:
                schema_dict = json.load(f)
                SCHEMA_CACHE[uri] = schema_dict
                return schema_dict
        except Exception:
            pass  # If corrupted, fallback to network

    # 3. Network Fetch
    click.secho(f"    [Network] Fetching: {uri}", fg="yellow", dim=True)
    req = urllib.request.Request(uri, headers={"User-Agent": "stac-fast-cli/5.0"})
    try:
        with urllib.request.urlopen(req) as response:
            schema_dict = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as e:
        click.secho(
            f"\n🚨 FATAL ERROR: Could not resolve schema: {uri}", fg="red", bold=True
        )
        click.secho(f"Reason: {e}", fg="red")
        sys.exit(1)

    # 4. Save to Disk Cache
    os.makedirs(os.path.dirname(local_path), exist_ok=True)
    try:
        with open(local_path, "w") as f:
            json.dump(schema_dict, f)
    except IOError:
        pass  # If we can't write to disk, no big deal, keep going

    # 5. Save to RAM Cache
    SCHEMA_CACHE[uri] = schema_dict
    return schema_dict


def get_validator(stac_type: str, stac_version: str, extensions: List[str]):
    """Builds and caches a validator based on Object Type, Version, and Extensions."""
    ext_key = tuple(sorted(extensions))
    cache_key = (stac_type, stac_version, ext_key)

    if cache_key in VALIDATOR_CACHE:
        return VALIDATOR_CACHE[cache_key], True

    # Determine base schema URI
    if stac_type == "Item":
        base_uri = f"https://schemas.stacspec.org/v{stac_version}/item-spec/json-schema/item.json"
    elif stac_type == "Collection":
        base_uri = f"https://schemas.stacspec.org/v{stac_version}/collection-spec/json-schema/collection.json"
    elif stac_type == "Catalog":
        base_uri = f"https://schemas.stacspec.org/v{stac_version}/catalog-spec/json-schema/catalog.json"
    else:
        raise ValueError(f"Unknown STAC type for validation: {stac_type}")

    # Build the dynamic compound schema
    dynamic_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "allOf": [{"$ref": base_uri}],
    }
    for ext in extensions:
        dynamic_schema["allOf"].append({"$ref": ext})

    validator = fastjsonschema.compile(
        dynamic_schema, handlers={"http": fetch_schema, "https": fetch_schema}
    )

    VALIDATOR_CACHE[cache_key] = validator
    return validator, False


@click.command()
@click.argument("filepath", type=click.Path(exists=True, dir_okay=False))
@click.option("-q", "--quiet", is_flag=True, help="Suppress individual item logs.")
def cli(filepath, quiet):
    """Universal high-speed STAC Validator (Items, Collections, Catalogs, FeatureCollections)"""

    click.secho(f"\n📂 Loading: {filepath}", fg="blue", bold=True)

    try:
        with open(filepath, "r") as f:
            data = json.load(f)
    except Exception as e:
        click.secho(f"❌ Error reading {filepath}: {e}", fg="red", bold=True)
        sys.exit(1)

    # Detect payload structure
    obj_type = data.get("type", "")
    items_to_validate = []

    if obj_type == "FeatureCollection":
        items_to_validate = data.get("features", [])
        click.secho(
            f"📦 Detected FeatureCollection ({len(items_to_validate)} Items)\n",
            fg="cyan",
        )
    elif obj_type == "Feature":
        items_to_validate = [data]
        click.secho("📄 Detected: STAC Item\n", fg="cyan")
    elif obj_type == "Collection":
        items_to_validate = [data]
        click.secho("📚 Detected: STAC Collection\n", fg="cyan")
    elif obj_type == "Catalog" or "id" in data and "description" in data:
        # Fallback for old catalogs missing the 'type' field
        data["type"] = "Catalog"
        items_to_validate = [data]
        click.secho("🗂️  Detected: STAC Catalog\n", fg="cyan")
    else:
        click.secho("❌ Unknown JSON type. Missing 'type' field.", fg="red", bold=True)
        sys.exit(1)

    # --- Metrics ---
    total_setup_ms = 0.0
    total_exec_ms = 0.0
    valid_count = 0
    invalid_count = 0
    error_registry = {}

    for index, item in enumerate(items_to_validate):
        # Determine specific STAC attributes for this object
        item_id = item.get("id", f"unknown-{index}")
        stac_version = item.get("stac_version", "1.0.0")
        extensions = item.get("stac_extensions", [])

        # Map Feature->Item, others keep their type
        actual_type = (
            "Item" if item.get("type") == "Feature" else item.get("type", "Catalog")
        )

        # --- Setup Timer ---
        t0 = time.perf_counter()
        try:
            validator, is_cached = get_validator(actual_type, stac_version, extensions)
        except Exception as e:
            if not quiet:
                click.secho(f"❌ Setup failed for {item_id}: {e}", fg="red")
            invalid_count += 1
            continue
        t1 = time.perf_counter()
        setup_time = (t1 - t0) * 1000
        total_setup_ms += setup_time

        # --- Execution Timer ---
        t2 = time.perf_counter()
        try:
            validator(item)
            t3 = time.perf_counter()
            exec_time = (t3 - t2) * 1000
            total_exec_ms += exec_time
            valid_count += 1
            status_text = click.style("✅ VALID", fg="green")

        except fastjsonschema.JsonSchemaValueException as e:
            t3 = time.perf_counter()
            exec_time = (t3 - t2) * 1000
            total_exec_ms += exec_time
            invalid_count += 1

            # --- The STAC Error Translator ---
            error_msg = f"{e.name} {e.message.replace(e.name, '').strip()}"
            if "disallowed definition" in error_msg:
                if "collection" in error_msg:
                    error_msg = "STAC Spec Violation: Missing {'rel': 'collection'} in links array."
                else:
                    error_msg = (
                        f"{e.name} violated a 'not' rule. Value: {repr(e.value)}"
                    )

            # Group errors
            if error_msg not in error_registry:
                error_registry[error_msg] = []
            error_registry[error_msg].append(item_id)
            status_text = click.style(f"❌ INVALID", fg="red")

        if not quiet:
            if index < 5 or (len(items_to_validate) < 20):
                cache_icon = "⚡" if is_cached else "🐌"
                click.echo(
                    f"[{index + 1}] ID: {item_id} | Type: {actual_type} | Cache {cache_icon} | Setup: {setup_time:>6.2f}ms | Exec: {exec_time:>5.2f}ms | {status_text}"
                )
            elif index == 5:
                click.secho(
                    "... silencing output for remaining items (validating at maximum speed) ...",
                    dim=True,
                )

    # --- Summary Report ---
    click.echo("\n" + "=" * 55)
    click.secho("📊 VALIDATION SUMMARY", bold=True)
    click.echo("=" * 55)
    click.echo(f"Total Objects Processed : {len(items_to_validate)}")
    click.echo(f"Valid Objects           : {click.style(str(valid_count), fg='green')}")

    invalid_color = "red" if invalid_count > 0 else "green"
    click.echo(
        f"Invalid Objects         : {click.style(str(invalid_count), fg=invalid_color)}"
    )

    click.echo("-" * 55)
    click.echo(f"Total Setup Time        : {total_setup_ms:.2f} ms")
    click.echo(f"Total Execution Time    : {total_exec_ms:.2f} ms")
    if len(items_to_validate) > 0:
        click.echo(
            f"Average Exec per Object : {(total_exec_ms / len(items_to_validate)):.3f} ms"
        )

    if invalid_count > 0:
        click.echo("=" * 55)
        click.secho("🚨 ERROR BREAKDOWN", bold=True, fg="red")
        click.echo("=" * 55)
        for err_msg, affected_ids in error_registry.items():
            count = len(affected_ids)
            click.echo(f"\n❌ {click.style(err_msg, fg='yellow', bold=True)}")
            click.echo(
                f"   Affected Items: {click.style(str(count), fg='red', bold=True)}"
            )
            sample_ids = ", ".join(affected_ids[:3])
            if count > 3:
                sample_ids += f" ... (and {count - 3} more)"
            click.echo(f"   Examples:       {sample_ids}")

    click.echo("\n")


if __name__ == "__main__":
    cli()

import io
import json
import logging
import os
import re
import tempfile
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from contextlib import redirect_stderr, redirect_stdout
from typing import Any, Callable, Dict, List, Optional, Set, Tuple
from urllib.parse import urljoin

import click
import fastjsonschema  # type: ignore
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .utilities import validate_with_ref_resolver

# Standard Python logger for FastAPI/Uvicorn integration
logger = logging.getLogger(__name__)


def parse_json_pointer(expr_name: Optional[str]) -> str:
    """Converts fastjsonschema variable names into clean JSON Pointers.

    Handles both bracket notation (data['properties']['eo:cloud_cover'])
    and dot notation (data.properties.eo:cloud_cover).
    """
    if not expr_name or not isinstance(expr_name, str) or expr_name == "data":
        return "$"
    # Bracket notation: data['properties']['eo:cloud_cover']
    keys = re.findall(r"['\"]([^'\"]*)['\"]", expr_name)
    if keys:
        return "$." + ".".join(keys)
    # Dot notation: data.properties.eo:cloud_cover
    if expr_name.startswith("data."):
        return "$." + expr_name[5:]
    return expr_name


class FastSTACValidationError(fastjsonschema.JsonSchemaValueException):
    """Custom validation exception inheriting from fastjsonschema.JsonSchemaValueException.

    Guarantees backward compatibility for legacy callers catching
    fastjsonschema.JsonSchemaValueException.
    """

    def __init__(self, source: str, field_path: str, raw_message: str):
        self.source = source
        self.field_path = field_path
        self.raw_message = raw_message
        formatted_msg = f"[{source}] Field '{field_path}': {raw_message}"

        # Populate fastjsonschema.JsonSchemaValueException superclass attributes:
        # self.message -> formatted_msg
        # self.name    -> field_path
        super().__init__(
            message=formatted_msg,
            value=None,
            name=field_path,
            definition=None,
        )

    def __str__(self) -> str:
        return f"[{self.source}] Field '{self.field_path}': {self.raw_message}"


class FastSTACMultiValidationError(FastSTACValidationError):
    """Container for all validation errors on a single STAC object.

    Inherits from FastSTACValidationError (and transitively JsonSchemaValueException),
    allowing legacy exception handlers to catch multi-error failures seamlessly.
    """

    def __init__(self, errors: List[FastSTACValidationError]):
        self.errors = errors
        first_err = (
            errors[0]
            if errors
            else FastSTACValidationError("Base STAC", "$", "Unknown validation error")
        )
        super().__init__(first_err.source, first_err.field_path, first_err.raw_message)

    def __str__(self) -> str:
        err_list_str = "; ".join(str(err) for err in self.errors)
        return f"Found {len(self.errors)} validation error(s): {err_list_str}"


def get_cache_directory() -> str:
    r"""Determines a writable disk cache directory across environments (Docker, Lambda, CLI).

    Priority:
    1. STAC_VALIDATOR_CACHE_DIR environment variable (explicit override)
    2. ~/.cache/stac_validator (standard user cache on Linux/macOS)
    3. %LOCALAPPDATA%\stac_validator (Windows user cache)
    4. tempfile.gettempdir()/stac_validator_cache (Docker/Lambda /tmp)

    Returns:
        Path to writable cache directory (guaranteed to exist or be creatable)
    """
    # 1. Respect explicit environment variable if set
    env_dir = os.environ.get("STAC_VALIDATOR_CACHE_DIR")
    if env_dir:
        try:
            os.makedirs(env_dir, exist_ok=True)
            logger.debug(f"Using STAC_VALIDATOR_CACHE_DIR: {env_dir}")
            return env_dir
        except (OSError, PermissionError) as e:
            logger.warning(f"Cannot write to STAC_VALIDATOR_CACHE_DIR ({env_dir}): {e}")

    # 2. Try standard user cache directory
    try:
        user_cache = os.path.join(os.path.expanduser("~"), ".cache", "stac_validator")
        os.makedirs(user_cache, exist_ok=True)
        logger.debug(f"Using user cache directory: {user_cache}")
        return user_cache
    except (OSError, PermissionError) as e:
        logger.debug(f"Cannot write to user cache ({user_cache}): {e}")

    # 3. Fallback to system temp directory
    temp_cache = os.path.join(tempfile.gettempdir(), "stac_validator_cache")
    try:
        os.makedirs(temp_cache, exist_ok=True)
        logger.debug(f"Falling back to temp cache: {temp_cache}")
        return temp_cache
    except (OSError, PermissionError) as e:
        logger.warning(f"Cannot write to temp cache ({temp_cache}): {e}")
        # Return temp_cache anyway - fetch_schema will handle write failures gracefully
        return temp_cache


# --- Thread-Safe Caches & Lock ---
SCHEMA_CACHE: Dict[str, Any] = {}
VALIDATOR_CACHE: Dict[Any, Any] = {}
# Builds in progress, so concurrent callers for the same key wait for one compile
VALIDATOR_BUILDS: Dict[Any, "Future[Any]"] = {}
CACHE_LOCK = threading.Lock()
# Dynamically determine writable cache directory across environments
LOCAL_SCHEMA_DIR = get_cache_directory()

# Default cap on "next" pages followed per paginated API endpoint
DEFAULT_MAX_PAGES = 1000

# Shared HTTP session with keep-alive connection pooling and retries for crawler workloads.
HTTP_SESSION = requests.Session()
_http_retries = Retry(
    total=3,
    backoff_factor=0.2,
    status_forcelist=[500, 502, 503, 504],
)
_http_adapter = HTTPAdapter(
    pool_connections=100,
    pool_maxsize=100,
    max_retries=_http_retries,
)
HTTP_SESSION.mount("http://", _http_adapter)
HTTP_SESSION.mount("https://", _http_adapter)
HTTP_SESSION.headers.update({"User-Agent": "stac-fast-cli/5.0"})


def get_local_path_for_uri(uri: str) -> str:
    """Creates a safe local filepath for a cached schema URL."""
    safe_filename = uri.replace("https://", "").replace("http://", "").replace("/", "_")
    return os.path.join(LOCAL_SCHEMA_DIR, safe_filename)


def fetch_schema(uri: str, quiet: bool = False) -> Dict[str, Any]:
    """The Ultimate Handler: RAM -> Disk -> Network -> Disk -> RAM

    Thread-safe schema fetching with three-tier caching (RAM -> Disk -> Network).

    Args:
        uri: Schema URI to fetch
        quiet: If True, suppress network fetch messages
    """
    # 1. RAM Cache (Thread-Safe Check)
    with CACHE_LOCK:
        if uri in SCHEMA_CACHE:
            return SCHEMA_CACHE[uri]

    local_path = get_local_path_for_uri(uri)

    # 2. Disk Cache
    if os.path.exists(local_path):
        try:
            with open(local_path, "r") as f:
                schema_dict = json.load(f)
                with CACHE_LOCK:
                    SCHEMA_CACHE[uri] = schema_dict
                return schema_dict
        except Exception:
            pass  # If corrupted, fallback to network

    # 3. Network Fetch
    if not quiet:
        click.secho(f"    [Network] Fetching: {uri}", fg="yellow", dim=True)
    logger.debug(f"Network cache miss. Fetching schema: {uri}")
    try:
        response = HTTP_SESSION.get(uri, timeout=10)
        response.raise_for_status()
        schema_dict = response.json()
    except requests.RequestException as e:
        raise RuntimeError(f"Could not resolve schema: {uri}. Reason: {e}")

    # 4. Save to Disk Cache (Safeguarded)
    # Fail gracefully if cache directory is unwritable (e.g., Docker/Lambda)
    # RAM cache (SCHEMA_CACHE) still functions normally even if disk write fails
    try:
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "w") as f:
            json.dump(schema_dict, f)
    except (IOError, OSError, PermissionError):
        # If we can't write to disk, no big deal - keep going with RAM cache
        pass

    # 5. Save to RAM Cache (Thread-Safe Store)
    with CACHE_LOCK:
        SCHEMA_CACHE[uri] = schema_dict
    return schema_dict


def compile_unrolled_schema(schema_dict: Dict[str, Any], quiet: bool = False) -> Any:
    """Unrolls top-level or allOf-nested oneOf/anyOf branches into separate compiled
    fastjsonschema functions so field-level errors are never swallowed by branch handling.

    Handles two patterns:
    1. Direct top-level oneOf/anyOf
    2. oneOf/anyOf nested inside allOf (e.g., Projection v2.0.0)

    Returns a validator function that tries each branch independently and reports
    the deepest error found (most specific field path).

    Args:
        schema_dict: The schema to compile
        quiet: If True, suppress network fetch messages
    """

    def handler(u: str) -> Dict[str, Any]:
        return fetch_schema(u, quiet=quiet)

    handlers_dict = {"http": handler, "https": handler}

    target_keyword = None
    branches = []
    base_meta = {}

    # Case 1: Direct top-level oneOf/anyOf
    if "oneOf" in schema_dict or "anyOf" in schema_dict:
        target_keyword = "oneOf" if "oneOf" in schema_dict else "anyOf"
        branches = schema_dict[target_keyword]
        base_meta = {
            k: v for k, v in schema_dict.items() if k not in ("oneOf", "anyOf")
        }

    # Case 2: oneOf/anyOf nested inside allOf (e.g., Projection v2.0.0)
    elif "allOf" in schema_dict and isinstance(schema_dict["allOf"], list):
        other_allOf = []
        for elem in schema_dict["allOf"]:
            if isinstance(elem, dict) and ("oneOf" in elem or "anyOf" in elem):
                target_keyword = "oneOf" if "oneOf" in elem else "anyOf"
                branches = elem[target_keyword]
                remainder = {
                    k: v for k, v in elem.items() if k not in ("oneOf", "anyOf")
                }
                if remainder:
                    other_allOf.append(remainder)
            else:
                other_allOf.append(elem)

        if branches:
            base_meta = {k: v for k, v in schema_dict.items() if k != "allOf"}
            if other_allOf:
                base_meta["allOf"] = other_allOf

    # Compile each branch independently
    if branches:
        compiled_branches = []
        for branch in branches:
            if "allOf" in base_meta:
                merged = {**base_meta, "allOf": base_meta["allOf"] + [branch]}
            else:
                merged = {**base_meta, **branch}

            try:
                # Tier 1: Standard optimization (keeps oneOf/allOf)
                opt = optimize_schema_for_compiler(merged, remove_allof=False)
                val = fastjsonschema.compile(opt, handlers=handlers_dict)
                compiled_branches.append(val)
            except Exception:
                try:
                    # Tier 2: Aggressive optimization (strips oneOf/allOf)
                    opt = optimize_schema_for_compiler(merged, remove_allof=True)
                    val = fastjsonschema.compile(opt, handlers=handlers_dict)
                    compiled_branches.append(val)
                except Exception:
                    pass

        if compiled_branches:

            def branch_validator(data: Dict[str, Any]) -> None:
                best_err = None
                max_depth = -1

                for val in compiled_branches:
                    try:
                        val(data)
                        return
                    except fastjsonschema.JsonSchemaValueException as err:
                        clean_p = parse_json_pointer(err.name)
                        # Root '$' errors score 0; deeper paths score higher
                        depth = (
                            0 if clean_p == "$" else len(re.split(r"[\[\.]", err.name))
                        )
                        if depth > max_depth:
                            max_depth = depth
                            best_err = err

                if best_err:
                    raise best_err

            return branch_validator

    opt = optimize_schema_for_compiler(schema_dict, remove_allof=False)
    return fastjsonschema.compile(opt, handlers=handlers_dict)


def optimize_schema_for_compiler(
    schema: Any,
    remove_allof: bool = False,
    in_props_branch: bool = False,
    in_shared_props: bool = False,
) -> Any:
    r"""Recursively patches STAC schemas in-memory for fastjsonschema code generation.

    Strips problematic constructs (like duration formats or dangling conditionals) and prunes
    empty subschemas ({}) that cause CPython IndentationErrors during compilation.

    Strips restrictive additionalProperties/unevaluatedProperties flags when traversing
    shared STAC Item properties so active extensions don't reject sibling fields,
    while preserving additionalProperties: false inside nested sub-objects (assets, links).

    Args:
        schema: The JSON schema dictionary to optimize
        remove_allof: If True, also remove allOf/oneOf/anyOf (used for aggressive patching)
        in_props_branch: True if we are inside a properties block (first level)
        in_shared_props: True if we are inside shared Item/Collection properties
    """
    if isinstance(schema, list):
        cleaned_list = []
        for item in schema:
            opt_item = optimize_schema_for_compiler(
                item, remove_allof, in_props_branch, in_shared_props
            )
            # Omit empty dictionaries inside composition lists (allOf, oneOf, anyOf)
            if isinstance(opt_item, dict) and not opt_item:
                continue
            cleaned_list.append(opt_item)
        return cleaned_list

    if isinstance(schema, dict):
        cleaned = {}
        for k, v in schema.items():
            # BUG FIX 1: fastjsonschema crashes on the 'duration' format
            if k == "format" and v == "duration":
                continue

            # BUG FIX 2: Strip unevaluatedProperties: false EVERYWHERE (Draft 2020-12 issue)
            # Modern extension schemas use unevaluatedProperties: false which causes false positives
            # when multiple extensions are composed. Each oneOf branch sees sibling extension fields
            # (eo:cloud_cover, datetime, etc.) and rejects them as unevaluated, collapsing to
            # "must be valid exactly by one definition (0 matches found)". Strip unconditionally.
            if k == "unevaluatedProperties" and v is False:
                continue

            # BUG FIX 3: Strip additionalProperties: false ONLY in shared Item properties
            # Preserve it in nested objects like assets, links, and sub-definitions
            if k == "additionalProperties" and v is False:
                if in_shared_props:
                    continue

            # BUG FIX 4: Conditionals & dependencies that produce empty Python code blocks
            if k in (
                "if",
                "then",
                "else",
                "dependencies",
                "dependentRequired",
                "dependentSchemas",
                "$comment",
            ):
                continue

            # BUG FIX 5: Remove allOf/oneOf/anyOf at top level when requested
            if remove_allof and k in ("allOf", "oneOf", "anyOf") and len(schema) > 1:
                continue

            # Context tracking across schema hierarchy
            next_in_props_branch = in_props_branch
            next_in_shared_props = in_shared_props

            if k == "properties":
                # Entering a properties block
                if in_props_branch or in_shared_props:
                    # Already in properties context, mark as shared
                    next_in_shared_props = True
                else:
                    # First properties block encountered
                    next_in_props_branch = True
            elif k in ("assets", "links"):
                # Nested objects - exit shared properties context
                next_in_shared_props = False
            elif k in ("$defs", "definitions"):
                # Definitions are part of shared properties context
                next_in_shared_props = True

            opt_v = optimize_schema_for_compiler(
                v, remove_allof, next_in_props_branch, next_in_shared_props
            )

            # BUG FIX 6: Prune empty subschemas ({}) in properties & patternProperties
            # BUG FIX 5: Prune empty subschemas ({}) in properties & patternProperties
            # to prevent fastjsonschema from generating empty for/else blocks
            if k in ("patternProperties", "properties", "dependentSchemas"):
                if isinstance(opt_v, dict):
                    non_empty_props = {
                        pk: pv
                        for pk, pv in opt_v.items()
                        if not (isinstance(pv, dict) and not pv)
                    }
                    if not non_empty_props:
                        continue
                    opt_v = non_empty_props

            if k in ("items", "additionalProperties", "unevaluatedProperties"):
                if isinstance(opt_v, dict) and not opt_v:
                    continue

            cleaned[k] = opt_v

        # Clean up empty composition keyword arrays
        for comp_key in ("allOf", "oneOf", "anyOf"):
            if (
                comp_key in cleaned
                and isinstance(cleaned[comp_key], list)
                and not cleaned[comp_key]
            ):
                del cleaned[comp_key]

        return cleaned

    return schema


def get_validator(
    stac_type: str, stac_version: str, extensions: List[str], quiet: bool = False
):
    """Builds and caches a validator based on Object Type, Version, and Extensions.

    Thread-safe validator compilation and caching.

    Args:
        stac_type: STAC object type (item, collection, catalog)
        stac_version: STAC version (e.g., "1.0.0")
        extensions: List of extension URIs
        quiet: If True, suppress network fetch and compilation messages
    """
    ext_key = tuple(sorted(extensions))
    cache_key = (stac_type, stac_version, ext_key)

    # Thread-safe Cache Read; join the in-flight build for this key if there is one
    with CACHE_LOCK:
        if cache_key in VALIDATOR_CACHE:
            return VALIDATOR_CACHE[cache_key], True
        build = VALIDATOR_BUILDS.get(cache_key)
        is_builder = build is None
        if build is None:
            build = VALIDATOR_BUILDS[cache_key] = Future()

    if not is_builder:
        # Another thread is building this key: share its validator or its exception.
        return build.result(), True

    try:
        validator = _build_validator(stac_type, stac_version, extensions, quiet)
    except BaseException as e:
        with CACHE_LOCK:
            del VALIDATOR_BUILDS[cache_key]
        build.set_exception(e)
        raise

    # Cache the resulting validator so future items use it instantly (Thread-safe Write)
    with CACHE_LOCK:
        VALIDATOR_CACHE[cache_key] = validator
        del VALIDATOR_BUILDS[cache_key]
    build.set_result(validator)
    return validator, False


def _build_validator(
    stac_type: str, stac_version: str, extensions: List[str], quiet: bool
) -> Callable[[Dict[str, Any]], None]:
    """Fetches and compiles the base and extension schemas into one validator."""
    # Determine base schema URI
    stac_type_lower = stac_type.lower()
    if stac_type_lower in ["item", "feature"]:
        base_uri = f"https://schemas.stacspec.org/v{stac_version}/item-spec/json-schema/item.json"
    elif stac_type_lower == "collection":
        base_uri = f"https://schemas.stacspec.org/v{stac_version}/collection-spec/json-schema/collection.json"
    elif stac_type_lower == "catalog":
        base_uri = f"https://schemas.stacspec.org/v{stac_version}/catalog-spec/json-schema/catalog.json"
    else:
        raise ValueError(f"Unknown STAC type for validation: {stac_type}")

    # Fetch the raw Base Schema directly
    raw_base_schema = fetch_schema(base_uri, quiet=quiet)

    def handler(u: str) -> Dict[str, Any]:
        return fetch_schema(u, quiet=quiet)

    handlers_dict = {"http": handler, "https": handler}

    try:
        # Tier 1: Try to compile with unrolled oneOf/anyOf branches first
        base_validator = compile_unrolled_schema(raw_base_schema, quiet=quiet)
        logger.debug(
            f"Base schema {stac_type} {stac_version} compiled with unrolled branch compilation"
        )
    except Exception:
        try:
            # Tier 2: If it fails, try aggressive patching (stripping allOf/oneOf/anyOf)
            optimized_base = optimize_schema_for_compiler(
                raw_base_schema, remove_allof=True
            )
            base_validator = fastjsonschema.compile(
                optimized_base, handlers=handlers_dict
            )
            logger.debug(
                f"Base schema {stac_type} {stac_version} compiled with fastjsonschema (aggressive patching)"
            )
        except Exception:
            # Tier 3: THE ULTIMATE FALLBACK
            # If fastjsonschema completely chokes, instantiate a cached jsonschema validator
            # that is strictly wired to use our high-speed fetch_schema session.
            import jsonschema

            resolver = jsonschema.RefResolver(
                base_uri=base_uri,
                referrer=raw_base_schema,
                handlers=handlers_dict,
            )
            ValidatorClass = jsonschema.validators.validator_for(raw_base_schema)

            # Pre-compile the jsonschema object ONCE, outside the execution loop
            js_validator = ValidatorClass(raw_base_schema, resolver=resolver)

            def base_validator(data):
                js_validator.validate(data)

            logger.debug(
                f"Base schema {stac_type} {stac_version} compiled with cached jsonschema fallback"
            )

    ext_validators: List[Tuple[str, Any, Any]] = []
    skipped_extensions = []

    if extensions:
        logger.info(
            f"Warming STAC Validator Cache: Compiling {len(extensions)} extension(s) for {stac_type} {stac_version}..."
        )
        if not quiet:
            click.secho(
                f"    [Extensions] Compiling {len(extensions)} extension(s):",
                fg="cyan",
                dim=True,
            )

    for ext in extensions:
        try:
            raw_ext_schema = fetch_schema(ext, quiet=quiet)

            # 1. Primary validator compilation with graceful fallback
            ext_val = None
            try:
                # Tier 1a: Raw unpatched schema
                ext_val = fastjsonschema.compile(
                    raw_ext_schema,
                    handlers=handlers_dict,
                )
            except Exception:
                try:
                    # Tier 1b: Standard optimization (strips duration format, if/then/else, keeps oneOf/allOf)
                    opt_schema = optimize_schema_for_compiler(
                        raw_ext_schema, remove_allof=False
                    )
                    ext_val = fastjsonschema.compile(
                        opt_schema,
                        handlers=handlers_dict,
                    )
                except Exception:
                    # Tier 1c: Aggressive optimization (strips top-level allOf/oneOf as last resort)
                    opt_schema_aggr = optimize_schema_for_compiler(
                        raw_ext_schema, remove_allof=True
                    )
                    ext_val = fastjsonschema.compile(
                        opt_schema_aggr,
                        handlers=handlers_dict,
                    )

            # 2. Pre-compile unrolled branch validator as a lazy diagnostic backup
            branch_val = None
            has_branches = "oneOf" in raw_ext_schema or "anyOf" in raw_ext_schema
            # Also check for oneOf/anyOf nested inside allOf (e.g., Projection v2.0.0)
            if (
                not has_branches
                and "allOf" in raw_ext_schema
                and isinstance(raw_ext_schema["allOf"], list)
            ):
                for elem in raw_ext_schema["allOf"]:
                    if isinstance(elem, dict) and ("oneOf" in elem or "anyOf" in elem):
                        has_branches = True
                        break

            if has_branches:
                try:
                    branch_val = compile_unrolled_schema(raw_ext_schema, quiet=quiet)
                except Exception:
                    pass

            ext_validators.append((ext, ext_val, branch_val))
            logger.debug(f"Successfully compiled STAC extension: {ext}")
            if not quiet:
                click.secho(f"      ✅ {ext}", fg="green", dim=True)

        except Exception as e:
            logger.warning(
                f"Skipped extension due to compiler incompatibility: {ext} - {type(e).__name__}: {str(e)[:100]}"
            )
            if not quiet:
                click.secho(f"      ❌ {ext}: {type(e).__name__}", fg="red", dim=True)
            skipped_extensions.append(ext)

    if skipped_extensions and not quiet:
        click.secho(
            f"    [Warning] Skipped {len(skipped_extensions)} extension(s) due to fastjsonschema incompatibility:",
            fg="yellow",
            dim=True,
        )
        for ext in skipped_extensions:
            click.secho(f"      - {ext}", fg="yellow", dim=True)
        click.secho(
            "    For strict validation of all extensions, use: stac-valid validate <file>",
            fg="yellow",
            dim=True,
        )

    def validator(data: Dict[str, Any]) -> None:
        collected_errors: List[FastSTACValidationError] = []

        # 1. Base STAC Schema
        try:
            base_validator(data)
        except fastjsonschema.JsonSchemaValueException as e:
            clean_path = parse_json_pointer(e.name)
            msg = e.message.replace(e.name, "").strip()
            collected_errors.append(
                FastSTACValidationError(f"Base {stac_type}", clean_path, msg)
            )

        # 2. Individual Extension Schemas (evaluate ALL extensions)
        for ext_uri, ext_val, branch_val in ext_validators:
            try:
                ext_val(data)
            except fastjsonschema.JsonSchemaValueException as e:
                clean_path = parse_json_pointer(e.name)
                msg = e.message.replace(e.name, "").strip()

                # If we have a branch validator, try it to unmask composition errors
                # (e.g., oneOf/anyOf where fastjsonschema swallows the real error)
                if branch_val is not None:
                    try:
                        branch_val(data)
                        # Branch validator passed - item is valid, don't report error
                        continue
                    except fastjsonschema.JsonSchemaValueException as branch_e:
                        # Branch validator also failed - use its more specific error
                        clean_path = parse_json_pointer(branch_e.name)
                        msg = branch_e.message.replace(branch_e.name, "").strip()

                collected_errors.append(
                    FastSTACValidationError(f"Extension: {ext_uri}", clean_path, msg)
                )

        # Raise all accumulated errors at the end of the item pass
        if collected_errors:
            raise FastSTACMultiValidationError(collected_errors)

    return validator


class FastValidator:
    def __init__(
        self,
        stac_file: str,
        quiet: bool = False,
        verbose: bool = False,
        limit: Optional[int] = None,
        validate_geometry: bool = False,
        max_depth: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: float = 15,
        session: Optional[requests.Session] = None,
        keep_documents: bool = False,
        max_pages: Optional[int] = None,
    ):
        self.stac_file = stac_file
        self.quiet = quiet
        self.valid = True
        self.verbose = verbose
        self.limit = limit
        self.validate_geometry = validate_geometry
        # Maximum recursion depth (root = 0); None means unlimited
        self.max_depth = max_depth
        # Transport for STAC resource fetches; schema fetching always uses
        # the module-level HTTP_SESSION
        self.timeout = timeout
        self.session = session or HTTP_SESSION
        self.headers = headers
        # Opt-in result path -> loaded document map for consumers that need
        # the documents without re-fetching
        self.keep_documents = keep_documents
        self.loaded_objects: Dict[str, Any] = {}
        # Maximum "next" pages consumed per paginated endpoint, counting the
        # first page; 0 follows every page, None uses the default cap.
        # Endpoints cut short by the cap are recorded as
        # (first page path, pages consumed).
        if max_pages is not None and max_pages < 0:
            raise ValueError("max_pages must be 0 or greater")
        self.max_pages = DEFAULT_MAX_PAGES if max_pages is None else max_pages
        self.truncated_endpoints: List[Tuple[str, int]] = []
        # Per-thread sessions for parallel fetches (requests.Session is not
        # documented thread-safe)
        self._thread_local = threading.local()
        self.message: List[Dict[str, Any]] = []

    def _validate_datetime_range(self, data: Dict[str, Any]) -> None:
        """Ensures start_datetime is not strictly after end_datetime per STAC Spec.

        Uses lexicographical string comparison since RFC 3339 timestamps sort
        chronologically when compared as strings. This avoids datetime parsing
        issues in Python 3.8/3.9 with non-standard ISO 8601 formats.
        """
        if data.get("type") != "Feature":
            return

        properties = data.get("properties", {})
        start_str = properties.get("start_datetime")
        end_str = properties.get("end_datetime")

        if start_str and end_str:
            # RFC 3339 timestamps sort lexicographically, so we can compare as strings
            # This avoids datetime.fromisoformat() parsing issues in Python 3.8/3.9
            if start_str > end_str:
                raise ValueError(
                    f"Logical Error: start_datetime ({start_str}) cannot be strictly after end_datetime ({end_str})"
                )

    def _validate_geometry(self, data: Dict[str, Any]) -> None:
        """Lightweight topology check for global bounds and antimeridian crossings."""
        if data.get("type") != "Feature":
            return

        geometry = data.get("geometry")
        if not geometry:
            return

        geom_type = geometry.get("type")
        coords = geometry.get("coordinates")
        if not coords or geom_type not in ("Polygon", "MultiPolygon"):
            return

        def check_bounds(c: list):
            if not c:
                return
            if isinstance(c[0], (int, float)):
                if not (-180 <= c[0] <= 180) or not (-90 <= c[1] <= 90):
                    raise ValueError(f"Geometry out of global WGS84 bounds: {c}")
            else:
                for sub in c:
                    check_bounds(sub)

        check_bounds(coords)

        def check_rings(rings: list):
            max_vertices = int(os.environ.get("MAX_TOPOLOGY_VERTICES", 5000))
            for ring in rings:
                if len(ring) < 4:
                    raise ValueError("Polygon ring must have at least 4 coordinates.")
                if len(ring) > max_vertices:
                    raise ValueError(
                        f"Geometry exceeds maximum allowed vertices ({max_vertices}). Found {len(ring)}."
                    )
                for i in range(len(ring) - 1):
                    if abs(ring[i][0] - ring[i + 1][0]) > 180:
                        raise ValueError(
                            f"Improper antimeridian crossing between {ring[i][0]} and {ring[i + 1][0]}"
                        )

        if geom_type == "Polygon":
            check_rings(coords)
        elif geom_type == "MultiPolygon":
            for poly in coords:
                check_rings(poly)

    def _limit_reached(self, results: List[Dict]) -> bool:
        return self.limit is not None and len(results) >= self.limit

    def _get_base_schema_uri(self, stac_type: str, stac_version: str) -> str:
        stac_type_lower = stac_type.lower()
        if stac_type_lower in ["item", "feature"]:
            return f"https://schemas.stacspec.org/v{stac_version}/item-spec/json-schema/item.json"
        if stac_type_lower == "collection":
            return f"https://schemas.stacspec.org/v{stac_version}/collection-spec/json-schema/collection.json"
        if stac_type_lower == "catalog":
            return f"https://schemas.stacspec.org/v{stac_version}/catalog-spec/json-schema/catalog.json"
        raise ValueError(f"Unknown STAC type for validation: {stac_type}")

    def _is_ref_resolution_error(self, err: Exception) -> bool:
        err_text = str(err)
        err_type = err.__class__.__name__
        return (
            "Unresolvable JSON pointer" in err_text
            or "RefResolutionError" in err_type
            or "Unresolvable" in err_type
        )

    def _validate_with_jsonschema_fallback(
        self,
        item: Dict[str, Any],
        stac_type: str,
        stac_version: str,
        extensions: List[str],
    ) -> None:
        """Fallback validation path using the main jsonschema resolver utility."""
        base_schema = self._get_base_schema_uri(stac_type, stac_version)
        validate_with_ref_resolver(base_schema, item)
        for ext_schema in extensions:
            validate_with_ref_resolver(ext_schema, item)

    @staticmethod
    def _resolve_link_path(file_path: str, href: str) -> str:
        """Resolve a link href relative to the document containing it.

        os.path.normpath collapses "//" to "/", which corrupts URLs like
        "https://host" into "https:/host", so URL bases use urljoin instead.
        """
        if href.startswith("http"):
            return href
        if file_path.startswith("http"):
            return urljoin(file_path, href)
        return os.path.normpath(os.path.join(os.path.dirname(file_path), href))

    def _session_for_current_thread(self) -> requests.Session:
        """Return the session to use on the current thread.

        requests.Session is not documented thread-safe, so worker threads in
        the parallel prefetch get their own session mirroring the base one.
        A user-supplied session is always used as-is (its thread-safety is
        the caller's responsibility).
        """
        if self.session is not HTTP_SESSION:
            return self.session
        if threading.current_thread() is threading.main_thread():
            return HTTP_SESSION
        sess = getattr(self._thread_local, "session", None)
        if sess is None:
            sess = requests.Session()
            sess.mount("http://", _http_adapter)
            sess.mount("https://", _http_adapter)
            sess.headers.update(HTTP_SESSION.headers)
            # Preserve instance-level overrides, e.g. a monkeypatched get()
            override = HTTP_SESSION.__dict__.get("get")
            if override is not None:
                sess.get = override  # type: ignore[method-assign]
            self._thread_local.session = sess
        return sess

    def _load_json_resource(self, resource_path: str) -> Dict[str, Any]:
        if resource_path.startswith("http"):
            # Only pass headers when configured so custom sessions and
            # patched HTTP_SESSION.get signatures keep working
            kwargs: Dict[str, Any] = {"timeout": self.timeout}
            if self.headers:
                kwargs["headers"] = self.headers
            response = self._session_for_current_thread().get(resource_path, **kwargs)
            response.raise_for_status()
            data = response.json()
        else:
            with open(resource_path, "r") as f:
                data = json.load(f)
        if self.keep_documents:
            self.loaded_objects[resource_path] = data
        return data

    def _get_parallel_fetch_workers(self, item_count: int) -> int:
        return max(1, min(8, item_count))

    def _load_collection_documents(
        self, collection_urls: List[str]
    ) -> List[Tuple[str, Optional[Dict[str, Any]], Optional[Exception]]]:
        if len(collection_urls) <= 1:
            results_single: List[
                Tuple[str, Optional[Dict[str, Any]], Optional[Exception]]
            ] = []
            for collection_url in collection_urls:
                try:
                    results_single.append(
                        (collection_url, self._load_json_resource(collection_url), None)
                    )
                except Exception as exc:
                    results_single.append((collection_url, None, exc))
            return results_single

        with ThreadPoolExecutor(
            max_workers=self._get_parallel_fetch_workers(len(collection_urls))
        ) as executor:
            futures: List[Future[Dict[str, Any]]] = [
                executor.submit(self._load_json_resource, collection_url)
                for collection_url in collection_urls
            ]

            results_parallel: List[
                Tuple[str, Optional[Dict[str, Any]], Optional[Exception]]
            ] = []
            for collection_url, future in zip(collection_urls, futures):
                try:
                    results_parallel.append((collection_url, future.result(), None))
                except Exception as exc:
                    results_parallel.append((collection_url, None, exc))

        return results_parallel

    def _prefetch_api_collection_resources(
        self, collection_url: str, remaining_capacity: Optional[int] = None
    ) -> Tuple[str, Optional[Dict[str, Dict[str, Any]]], Optional[Exception]]:
        try:
            collection_data = self._load_json_resource(collection_url)
        except Exception as exc:
            return collection_url, None, exc

        resources = {collection_url: collection_data}

        # Don't fetch items pages when the result limit is already exhausted
        if remaining_capacity is not None and remaining_capacity <= 0:
            return collection_url, resources, None

        for link in collection_data.get("links", []):
            if link.get("rel") != "items":
                continue

            href = link.get("href", "")
            if not href:
                continue

            items_path = self._resolve_link_path(collection_url, href)

            try:
                resources[items_path] = self._load_json_resource(items_path)
            except Exception as exc:
                # The link loop retries and reports the failure; log so the
                # prefetch error itself isn't invisible
                logger.warning("Prefetch failed for %s: %s", items_path, exc)

        return collection_url, resources, None

    def _prefetch_api_collection_resources_batch(
        self,
        collection_urls: List[str],
        remaining_capacity: Optional[int] = None,
    ) -> List[Tuple[str, Optional[Dict[str, Dict[str, Any]]], Optional[Exception]]]:
        if len(collection_urls) <= 1:
            return [
                self._prefetch_api_collection_resources(
                    collection_url, remaining_capacity
                )
                for collection_url in collection_urls
            ]

        with ThreadPoolExecutor(
            max_workers=self._get_parallel_fetch_workers(len(collection_urls))
        ) as executor:
            futures: List[
                Future[
                    Tuple[str, Optional[Dict[str, Dict[str, Any]]], Optional[Exception]]
                ]
            ] = [
                executor.submit(
                    self._prefetch_api_collection_resources,
                    collection_url,
                    remaining_capacity,
                )
                for collection_url in collection_urls
            ]
            return [future.result() for future in futures]

    def _validate_single_item(
        self, item: Dict[str, Any], item_index: int
    ) -> Tuple[bool, float, float, str, List[str]]:
        """Validate a single STAC item and return (is_valid, setup_ms, exec_ms, item_id, error_messages).

        This helper eliminates code duplication between run() and run_dict() by providing
        a unified validation pipeline for individual items.

        Returns:
            Tuple of (is_valid, setup_time_ms, exec_time_ms, item_id, error_messages)
        """
        item_id = item.get("id", f"unknown-{item_index}")
        stac_version = item.get("stac_version", "1.0.0")
        extensions = item.get("stac_extensions", [])

        # Map Feature->Item, others keep their type
        actual_type = (
            "Item" if item.get("type") == "Feature" else item.get("type", "Catalog")
        )

        # --- Setup Timer ---
        t0 = time.perf_counter()
        try:
            validator, _ = get_validator(
                actual_type, stac_version, extensions, quiet=self.quiet
            )
        except Exception as e:
            t1 = time.perf_counter()
            setup_time = (t1 - t0) * 1000
            error_msg = f"Setup failed: {str(e)}"
            return False, setup_time, 0.0, item_id, [error_msg]

        t1 = time.perf_counter()
        setup_time = (t1 - t0) * 1000

        # --- Execution Timer ---
        t2 = time.perf_counter()
        error_messages: List[str] = []

        try:
            validator(item)
            # Run logical firewalls
            self._validate_datetime_range(item)
            if self.validate_geometry:
                self._validate_geometry(item)
            t3 = time.perf_counter()
            exec_time = (t3 - t2) * 1000
            return True, setup_time, exec_time, item_id, error_messages

        except FastSTACMultiValidationError as e:
            t3 = time.perf_counter()
            exec_time = (t3 - t2) * 1000
            error_messages = [str(single_err) for single_err in e.errors]
            return False, setup_time, exec_time, item_id, error_messages

        except FastSTACValidationError as e:
            t3 = time.perf_counter()
            exec_time = (t3 - t2) * 1000
            error_messages = [str(e)]
            return False, setup_time, exec_time, item_id, error_messages

        except fastjsonschema.JsonSchemaValueException as e:
            t3 = time.perf_counter()
            exec_time = (t3 - t2) * 1000
            error_msg = f"{e.name} {e.message.replace(e.name, '').strip()}"
            if "disallowed definition" in error_msg and "collection" in error_msg:
                error_msg = (
                    "STAC Spec Violation: Missing {'rel': 'collection'} in links array."
                )
            error_messages = [error_msg]
            return False, setup_time, exec_time, item_id, error_messages

        except ValueError as e:
            t3 = time.perf_counter()
            exec_time = (t3 - t2) * 1000
            error_messages = [str(e)]
            return False, setup_time, exec_time, item_id, error_messages

        except Exception as e:
            t3 = time.perf_counter()
            exec_time = (t3 - t2) * 1000

            if self._is_ref_resolution_error(e):
                try:
                    self._validate_with_jsonschema_fallback(
                        item, actual_type, stac_version, extensions
                    )
                    return True, setup_time, exec_time, item_id, error_messages
                except Exception as fallback_err:
                    error_messages = [str(fallback_err)]
                    return False, setup_time, exec_time, item_id, error_messages
            else:
                error_messages = [str(e)]
                return False, setup_time, exec_time, item_id, error_messages

    def run(self):
        """Universal high-speed STAC Validator (Items, Collections, Catalogs, FeatureCollections)"""
        if not self.quiet:
            click.secho(f"\n📂 Loading: {self.stac_file}", fg="blue", bold=True)

        try:
            data = self._load_json_resource(self.stac_file)
        except Exception as e:
            if not self.quiet:
                click.secho(
                    f"❌ Error reading {self.stac_file}: {e}", fg="red", bold=True
                )
            self.valid = False
            self.message = [
                {
                    "path": self.stac_file,
                    "id": "unknown",
                    "valid_stac": False,
                    "stac_type": "unknown",
                    "stac_version": "unknown",
                    "error_message": f"Failed to load: {e}",
                }
            ]
            return

        if not isinstance(data, dict):
            self.valid = False
            self.message = [
                {
                    "path": self.stac_file,
                    "id": "unknown",
                    "valid_stac": False,
                    "stac_type": "unknown",
                    "stac_version": "unknown",
                    "error_message": "Root document is not a JSON object.",
                }
            ]
            return

        # Detect payload structure
        obj_type = data.get("type", "")
        items_to_validate = []

        if obj_type == "FeatureCollection":
            items_to_validate = data.get("features", [])
            if not self.quiet:
                click.secho(
                    f"📦 Detected FeatureCollection ({len(items_to_validate)} Items)\n",
                    fg="cyan",
                )
        elif obj_type == "Feature":
            items_to_validate = [data]
            if not self.quiet:
                click.secho("📄 Detected: STAC Item\n", fg="cyan")
        elif obj_type == "Collection":
            items_to_validate = [data]
            if not self.quiet:
                click.secho("📚 Detected: STAC Collection\n", fg="cyan")
        elif obj_type == "Catalog" or ("id" in data and "description" in data):
            # Fallback for old catalogs missing the 'type' field
            data["type"] = "Catalog"
            items_to_validate = [data]
            if not self.quiet:
                click.secho("🗂️  Detected: STAC Catalog\n", fg="cyan")
        else:
            if "type" in data:
                click.secho(
                    f"❌ Unknown JSON type. Unsupported 'type' value: {obj_type!r}.",
                    fg="red",
                    bold=True,
                )
            else:
                click.secho(
                    "❌ Unknown JSON type. Missing 'type' field.", fg="red", bold=True
                )
            self.valid = False
            return

        # --- Metrics ---
        available_objects = len(items_to_validate)
        if self.limit is not None:
            items_to_validate = items_to_validate[: self.limit]
            if not self.quiet and available_objects > self.limit:
                click.secho(
                    f"🔢 Limiting validation to first {self.limit} objects (out of {available_objects}).",
                    fg="yellow",
                )

        total_setup_ms = 0.0
        total_exec_ms = 0.0
        valid_count = 0
        invalid_count = 0
        error_registry: Dict[str, List[str]] = {}
        stac_versions_found: Set[str] = set()
        schemas_checked: Set[str] = set()

        for index, item in enumerate(items_to_validate):
            # Use unified validation helper
            is_valid, setup_time, exec_time, item_id, error_messages = (
                self._validate_single_item(item, index)
            )

            # Track versions and schemas
            stac_version = item.get("stac_version", "1.0.0")
            extensions = item.get("stac_extensions", [])
            actual_type = (
                "Item" if item.get("type") == "Feature" else item.get("type", "Catalog")
            )

            stac_versions_found.add(stac_version)

            # Build schema URI for this object type
            try:
                base_schema = self._get_base_schema_uri(actual_type, stac_version)
            except ValueError:
                base_schema = ""

            if base_schema:
                schemas_checked.add(base_schema)

            # Track extensions
            for ext in extensions:
                schemas_checked.add(ext)

            # Accumulate metrics
            total_setup_ms += setup_time
            total_exec_ms += exec_time

            if is_valid:
                valid_count += 1
                status_text = click.style("✅ VALID", fg="green")
            else:
                invalid_count += 1
                self.valid = False
                status_text = click.style("❌ INVALID", fg="red")
                # Register all errors for this item
                for error_msg in error_messages:
                    if error_msg not in error_registry:
                        error_registry[error_msg] = []
                    error_registry[error_msg].append(item_id)

            if not self.quiet:
                if self.verbose or index < 5 or (len(items_to_validate) < 20):
                    # Note: is_cached info is not available from helper, use placeholder
                    click.echo(
                        f"[{index + 1}] ID: {item_id} | Type: {actual_type} | Setup: {setup_time:>6.2f}ms | Exec: {exec_time:>5.2f}ms | {status_text}"
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
        click.echo(
            f"Valid Objects           : {click.style(str(valid_count), fg='green')}"
        )

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

        # Populate the message attribute for API usage (similar to StacValidate)
        self.message = [
            {
                "path": self.stac_file,
                "valid_stac": self.valid,
                "stac_versions": sorted(list(stac_versions_found)),
                "schemas_checked": sorted(list(schemas_checked)),
                "total_objects": len(items_to_validate),
                "valid_objects": valid_count,
                "invalid_objects": invalid_count,
                "setup_time_ms": total_setup_ms,
                "execution_time_ms": total_exec_ms,
                "errors": [
                    {
                        "error_message": err_msg,
                        "affected_items": affected_ids,
                        "count": len(affected_ids),
                    }
                    for err_msg, affected_ids in error_registry.items()
                ],
            }
        ]

        click.echo("\n")

    def run_dict(self, stac_dict: Dict[str, Any], source_name: str = "in-memory"):
        """Validate a native Python dictionary directly without file/network loading."""
        if not isinstance(stac_dict, dict):
            self.valid = False
            self.message = [
                {
                    "path": source_name,
                    "valid_stac": False,
                    "error_message": "Input to run_dict must be a dictionary.",
                }
            ]
            return

        self.stac_file = source_name

        data = dict(stac_dict)
        obj_type = data.get("type", "")
        items_to_validate: List[Dict[str, Any]] = []

        if obj_type == "FeatureCollection":
            features = data.get("features", [])
            items_to_validate = features if isinstance(features, list) else []
        elif obj_type in ["Feature", "Collection"]:
            items_to_validate = [data]
        elif obj_type == "Catalog" or ("id" in data and "description" in data):
            data["type"] = "Catalog"
            items_to_validate = [data]
        else:
            self.valid = False
            if "type" in data:
                error_msg = (
                    f"Unknown JSON type. Unsupported 'type' value: {obj_type!r}."
                )
            else:
                error_msg = "Unknown JSON type. Missing 'type' field."

            self.message = [
                {
                    "path": source_name,
                    "valid_stac": False,
                    "error_message": error_msg,
                }
            ]
            return

        available_objects = len(items_to_validate)
        if self.limit is not None:
            items_to_validate = items_to_validate[: self.limit]

        total_setup_ms = 0.0
        total_exec_ms = 0.0
        valid_count = 0
        invalid_count = 0
        error_registry: Dict[str, List[str]] = {}
        stac_versions_found: Set[str] = set()
        schemas_checked: Set[str] = set()

        self.valid = True

        for index, item in enumerate(items_to_validate):
            # Use unified validation helper
            is_valid, setup_time, exec_time, item_id, error_messages = (
                self._validate_single_item(item, index)
            )

            # Track versions and schemas
            stac_version = item.get("stac_version", "1.0.0")
            extensions = item.get("stac_extensions", [])
            actual_type = (
                "Item" if item.get("type") == "Feature" else item.get("type", "Catalog")
            )

            stac_versions_found.add(stac_version)

            try:
                base_schema = self._get_base_schema_uri(actual_type, stac_version)
            except ValueError:
                base_schema = ""

            if base_schema:
                schemas_checked.add(base_schema)

            for ext in extensions:
                schemas_checked.add(ext)

            # Accumulate metrics
            total_setup_ms += setup_time
            total_exec_ms += exec_time

            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1
                self.valid = False
                # Register all errors for this item
                for error_msg in error_messages:
                    if error_msg not in error_registry:
                        error_registry[error_msg] = []
                    error_registry[error_msg].append(item_id)

        self.message = [
            {
                "path": source_name,
                "valid_stac": self.valid,
                "stac_versions": sorted(list(stac_versions_found)),
                "schemas_checked": sorted(list(schemas_checked)),
                "total_objects": len(items_to_validate),
                "valid_objects": valid_count,
                "invalid_objects": invalid_count,
                "setup_time_ms": total_setup_ms,
                "execution_time_ms": total_exec_ms,
                "input_objects": available_objects,
                "errors": [
                    {
                        "error_message": err_msg,
                        "affected_items": affected_ids,
                        "count": len(affected_ids),
                    }
                    for err_msg, affected_ids in error_registry.items()
                ],
            }
        ]

    def run_recursive(self):
        """Recursively validate a local STAC catalog/collection and all its children."""
        start_time = time.perf_counter()

        # Load the root STAC object
        try:
            root_data = self._load_json_resource(self.stac_file)
            root_path = (
                self.stac_file
                if self.stac_file.startswith("http")
                else os.path.abspath(self.stac_file)
            )
            if self.keep_documents:
                # Results reference root_path (abspath for local files),
                # while _load_json_resource keys the map by stac_file
                self.loaded_objects.setdefault(root_path, root_data)
        except Exception as e:
            if not self.quiet:
                click.secho(
                    f"❌ Error reading {self.stac_file}: {e}", fg="red", bold=True
                )
            self.valid = False
            self.message = [
                {
                    "path": self.stac_file,
                    "id": "unknown",
                    "valid_stac": False,
                    "stac_type": "unknown",
                    "stac_version": "unknown",
                    "error_message": f"Failed to load: {e}",
                }
            ]
            return

        if not isinstance(root_data, dict):
            self.valid = False
            self.message = [
                {
                    "path": root_path,
                    "id": "unknown",
                    "valid_stac": False,
                    "stac_type": "unknown",
                    "stac_version": "unknown",
                    "error_message": "Root document is not a JSON object.",
                }
            ]
            return

        if "conformsTo" in root_data and not self.quiet:
            click.secho(
                "⚠️  STAC API detected; only 'child'/'item' links are followed "
                "in recursive mode. Use --api or run_api() to traverse API links.",
                fg="yellow",
            )

        # Recursively validate the root and all children
        results = []
        visited = set()
        visited.add(root_path)
        self._validate_recursive(
            root_data, root_path, results, visited, is_api=False, depth=0
        )

        if self.limit is not None and not self.quiet and len(results) >= self.limit:
            click.secho(
                f"🔢 Validation limit reached ({self.limit} objects).",
                fg="yellow",
            )

        if not self.quiet:
            # Display results
            click.echo("\n" + "=" * 55)
            click.secho("📊 RECURSIVE VALIDATION SUMMARY", bold=True, fg="blue")
            click.echo("=" * 55)

            valid_count = sum(1 for r in results if r["valid_stac"])
            invalid_count = len(results) - valid_count
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            click.echo(f"Total Objects Validated: {len(results)}")
            click.echo(f"Valid Objects:           {valid_count}")
            click.echo(f"Invalid Objects:         {invalid_count}")
            click.echo(f"Execution Time:          {elapsed_ms:.2f} ms")

            if invalid_count > 0:
                click.echo("\n" + "=" * 55)
                click.secho("🚨 INVALID OBJECTS", bold=True, fg="red")
                click.echo("=" * 55)

                # Group errors by message
                error_groups = {}
                for result in results:
                    if not result["valid_stac"]:
                        error_msg = result.get("error_message", "Unknown error")
                        if error_msg not in error_groups:
                            error_groups[error_msg] = []
                        # Store both path and ID for better identification
                        object_id = result.get("id", "unknown")
                        error_groups[error_msg].append(
                            {"path": result["path"], "id": object_id}
                        )

                # Display grouped errors
                for error_msg, items in error_groups.items():
                    click.echo(f"\n❌ {error_msg}")
                    click.echo(f"   Affected Objects: {len(items)}")
                    # Show first 5 examples
                    for item in items[:5]:
                        item_id = item["id"] if item["id"] != "unknown" else ""
                        if item_id:
                            click.echo(f"   - {item['path']} (ID: {item_id})")
                        else:
                            click.echo(f"   - {item['path']}")
                    if len(items) > 5:
                        click.echo(f"   ... and {len(items) - 5} more")

        # Set overall validity
        self.valid = all(r.get("valid_stac", False) for r in results)
        self.message = results

    def run_api(self):
        """Recursively validate a STAC API catalog and all its collections/items."""
        start_time = time.perf_counter()

        if not self.quiet:
            click.secho("🚀 Starting STAC API validation...", fg="blue", bold=True)
            click.secho(
                "⏳ Fetching API root and discovery links...", fg="cyan", dim=True
            )

        # Load the root STAC API object
        try:
            root_data = self._load_json_resource(self.stac_file)
            root_path = (
                self.stac_file
                if self.stac_file.startswith("http")
                else os.path.abspath(self.stac_file)
            )
            if self.keep_documents:
                # Results reference root_path (abspath for local files),
                # while _load_json_resource keys the map by stac_file
                self.loaded_objects.setdefault(root_path, root_data)
        except Exception as e:
            if not self.quiet:
                click.secho(
                    f"❌ Error reading {self.stac_file}: {e}", fg="red", bold=True
                )
            self.valid = False
            self.message = [
                {
                    "path": self.stac_file,
                    "id": "unknown",
                    "valid_stac": False,
                    "stac_type": "unknown",
                    "stac_version": "unknown",
                    "error_message": f"Failed to load: {e}",
                }
            ]
            return

        if not isinstance(root_data, dict):
            self.valid = False
            self.message = [
                {
                    "path": root_path,
                    "id": "unknown",
                    "valid_stac": False,
                    "stac_type": "unknown",
                    "stac_version": "unknown",
                    "error_message": "Root document is not a JSON object.",
                }
            ]
            return

        # Recursively validate the root and all children (API mode)
        results = []
        visited = set()
        visited.add(root_path)
        self._progress_count = 0

        if not self.quiet:
            click.secho(
                "🧠 Compiling/warming schemas (first objects may be slower)...",
                fg="cyan",
                dim=True,
            )

        self._validate_recursive(
            root_data, root_path, results, visited, is_api=True, depth=0
        )

        if self.limit is not None and not self.quiet and len(results) >= self.limit:
            click.secho(
                f"🔢 Validation limit reached ({self.limit} objects).",
                fg="yellow",
            )

        if self.truncated_endpoints and not self.quiet:
            click.secho(
                f"⚠️  Pagination cap ({self.max_pages} pages) reached; "
                "results are incomplete for:",
                fg="yellow",
            )
            for endpoint, pages in self.truncated_endpoints:
                click.secho(f"   {endpoint} ({pages} pages)", fg="yellow", dim=True)

        if not self.quiet:
            # Display results
            click.echo("\n" + "=" * 55)
            click.secho("📊 STAC API VALIDATION SUMMARY", bold=True, fg="blue")
            click.echo("=" * 55)

            valid_count = sum(1 for r in results if r["valid_stac"])
            invalid_count = len(results) - valid_count
            elapsed_ms = (time.perf_counter() - start_time) * 1000

            click.echo(f"Total Objects Validated: {len(results)}")
            click.echo(f"Valid Objects:           {valid_count}")
            click.echo(f"Invalid Objects:         {invalid_count}")
            click.echo(f"Execution Time:          {elapsed_ms:.2f} ms")

            if invalid_count > 0:
                click.echo("\n" + "=" * 55)
                click.secho("🚨 INVALID OBJECTS", bold=True, fg="red")
                click.echo("=" * 55)

                # Group errors by message
                error_groups = {}
                for result in results:
                    if not result["valid_stac"]:
                        error_msg = result.get("error_message", "Unknown error")
                        if error_msg not in error_groups:
                            error_groups[error_msg] = []
                        # Store both path and ID for better identification
                        object_id = result.get("id", "unknown")
                        error_groups[error_msg].append(
                            {"path": result["path"], "id": object_id}
                        )

                # Display grouped errors
                for error_msg, items in error_groups.items():
                    click.echo(f"\n❌ {error_msg}")
                    click.echo(f"   Affected Objects: {len(items)}")
                    # Show first 5 examples
                    for item in items[:5]:
                        item_id = item["id"] if item["id"] != "unknown" else ""
                        if item_id:
                            click.echo(f"   - {item['path']} (ID: {item_id})")
                        else:
                            click.echo(f"   - {item['path']}")
                    if len(items) > 5:
                        click.echo(f"   ... and {len(items) - 5} more")

        # Set overall validity
        self.valid = all(r.get("valid_stac", False) for r in results)
        self.message = results

    def _next_page_path(
        self, page_data: Dict[str, Any], page_path: str, visited: Set[str]
    ) -> Optional[str]:
        """Resolve the "next" pagination link of an API page, if unvisited."""
        for link in page_data.get("links", []):
            if isinstance(link, dict) and link.get("rel") == "next":
                href = link.get("href", "")
                if not href:
                    return None
                next_path = self._resolve_link_path(page_path, href)
                if next_path in visited:
                    return None
                visited.add(next_path)
                return next_path
        return None

    def _validate_recursive(
        self,
        data: Dict[str, Any],
        file_path: str,
        results: List[Dict],
        visited: Set[str],
        is_api: bool = False,
        collection_id: Optional[str] = None,
        prefetched_resources: Optional[Dict[str, Dict[str, Any]]] = None,
        depth: int = 0,
    ):
        """Recursively validate a STAC object and its children.

        Args:
            data: The STAC object to validate
            file_path: Path or URL to the object
            results: List to accumulate validation results
            visited: Set of already-visited paths to prevent circular references
            is_api: If True, follow API-specific links (data, items, next); if False, follow catalog links (child, item)
            collection_id: Optional collection ID for items from FeatureCollections
            depth: Current recursion depth (0 at root)
        """
        # Protect against deeply nested catalog structures
        MAX_RECURSION_DEPTH = 250
        if depth > MAX_RECURSION_DEPTH:
            results.append(
                {
                    "path": file_path,
                    "valid_stac": False,
                    "error_message": f"Maximum catalog depth ({MAX_RECURSION_DEPTH}) exceeded.",
                }
            )
            return

        # User-configured depth cap: objects at or beyond it are skipped
        if self.max_depth is not None and depth >= self.max_depth:
            return

        if self._limit_reached(results):
            return

        # Determine STAC type - could be "Catalog", "Collection", or "Feature"
        # (Item). STAC <1.0 documents lack a "type" member, so infer
        # structurally: 'extent' marks a Collection (a bare 'license' does not -
        # pre-1.0 catalogs may carry one), anything else is a Catalog.
        raw_type = data.get("type")
        if raw_type in ("Feature", "Collection", "Catalog"):
            stac_type = {
                "Feature": "item",
                "Collection": "collection",
                "Catalog": "catalog",
            }[raw_type]
        elif raw_type:
            stac_type = str(raw_type).lower()
        else:
            stac_type = "collection" if "extent" in data else "catalog"

        stac_version = data.get("stac_version", "unknown")

        # Log progress in API mode
        if is_api and not self.quiet:
            self._progress_count += 1
            object_id = data.get("id", "unknown")
            object_type = raw_type if raw_type else stac_type.capitalize()
            if collection_id and object_type == "Feature":
                click.secho(
                    f"  [{self._progress_count}] Validating {object_type}: {object_id} (Collection: {collection_id})",
                    fg="cyan",
                    dim=True,
                )
            else:
                click.secho(
                    f"  [{self._progress_count}] Validating {object_type}: {object_id}",
                    fg="cyan",
                    dim=True,
                )

        # Validate current object using get_validator (same as run() does)
        # Skip validation for STAC API responses (they have conformsTo instead of stac_extensions)
        is_stac_api = "conformsTo" in data

        if is_stac_api:
            # STAC API catalogs don't validate against STAC schemas, just mark as valid
            is_valid = True
            error_msg = None
        else:
            try:
                extensions = data.get("stac_extensions", [])

                # Mute noisy "[Fallback]" and "[Network]" prints from validation execution path
                with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
                    validator, _ = get_validator(
                        stac_type, stac_version, extensions, quiet=self.quiet
                    )
                    validator(data)

                is_valid = True
                error_msg = None
            except FastSTACMultiValidationError as e:
                is_valid = False
                # Aggregate all errors into a single message for display
                error_msg = "; ".join(str(err) for err in e.errors)
            except FastSTACValidationError as e:
                is_valid = False
                error_msg = str(e)
            except fastjsonschema.JsonSchemaValueException as e:
                is_valid = False
                error_msg = f"{e.name} {e.message.replace(e.name, '').strip()}"
            except Exception as e:
                if self._is_ref_resolution_error(e):
                    try:
                        self._validate_with_jsonschema_fallback(
                            data,
                            stac_type,
                            stac_version,
                            extensions,
                        )
                        is_valid = True
                        error_msg = None
                    except Exception as fallback_err:
                        is_valid = False
                        error_msg = str(fallback_err)
                else:
                    is_valid = False
                    error_msg = str(e)

        # Create result for this object
        # Extract ID if available
        object_id = data.get("id", "unknown")

        result = {
            "path": file_path,
            "id": object_id,
            "valid_stac": is_valid,
            "stac_type": stac_type,
            "stac_version": stac_version,
        }
        if error_msg:
            result["error_message"] = error_msg

        results.append(result)

        if self._limit_reached(results):
            return

        # Process child links
        links = data.get("links", [])

        for link in links:
            if self._limit_reached(results):
                break

            if not isinstance(link, dict):
                continue

            rel = link.get("rel", "")
            href = link.get("href", "")

            # Determine if we should follow this link based on mode
            should_follow = False
            if is_api:
                # API mode: follow "data" (collections), "catalogs"/"collections"
                # index endpoints, "child", "item", "items", and "next"
                # pagination links
                if (
                    rel
                    in [
                        "data",
                        "catalogs",
                        "collections",
                        "child",
                        "item",
                        "items",
                        "next",
                    ]
                    and href
                ):
                    should_follow = True
            else:
                # Local mode: follow "child" and "item" links only
                if rel in ["child", "item"] and href:
                    should_follow = True

            if should_follow:
                # Don't fetch children that would exceed the depth cap
                if self.max_depth is not None and depth + 1 >= self.max_depth:
                    break

                # Resolve relative path
                child_path = self._resolve_link_path(file_path, href)

                if child_path in visited:
                    continue
                visited.add(child_path)

                # Load and validate child
                try:
                    if prefetched_resources and child_path in prefetched_resources:
                        child_data = prefetched_resources[child_path]
                    else:
                        if is_api and not self.quiet and rel in ["data", "items"]:
                            label = "collections" if rel == "data" else "items"
                            click.secho(
                                f"  Discovering {label}: {child_path}",
                                fg="cyan",
                                dim=True,
                            )
                        child_data = self._load_json_resource(child_path)

                    if not isinstance(child_data, dict):
                        results.append(
                            {
                                "path": child_path,
                                "valid_stac": False,
                                "error_message": "Linked resource is not a JSON object.",
                            }
                        )
                        continue

                    # A "next" page continues the endpoint that produced it,
                    # and "catalogs"/"collections" rels point at index
                    # endpoints like "data" - route them by content.
                    effective_rel = rel
                    if rel == "next" or rel in ("catalogs", "collections"):
                        if isinstance(child_data.get("features"), list):
                            effective_rel = "items"
                        elif isinstance(
                            child_data.get("collections"), list
                        ) or isinstance(child_data.get("catalogs"), list):
                            effective_rel = "data"

                    # If this is a collections list endpoint, extract individual collections
                    if effective_rel == "data" and is_api:
                        # "collections" and "catalogs" payloads are both index
                        # lists of {id}-bearing members
                        collections = child_data.get("collections") or child_data.get(
                            "catalogs"
                        )
                        if not isinstance(collections, list):
                            collections = []
                        if collections:
                            # This is a collections list - process each
                            # collection, following "next" pagination
                            page_data = child_data
                            page_path = child_path
                            pages_followed = 0
                            while collections:
                                collection_urls = []
                                for collection in collections:
                                    collection_id = collection.get("id")
                                    if collection_id:
                                        collection_urls.append(
                                            f"{page_path.split('?')[0].rstrip('/')}/{collection_id}"
                                        )

                                # Avoid prefetching beyond remaining validation capacity.
                                if self.limit is not None:
                                    remaining = max(1, self.limit - len(results))
                                    collection_urls = collection_urls[:remaining]

                                # The collections being prefetched consume the
                                # remaining slots themselves, so items pages
                                # are only fetched when capacity is left over
                                remaining_capacity = None
                                if self.limit is not None:
                                    remaining_capacity = (
                                        self.limit - len(results) - len(collection_urls)
                                    )

                                for (
                                    collection_url,
                                    prefetched_collection_resources,
                                    load_error,
                                ) in self._prefetch_api_collection_resources_batch(
                                    collection_urls, remaining_capacity
                                ):
                                    if self._limit_reached(results):
                                        break

                                    if load_error is not None:
                                        results.append(
                                            {
                                                "path": collection_url,
                                                "valid_stac": False,
                                                "error_message": f"Failed to load: {str(load_error)}",
                                            }
                                        )
                                        continue

                                    visited.add(collection_url)
                                    if prefetched_collection_resources is None:
                                        continue
                                    collection_data = prefetched_collection_resources[
                                        collection_url
                                    ]

                                    self._validate_recursive(
                                        collection_data,
                                        collection_url,
                                        results,
                                        visited,
                                        is_api,
                                        prefetched_resources=prefetched_collection_resources,
                                        depth=depth + 1,
                                    )

                                if self._limit_reached(results):
                                    break

                                next_path = self._next_page_path(
                                    page_data, page_path, visited
                                )
                                if next_path is None:
                                    break
                                if (
                                    self.max_pages
                                    and pages_followed + 1 >= self.max_pages
                                ):
                                    self.truncated_endpoints.append(
                                        (child_path, pages_followed + 1)
                                    )
                                    # The capped page was resolved only to
                                    # detect the truncation — release it so
                                    # the same URL can be reached via other
                                    # links later in the walk
                                    visited.discard(next_path)
                                    break
                                try:
                                    page_data = self._load_json_resource(next_path)
                                except Exception as e:
                                    results.append(
                                        {
                                            "path": next_path,
                                            "valid_stac": False,
                                            "error_message": f"Failed to load: {str(e)}",
                                        }
                                    )
                                    break
                                if not isinstance(page_data, dict):
                                    results.append(
                                        {
                                            "path": next_path,
                                            "valid_stac": False,
                                            "error_message": "Linked resource is not a JSON object.",
                                        }
                                    )
                                    break
                                page_path = next_path
                                pages_followed += 1
                                collections = page_data.get("collections", [])
                        else:
                            # Not a collections list, validate as normal
                            self._validate_recursive(
                                child_data,
                                child_path,
                                results,
                                visited,
                                is_api,
                                depth=depth + 1,
                            )
                    # If this is an items endpoint (GeoJSON FeatureCollection), validate only Features
                    elif effective_rel == "items" and is_api:
                        page_data = child_data
                        page_path = child_path
                        pages_followed = 0
                        while isinstance(page_data.get("features"), list):
                            # Extract collection ID from URL (e.g., /collections/{id}/items)
                            collection_id_from_items: Optional[str] = None
                            if "/collections/" in page_path:
                                parts = page_path.split("/collections/")
                                if len(parts) > 1:
                                    collection_parts = parts[1].split("/items")
                                    collection_id_from_items = (
                                        collection_parts[0]
                                        if collection_parts
                                        else None
                                    )

                            # Validate each feature item from the items page, not the FeatureCollection container.
                            for feature in page_data["features"]:
                                if self._limit_reached(results):
                                    break

                                item_id = (
                                    feature.get("id", "unknown")
                                    if isinstance(feature, dict)
                                    else "unknown"
                                )
                                item_path = f"{page_path}#{item_id}"

                                # Skip items already validated on an earlier
                                # page of this endpoint
                                dedup_key = (
                                    "item:"
                                    + (
                                        collection_id_from_items
                                        or page_path.split("?")[0]
                                    )
                                    + f"#{item_id}"
                                )
                                if dedup_key in visited:
                                    continue
                                visited.add(dedup_key)

                                if not isinstance(feature, dict):
                                    results.append(
                                        {
                                            "path": item_path,
                                            "valid_stac": False,
                                            "error_message": "Item is not a JSON object.",
                                        }
                                    )
                                    continue

                                if self.keep_documents:
                                    self.loaded_objects[item_path] = feature

                                self._validate_recursive(
                                    feature,
                                    item_path,
                                    results,
                                    visited,
                                    is_api,
                                    collection_id_from_items,
                                    depth=depth + 1,
                                )

                            if self._limit_reached(results):
                                break

                            next_path = self._next_page_path(
                                page_data, page_path, visited
                            )
                            if next_path is None:
                                break
                            if self.max_pages and pages_followed + 1 >= self.max_pages:
                                self.truncated_endpoints.append(
                                    (child_path, pages_followed + 1)
                                )
                                # The capped page was resolved only to
                                # detect the truncation — release it so the
                                # same URL can be reached via other links
                                # later in the walk
                                visited.discard(next_path)
                                break
                            try:
                                page_data = self._load_json_resource(next_path)
                            except Exception as e:
                                results.append(
                                    {
                                        "path": next_path,
                                        "valid_stac": False,
                                        "error_message": f"Failed to load: {str(e)}",
                                    }
                                )
                                break
                            if not isinstance(page_data, dict):
                                results.append(
                                    {
                                        "path": next_path,
                                        "valid_stac": False,
                                        "error_message": "Linked resource is not a JSON object.",
                                    }
                                )
                                break
                            page_path = next_path
                            pages_followed += 1
                    else:
                        # Recursively validate child
                        self._validate_recursive(
                            child_data,
                            child_path,
                            results,
                            visited,
                            is_api,
                            depth=depth + 1,
                        )
                except Exception as e:
                    if self._limit_reached(results):
                        break

                    results.append(
                        {
                            "path": child_path,
                            "valid_stac": False,
                            "error_message": f"Failed to load: {str(e)}",
                        }
                    )

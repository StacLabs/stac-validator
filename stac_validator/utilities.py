import functools
import json
import os
import ssl
from typing import Dict, Optional, Tuple
from urllib.parse import urlparse
from urllib.request import Request, urlopen

import requests  # type: ignore
import yaml  # type: ignore
from jsonschema import Draft202012Validator
from referencing import Registry, Resource  # type: ignore
from referencing.jsonschema import DRAFT202012  # type: ignore
from referencing.typing import URI  # type: ignore

NEW_VERSIONS = [
    "1.0.0-beta.2",
    "1.0.0-rc.1",
    "1.0.0-rc.2",
    "1.0.0-rc.3",
    "1.0.0-rc.4",
    "1.0.0",
    "1.1.0-beta.1",
    "1.1.0",
]


def validate_stac_version_field(stac_content: Dict) -> Tuple[bool, str, str]:
    """Validate the stac_version field in STAC content.

    Args:
        stac_content (dict): The STAC content dictionary.

    Returns:
        Tuple[bool, str, str]: (is_valid, error_type, error_message)
            - is_valid: True if the version is valid
            - error_type: Error type string if invalid, empty string if valid
            - error_message: Error message if invalid, empty string if valid
    """
    version = stac_content.get("stac_version", "")

    # Check if version is present and not empty
    if not version or not isinstance(version, str) or version.strip() == "":
        error_type = "MissingSTACVersion"
        error_msg = (
            "The 'stac_version' field is missing or empty. "
            "Please ensure your STAC object includes a valid 'stac_version' field "
            "(e.g., '1.0.0', '1.1.0'). This field is required for proper schema validation."
        )
        return False, error_type, error_msg

    # Validate version format
    format_valid, format_error = validate_version_format(version)
    if not format_valid:
        return False, "InvalidSTACVersionFormat", format_error

    return True, "", ""


def validate_version_format(version: str) -> Tuple[bool, str]:
    """Validate that a STAC version string has the correct format.

    Args:
        version (str): The version string to validate.

    Returns:
        Tuple[bool, str]: (is_valid, error_message)
            - is_valid: True if the version format is valid
            - error_message: Description of the issue if invalid, empty string if valid

    Valid formats:
        - Standard semver: "1.0.0", "1.1.0", "0.9.0"
        - Pre-release versions: "1.0.0-beta.1", "1.0.0-rc.1"
    """
    if not version:
        return False, "Version is empty"

    import re

    # Regex for semantic versioning: major.minor.patch with optional pre-release
    semver_pattern = r"^\d+\.\d+\.\d+(-[\w\.\-]+)?$"

    if not re.match(semver_pattern, version):
        return False, (
            f"Version '{version}' does not match expected format. "
            "STAC versions should be in semantic versioning format (e.g., '1.0.0', '1.1.0', '1.0.0-beta.1'). "
            "Please check your 'stac_version' field."
        )

    return True, ""


def is_url(url: str) -> bool:
    """Checks whether the input string is a valid URL.

    Args:
        url (str): The string to check.

    Returns:
        bool: True if the input string is a valid URL, False otherwise.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def is_valid_url(url: str) -> bool:
    """Checks if a given string is a valid URL.

    Args:
        url: A string to check for validity as a URL.

    Returns:
        A boolean value indicating whether the input string is a valid URL.
    """
    return urlparse(url).scheme in ["http", "https"]


def get_stac_type(stac_content: Dict) -> str:
    """Determine the type of a STAC resource.

    Given a dictionary representing a STAC resource, this function determines the
    resource's type and returns a string representing that type. The resource type
    can be one of 'Item', 'Catalog', or 'Collection'.

    Args:
        stac_content: A dictionary representing a STAC resource.

    Returns:
        A string representing the type of the STAC resource.

    Raises:
        TypeError: If the input is not a dictionary.
    """
    try:
        content_types = ["Item", "Catalog", "Collection"]
        if "type" in stac_content and stac_content["type"] == "Feature":
            return "Item"
        elif "type" in stac_content and stac_content["type"] in content_types:
            return stac_content["type"]
        elif "extent" in stac_content or "license" in stac_content:
            return "Collection"
        else:
            return "Catalog"
    except TypeError as e:
        return str(e)


def fetch_and_parse_file(input_path: str, headers: Optional[Dict] = None) -> Dict:
    """Fetches and parses a JSON file from a URL or local file.

    Given a URL or local file path to a JSON file, this function fetches the file,
    and parses its contents into a dictionary. If the input path is a valid URL, the
    function uses the requests library to download the file, otherwise it opens the
    local file with the json library.

    Args:
        input_path: A string representing the URL or local file path to the JSON file.
        headers: For URLs: HTTP headers to include in the request

    Returns:
        A dictionary containing the parsed contents of the JSON file.

    Raises:
        ValueError: If the input is not a valid URL or local file path.
        requests.exceptions.RequestException: If there is an error while downloading the file.
    """
    try:
        if is_url(input_path):
            resp = requests.get(input_path, headers=headers)
            resp.raise_for_status()
            data = resp.json()
        else:
            with open(input_path) as f:
                data = json.load(f)

        return data
    except (ValueError, requests.exceptions.RequestException) as e:
        raise e


@functools.lru_cache(maxsize=256)
def fetch_and_parse_schema(input_path: str) -> Dict:
    """Fetches and parses a JSON schema file from a URL or local file using a cache.

    Given a URL or local file path to a JSON schema file, this function fetches the file
    and parses its contents into a dictionary. If the input path is a valid URL, the
    function uses the requests library to download the file, otherwise it opens the
    local file with the json library. Additionally, this function caches the results of
    previous function calls to reduce the number of times the file is fetched and parsed.

    Args:
        input_path: A string representing the URL or local file path to the JSON schema file.

    Returns:
        A dictionary containing the parsed contents of the JSON schema file.

    Raises:
        ValueError: If the input is not a valid URL or local file path.
        requests.exceptions.RequestException: If there is an error while downloading the file.
    """
    return fetch_and_parse_file(input_path)


def set_schema_addr(version: str, stac_type: str) -> str:
    """Set the URL address for the JSON schema to be used for validating the STAC object.
    Validate new versions at schemas.stacspec.org

    Args:
        version (str): The version number of the STAC object.
        stac_type (str): The type of the STAC object (e.g. "item", "collection").

    Returns:
        str: The URL address for the JSON schema.
    """
    if version in NEW_VERSIONS:
        return f"https://schemas.stacspec.org/v{version}/{stac_type}-spec/json-schema/{stac_type}.json"
    else:
        return f"https://cdn.staclint.com/v{version}/{stac_type}.json"


def link_request(
    link: Dict, initial_message: Dict, open_urls: bool = True, headers: Dict = {}
) -> None:
    """Makes a request to a URL and appends it to the relevant field of the initial message.

    Args:
        link: A dictionary containing a "href" key which is a string representing a URL.
        initial_message: A dictionary containing lists for "request_valid", "request_invalid",
        "format_valid", and "format_invalid" URLs.
        open_urls: Whether to open link href URL
        headers: HTTP headers to include in the request

    Returns:
        None

    """
    if is_url(link["href"]):
        try:
            if open_urls:
                request = Request(link["href"], headers=headers)
                if "s3" in link["href"]:
                    context = ssl._create_unverified_context()
                    response = urlopen(request, context=context)
                else:
                    response = urlopen(request)
                status_code = response.getcode()
                if status_code == 200:
                    initial_message["request_valid"].append(link["href"])
        except Exception:
            initial_message["request_invalid"].append(link["href"])
        initial_message["format_valid"].append(link["href"])
    else:
        initial_message["request_invalid"].append(link["href"])
        initial_message["format_invalid"].append(link["href"])


def cached_retrieve(uri: URI, schema_map: Optional[Dict] = None) -> Resource[Dict]:
    """
    Retrieve and cache a remote schema.

    Args:
        uri (str): The URI of the schema.
        schema_map_keys: Override schema location to validate against local versions of a schema

    Returns:
        dict: The parsed JSON dict of the schema.

    Raises:
        requests.RequestException: If the request to fetch the schema fails.
        Exception: For any other unexpected errors.
    """
    return Resource.from_contents(
        fetch_schema_with_override(uri, schema_map=schema_map)
    )


def fetch_schema_with_override(
    schema_path: str, schema_map: Optional[Dict] = None
) -> Dict:
    """
    Retrieve and cache a remote schema.

    Args:
        schema_path (str): Path or URI of the schema.
        schema_map (dict): Override schema location to validate against local versions of a schema

    Returns:
        dict: The parsed JSON dict of the schema.
    """

    if schema_map:
        if schema_path in schema_map:
            schema_path = schema_map[schema_path]

    # Load the schema
    return fetch_and_parse_schema(schema_path)


def validate_with_ref_resolver(
    schema_path: str, content: Dict, schema_map: Optional[Dict] = None
) -> None:
    """
    Validate a JSON document against a JSON Schema with dynamic reference resolution.

    Args:
        schema_path (str): Path or URI of the JSON Schema.
        content (dict): JSON content to validate.
        schema_map (dict): Override schema location to validate against local versions of a schema

    Raises:
        jsonschema.exceptions.ValidationError: If validation fails.
        requests.RequestException: If fetching a remote schema fails.
        FileNotFoundError: If a local schema file is not found.
        Exception: If any other error occurs during validation.
    """
    schema = fetch_schema_with_override(schema_path, schema_map=schema_map)
    # Set up the resource and registry for schema resolution
    cached_retrieve_with_schema_map = functools.partial(
        cached_retrieve, schema_map=schema_map
    )
    resource: Resource = Resource(contents=schema, specification=DRAFT202012)  # type: ignore
    registry: Registry = Registry(retrieve=cached_retrieve_with_schema_map).with_resource(  # type: ignore
        uri=schema_path, resource=resource
    )  # type: ignore

    # Validate the content against the schema
    validator = Draft202012Validator(schema, registry=registry)
    validator.validate(content)


def load_schema_config(config_path: str) -> dict:
    """
    Loads a schema config file (YAML or JSON) that maps remote schema URLs to local file paths.
    Supports an optional top-level 'schemas' key.

    Args:
        config_path: Path to the schema config file.

    Returns:
        A dict mapping remote schema URLs to local file paths.

    Raises:
        FileNotFoundError: If the config file does not exist.
        ValueError: If the file is not valid YAML/JSON or is missing required keys.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Schema config file not found: {config_path}")
    with open(config_path, "r") as f:
        if config_path.endswith(".json"):
            data = json.load(f)
        else:
            data = yaml.safe_load(f)
    # Support both top-level and nested under 'schemas'
    if "schemas" in data:
        return data["schemas"]
    return data


def extract_relevant_oneof_error(error, instance=None):
    """Extract the most relevant error from a 'oneOf' validation error.

    Given a jsonschema.ValidationError for a 'oneOf' failure, this function returns
    the most relevant sub-error, with preference given to errors matching the instance's 'type'.
    If no matching type is found, it falls back to returning the first sub-error.

    Args:
        error (jsonschema.ValidationError): The validation error from a 'oneOf' validation.
        instance (dict, optional): The instance being validated. If provided and contains a 'type'
            field, the function will try to find a matching schema for that type. Defaults to None.

    Returns:
        jsonschema.ValidationError: The most relevant sub-error from the 'oneOf' validation.
            If the error is not a 'oneOf' validation error or has no context, returns the
            original error unchanged.
    """
    if error.validator == "oneOf" and hasattr(error, "context") and error.context:
        if instance and "type" in instance:
            for suberror in error.context:
                # Try to match the instance 'type' to the schema's 'type'
                props = suberror.schema.get("properties", {})
                type_schema = props.get("type", {})
                if (
                    isinstance(type_schema, dict)
                    and "const" in type_schema
                    and instance["type"] == type_schema["const"]
                ):
                    return suberror
        # Fallback to the first suberror
        return error.context[0]
    return error

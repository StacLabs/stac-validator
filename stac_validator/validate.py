import json
import os
from json.decoder import JSONDecodeError
from typing import Any, Dict, List, Optional, Union
from urllib.error import HTTPError, URLError

import click  # type: ignore
import jsonschema  # type: ignore
from jsonschema.exceptions import best_match
from requests import exceptions  # type: ignore

from .utilities import (
    extract_relevant_oneof_error,
    fetch_and_parse_file,
    fetch_and_parse_schema,
    get_stac_type,
    is_valid_url,
    link_request,
    load_schema_config,
    set_schema_addr,
    validate_stac_version_field,
    validate_with_ref_resolver,
)


class StacValidate:
    """
    Class that validates STAC objects.

    Attributes:
        stac_file (str): The path or URL to the STAC object to be validated.
        collections (bool): Validate response from a /collections endpoint.
        item_collection (bool): Whether the STAC object to be validated is an item collection.
        pages (int): The maximum number of pages to validate if `item_collection` is True.
        recursive (bool): Whether to recursively validate related STAC objects.
        max_depth (int): The maximum depth to traverse when recursively validating related STAC objects.
        core (bool): Whether to only validate the core STAC object (without extensions).
        links (bool): Whether to additionally validate links (only works in default mode).
        assets (bool): Whether to additionally validate assets (only works in default mode).
        assets_open_urls (bool): Whether to open assets URLs when validating assets.
        headers (dict): HTTP headers to include in the requests.
        extensions (bool): Whether to only validate STAC object extensions.
        custom (str): The local filepath or remote URL of a custom JSON schema to validate the STAC object.
        trace_recursion (bool): Whether to enable verbose output in recursive mode.
        log (str): The local filepath to save the output of the recursive validation to.
        pydantic (bool): Whether to validate using Pydantic models.
        schema_config (str): The local filepath or remote URL of a custom JSON schema config to validate the STAC object.
        schema_map (Optional[Dict[str, str]]): A dictionary mapping schema paths to their replacements.
        verbose (bool): Whether to enable verbose output.

    Methods:
        run(): Validates the STAC object and returns whether it is valid.
        validate_item_collection(): Validates an item collection.
    """

    def __init__(
        self,
        stac_file: Optional[str] = None,
        collections: bool = False,
        item_collection: bool = False,
        pages: Optional[int] = None,
        recursive: bool = False,
        max_depth: Optional[int] = None,
        core: bool = False,
        links: bool = False,
        assets: bool = False,
        assets_open_urls: bool = True,
        headers: dict = {},
        extensions: bool = False,
        custom: str = "",
        schema_config: Optional[str] = None,
        schema_map: Optional[Dict[str, str]] = None,
        trace_recursion: bool = False,
        log: str = "",
        pydantic: bool = False,
        verbose: bool = False,
    ):
        self.stac_file = stac_file
        self.collections = collections
        self.item_collection = item_collection
        self.pages = pages
        self.message: List = []
        self._schema = custom
        self.schema_map = schema_map
        self.schema_config = schema_config
        self.links = links
        self.assets = assets
        self.assets_open_urls = assets_open_urls
        self.headers: Dict = headers
        self.recursive = recursive
        self.max_depth = max_depth
        self.extensions = extensions
        self.core = core
        self.stac_content: Dict = {}
        self.version = ""
        self.depth: int = 0
        self.skip_val = False
        self.trace_recursion = trace_recursion
        self.valid = False
        self.log = log
        self.pydantic = pydantic
        self.verbose = verbose

        self._original_schema_paths = {}
        cli_schema_map = schema_map or {}

        # Load config mappings if provided
        config_mappings = {}
        if schema_config:
            try:
                config_mappings = load_schema_config(schema_config)
                config_dir = os.path.dirname(os.path.abspath(schema_config))
                # Handle config mappings
                for url, path in list(config_mappings.items()):
                    self._original_schema_paths[url] = path
                    # Resolve relative to config file dir for loading
                    if not os.path.isabs(path) and not is_valid_url(path):
                        config_mappings[url] = os.path.join(config_dir, path)
                    abs_path = os.path.abspath(config_mappings[url])
                    self._original_schema_paths[abs_path] = (
                        path  # <-- This line is critical
                    )

            except Exception as e:
                click.secho(
                    f"Error loading schema config file: {e}", fg="red", err=True
                )
                config_mappings = {}

        # Handle CLI mappings
        for url, path in list(cli_schema_map.items()):
            self._original_schema_paths[url] = path
            # Resolve relative to CWD for loading
            if not os.path.isabs(path) and not is_valid_url(path):
                cli_schema_map[url] = os.path.abspath(path)
            abs_path = os.path.abspath(cli_schema_map[url])
            self._original_schema_paths[abs_path] = path  # <-- This line is critical

        # Merge config with CLI (CLI wins)
        self.schema_map = {**config_mappings, **cli_schema_map}

    @property
    def schema(self) -> str:
        return self._schema

    @schema.setter
    def schema(self, schema_path: str):
        if self.schema_map:
            if schema_path in self.schema_map:
                schema_path = self.schema_map[schema_path]
        self._schema = schema_path

    def _format_jsonschema_error_verbose(
        self, error: jsonschema.exceptions.ValidationError
    ) -> Dict[str, Any]:
        """Format a JSON Schema validation error into a detailed dictionary.

        This method transforms a jsonschema ValidationError into a structured dictionary
        containing comprehensive information about the validation failure, including
        error details, schema information, and relevant paths.

        Args:
            error: The jsonschema ValidationError to be formatted.

        Returns:
            Dict[str, Any]: A dictionary containing detailed information about the
                validation error, including:
                - error_type: Type of validation error
                - detail: Error message
                - validator: The validator that failed
                - path_in_document: Path to the error in the validated document
                - path_in_schema: Path to the error in the schema
                - schema: The relevant schema section that caused the validation failure
                - validator_value: The value that failed validation
                - instance: The actual value that caused the validation failure
        """
        verbose_details: Dict[str, Any] = {}

        verbose_details["validator"] = error.validator
        if error.validator_value is not None:
            val_value_repr = repr(error.validator_value)
            if len(val_value_repr) > 800:
                val_value_repr = val_value_repr[:800] + "... (truncated)"
            verbose_details["validator_value"] = val_value_repr
        else:
            verbose_details["validator_value"] = None

        # if error.instance is not None:
        #     instance_repr = repr(error.instance)
        #     if len(instance_repr) > 200: # Max length for instance snippet
        #         instance_repr = instance_repr[:200] + "... (truncated)"
        #     verbose_details["instance_snippet"] = instance_repr
        # else:
        #     verbose_details["instance_snippet"] = None

        if (
            error.schema is not None
            and error.validator is not None
            and isinstance(error.schema, dict)
            and isinstance(error.validator, str)
        ):
            verbose_details["schema"] = error.schema.get(error.validator)
        else:
            verbose_details["schema"] = None

        verbose_details["path_in_document"] = list(error.absolute_path)
        verbose_details["path_in_schema"] = list(error.absolute_schema_path)

        # if error.context:
        #     context_errors_list = []
        #     for context_error in sorted(error.context, key=jsonschema.exceptions.relevance):
        #         # Recursively format context errors, ensuring best_match is handled if nested
        #         best_context_error = best_match([context_error]) if context_error.context else context_error
        #         context_errors_list.append(self._format_jsonschema_error_verbose(best_context_error))
        #     verbose_details["context_errors"] = context_errors_list

        return verbose_details

    def _create_verbose_err_msg(self, error_input: Any) -> Union[Dict[str, Any], str]:
        """Create a verbose error message from various error input types.

        Args:
            error_input: The error input to process. Can be a jsonschema ValidationError,
                dictionary, Exception, or any other type that can be converted to string.

        Returns:
            Union[Dict[str, Any], str]: A detailed error message. For jsonschema ValidationError,
                returns a dictionary with detailed validation information. For other Exception types,
                returns a dictionary with error type and detail. For dictionaries, returns the
                dictionary as-is. For all other types, returns the string representation.
        """
        if isinstance(error_input, jsonschema.exceptions.ValidationError):
            return self._format_jsonschema_error_verbose(error_input)
        elif isinstance(error_input, dict):
            return error_input
        elif isinstance(error_input, Exception):
            return {
                "error_type": type(error_input).__name__,
                "detail": str(error_input),
            }
        elif error_input is None:
            return {}
        return str(error_input)  # Fallback to string representation

    def create_err_msg(
        self,
        err_type: str,
        err_msg: str,
        error_obj: Optional[Exception] = None,
        schema_uri: str = "",
        version: Optional[str] = None,
    ) -> Dict[str, Union[str, bool, List[str], Dict[str, Any]]]:
        """
        Create a standardized error message dictionary and mark validation as failed.

        Args:
            err_type (str): The type of error.
            err_msg (str): The error message.
            error_obj (Optional[Exception]): The raw exception object for verbose details.
            schema_uri (str, optional): The URI of the schema that failed validation.
            version (Optional[str]): Override version to use in the error message.

        Returns:
            dict: Dictionary containing error information.
        """
        self.valid = False

        # Ensure all values are of the correct type
        if not isinstance(err_type, str):
            err_type = str(err_type)
        if not isinstance(err_msg, str):
            err_msg = str(err_msg)

        # Use provided version or fall back to self.version
        version_to_use = (
            version
            if version is not None
            else (str(self.version) if hasattr(self, "version") else "")
        )

        # Initialize the message with common fields
        message: Dict[str, Any] = {
            "version": version_to_use,
            "path": str(self.stac_file) if hasattr(self, "stac_file") else "",
            "schema": (
                [self._original_schema_paths.get(self.schema, self.schema)]
                if hasattr(self, "schema")
                else [""]
            ),
            "valid_stac": False,
            "error_type": err_type,
            "error_message": err_msg,
            "failed_schema": schema_uri if schema_uri else "",
            "recommendation": "For more accurate error information, rerun with --verbose.",
        }

        # Add asset_type and validation_method if available
        if hasattr(self, "stac_content"):
            try:
                stac_type = get_stac_type(self.stac_content)
                if stac_type:
                    message["asset_type"] = stac_type.upper()
                    message["validation_method"] = (
                        "recursive"
                        if hasattr(self, "recursive") and self.recursive
                        else "default"
                    )
            except Exception:  # noqa: BLE001
                pass

        # Ensure schema is properly typed
        schema_value: str = ""
        if self.schema is not None:
            schema_value = str(self.schema)
        schema_field: List[str] = [schema_value] if schema_value else []

        # Initialize the error message with common fields
        error_message: Dict[str, Union[str, bool, List[str], Dict[str, Any]]] = {
            "version": version_to_use,
            "path": str(self.stac_file) if self.stac_file is not None else "",
            "schema": schema_field,  # All schemas that were checked
            "valid_stac": False,
            "error_type": err_type,
            "error_message": err_msg,
            "failed_schema": "",  # Will be populated if we can determine which schema failed
        }

        # Try to extract the failed schema from the error message if it's a validation error
        if error_obj and hasattr(error_obj, "schema"):
            if isinstance(error_obj.schema, dict) and "$id" in error_obj.schema:
                error_message["failed_schema"] = error_obj.schema["$id"]
            elif hasattr(error_obj, "schema_url"):
                error_message["failed_schema"] = error_obj.schema_url
            # If we can't find a schema ID, try to get it from the schema map
            elif schema_field and len(schema_field) == 1:
                error_message["failed_schema"] = schema_field[0]

        if self.verbose and error_obj is not None:
            verbose_err = self._create_verbose_err_msg(error_obj)
            if isinstance(verbose_err, dict):
                error_message["error_verbose"] = verbose_err
            else:
                error_message["error_verbose"] = {"detail": str(verbose_err)}
            # Add recommendation to check the schema if the error is not clear
            if error_message.get("failed_schema"):
                error_message["recommendation"] = (
                    "If the error is unclear, please check the schema documentation at: "
                    f"{error_message['failed_schema']}"
                )
        else:
            error_message["recommendation"] = (
                "For more accurate error information, rerun with --verbose."
            )

        return error_message

    def create_links_message(self) -> Dict:
        """
        Create an initial links validation message structure.

        Returns:
            dict: An empty validation structure for link checking.
        """
        format_valid: List = []
        format_invalid: List = []
        request_valid: List = []
        request_invalid: List = []
        return {
            "format_valid": format_valid,
            "format_invalid": format_invalid,
            "request_valid": request_valid,
            "request_invalid": request_invalid,
        }

    def create_message(self, stac_type: str, val_type: str) -> Dict:
        """
        Create a standardized validation message dictionary.

        Args:
            stac_type (str): The STAC object type.
            val_type (str): The type of validation (e.g., "default", "core").

        Returns:
            dict: Dictionary containing general validation information.
        """
        return {
            "version": self.version,
            "path": self.stac_file,
            "schema": [self._original_schema_paths.get(self.schema, self.schema)],
            "valid_stac": False,
            "asset_type": stac_type.upper(),
            "validation_method": val_type,
        }

    def assets_validator(self) -> Dict:
        """
        Validate the 'assets' field in STAC content if present.

        Returns:
            dict: A dictionary containing the asset validation results.
        """
        initial_message = self.create_links_message()
        assets = self.stac_content.get("assets")
        if assets:
            for asset in assets.values():
                link_request(
                    asset, initial_message, self.assets_open_urls, self.headers
                )
        return initial_message

    def links_validator(self) -> Dict:
        """
        Validate the 'links' field in STAC content.

        Returns:
            dict: A dictionary containing the link validation results.
        """
        initial_message = self.create_links_message()
        root_url = ""

        # Try to locate a self/alternate link that is a valid URL for root reference
        for link in self.stac_content["links"]:
            if link["rel"] in ["self", "alternate"] and is_valid_url(link["href"]):
                root_url = (
                    link["href"].split("/")[0] + "//" + link["href"].split("/")[2]
                )

        # Validate each link, making it absolute if necessary
        for link in self.stac_content["links"]:
            if not is_valid_url(link["href"]):
                link["href"] = root_url + link["href"][1:]
            link_request(link, initial_message, True, self.headers)

        return initial_message

    def custom_validator(self) -> None:
        """
        Validate a STAC JSON file against a custom or dynamically resolved JSON schema.

        1. If `self.schema` is a valid URL, fetch and validate.
        2. If it is a local file path, use it.
        3. Otherwise, assume it is a relative path and resolve relative to the STAC file.

        Returns:
            None
        """
        if is_valid_url(self.schema):
            validate_with_ref_resolver(
                self.schema, self.stac_content, schema_map=self.schema_map
            )
        elif os.path.exists(self.schema):
            validate_with_ref_resolver(
                self.schema, self.stac_content, schema_map=self.schema_map
            )
        else:
            file_directory = os.path.dirname(os.path.abspath(str(self.stac_file)))
            schema = os.path.join(file_directory, self.schema)
            schema = os.path.abspath(os.path.realpath(schema))
            validate_with_ref_resolver(
                schema, self.stac_content, schema_map=self.schema_map
            )

    def core_validator(self, stac_type: str) -> None:
        """
        Validate the STAC content against the core schema determined by stac_type and version.

        Args:
            stac_type (str): The type of the STAC object (e.g., "item", "collection").
        """
        stac_type = stac_type.lower()
        self.schema = set_schema_addr(self.version, stac_type)
        validate_with_ref_resolver(
            self.schema, self.stac_content, schema_map=self.schema_map
        )

    def extensions_validator(self, stac_type: str) -> Dict:
        """
        Validate STAC extensions for an ITEM or validate the core schema for a COLLECTION.

        Args:
            stac_type (str): The STAC object type ("ITEM" or "COLLECTION").

        Returns:
            dict: A dictionary containing extension (or core) validation results.
        """
        message = self.create_message(stac_type, "extensions")
        message["schema"] = []
        valid = True
        extension = None

        try:
            if (
                "stac_extensions" in self.stac_content
                and len(self.stac_content["stac_extensions"]) > 0
            ):
                # Handle legacy "proj" to "projection" mapping
                if "proj" in self.stac_content["stac_extensions"]:
                    index = self.stac_content["stac_extensions"].index("proj")
                    self.stac_content["stac_extensions"][index] = "projection"

                schemas = self.stac_content["stac_extensions"]
                for extension in schemas:
                    if not (is_valid_url(extension) or extension.endswith(".json")):
                        if self.version == "1.0.0-beta.2":
                            self.stac_content["stac_version"] = "1.0.0-beta.1"
                            self.version = self.stac_content["stac_version"]
                        extension = (
                            f"https://cdn.staclint.com/v{self.version}/extension/"
                            f"{extension}.json"
                        )
                    self.schema = extension
                    self.custom_validator()
                    display_path = self._original_schema_paths.get(extension, extension)
                    message["schema"].append(display_path)
            else:
                self.core_validator(stac_type)
                display_path = self._original_schema_paths.get(self.schema, self.schema)
                message["schema"] = [display_path]

        except jsonschema.exceptions.ValidationError as e:
            verbose_error = e
            e = extract_relevant_oneof_error(e, self.stac_content)
            if self.recursive:
                raise
            if e.context:
                e = best_match(e.context)  # type: ignore
            valid = False
            # Get the current schema (extension) that caused the validation error
            failed_schema = (
                self._original_schema_paths.get(extension, extension)
                if extension
                else "unknown schema"
            )

            # Build the error message with path information
            err_msg = e.message
            path_info = (
                f"Error is in {' -> '.join(map(str, e.absolute_path))} "
                if e.absolute_path
                else ""
            )
            if path_info:
                err_msg = f"{err_msg}. {path_info}"

            # Create the error message with the original error object
            message = self.create_err_msg(
                err_type="JSONSchemaValidationError",
                err_msg=err_msg,
                error_obj=verbose_error,
            )

            # Set the failed_schema in the message if we have it
            if failed_schema:
                message["failed_schema"] = failed_schema
            return message

        except Exception as e:
            if self.recursive:
                raise
            valid = False
            # Include the current schema in the error message for other types of exceptions
            current_schema = (
                self._original_schema_paths.get(extension, extension)
                if extension
                else "unknown schema"
            )
            err_msg = f"{e} [Schema: {current_schema}]. Error in Extensions."
            return self.create_err_msg(
                err_type="Exception", err_msg=err_msg, error_obj=e
            )

        self.valid = valid
        message["valid_stac"] = valid
        return message

    def default_validator(self, stac_type: str) -> Dict:
        """
        Validate a STAC Catalog or Item against the core schema and its extensions.

        Args:
            stac_type (str): The type of STAC object. Must be "catalog" or "item".

        Returns:
            dict: A dictionary with results of the default validation.
        """
        message = self.create_message(stac_type, "default")
        message["schema"] = []

        # Validate core
        self.core_validator(stac_type)
        core_schema = self.schema
        display_path = self._original_schema_paths.get(core_schema, core_schema)
        if display_path not in message["schema"]:
            message["schema"].append(display_path)
        stac_upper = stac_type.upper()

        # Validate extensions if ITEM
        if stac_upper == "ITEM" or stac_upper == "COLLECTION":
            message = self.extensions_validator(stac_upper)
            message["validation_method"] = "default"
            display_path = self._original_schema_paths.get(core_schema, core_schema)
            if display_path not in message["schema"]:
                message["schema"].append(display_path)

        # Optionally validate links
        if self.links:
            message["links_validated"] = self.links_validator()

        # Optionally validate assets
        if self.assets:
            message["assets_validated"] = self.assets_validator()

        return message

    def recursive_validator(self, stac_type: str) -> bool:
        """
        Recursively validate a STAC JSON document and its children/items.

        Follows "child" and "item" links, calling the appropriate validator on each.
        Uses pydantic_validator if self.pydantic is True, otherwise uses default_validator.

        Args:
            stac_type (str): The STAC object type to validate.

        Returns:
            bool: True if all validations are successful, False otherwise.
        """
        valid = False
        if not self.skip_val:
            self.schema = set_schema_addr(self.version, stac_type.lower())
            message = self.create_message(stac_type, "recursive")
            message["valid_stac"] = False
            # Add validator_engine field to track validation method
            message["validator_engine"] = "pydantic" if self.pydantic else "jsonschema"

            try:
                if self.pydantic:
                    # Set pydantic model info in schema field
                    model_name = f"stac-pydantic {stac_type.capitalize()} model"
                    message["schema"] = [model_name]
                    # Run pydantic validation
                    msg = self.pydantic_validator(stac_type)
                else:
                    msg = self.default_validator(stac_type)
                    message["schema"] = msg["schema"]

            except jsonschema.exceptions.ValidationError as e:
                if e.context:
                    e = best_match(e.context)  # type: ignore
                if e.absolute_path:
                    err_msg = (
                        f"{e.message}. Error is in "
                        f"{' -> '.join([str(i) for i in e.absolute_path])} "
                    )
                else:
                    err_msg = f"{e.message}"
                message.update(
                    self.create_err_msg(
                        err_type="JSONSchemaValidationError",
                        err_msg=err_msg,
                        error_obj=e,
                        schema_uri=(
                            e.schema.get("$id", "")
                            if hasattr(e, "schema") and isinstance(e.schema, dict)
                            else ""
                        ),
                    )
                )
                self.message.append(message)
                if self.trace_recursion:
                    click.echo(json.dumps(message, indent=4))
                return valid
            except Exception as e:
                if self.pydantic and "pydantic" in str(e.__class__.__module__):
                    message.update(
                        self.create_err_msg(
                            err_type="PydanticValidationError",
                            err_msg=str(e),
                            error_obj=e,
                        )
                    )
                    self.message.append(message)
                    if self.trace_recursion:
                        click.echo(json.dumps(message, indent=4))
                    return valid
                raise

            valid = True
            message["valid_stac"] = valid
            self.message.append(message)
            if self.trace_recursion:
                click.echo(json.dumps(message, indent=4))

            self.depth += 1
            if self.max_depth and self.depth >= self.max_depth:
                self.skip_val = True

            base_url = self.stac_file

            child_validity = []
            for link in self.stac_content["links"]:
                if link["rel"] in ("child", "item"):
                    address = link["href"]
                    if not is_valid_url(address):
                        path_parts = str(base_url).split("/")
                        path_parts.pop(-1)
                        root = path_parts[0]
                        for i in range(1, len(path_parts)):
                            root = f"{root}/{path_parts[i]}"
                        self.stac_file = f"{root}/{address}"
                    else:
                        self.stac_file = address

                    self.stac_content = fetch_and_parse_file(
                        str(self.stac_file), self.headers
                    )
                    self.stac_content["stac_version"] = self.version
                    stac_type = get_stac_type(self.stac_content).lower()

                if link["rel"] == "child":
                    if not self.skip_val:
                        valid_child = self.recursive_validator(stac_type)
                        child_validity.append(valid_child)

                if link["rel"] == "item":
                    self.schema = set_schema_addr(self.version, stac_type.lower())
                    message = self.create_message(stac_type, "recursive")
                    message["validator_engine"] = (
                        "pydantic" if self.pydantic else "jsonschema"
                    )
                    try:
                        if self.pydantic:
                            # Set pydantic model info in schema field for child items
                            model_name = f"stac-pydantic {stac_type.capitalize()} model"
                            message["schema"] = [model_name]
                            # Run pydantic validation
                            msg = self.pydantic_validator(stac_type)
                        elif self.version == "0.7.0":
                            schema = fetch_and_parse_schema(self.schema)
                            # Prevent unknown url type issue
                            schema["allOf"] = [{}]
                            jsonschema.validate(self.stac_content, schema)
                        else:
                            msg = self.default_validator(stac_type)
                            message["schema"] = msg["schema"]
                        message["valid_stac"] = True
                    except Exception as e:
                        if self.pydantic and "pydantic" in str(e.__class__.__module__):
                            message.update(
                                self.create_err_msg(
                                    err_type="PydanticValidationError",
                                    err_msg=str(e),
                                    error_obj=e,
                                )
                            )
                            message["valid_stac"] = False
                        else:
                            raise

                    if self.log or (not self.max_depth or self.max_depth < 5):
                        self.message.append(message)
            if all(child_validity):
                valid = True
            else:
                valid = False
        return valid

    def validate_dict(self, stac_content: Dict) -> bool:
        """
        Validate the contents of a dictionary representing a STAC object.

        Args:
            stac_content (dict): The dictionary representation of the STAC object.

        Returns:
            bool: True if validation succeeded, False otherwise.
        """
        self.stac_content = stac_content
        return self.run()

    def validate_item_collection_dict(self, item_collection: Dict) -> None:
        """
        Validate the contents of a STAC Item Collection.

        Args:
            item_collection (dict): The dictionary representation of the item collection.
        """
        # Store the original stac_file to restore it later
        original_stac_file = self.stac_file

        for item in item_collection["features"]:
            # Update the path to include the item ID for better traceability
            if isinstance(original_stac_file, str) and "id" in item:
                # Remove any query string from the URL before appending the item ID
                base_url = original_stac_file.split("?")[0]
                self.stac_file = f"{base_url}/{item['id']}"

            self.schema = ""
            self.validate_dict(item)

        # Restore the original stac_file
        self.stac_file = original_stac_file

    def validate_collections(self) -> None:
        """
        Validate STAC Collections from a /collections endpoint.

        Raises:
            URLError, JSONDecodeError, ValueError, TypeError, FileNotFoundError,
            ConnectionError, exceptions.SSLError, OSError, KeyError, HTTPError,
            jsonschema.exceptions.ValidationError, Exception: Various errors
            during fetching or parsing.
        """
        collections = fetch_and_parse_file(str(self.stac_file), self.headers)
        for collection in collections["collections"]:
            self.schema = ""
            self.validate_dict(collection)

    def validate_item_collection(self) -> None:
        """
        Validate a STAC Item Collection with optional pagination.

        Raises:
            URLError, JSONDecodeError, ValueError, TypeError, FileNotFoundError,
            ConnectionError, exceptions.SSLError, OSError, KeyError, HTTPError,
            jsonschema.exceptions.ValidationError, Exception: Various errors
            during fetching or parsing.
        """
        page = 1
        print(f"processing page {page}")
        item_collection = fetch_and_parse_file(str(self.stac_file), self.headers)
        self.validate_item_collection_dict(item_collection)

        try:
            if self.pages is not None:
                for _ in range(self.pages - 1):
                    if "links" in item_collection:
                        for link in item_collection["links"]:
                            if link["rel"] == "next":
                                page += 1
                                print(f"processing page {page}")
                                next_link = link["href"]
                                self.stac_file = next_link
                                item_collection = fetch_and_parse_file(
                                    str(self.stac_file), self.headers
                                )
                                self.validate_item_collection_dict(item_collection)
                                break
        except Exception as e:
            message = {
                "pagination_error": (
                    f"Validating the item collection failed on page {page}: {str(e)}"
                )
            }
            self.message.append(message)

    def pydantic_validator(self, stac_type: str) -> Dict:
        """
        Validate STAC content using Pydantic models.

        Args:
            stac_type (str): The STAC object type (e.g., "ITEM", "COLLECTION", "CATALOG").

        Returns:
            dict: A dictionary containing validation results.
        """
        message = self.create_message(stac_type, "pydantic")
        message["schema"] = [""]

        try:
            # Import dependencies
            from pydantic import ValidationError  # type: ignore
            from stac_pydantic import Catalog, Collection, Item  # type: ignore
            from stac_pydantic.extensions import validate_extensions  # type: ignore

            # Validate based on STAC type
            if stac_type == "ITEM":
                item_model = Item.model_validate(self.stac_content)
                message["schema"] = ["stac-pydantic Item model"]
                self._validate_extensions(item_model, message, validate_extensions)

            elif stac_type == "COLLECTION":
                collection_model = Collection.model_validate(self.stac_content)
                message["schema"] = [
                    "stac-pydantic Collection model"
                ]  # Fix applied here
                self._validate_extensions(
                    collection_model, message, validate_extensions
                )

            elif stac_type == "CATALOG":
                Catalog.model_validate(self.stac_content)
                message["schema"] = ["stac-pydantic Catalog model"]

            else:
                raise ValueError(
                    f"Unsupported STAC type for Pydantic validation: {stac_type}"
                )

            self.valid = True
            message["model_validation"] = "passed"

        except ValidationError as e:
            self.valid = False
            error_details = [
                f"{' -> '.join(map(str, error.get('loc', [])))}: {error.get('msg', '')}"
                for error in e.errors()
            ]
            error_message = f"Pydantic validation failed for {stac_type}: {'; '.join(error_details)}"
            message.update(
                self.create_err_msg(
                    err_type="PydanticValidationError",
                    err_msg=error_message,
                    error_obj=e,
                )
            )

        except Exception as e:
            self.valid = False
            message.update(
                self.create_err_msg(
                    err_type="PydanticValidationError", err_msg=str(e), error_obj=e
                )
            )

        return message

    def _validate_extensions(self, model, message: Dict, validate_extensions) -> None:
        """
        Validate extensions for a given Pydantic model.

        Args:
            model: The Pydantic model instance.
            message (dict): The validation message dictionary to update.
            validate_extensions: The function to validate extensions.
        """
        if (
            "stac_extensions" in self.stac_content
            and self.stac_content["stac_extensions"]
        ):
            extension_schemas = []
            validate_extensions(model, reraise_exception=True)
            for ext in self.stac_content["stac_extensions"]:
                extension_schemas.append(ext)
            message["extension_schemas"] = extension_schemas

    def run(self) -> bool:
        """
        Run the STAC validation process based on the input parameters.

        Returns:
            bool: True if the STAC is valid, False otherwise.

        Raises:
            URLError, JSONDecodeError, ValueError, TypeError, FileNotFoundError,
            ConnectionError, exceptions.SSLError, OSError, KeyError, HTTPError,
            jsonschema.exceptions.ValidationError, Exception: Various errors
            during fetching or parsing.
        """
        message = {}
        try:
            # Fetch STAC content if not provided via item_collection/collections
            if (
                self.stac_file is not None
                and not self.item_collection
                and not self.collections
            ):
                self.stac_content = fetch_and_parse_file(self.stac_file, self.headers)

            stac_type = get_stac_type(self.stac_content).upper()
            version = self.stac_content.get("stac_version", "")

            # Validate stac_version field comprehensively
            version_valid, version_error_type, version_error_msg = (
                validate_stac_version_field(self.stac_content)
            )
            if not version_valid:
                message.update(
                    self.create_err_msg(
                        err_type=version_error_type,
                        err_msg=version_error_msg,
                        schema_uri="",
                        version=version,  # Pass the version we extracted
                    )
                )
                self.message.append(message)
                return self.valid

            self.version = version

            if self.core:
                message = self.create_message(stac_type, "core")
                self.core_validator(stac_type)
                display_path = self._original_schema_paths.get(self.schema, self.schema)
                message["schema"] = [display_path]
                self.valid = True

            elif self.schema:
                message = self.create_message(stac_type, "custom")
                display_path = self._original_schema_paths.get(self.schema, self.schema)
                message["schema"] = [display_path]
                self.custom_validator()
                self.valid = True

            elif self.recursive:
                self.valid = self.recursive_validator(stac_type)

            elif self.extensions:
                message = self.extensions_validator(stac_type)

            elif self.pydantic:
                message = self.pydantic_validator(stac_type)

            else:
                self.valid = True
                message = self.default_validator(stac_type)

        except jsonschema.exceptions.ValidationError as e:
            # Improve error message for collection field validation
            err_msg = e.message
            if (
                e.validator == "not"
                and list(e.absolute_path) == ["collection"]
                and "collection" in self.stac_content
            ):
                # Check if item has a collection link
                has_collection_link = False
                for link in self.stac_content.get("links", []):
                    if link.get("rel") == "collection":
                        has_collection_link = True
                        break

                if not has_collection_link:
                    err_msg = (
                        "Item has a 'collection' field but is missing a link with rel='collection'. "
                        "According to STAC v1.0.0 spec, items with a collection field must have a "
                        "corresponding link. Either remove the 'collection' field or add a link with "
                        "rel='collection' pointing to the collection."
                    )

            if e.absolute_path:
                err_msg = (
                    f"{err_msg}. Error is in "
                    f"{' -> '.join([str(i) for i in e.absolute_path])} "
                )
            message.update(
                self.create_err_msg(
                    err_type="JSONSchemaValidationError", err_msg=err_msg, error_obj=e
                )
            )

        except (
            URLError,
            JSONDecodeError,
            ValueError,
            TypeError,
            FileNotFoundError,
            ConnectionError,
            exceptions.SSLError,
            OSError,
            KeyError,
            HTTPError,
        ) as e:
            message.update(
                self.create_err_msg(
                    err_type=type(e).__name__, err_msg=str(e), error_obj=e
                )
            )

        except Exception as e:
            message.update(
                self.create_err_msg(err_type="Exception", err_msg=str(e), error_obj=e)
            )

        if message:
            message["valid_stac"] = self.valid
            self.message.append(message)

        # Write out log if path is provided
        if self.log:
            with open(self.log, "w") as f:
                f.write(json.dumps(self.message, indent=4))

        # filter message to only show errors if valid is False unless trace_recursion mode is on
        if self.recursive and not self.valid and not self.trace_recursion:
            filtered_messages = []
            for message in self.message:
                if not message["valid_stac"]:
                    filtered_messages.append(message)
            self.message = filtered_messages

        return self.valid

"""
Description: Test validation for recursion

"""

from stac_validator import stac_validator


def test_recursive_lvl_4_local_v100():
    stac_file = "tests/test_data/local_cat/open-science-catalog-testing/catalog.json"
    stac = stac_validator.StacValidate(stac_file, recursive=True, max_depth=4)
    stac.run()
    assert stac.valid
    assert stac.message == [
        {
            "version": "1.0.0",
            "path": "tests/test_data/local_cat/open-science-catalog-testing/catalog.json",
            "schema": [
                "https://schemas.stacspec.org/v1.0.0/catalog-spec/json-schema/catalog.json"
            ],
            "valid_stac": True,
            "asset_type": "CATALOG",
            "validation_method": "recursive",
            "validator_engine": "jsonschema",
        },
        {
            "version": "1.0.0",
            "path": "tests/test_data/local_cat/open-science-catalog-testing/./projects/catalog.json",
            "schema": [
                "https://schemas.stacspec.org/v1.0.0/catalog-spec/json-schema/catalog.json"
            ],
            "valid_stac": True,
            "asset_type": "CATALOG",
            "validation_method": "recursive",
            "validator_engine": "jsonschema",
        },
        {
            "version": "1.0.0",
            "path": "tests/test_data/local_cat/open-science-catalog-testing/./projects/./3d-earth/collection.json",
            "schema": [
                "https://stac-extensions.github.io/osc/v1.0.0-rc.3/schema.json",
                "https://stac-extensions.github.io/contacts/v0.1.1/schema.json",
                "https://schemas.stacspec.org/v1.0.0/collection-spec/json-schema/collection.json",
            ],
            "valid_stac": True,
            "asset_type": "COLLECTION",
            "validation_method": "recursive",
            "validator_engine": "jsonschema",
        },
        {
            "version": "1.0.0",
            "path": "tests/test_data/local_cat/open-science-catalog-testing/./projects/./3dctrl/collection.json",
            "schema": [
                "https://stac-extensions.github.io/osc/v1.0.0-rc.3/schema.json",
                "https://stac-extensions.github.io/contacts/v0.1.1/schema.json",
                "https://schemas.stacspec.org/v1.0.0/collection-spec/json-schema/collection.json",
            ],
            "valid_stac": True,
            "asset_type": "COLLECTION",
            "validation_method": "recursive",
            "validator_engine": "jsonschema",
        },
    ]


def test_recursive_local_v090():
    stac_file = "tests/test_data/v090/catalog.json"
    stac = stac_validator.StacValidate(stac_file, recursive=True, max_depth=1)
    stac.run()
    assert stac.message == [
        {
            "version": "0.9.0",
            "path": "tests/test_data/v090/catalog.json",
            "schema": ["https://cdn.staclint.com/v0.9.0/catalog.json"],
            "asset_type": "CATALOG",
            "validation_method": "recursive",
            "valid_stac": True,
            "validator_engine": "jsonschema",
        },
        {
            "version": "0.9.0",
            "path": "tests/test_data/v090/items/sample.json",
            "schema": ["https://cdn.staclint.com/v0.9.0/item.json"],
            "asset_type": "ITEM",
            "validation_method": "recursive",
            "valid_stac": True,
            "validator_engine": "jsonschema",
        },
        {
            "version": "0.9.0",
            "path": "tests/test_data/v090/items/good_item_v090.json",
            "schema": [
                "https://cdn.staclint.com/v0.9.0/extension/eo.json",
                "https://cdn.staclint.com/v0.9.0/extension/view.json",
                "https://cdn.staclint.com/v0.9.0/item.json",
            ],
            "asset_type": "ITEM",
            "validation_method": "recursive",
            "valid_stac": True,
            "validator_engine": "jsonschema",
        },
    ]


def test_recursive_v1beta1():
    stac_file = "tests/test_data/1beta1/sentinel2.json"
    stac = stac_validator.StacValidate(stac_file, recursive=True, max_depth=0)
    stac.run()
    assert stac.message == [
        {
            "version": "1.0.0-beta.1",
            "path": "tests/test_data/1beta1/sentinel2.json",
            "schema": ["https://cdn.staclint.com/v1.0.0-beta.1/collection.json"],
            "asset_type": "COLLECTION",
            "validation_method": "recursive",
            "valid_stac": True,
            "validator_engine": "jsonschema",
        }
    ]


def test_recursive_v1beta2():
    stac_file = "https://raw.githubusercontent.com/stac-utils/pystac/main/tests/data-files/examples/1.0.0-beta.2/collection-spec/examples/sentinel2.json"
    stac = stac_validator.StacValidate(stac_file, recursive=True, max_depth=0)
    stac.run()
    assert stac.message == [
        {
            "version": "1.0.0-beta.2",
            "path": "https://raw.githubusercontent.com/stac-utils/pystac/main/tests/data-files/examples/1.0.0-beta.2/collection-spec/examples/sentinel2.json",
            "schema": [
                "https://schemas.stacspec.org/v1.0.0-beta.2/collection-spec/json-schema/collection.json"
            ],
            "asset_type": "COLLECTION",
            "validation_method": "recursive",
            "valid_stac": True,
            "validator_engine": "jsonschema",
        }
    ]


def test_recursion_collection_local_v1rc1():
    stac_file = "tests/test_data/1rc1/collection.json"
    stac = stac_validator.StacValidate(stac_file, recursive=True, max_depth=1)
    stac.run()
    assert stac.message == [
        {
            "version": "1.0.0-rc.1",
            "path": "tests/test_data/1rc1/collection.json",
            "schema": [
                "https://schemas.stacspec.org/v1.0.0-rc.1/collection-spec/json-schema/collection.json"
            ],
            "asset_type": "COLLECTION",
            "validation_method": "recursive",
            "valid_stac": True,
            "validator_engine": "jsonschema",
        },
        {
            "version": "1.0.0-rc.1",
            "path": "tests/test_data/1rc1/./simple-item.json",
            "schema": [
                "https://schemas.stacspec.org/v1.0.0-rc.1/item-spec/json-schema/item.json"
            ],
            "asset_type": "ITEM",
            "validation_method": "recursive",
            "valid_stac": True,
            "validator_engine": "jsonschema",
        },
        {
            "version": "1.0.0-rc.1",
            "path": "tests/test_data/1rc1/./core-item.json",
            "schema": [
                "https://schemas.stacspec.org/v1.0.0-rc.1/item-spec/json-schema/item.json"
            ],
            "asset_type": "ITEM",
            "validation_method": "recursive",
            "valid_stac": True,
            "validator_engine": "jsonschema",
        },
        {
            "version": "1.0.0-rc.1",
            "path": "tests/test_data/1rc1/./extended-item.json",
            "schema": [
                "https://cdn.staclint.com/v1.0.0-rc.1/extension/eo.json",
                "https://cdn.staclint.com/v1.0.0-rc.1/extension/projection.json",
                "https://cdn.staclint.com/v1.0.0-rc.1/extension/scientific.json",
                "https://cdn.staclint.com/v1.0.0-rc.1/extension/view.json",
                "https://schemas.stacspec.org/v1.0.0-rc.1/item-spec/json-schema/item.json",
            ],
            "asset_type": "ITEM",
            "validation_method": "recursive",
            "valid_stac": True,
            "validator_engine": "jsonschema",
        },
    ]


def test_recursion_collection_local_v1rc2():
    stac_file = "tests/test_data/1rc2/collection.json"
    stac = stac_validator.StacValidate(stac_file, recursive=True, max_depth=1)
    stac.run()
    assert stac.message == [
        {
            "version": "1.0.0-rc.2",
            "path": "tests/test_data/1rc2/collection.json",
            "schema": [
                "https://schemas.stacspec.org/v1.0.0-rc.2/collection-spec/json-schema/collection.json"
            ],
            "asset_type": "COLLECTION",
            "validation_method": "recursive",
            "valid_stac": True,
            "validator_engine": "jsonschema",
        },
        {
            "version": "1.0.0-rc.2",
            "path": "tests/test_data/1rc2/./simple-item.json",
            "schema": [
                "https://schemas.stacspec.org/v1.0.0-rc.2/item-spec/json-schema/item.json"
            ],
            "asset_type": "ITEM",
            "validation_method": "recursive",
            "valid_stac": True,
            "validator_engine": "jsonschema",
        },
        {
            "version": "1.0.0-rc.2",
            "path": "tests/test_data/1rc2/./core-item.json",
            "schema": [
                "https://schemas.stacspec.org/v1.0.0-rc.2/item-spec/json-schema/item.json"
            ],
            "asset_type": "ITEM",
            "validation_method": "recursive",
            "valid_stac": True,
            "validator_engine": "jsonschema",
        },
        {
            "version": "1.0.0-rc.2",
            "path": "tests/test_data/1rc2/./extended-item.json",
            "schema": [
                "https://stac-extensions.github.io/eo/v1.0.0/schema.json",
                "https://stac-extensions.github.io/projection/v1.0.0/schema.json",
                "https://stac-extensions.github.io/scientific/v1.0.0/schema.json",
                "https://stac-extensions.github.io/view/v1.0.0/schema.json",
                "https://stac-extensions.github.io/remote-data/v1.0.0/schema.json",
                "https://schemas.stacspec.org/v1.0.0-rc.2/item-spec/json-schema/item.json",
            ],
            "asset_type": "ITEM",
            "validation_method": "recursive",
            "valid_stac": True,
            "validator_engine": "jsonschema",
        },
    ]


def test_recursion_collection_local_2_v1rc2():
    stac_file = "tests/test_data/1rc2/extensions-collection/collection.json"
    stac = stac_validator.StacValidate(stac_file, recursive=True, max_depth=1)
    stac.run()
    assert stac.message == [
        {
            "version": "1.0.0-rc.2",
            "path": "tests/test_data/1rc2/extensions-collection/collection.json",
            "schema": [
                "https://stac-extensions.github.io/projection/v1.1.0/schema.json",
                "https://schemas.stacspec.org/v1.0.0-rc.2/collection-spec/json-schema/collection.json",
            ],
            "asset_type": "COLLECTION",
            "validation_method": "recursive",
            "valid_stac": True,
            "validator_engine": "jsonschema",
        },
        {
            "version": "1.0.0-rc.2",
            "path": "tests/test_data/1rc2/extensions-collection/./proj-example/proj-example.json",
            "schema": [
                "https://schemas.stacspec.org/v1.0.0-rc.2/item-spec/json-schema/item.json"
            ],
            "asset_type": "ITEM",
            "validation_method": "recursive",
            "valid_stac": True,
            "validator_engine": "jsonschema",
        },
    ]


def test_recursion_without_max_depth():
    stac_file = "tests/test_data/v100/catalog.json"
    stac = stac_validator.StacValidate(stac_file, recursive=True)
    stac.run()
    assert len(stac.message) == 6


def test_recursion_with_bad_item():
    stac_file = "tests/test_data/v100/catalog-with-bad-item.json"
    stac = stac_validator.StacValidate(stac_file, recursive=True)
    stac.run()
    assert not stac.valid
    assert len(stac.message) == 1
    assert stac.message == [
        {
            "version": "1.0.0",
            "path": "tests/test_data/v100/./bad-item.json",
            "schema": [
                "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/item.json"
            ],
            "valid_stac": False,
            "asset_type": "ITEM",
            "validation_method": "recursive",
            "validator_engine": "jsonschema",
            "error_type": "JSONSchemaValidationError",
            "failed_schema": "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/item.json",
            "error_message": "'id' is a required property",
            "recommendation": "For more accurate error information, rerun with --verbose.",
        },
    ]


def test_recursion_with_bad_item_trace_recursion():
    # The catalog links an invalid item first and a valid item second — the
    # walk must continue past the failure and validate both.
    stac_file = "tests/test_data/v100/catalog-with-bad-item.json"
    stac = stac_validator.StacValidate(stac_file, recursive=True, trace_recursion=True)
    stac.run()
    assert not stac.valid
    assert len(stac.message) == 3
    assert stac.message == [
        {
            "version": "1.0.0",
            "path": "tests/test_data/v100/catalog-with-bad-item.json",
            "schema": [
                "https://schemas.stacspec.org/v1.0.0/catalog-spec/json-schema/catalog.json"
            ],
            "valid_stac": True,
            "asset_type": "CATALOG",
            "validation_method": "recursive",
            "validator_engine": "jsonschema",
        },
        {
            "version": "1.0.0",
            "path": "tests/test_data/v100/./bad-item.json",
            "schema": [
                "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/item.json"
            ],
            "valid_stac": False,
            "asset_type": "ITEM",
            "validation_method": "recursive",
            "validator_engine": "jsonschema",
            "error_type": "JSONSchemaValidationError",
            "failed_schema": "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/item.json",
            "error_message": "'id' is a required property",
            "recommendation": "For more accurate error information, rerun with --verbose.",
        },
        {
            "version": "1.0.0",
            "path": "tests/test_data/v100/./collectionless-item.json",
            "schema": [
                "https://stac-extensions.github.io/eo/v1.0.0/schema.json",
                "https://stac-extensions.github.io/view/v1.0.0/schema.json",
                "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/item.json",
            ],
            "valid_stac": True,
            "asset_type": "ITEM",
            "validation_method": "recursive",
            "validator_engine": "jsonschema",
        },
    ]


def test_recursion_with_bad_child_collection():
    # It is important here that there is a second good child in the collection
    # since a previous bug did not correctly set the valid variable if the last
    # child passed validation
    stac_file = "tests/test_data/v100/catalog-with-bad-child-collection.json"
    stac = stac_validator.StacValidate(stac_file, recursive=True)
    stac.run()
    assert not stac.valid
    assert len(stac.message) == 1
    assert stac.message == [
        {
            "version": "1.0.0",
            "path": "tests/test_data/v100/./collection-only/bad-collection.json",
            "schema": [
                "https://schemas.stacspec.org/v1.0.0/collection-spec/json-schema/collection.json"
            ],
            "valid_stac": False,
            "asset_type": "COLLECTION",
            "validation_method": "recursive",
            "validator_engine": "jsonschema",
            "error_type": "JSONSchemaValidationError",
            "failed_schema": "https://schemas.stacspec.org/v1.0.0/collection-spec/json-schema/collection.json",
            "error_message": "'id' is a required property",
            "recommendation": "For more accurate error information, rerun with --verbose.",
        }
    ]


def test_recursion_with_missing_collection_link():
    stac_file = "tests/test_data/v100/item-without-collection-link.json"
    stac = stac_validator.StacValidate(stac_file, recursive=True)
    assert not stac.run()
    assert not stac.valid
    assert len(stac.message) == 1
    assert stac.message == [
        {
            "asset_type": "ITEM",
            "version": "1.0.0",
            "path": "tests/test_data/v100/item-without-collection-link.json",
            "schema": [
                "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/item.json"
            ],
            "valid_stac": False,
            "validation_method": "recursive",
            "validator_engine": "jsonschema",
            "error_type": "JSONSchemaValidationError",
            "failed_schema": "https://schemas.stacspec.org/v1.0.0/item-spec/json-schema/item.json",
            "error_message": "'simple-collection' should not be valid under {}. Error is in collection ",
            "recommendation": "For more accurate error information, rerun with --verbose.",
        },
    ]

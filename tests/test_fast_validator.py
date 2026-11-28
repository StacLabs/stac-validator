import json
import os
import threading
import time
from concurrent.futures import Future

import pytest

from stac_validator import fast_validator
from stac_validator.fast_validator import FastSTACMultiValidationError, FastValidator


@pytest.fixture
def valid_item(tmp_path):
    """Create a valid STAC Item."""
    item_path = tmp_path / "valid_item.json"
    item_data = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "id": "test-item",
        "geometry": None,
        "properties": {"datetime": "2023-01-01T00:00:00Z"},
        "links": [{"rel": "self", "href": "http://example.com"}],
        "assets": {},
    }
    item_path.write_text(json.dumps(item_data))
    return str(item_path)


@pytest.fixture
def valid_collection(tmp_path):
    """Create a valid STAC Collection."""
    coll_path = tmp_path / "valid_collection.json"
    coll_data = {
        "stac_version": "1.0.0",
        "type": "Collection",
        "id": "test-collection",
        "description": "Test collection",
        "license": "MIT",
        "extent": {
            "spatial": {"bbox": [[-180, -90, 180, 90]]},
            "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
        },
        "links": [],
    }
    coll_path.write_text(json.dumps(coll_data))
    return str(coll_path)


@pytest.fixture
def valid_catalog(tmp_path):
    """Create a valid STAC Catalog."""
    cat_path = tmp_path / "valid_catalog.json"
    cat_data = {
        "stac_version": "1.0.0",
        "type": "Catalog",
        "id": "test-catalog",
        "description": "Test catalog",
        "links": [],
    }
    cat_path.write_text(json.dumps(cat_data))
    return str(cat_path)


@pytest.fixture
def valid_feature_collection(tmp_path):
    """Create a valid FeatureCollection with multiple items."""
    fc_path = tmp_path / "valid_fc.json"
    fc_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "stac_version": "1.0.0",
                "type": "Feature",
                "id": f"item-{i}",
                "geometry": None,
                "properties": {"datetime": "2023-01-01T00:00:00Z"},
                "links": [{"rel": "self", "href": "http://example.com"}],
                "assets": {},
            }
            for i in range(5)
        ],
    }
    fc_path.write_text(json.dumps(fc_data))
    return str(fc_path)


@pytest.fixture
def invalid_item(tmp_path):
    """Create an invalid STAC Item (missing required 'id')."""
    item_path = tmp_path / "invalid_item.json"
    item_data = {
        "stac_version": "1.0.0",
        "type": "Feature",
        "geometry": None,
        "properties": {"datetime": "2023-01-01T00:00:00Z"},
        "links": [],
        "assets": {},
    }
    item_path.write_text(json.dumps(item_data))
    return str(item_path)


@pytest.fixture
def invalid_feature_collection(tmp_path):
    """Create a FeatureCollection with some invalid items."""
    fc_path = tmp_path / "invalid_fc.json"
    fc_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "stac_version": "1.0.0",
                "type": "Feature",
                "id": "valid-item",
                "geometry": None,
                "properties": {"datetime": "2023-01-01T00:00:00Z"},
                "links": [{"rel": "self", "href": "http://example.com"}],
                "assets": {},
            },
            {
                "stac_version": "1.0.0",
                "type": "Feature",
                "geometry": None,
                "properties": {"datetime": "2023-01-01T00:00:00Z"},
                "links": [],
                "assets": {},
            },
        ],
    }
    fc_path.write_text(json.dumps(fc_data))
    return str(fc_path)


class TestFastValidatorBasic:
    """Test basic functionality of FastValidator."""

    def test_valid_item(self, valid_item):
        """Test validation of a valid STAC Item."""
        fv = FastValidator(valid_item, quiet=True)
        fv.run()
        assert fv.valid is True

    def test_valid_collection(self, valid_collection):
        """Test validation of a valid STAC Collection."""
        fv = FastValidator(valid_collection, quiet=True)
        fv.run()
        assert fv.valid is True

    def test_valid_catalog(self, valid_catalog):
        """Test validation of a valid STAC Catalog."""
        fv = FastValidator(valid_catalog, quiet=True)
        fv.run()
        assert fv.valid is True

    def test_valid_feature_collection(self, valid_feature_collection):
        """Test validation of a valid FeatureCollection."""
        fv = FastValidator(valid_feature_collection, quiet=True)
        fv.run()
        assert fv.valid is True

    def test_invalid_item(self, invalid_item):
        """Test that invalid items are detected."""
        fv = FastValidator(invalid_item, quiet=True)
        fv.run()
        assert fv.valid is False

    def test_invalid_feature_collection(self, invalid_feature_collection):
        """Test that FeatureCollections with invalid items are detected."""
        fv = FastValidator(invalid_feature_collection, quiet=True)
        fv.run()
        assert fv.valid is False


class TestFastValidatorOptions:
    """Test FastValidator options."""

    def test_quiet_mode(self, valid_item, capsys):
        """Test quiet mode suppresses item-level output."""
        fv = FastValidator(valid_item, quiet=True)
        fv.run()
        captured = capsys.readouterr()
        assert "VALIDATION SUMMARY" in captured.out

    def test_verbose_mode(self, valid_feature_collection, capsys):
        """Test verbose mode shows all items."""
        fv = FastValidator(valid_feature_collection, quiet=False, verbose=True)
        fv.run()
        captured = capsys.readouterr()
        assert "[1]" in captured.out
        assert "[5]" in captured.out

    def test_non_verbose_mode(self, tmp_path, capsys):
        """Test non-verbose mode shows first 5 items and silences rest."""
        fc_path = tmp_path / "large_fc.json"
        fc_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "stac_version": "1.0.0",
                    "type": "Feature",
                    "id": f"item-{i}",
                    "geometry": None,
                    "properties": {"datetime": "2023-01-01T00:00:00Z"},
                    "links": [{"rel": "self", "href": "http://example.com"}],
                    "assets": {},
                }
                for i in range(20)
            ],
        }
        fc_path.write_text(json.dumps(fc_data))

        fv = FastValidator(str(fc_path), quiet=False, verbose=False)
        fv.run()
        captured = capsys.readouterr()
        assert "[1]" in captured.out
        assert "silencing output" in captured.out

    def test_limit_reduces_validated_objects(self, tmp_path):
        """Test limit option validates only the first N objects."""
        fc_path = tmp_path / "limited_fc.json"
        fc_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "stac_version": "1.0.0",
                    "type": "Feature",
                    "id": f"item-{i}",
                    "geometry": None,
                    "properties": {"datetime": "2023-01-01T00:00:00Z"},
                    "links": [{"rel": "self", "href": "http://example.com"}],
                    "assets": {},
                }
                for i in range(10)
            ],
        }
        fc_path.write_text(json.dumps(fc_data))

        fv = FastValidator(str(fc_path), quiet=True, limit=3)
        fv.run()

        msg = fv.message[0]
        assert msg["total_objects"] == 3
        assert msg["valid_objects"] == 3
        assert msg["invalid_objects"] == 0

    def test_limit_above_total_does_not_change_count(self, valid_feature_collection):
        """Test limit larger than object count validates all objects."""
        fv = FastValidator(valid_feature_collection, quiet=True, limit=20)
        fv.run()

        msg = fv.message[0]
        assert msg["total_objects"] == 5
        assert msg["valid_objects"] == 5


class TestFastValidatorRunDict:
    """Test in-memory dictionary validation entrypoint."""

    def test_run_dict_valid_item(self):
        payload = {
            "stac_version": "1.0.0",
            "type": "Feature",
            "id": "test-item",
            "geometry": None,
            "properties": {"datetime": "2023-01-01T00:00:00Z"},
            "links": [{"rel": "self", "href": "http://example.com"}],
            "assets": {},
        }

        fv = FastValidator("", quiet=True)
        fv.run_dict(payload)

        assert fv.valid is True
        assert fv.message[0]["path"] == "in-memory"
        assert fv.message[0]["total_objects"] == 1
        assert fv.message[0]["valid_objects"] == 1
        assert fv.message[0]["invalid_objects"] == 0

    def test_run_dict_invalid_item(self):
        payload = {
            "stac_version": "1.0.0",
            "type": "Feature",
            "geometry": None,
            "properties": {"datetime": "2023-01-01T00:00:00Z"},
            "links": [],
            "assets": {},
        }

        fv = FastValidator("", quiet=True)
        fv.run_dict(payload)

        assert fv.valid is False
        assert fv.message[0]["total_objects"] == 1
        assert fv.message[0]["valid_objects"] == 0
        assert fv.message[0]["invalid_objects"] == 1
        assert len(fv.message[0]["errors"]) > 0

    def test_run_dict_feature_collection_limit(self):
        payload = {
            "type": "FeatureCollection",
            "features": [
                {
                    "stac_version": "1.0.0",
                    "type": "Feature",
                    "id": f"item-{i}",
                    "geometry": None,
                    "properties": {"datetime": "2023-01-01T00:00:00Z"},
                    "links": [{"rel": "self", "href": "http://example.com"}],
                    "assets": {},
                }
                for i in range(5)
            ],
        }

        fv = FastValidator("", quiet=True, limit=2)
        fv.run_dict(payload)

        assert fv.valid is True
        assert fv.message[0]["input_objects"] == 5
        assert fv.message[0]["total_objects"] == 2
        assert fv.message[0]["valid_objects"] == 2


class TestFastValidatorRecursiveAndApi:
    """Test recursive and API traversal behavior."""

    def test_load_collection_documents_keeps_order_and_errors(self, monkeypatch):
        """Test parallel collection loading preserves URL order and captures per-URL errors."""

        def _fake_load(self, resource_path):
            if resource_path.endswith("two"):
                raise RuntimeError("boom")
            return {"id": resource_path.rsplit("/", 1)[-1]}

        monkeypatch.setattr(FastValidator, "_load_json_resource", _fake_load)

        fv = FastValidator("https://api.example.com", quiet=True)
        loaded = fv._load_collection_documents(
            [
                "https://api.example.com/one",
                "https://api.example.com/two",
                "https://api.example.com/three",
            ]
        )

        assert [entry[0] for entry in loaded] == [
            "https://api.example.com/one",
            "https://api.example.com/two",
            "https://api.example.com/three",
        ]
        assert loaded[0][1] == {"id": "one"}
        assert loaded[0][2] is None
        assert loaded[1][1] is None
        assert str(loaded[1][2]) == "boom"
        assert loaded[2][1] == {"id": "three"}
        assert loaded[2][2] is None

    def test_prefetch_api_collection_resources_batch_prefetches_items(
        self, monkeypatch
    ):
        """Test API collection prefetch preserves order and includes items pages."""

        payloads = {
            "https://api.example.com/one": {
                "id": "one",
                "links": [
                    {
                        "rel": "items",
                        "href": "https://api.example.com/one/items",
                    }
                ],
            },
            "https://api.example.com/one/items": {
                "type": "FeatureCollection",
                "features": [],
            },
            "https://api.example.com/two": {"id": "two", "links": []},
        }

        def _fake_load(self, resource_path):
            return payloads[resource_path]

        monkeypatch.setattr(FastValidator, "_load_json_resource", _fake_load)

        fv = FastValidator("https://api.example.com", quiet=True)
        loaded = fv._prefetch_api_collection_resources_batch(
            [
                "https://api.example.com/one",
                "https://api.example.com/two",
            ]
        )

        assert [entry[0] for entry in loaded] == [
            "https://api.example.com/one",
            "https://api.example.com/two",
        ]
        assert loaded[0][1]["https://api.example.com/one"]["id"] == "one"
        assert (
            loaded[0][1]["https://api.example.com/one/items"]["type"]
            == "FeatureCollection"
        )
        assert loaded[1][1]["https://api.example.com/two"]["id"] == "two"

    def test_api_prefetch_truncates_to_remaining_limit(self, monkeypatch):
        """Test API data-link prefetch list is trimmed to remaining validation capacity."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "description": "api root",
                "links": [
                    {"rel": "data", "href": "https://api.example.com/collections"}
                ],
            },
            "https://api.example.com/collections": {
                "collections": [
                    {"id": "c1"},
                    {"id": "c2"},
                    {"id": "c3"},
                ]
            },
        }

        def _fake_load(self, resource_path):
            return payloads[resource_path]

        captured = []

        def _fake_prefetch(self, collection_urls, include_items=True):
            captured.extend(collection_urls)
            return []

        monkeypatch.setattr(FastValidator, "_load_json_resource", _fake_load)
        monkeypatch.setattr(
            FastValidator,
            "_prefetch_api_collection_resources_batch",
            _fake_prefetch,
        )

        fv = FastValidator("https://api.example.com", quiet=True, limit=2)
        fv.run_api()

        # One slot is consumed by the root catalog, so only one collection should be prefetched.
        assert captured == ["https://api.example.com/collections/c1"]

    def test_recursive_mode_respects_limit(self, tmp_path, monkeypatch):
        """Test recursive validation follows links and stops at limit."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        root = {
            "stac_version": "1.0.0",
            "type": "Catalog",
            "id": "root",
            "description": "root catalog",
            "links": [{"rel": "child", "href": "child.json"}],
        }
        child = {
            "stac_version": "1.0.0",
            "type": "Catalog",
            "id": "child",
            "description": "child catalog",
            "links": [
                {"rel": "item", "href": "item-1.json"},
                {"rel": "item", "href": "item-2.json"},
            ],
        }
        item_1 = {
            "stac_version": "1.0.0",
            "type": "Feature",
            "id": "item-1",
            "geometry": None,
            "properties": {"datetime": "2023-01-01T00:00:00Z"},
            "links": [{"rel": "self", "href": "http://example.com/item-1"}],
            "assets": {},
        }
        item_2 = {
            "stac_version": "1.0.0",
            "type": "Feature",
            "id": "item-2",
            "geometry": None,
            "properties": {"datetime": "2023-01-01T00:00:00Z"},
            "links": [{"rel": "self", "href": "http://example.com/item-2"}],
            "assets": {},
        }

        root_path = tmp_path / "catalog.json"
        (tmp_path / "child.json").write_text(json.dumps(child))
        (tmp_path / "item-1.json").write_text(json.dumps(item_1))
        (tmp_path / "item-2.json").write_text(json.dumps(item_2))
        root_path.write_text(json.dumps(root))

        fv = FastValidator(str(root_path), quiet=True, limit=2)
        fv.run_recursive()

        assert fv.valid is True
        assert len(fv.message) == 2
        assert fv.message[0]["id"] == "root"
        assert fv.message[1]["id"] == "child"

    def test_recursive_mode_summary_includes_execution_time(
        self, tmp_path, monkeypatch, capsys
    ):
        """Test recursive mode keeps recursive summary format and includes execution time."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        root = {
            "stac_version": "1.0.0",
            "type": "Catalog",
            "id": "root",
            "description": "root catalog",
            "links": [{"rel": "child", "href": "child.json"}],
        }
        child = {
            "stac_version": "1.0.0",
            "type": "Catalog",
            "id": "child",
            "description": "child catalog",
            "links": [],
        }

        root_path = tmp_path / "catalog.json"
        (tmp_path / "child.json").write_text(json.dumps(child))
        root_path.write_text(json.dumps(root))

        fv = FastValidator(str(root_path), quiet=False, verbose=True)
        fv.run_recursive()

        captured = capsys.readouterr()
        assert "RECURSIVE VALIDATION SUMMARY" in captured.out
        assert "Execution Time" in captured.out

    def test_api_mode_respects_limit(self, monkeypatch):
        """Test API validation follows API links and stops at limit."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "description": "api root",
                "links": [
                    {"rel": "data", "href": "https://api.example.com/collections"}
                ],
            },
            "https://api.example.com/collections": {
                "collections": [{"id": "demo-collection"}],
            },
            "https://api.example.com/collections/demo-collection": {
                "stac_version": "1.0.0",
                "type": "Collection",
                "id": "demo-collection",
                "description": "demo",
                "license": "MIT",
                "extent": {
                    "spatial": {"bbox": [[-180, -90, 180, 90]]},
                    "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
                },
                "links": [
                    {
                        "rel": "items",
                        "href": "https://api.example.com/collections/demo-collection/items",
                    }
                ],
            },
            "https://api.example.com/collections/demo-collection/items": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "stac_version": "1.0.0",
                        "type": "Feature",
                        "id": "item-1",
                        "geometry": None,
                        "properties": {"datetime": "2023-01-01T00:00:00Z"},
                        "links": [
                            {
                                "rel": "self",
                                "href": "https://api.example.com/items/item-1",
                            }
                        ],
                        "assets": {},
                    }
                ],
            },
        }

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=True, limit=2)
        fv.run_api()

        assert fv.valid is True
        assert len(fv.message) == 2
        assert fv.message[0]["id"] == "api-root"
        assert fv.message[1]["id"] == "demo-collection"

    def test_api_mode_summary_includes_execution_time(self, monkeypatch, capsys):
        """Test API mode keeps API summary format and includes execution time."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "description": "api root",
                "links": [
                    {"rel": "data", "href": "https://api.example.com/collections"}
                ],
            },
            "https://api.example.com/collections": {
                "collections": [{"id": "demo-collection"}],
            },
            "https://api.example.com/collections/demo-collection": {
                "stac_version": "1.0.0",
                "type": "Collection",
                "id": "demo-collection",
                "description": "demo",
                "license": "MIT",
                "extent": {
                    "spatial": {"bbox": [[-180, -90, 180, 90]]},
                    "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
                },
                "links": [],
            },
        }

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=False, verbose=True)
        fv.run_api()

        captured = capsys.readouterr()
        assert "[1] Validating Catalog: api-root" in captured.out
        assert "STAC API VALIDATION SUMMARY" in captured.out
        assert "Execution Time" in captured.out

    def test_api_mode_does_not_validate_items_featurecollection(self, monkeypatch):
        """Test API mode validates item features, not the /items FeatureCollection object."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "description": "api root",
                "links": [
                    {"rel": "data", "href": "https://api.example.com/collections"}
                ],
            },
            "https://api.example.com/collections": {
                "collections": [{"id": "demo-collection"}],
            },
            "https://api.example.com/collections/demo-collection": {
                "stac_version": "1.0.0",
                "type": "Collection",
                "id": "demo-collection",
                "description": "demo",
                "license": "MIT",
                "extent": {
                    "spatial": {"bbox": [[-180, -90, 180, 90]]},
                    "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
                },
                "links": [
                    {
                        "rel": "items",
                        "href": "https://api.example.com/collections/demo-collection/items",
                    }
                ],
            },
            "https://api.example.com/collections/demo-collection/items": {
                "type": "FeatureCollection",
                "features": [],
                "links": [],
            },
        }

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=True)
        fv.run_api()

        assert fv.valid is True
        assert len(fv.message) == 2
        paths = {entry["path"] for entry in fv.message}
        assert "https://api.example.com/collections/demo-collection/items" not in paths

    def test_resolve_link_path_remote_base(self):
        """Relative hrefs under an http base resolve via urljoin, not normpath."""
        resolve = FastValidator._resolve_link_path
        assert (
            resolve("https://api.example.com/root/catalog.json", "./child/c.json")
            == "https://api.example.com/root/child/c.json"
        )
        assert (
            resolve("https://api.example.com/root/catalog.json", "child/c.json")
            == "https://api.example.com/root/child/c.json"
        )
        assert (
            resolve("https://api.example.com/root/catalog.json", "/c.json")
            == "https://api.example.com/c.json"
        )
        assert (
            resolve("https://api.example.com/a", "https://other.example.com/x")
            == "https://other.example.com/x"
        )
        assert resolve("/root/catalog.json", "./child/c.json") == "/root/child/c.json"

    def test_canonical_url_normalizes_spelling(self):
        """Equivalent URL spellings canonicalize identically for dedup."""
        canon = FastValidator._canonical_url
        assert canon("HTTP://EXAMPLE.COM:80/a//b/../c/") == "http://example.com/a/c"
        assert canon("https://example.com:443/x") == "https://example.com/x"
        assert canon("https://example.com:8443/x") == "https://example.com:8443/x"
        assert canon("https://example.com") == "https://example.com/"
        # Query strings and fragments are preserved verbatim
        assert (
            canon("https://example.com/x?page=2&token=a%20b#frag")
            == "https://example.com/x?page=2&token=a%20b#frag"
        )

    def test_resolve_link_path_canonicalizes(self):
        """Resolved URLs come back in canonical form for visited dedup."""
        resolve = FastValidator._resolve_link_path
        assert (
            resolve("https://api.example.com/a", "https://api.example.com/p/../q/")
            == "https://api.example.com/q"
        )
        assert (
            resolve("https://api.example.com/a", "//api.example.com:443/x/")
            == "https://api.example.com/x"
        )

    def test_api_mode_relative_child_links(self, monkeypatch):
        """Relative hrefs under a remote base must not be corrupted to 'https:/host'."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        payloads = {
            "https://api.example.com/root/catalog.json": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "links": [
                    {"rel": "child", "href": "./child/catalog.json"},
                ],
            },
            "https://api.example.com/root/child/catalog.json": {
                "stac_version": "1.0.0",
                "type": "Catalog",
                "id": "child-catalog",
                "description": "child",
                "links": [],
            },
        }

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com/root/catalog.json", quiet=True)
        fv.run_api()

        assert fv.valid is True
        assert len(fv.message) == 2
        assert fv.message[1]["path"] == (
            "https://api.example.com/root/child/catalog.json"
        )

    def test_api_mode_items_pagination_follows_next(self, monkeypatch):
        """Items FeatureCollections paginated via rel=next validate all pages."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        def _item(item_id):
            return {
                "stac_version": "1.0.0",
                "type": "Feature",
                "id": item_id,
                "geometry": None,
                "properties": {"datetime": "2023-01-01T00:00:00Z"},
                "links": [],
                "assets": {},
            }

        base = "https://api.example.com/collections/demo-collection/items"
        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "links": [
                    {"rel": "data", "href": "https://api.example.com/collections"}
                ],
            },
            "https://api.example.com/collections": {
                "collections": [{"id": "demo-collection"}],
            },
            "https://api.example.com/collections/demo-collection": {
                "stac_version": "1.0.0",
                "type": "Collection",
                "id": "demo-collection",
                "license": "MIT",
                "extent": {
                    "spatial": {"bbox": [[-180, -90, 180, 90]]},
                    "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
                },
                "links": [{"rel": "items", "href": base}],
            },
            base: {
                "type": "FeatureCollection",
                "features": [_item("item-1")],
                "links": [{"rel": "next", "href": f"{base}?cursor=2"}],
            },
            f"{base}?cursor=2": {
                "type": "FeatureCollection",
                "features": [_item("item-2"), _item("item-1")],
                "links": [],
            },
        }

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=True)
        fv.run_api()

        assert fv.valid is True
        item_results = [r for r in fv.message if r.get("stac_type") == "item"]
        item_ids = sorted(r["id"] for r in item_results)
        # item-1 appears on both pages but is validated once
        assert item_ids == ["item-1", "item-2"]

    def test_api_mode_non_dict_linked_resource(self, monkeypatch):
        """A linked resource that is not a JSON object fails cleanly."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "links": [
                    {"rel": "child", "href": "https://api.example.com/list.json"}
                ],
            },
            "https://api.example.com/list.json": ["not", "a", "stac", "object"],
        }

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=True)
        fv.run_api()

        assert fv.valid is False
        assert len(fv.message) == 2
        bad = fv.message[1]
        assert bad["path"] == "https://api.example.com/list.json"
        assert bad["valid_stac"] is False
        assert bad["error_message"] == "Linked resource is not a JSON object."

    def test_recursive_max_depth(self, tmp_path, monkeypatch):
        """max_depth caps how many link levels are validated (root = 1)."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        root = {
            "stac_version": "1.0.0",
            "type": "Catalog",
            "id": "root",
            "description": "root catalog",
            "links": [{"rel": "child", "href": "child.json"}],
        }
        child = {
            "stac_version": "1.0.0",
            "type": "Catalog",
            "id": "child",
            "description": "child catalog",
            "links": [{"rel": "item", "href": "item.json"}],
        }
        item = {
            "stac_version": "1.0.0",
            "type": "Feature",
            "id": "item",
            "geometry": None,
            "properties": {"datetime": "2023-01-01T00:00:00Z"},
            "links": [],
            "assets": {},
        }

        root_path = tmp_path / "catalog.json"
        (tmp_path / "child.json").write_text(json.dumps(child))
        (tmp_path / "item.json").write_text(json.dumps(item))
        root_path.write_text(json.dumps(root))

        fv = FastValidator(str(root_path), quiet=True, max_depth=1)
        fv.run_recursive()
        assert [r["id"] for r in fv.message] == ["root"]

        fv = FastValidator(str(root_path), quiet=True, max_depth=2)
        fv.run_recursive()
        assert [r["id"] for r in fv.message] == ["root", "child"]

        fv = FastValidator(str(root_path), quiet=True)
        fv.run_recursive()
        assert [r["id"] for r in fv.message] == ["root", "child", "item"]

    def test_root_load_failure_structured_result(self):
        """A root that fails to load produces a structured error result."""
        fv = FastValidator("/does/not/exist/catalog.json", quiet=True)
        fv.run_recursive()

        assert fv.valid is False
        assert len(fv.message) == 1
        msg = fv.message[0]
        assert msg["path"] == "/does/not/exist/catalog.json"
        assert msg["valid_stac"] is False
        assert msg["stac_type"] == "unknown"
        assert "Failed to load" in msg["error_message"]

    def test_custom_session_headers_and_timeout(self, monkeypatch):
        """session/headers/timeout kwargs drive remote resource fetches."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        calls = []

        class _Response:
            def raise_for_status(self):
                return None

            def json(self):
                return {
                    "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                    "id": "api-root",
                    "type": "Catalog",
                    "links": [],
                }

        class _FakeSession:
            def get(self, url, timeout=None, headers=None):
                calls.append((url, timeout, headers))
                return _Response()

        fv = FastValidator(
            "https://api.example.com",
            quiet=True,
            headers={"Authorization": "Bearer token"},
            timeout=30,
            session=_FakeSession(),
        )
        fv.run_api()

        assert fv.valid is True
        assert calls == [
            (
                "https://api.example.com",
                30,
                {"Authorization": "Bearer token"},
            )
        ]

    def test_keep_documents_map(self, monkeypatch):
        """keep_documents populates loaded_objects keyed by result path."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        items_url = "https://api.example.com/collections/demo-collection/items"
        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "links": [
                    {"rel": "data", "href": "https://api.example.com/collections"}
                ],
            },
            "https://api.example.com/collections": {
                "collections": [{"id": "demo-collection"}],
            },
            "https://api.example.com/collections/demo-collection": {
                "stac_version": "1.0.0",
                "type": "Collection",
                "id": "demo-collection",
                "license": "MIT",
                "extent": {
                    "spatial": {"bbox": [[-180, -90, 180, 90]]},
                    "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
                },
                "links": [{"rel": "items", "href": items_url}],
            },
            items_url: {
                "type": "FeatureCollection",
                "features": [
                    {
                        "stac_version": "1.0.0",
                        "type": "Feature",
                        "id": "item-1",
                        "geometry": None,
                        "properties": {"datetime": "2023-01-01T00:00:00Z"},
                        "links": [],
                        "assets": {},
                    }
                ],
                "links": [],
            },
        }

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=True, keep_documents=True)
        fv.run_api()

        assert fv.valid is True
        item_path = f"{items_url}#item-1"
        assert fv.loaded_objects[item_path]["id"] == "item-1"
        assert (
            fv.loaded_objects["https://api.example.com/collections/demo-collection"][
                "type"
            ]
            == "Collection"
        )

        fv = FastValidator("https://api.example.com", quiet=True)
        fv.run_api()
        assert fv.loaded_objects == {}

    def test_pre_1_0_type_inference(self, tmp_path, monkeypatch):
        """STAC <1.0 documents without a 'type' member get inferred types."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        # Pre-1.0 catalog has no "type"; a bare "license" must not make it a
        # Collection - only "extent" does.
        root = {
            "stac_version": "0.9.0",
            "id": "root",
            "description": "old catalog",
            "license": "MIT",
            "links": [{"rel": "child", "href": "collection.json"}],
        }
        collection = {
            "stac_version": "0.9.0",
            "id": "old-collection",
            "description": "old collection",
            "license": "MIT",
            "extent": {
                "spatial": {"bbox": [[-180, -90, 180, 90]]},
                "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
            },
            "links": [],
        }

        root_path = tmp_path / "catalog.json"
        (tmp_path / "collection.json").write_text(json.dumps(collection))
        root_path.write_text(json.dumps(root))

        fv = FastValidator(str(root_path), quiet=True)
        fv.run_recursive()

        assert len(fv.message) == 2
        assert fv.message[0]["stac_type"] == "catalog"
        assert fv.message[1]["stac_type"] == "collection"

    def test_prefetch_skips_items_when_limit_exhausted(self, monkeypatch):
        """Prefetch does not fetch items pages once the limit is exhausted."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        items_url = "https://api.example.com/collections/demo-collection/items"
        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "links": [
                    {"rel": "data", "href": "https://api.example.com/collections"}
                ],
            },
            "https://api.example.com/collections": {
                "collections": [{"id": "demo-collection"}],
            },
            "https://api.example.com/collections/demo-collection": {
                "stac_version": "1.0.0",
                "type": "Collection",
                "id": "demo-collection",
                "license": "MIT",
                "extent": {
                    "spatial": {"bbox": [[-180, -90, 180, 90]]},
                    "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
                },
                "links": [{"rel": "items", "href": items_url}],
            },
            # items_url deliberately absent: if prefetch fetched it, _fake_get
            # would raise
        }

        fetched = []

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            fetched.append(url)
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=True, limit=2)
        fv.run_api()

        assert items_url not in fetched
        assert len(fv.message) == 2

    def test_prefetch_skips_items_beyond_max_depth(self, monkeypatch):
        """Prefetch does not fetch items pages the depth cap would exclude."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        items_url = "https://api.example.com/collections/demo-collection/items"
        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "links": [
                    {"rel": "data", "href": "https://api.example.com/collections"}
                ],
            },
            "https://api.example.com/collections": {
                "collections": [{"id": "demo-collection"}],
            },
            "https://api.example.com/collections/demo-collection": {
                "stac_version": "1.0.0",
                "type": "Collection",
                "id": "demo-collection",
                "license": "MIT",
                "extent": {
                    "spatial": {"bbox": [[-180, -90, 180, 90]]},
                    "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
                },
                "links": [{"rel": "items", "href": items_url}],
            },
            # items_url deliberately absent: if prefetch fetched it,
            # _fake_get would raise
        }

        fetched = []

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            fetched.append(url)
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=True, max_depth=2)
        fv.run_api()

        assert items_url not in fetched
        # root + collection are still validated; items are excluded by the cap
        assert len(fv.message) == 2

    def test_prefetch_fetches_items_within_max_depth(self, monkeypatch):
        """With room under the depth cap, items pages are still prefetched."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        items_url = "https://api.example.com/collections/demo-collection/items"
        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "links": [
                    {"rel": "data", "href": "https://api.example.com/collections"}
                ],
            },
            "https://api.example.com/collections": {
                "collections": [{"id": "demo-collection"}],
            },
            "https://api.example.com/collections/demo-collection": {
                "stac_version": "1.0.0",
                "type": "Collection",
                "id": "demo-collection",
                "license": "MIT",
                "extent": {
                    "spatial": {"bbox": [[-180, -90, 180, 90]]},
                    "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
                },
                "links": [{"rel": "items", "href": items_url}],
            },
            items_url: {
                "type": "FeatureCollection",
                "features": [],
                "links": [],
            },
        }

        fetched = []

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            fetched.append(url)
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=True, max_depth=3)
        fv.run_api()

        assert items_url in fetched

    def test_prefetch_skips_items_beyond_max_depth_nested_catalogs(self, monkeypatch):
        """On catalogs-extension chains, items pages past the depth cap
        are not prefetched at any nesting level."""
        items_url = "https://api.example.com/cat1-collections/c1/items"
        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "links": [
                    {
                        "rel": "catalogs",
                        "href": "https://api.example.com/catalogs-idx",
                    }
                ],
            },
            "https://api.example.com/catalogs-idx": {
                "catalogs": [{"id": "cat1"}],
            },
            # sub-catalog at depth 1, linking its collections index
            "https://api.example.com/catalogs-idx/cat1": {
                "stac_version": "1.0.0",
                "type": "Catalog",
                "id": "cat1",
                "links": [
                    {
                        "rel": "collections",
                        "href": "https://api.example.com/cat1-collections",
                    }
                ],
            },
            "https://api.example.com/cat1-collections": {
                "collections": [{"id": "c1"}],
            },
            # collection at depth 2; its items would land at depth 3
            "https://api.example.com/cat1-collections/c1": {
                "stac_version": "1.0.0",
                "type": "Collection",
                "id": "c1",
                "license": "MIT",
                "extent": {
                    "spatial": {"bbox": [[-180, -90, 180, 90]]},
                    "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
                },
                "links": [{"rel": "items", "href": items_url}],
            },
            # items_url deliberately absent: if prefetch fetched it,
            # _fake_get would raise
        }

        fetched = []

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            fetched.append(url)
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )
        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=True, max_depth=3)
        fv.run_api()

        assert items_url not in fetched
        # collections at depth 2 are still validated
        assert any(m["path"].endswith("/c1") for m in fv.message)

    def test_prefetch_fetches_items_under_max_depth_nested_catalogs(self, monkeypatch):
        """Items pages are still prefetched on catalogs-extension chains
        when items land inside the depth cap."""
        items_url = "https://api.example.com/cat1-collections/c1/items"
        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "links": [
                    {
                        "rel": "catalogs",
                        "href": "https://api.example.com/catalogs-idx",
                    }
                ],
            },
            "https://api.example.com/catalogs-idx": {
                "catalogs": [{"id": "cat1"}],
            },
            "https://api.example.com/catalogs-idx/cat1": {
                "stac_version": "1.0.0",
                "type": "Catalog",
                "id": "cat1",
                "links": [
                    {
                        "rel": "collections",
                        "href": "https://api.example.com/cat1-collections",
                    }
                ],
            },
            "https://api.example.com/cat1-collections": {
                "collections": [{"id": "c1"}],
            },
            "https://api.example.com/cat1-collections/c1": {
                "stac_version": "1.0.0",
                "type": "Collection",
                "id": "c1",
                "license": "MIT",
                "extent": {
                    "spatial": {"bbox": [[-180, -90, 180, 90]]},
                    "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
                },
                "links": [{"rel": "items", "href": items_url}],
            },
            items_url: {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "stac_version": "1.0.0",
                        "id": "i1",
                        "geometry": None,
                        "properties": {"datetime": "2023-01-01T00:00:00Z"},
                        "links": [],
                        "assets": {},
                    }
                ],
            },
        }

        fetched = []

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            fetched.append(url)
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )
        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=True, max_depth=4)
        fv.run_api()

        assert items_url in fetched

    def test_prefetch_dedupes_collection_members_across_pages(self, monkeypatch):
        """A collection repeated on paginated index pages is fetched and
        validated only once."""
        coll_url = "https://api.example.com/collections/c1"
        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "links": [
                    {
                        "rel": "data",
                        "href": "https://api.example.com/collections",
                    }
                ],
            },
            "https://api.example.com/collections": {
                "collections": [{"id": "c1"}, {"id": "c1"}],
                "links": [
                    {
                        "rel": "next",
                        "href": "https://api.example.com/collections?page=2",
                    }
                ],
            },
            "https://api.example.com/collections?page=2": {
                "collections": [{"id": "c1"}, {"id": "c2"}],
            },
            coll_url: {
                "stac_version": "1.0.0",
                "type": "Collection",
                "id": "c1",
                "license": "MIT",
                "extent": {
                    "spatial": {"bbox": [[-180, -90, 180, 90]]},
                    "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
                },
                "links": [],
            },
            "https://api.example.com/collections/c2": {
                "stac_version": "1.0.0",
                "type": "Collection",
                "id": "c2",
                "license": "MIT",
                "extent": {
                    "spatial": {"bbox": [[-180, -90, 180, 90]]},
                    "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
                },
                "links": [],
            },
        }

        fetched = []

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            fetched.append(url)
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )
        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=True)
        fv.run_api()

        # c1 is listed twice on page 1 and again on page 2
        assert fetched.count(coll_url) == 1
        assert len([m for m in fv.message if m["path"] == coll_url]) == 1
        assert any(m["path"].endswith("/c2") for m in fv.message)

    def test_prefetch_skips_items_pages_under_limit(self, monkeypatch):
        """Under a result limit, items pages are not eagerly prefetched for
        every member; they load on demand only for collections that are
        actually validated."""
        items_c1 = "https://api.example.com/collections/c1/items"
        items_c2 = "https://api.example.com/collections/c2/items"
        items_c3 = "https://api.example.com/collections/c3/items"

        def _collection(cid, items_url):
            return {
                "stac_version": "1.0.0",
                "type": "Collection",
                "id": cid,
                "license": "MIT",
                "extent": {
                    "spatial": {"bbox": [[-180, -90, 180, 90]]},
                    "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
                },
                "links": [{"rel": "items", "href": items_url}],
            }

        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "links": [
                    {"rel": "data", "href": "https://api.example.com/collections"}
                ],
            },
            "https://api.example.com/collections": {
                "collections": [{"id": "c1"}, {"id": "c2"}, {"id": "c3"}],
            },
            "https://api.example.com/collections/c1": _collection("c1", items_c1),
            "https://api.example.com/collections/c2": _collection("c2", items_c2),
            "https://api.example.com/collections/c3": _collection("c3", items_c3),
            items_c1: {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "stac_version": "1.0.0",
                        "id": "i1",
                        "geometry": None,
                        "properties": {"datetime": "2023-01-01T00:00:00Z"},
                        "links": [],
                        "assets": {},
                    }
                ],
            },
            # items_c2/items_c3 deliberately absent: fetching them raises
        }

        fetched = []

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            fetched.append(url)
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )
        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        # limit=3: root + c1 + one item consume the results; c2/c3 never
        # validate so their items pages must never be requested
        fv = FastValidator("https://api.example.com", quiet=True, limit=3)
        fv.run_api()

        assert items_c1 in fetched
        assert items_c2 not in fetched
        assert items_c3 not in fetched
        assert len(fv.message) == 3

    def test_api_mode_catalogs_rel_traversal(self, monkeypatch):
        """rel=catalogs index endpoints are traversed like rel=data."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "links": [
                    {"rel": "catalogs", "href": "https://api.example.com/catalogs"}
                ],
            },
            "https://api.example.com/catalogs": {
                "catalogs": [{"id": "sub-catalog"}],
            },
            "https://api.example.com/catalogs/sub-catalog": {
                "stac_version": "1.0.0",
                "type": "Catalog",
                "id": "sub-catalog",
                "description": "sub catalog",
                "links": [
                    {
                        "rel": "collections",
                        "href": "https://api.example.com/catalogs/sub-catalog/collections",
                    }
                ],
            },
            "https://api.example.com/catalogs/sub-catalog/collections": {
                "collections": [{"id": "demo-collection"}],
            },
            "https://api.example.com/catalogs/sub-catalog/collections/demo-collection": {
                "stac_version": "1.0.0",
                "type": "Collection",
                "id": "demo-collection",
                "license": "MIT",
                "extent": {
                    "spatial": {"bbox": [[-180, -90, 180, 90]]},
                    "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
                },
                "links": [],
            },
        }

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=True)
        fv.run_api()

        assert fv.valid is True
        ids = [r["id"] for r in fv.message]
        assert ids == ["api-root", "sub-catalog", "demo-collection"]

    def test_api_mode_catalogs_index_pagination(self, monkeypatch):
        """Paginated rel=catalogs indexes follow next pages and validate
        catalogs members from every page."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "links": [
                    {"rel": "catalogs", "href": "https://api.example.com/catalogs"}
                ],
            },
            "https://api.example.com/catalogs": {
                "catalogs": [{"id": "cat1"}],
                "links": [
                    {
                        "rel": "next",
                        "href": "https://api.example.com/catalogs?page=2",
                    }
                ],
            },
            "https://api.example.com/catalogs?page=2": {
                "catalogs": [{"id": "cat2"}],
            },
            "https://api.example.com/catalogs/cat1": {
                "stac_version": "1.0.0",
                "type": "Catalog",
                "id": "cat1",
                "description": "catalog one",
                "links": [],
            },
            "https://api.example.com/catalogs/cat2": {
                "stac_version": "1.0.0",
                "type": "Catalog",
                "id": "cat2",
                "description": "catalog two",
                "links": [],
            },
        }

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=True)
        fv.run_api()

        assert fv.valid is True
        ids = [r["id"] for r in fv.message]
        assert ids == ["api-root", "cat1", "cat2"]

    def test_api_mode_dedups_differently_spelled_urls(self, monkeypatch):
        """A resource reachable under differently-spelled URLs is fetched
        and validated only once."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        c1_doc = {
            "stac_version": "1.0.0",
            "type": "Collection",
            "id": "c1",
            "license": "MIT",
            "extent": {
                "spatial": {"bbox": [[-180, -90, 180, 90]]},
                "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
            },
            "links": [],
        }
        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "links": [
                    {
                        "rel": "data",
                        "href": "https://api.example.com/collections",
                    },
                    # The same collection reachable under other spellings
                    {
                        "rel": "child",
                        "href": "https://api.example.com/collections/../collections/c1",
                    },
                    {
                        "rel": "child",
                        "href": "https://api.example.com/collections/c1/",
                    },
                ],
            },
            "https://api.example.com/collections": {
                "collections": [{"id": "c1"}],
            },
            "https://api.example.com/collections/c1": c1_doc,
            # Pre-canonicalization spellings would resolve to the same doc
            "https://api.example.com/collections/../collections/c1": c1_doc,
            "https://api.example.com/collections/c1/": c1_doc,
        }

        fetched = []

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            fetched.append(url)
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=True)
        fv.run_api()

        assert fv.valid is True
        assert [r["id"] for r in fv.message] == ["api-root", "c1"]
        assert fetched.count("https://api.example.com/collections/c1") == 1
        assert "https://api.example.com/collections/../collections/c1" not in fetched
        assert "https://api.example.com/collections/c1/" not in fetched

    def test_quiet_suppresses_summary(self, monkeypatch, capsys):
        """quiet=True silences the validation summary output."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        root = {
            "stac_version": "1.0.0",
            "type": "Catalog",
            "id": "r",
            "description": "r",
            "links": [],
        }

        class _Response:
            def raise_for_status(self):
                return None

            def json(self):
                return root

        monkeypatch.setattr(
            "stac_validator.fast_validator.HTTP_SESSION.get",
            lambda url, timeout=15: _Response(),
        )

        fv = FastValidator("https://api.example.com", quiet=True)
        fv.run_api()

        assert "VALIDATION SUMMARY" not in capsys.readouterr().out

    def test_run_recursive_warns_on_api_root(self, monkeypatch, capsys):
        """run_recursive warns when the root looks like a STAC API."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        root = {
            "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
            "id": "api-root",
            "type": "Catalog",
            "links": [],
        }

        class _Response:
            def raise_for_status(self):
                return None

            def json(self):
                return root

        monkeypatch.setattr(
            "stac_validator.fast_validator.HTTP_SESSION.get",
            lambda url, timeout=15: _Response(),
        )

        fv = FastValidator("https://api.example.com", quiet=False)
        fv.run_recursive()

        assert "STAC API detected" in capsys.readouterr().out

    def test_max_pages_truncates_pagination(self, monkeypatch):
        """max_pages caps pages per endpoint and records the truncation."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        def _item(item_id):
            return {
                "stac_version": "1.0.0",
                "type": "Feature",
                "id": item_id,
                "geometry": None,
                "properties": {"datetime": "2023-01-01T00:00:00Z"},
                "links": [],
                "assets": {},
            }

        base = "https://api.example.com/collections/demo/items"
        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "links": [
                    {"rel": "items", "href": base},
                ],
            },
            base: {
                "type": "FeatureCollection",
                "features": [_item("item-1")],
                "links": [{"rel": "next", "href": f"{base}?cursor=2"}],
            },
            f"{base}?cursor=2": {
                "type": "FeatureCollection",
                "features": [_item("item-2")],
                "links": [],
            },
        }

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=True, max_pages=1)
        fv.run_api()

        item_ids = [r["id"] for r in fv.message if r.get("stac_type") == "item"]
        # Page 2 is never fetched: only the first page's item was validated
        assert item_ids == ["item-1"]
        assert fv.truncated_endpoints == [(base, 1)]

    def test_max_pages_truncation_warns(self, monkeypatch, capsys):
        """run_api prints a warning listing endpoints cut short by the cap."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        base = "https://api.example.com/collections/demo/items"
        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "links": [{"rel": "items", "href": base}],
            },
            base: {
                "type": "FeatureCollection",
                "features": [
                    {
                        "stac_version": "1.0.0",
                        "type": "Feature",
                        "id": "item-1",
                        "geometry": None,
                        "properties": {"datetime": "2023-01-01T00:00:00Z"},
                        "links": [],
                        "assets": {},
                    }
                ],
                "links": [{"rel": "next", "href": f"{base}?cursor=2"}],
            },
        }

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=False, max_pages=1)
        fv.run_api()

        out = capsys.readouterr().out
        assert "Pagination cap" in out
        assert base in out

    def test_max_pages_zero_follows_all_pages(self, monkeypatch):
        """max_pages=0 disables the page cap."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        def _item(item_id):
            return {
                "stac_version": "1.0.0",
                "type": "Feature",
                "id": item_id,
                "geometry": None,
                "properties": {"datetime": "2023-01-01T00:00:00Z"},
                "links": [],
                "assets": {},
            }

        base = "https://api.example.com/collections/demo/items"
        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "links": [
                    {"rel": "items", "href": base},
                ],
            },
            base: {
                "type": "FeatureCollection",
                "features": [_item("item-1")],
                "links": [{"rel": "next", "href": f"{base}?cursor=2"}],
            },
            f"{base}?cursor=2": {
                "type": "FeatureCollection",
                "features": [_item("item-2")],
                "links": [{"rel": "next", "href": f"{base}?cursor=3"}],
            },
            f"{base}?cursor=3": {
                "type": "FeatureCollection",
                "features": [_item("item-3")],
                "links": [],
            },
        }

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=True, max_pages=0)
        fv.run_api()

        item_ids = sorted(r["id"] for r in fv.message if r.get("stac_type") == "item")
        assert item_ids == ["item-1", "item-2", "item-3"]
        assert fv.truncated_endpoints == []

    def test_keep_documents_indexes_root_by_result_path(self, tmp_path, monkeypatch):
        """run_recursive keys loaded_objects by the abspath used in results."""

        def _ok_validator(data):
            return None

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_ok_validator, True),
        )

        catalog = {
            "stac_version": "1.0.0",
            "type": "Catalog",
            "id": "root",
            "description": "root catalog",
            "links": [],
        }
        catalog_file = tmp_path / "catalog.json"
        catalog_file.write_text(json.dumps(catalog))

        fv = FastValidator(str(catalog_file), quiet=True, keep_documents=True)
        fv.run_recursive()

        result_path = fv.message[0]["path"]
        assert os.path.isabs(result_path)
        assert fv.loaded_objects[result_path] == catalog

    def test_quiet_suppresses_root_load_error(self, monkeypatch, capsys):
        """quiet=True suppresses the printed root-load error; the result stays."""

        def _fail_get(url, timeout=15):
            raise RuntimeError("connection refused")

        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fail_get)

        fv = FastValidator("https://api.example.com", quiet=True)
        fv.run_api()

        assert fv.valid is False
        assert fv.message[0]["error_message"].startswith("Failed to load")
        assert capsys.readouterr().out == ""

    def test_negative_max_pages_rejected(self):
        """Negative max_pages raises instead of silently truncating."""
        with pytest.raises(ValueError, match="max_pages"):
            FastValidator("https://api.example.com", max_pages=-1)


class TestFastValidatorRefResolutionFallback:
    """Test fallback behavior when fast path hits ref-resolution errors."""

    def test_run_falls_back_to_jsonschema_on_ref_error(self, valid_item, monkeypatch):
        """run() should retry via jsonschema resolver on ref-resolution errors."""

        class FakeRefError(Exception):
            pass

        def _raise_ref_error(_data):
            raise FakeRefError("Unresolvable JSON pointer: 'definitions/link'")

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_raise_ref_error, True),
        )

        fallback_calls = []

        def _fallback(schema_path, content):
            fallback_calls.append(schema_path)

        monkeypatch.setattr(
            "stac_validator.fast_validator.validate_with_ref_resolver",
            _fallback,
        )

        fv = FastValidator(valid_item, quiet=True)
        fv.run()

        assert fv.valid is True
        assert len(fallback_calls) == 1
        assert "item-spec/json-schema/item.json" in fallback_calls[0]
        assert fv.message[0]["invalid_objects"] == 0

    def test_run_api_falls_back_to_jsonschema_on_ref_error(self, monkeypatch):
        """run_api() should retry via jsonschema resolver on ref-resolution errors."""

        class FakeRefError(Exception):
            pass

        def _raise_ref_error(_data):
            raise FakeRefError("Unresolvable JSON pointer: 'definitions/asset'")

        monkeypatch.setattr(
            "stac_validator.fast_validator.get_validator",
            lambda *args, **kwargs: (_raise_ref_error, True),
        )

        fallback_calls = []

        def _fallback(schema_path, content):
            fallback_calls.append(schema_path)

        monkeypatch.setattr(
            "stac_validator.fast_validator.validate_with_ref_resolver",
            _fallback,
        )

        payloads = {
            "https://api.example.com": {
                "conformsTo": ["https://api.stacspec.org/v1.0.0/core"],
                "id": "api-root",
                "type": "Catalog",
                "description": "api root",
                "links": [
                    {"rel": "data", "href": "https://api.example.com/collections"}
                ],
            },
            "https://api.example.com/collections": {
                "collections": [{"id": "demo-collection"}],
            },
            "https://api.example.com/collections/demo-collection": {
                "stac_version": "1.0.0",
                "type": "Collection",
                "id": "demo-collection",
                "description": "demo",
                "license": "MIT",
                "extent": {
                    "spatial": {"bbox": [[-180, -90, 180, 90]]},
                    "temporal": {"interval": [["2023-01-01T00:00:00Z", None]]},
                },
                "links": [],
            },
        }

        class _Response:
            def __init__(self, data):
                self._data = data

            def raise_for_status(self):
                return None

            def json(self):
                return self._data

        def _fake_get(url, timeout=15):
            if url not in payloads:
                raise RuntimeError(f"Unexpected URL: {url}")
            return _Response(payloads[url])

        monkeypatch.setattr("stac_validator.fast_validator.HTTP_SESSION.get", _fake_get)

        fv = FastValidator("https://api.example.com", quiet=True)
        fv.run_api()

        assert fv.valid is True
        assert len(fallback_calls) == 1
        assert "collection-spec/json-schema/collection.json" in fallback_calls[0]


class TestFastValidatorDetection:
    """Test STAC type detection."""

    def test_detects_item(self, valid_item, capsys):
        """Test detection of STAC Item."""
        fv = FastValidator(valid_item, quiet=False)
        fv.run()
        captured = capsys.readouterr()
        assert "Item" in captured.out or "Feature" in captured.out

    def test_detects_collection(self, valid_collection, capsys):
        """Test detection of STAC Collection."""
        fv = FastValidator(valid_collection, quiet=False)
        fv.run()
        captured = capsys.readouterr()
        assert "Collection" in captured.out

    def test_detects_catalog(self, valid_catalog, capsys):
        """Test detection of STAC Catalog."""
        fv = FastValidator(valid_catalog, quiet=False)
        fv.run()
        captured = capsys.readouterr()
        assert "Catalog" in captured.out

    def test_detects_feature_collection(self, valid_feature_collection, capsys):
        """Test detection of FeatureCollection."""
        fv = FastValidator(valid_feature_collection, quiet=False)
        fv.run()
        captured = capsys.readouterr()
        assert "FeatureCollection" in captured.out


class TestFastValidatorErrorHandling:
    """Test error handling."""

    def test_file_not_found(self):
        """Test handling of missing file."""
        fv = FastValidator("/nonexistent/path/file.json", quiet=True)
        fv.run()
        assert fv.valid is False

    def test_invalid_json(self, tmp_path):
        """Test handling of invalid JSON."""
        bad_json_path = tmp_path / "bad.json"
        bad_json_path.write_text("{ invalid json }")

        fv = FastValidator(str(bad_json_path), quiet=True)
        fv.run()
        assert fv.valid is False

    def test_unknown_type(self, tmp_path):
        """Test handling of unknown STAC type."""
        unknown_path = tmp_path / "unknown.json"
        unknown_data = {"type": "UnknownType", "id": "test"}
        unknown_path.write_text(json.dumps(unknown_data))

        fv = FastValidator(str(unknown_path), quiet=True)
        fv.run()
        assert fv.valid is False


class TestFastValidatorPerformance:
    """Test performance characteristics."""

    def test_caching_works(self, valid_feature_collection):
        """Test that validator caching works."""
        fv = FastValidator(valid_feature_collection, quiet=True)
        fv.run()
        assert fv.valid is True

    def test_large_feature_collection(self, tmp_path):
        """Test validation of a large FeatureCollection."""
        fc_path = tmp_path / "large_fc.json"
        fc_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "stac_version": "1.0.0",
                    "type": "Feature",
                    "id": f"item-{i}",
                    "geometry": None,
                    "properties": {"datetime": "2023-01-01T00:00:00Z"},
                    "links": [{"rel": "self", "href": "http://example.com"}],
                    "assets": {},
                }
                for i in range(100)
            ],
        }
        fc_path.write_text(json.dumps(fc_data))

        fv = FastValidator(str(fc_path), quiet=True)
        fv.run()
        assert fv.valid is True

    def test_message_attribute_structure(self, valid_item):
        """Test that the message attribute has the correct structure."""
        fv = FastValidator(valid_item, quiet=True)
        fv.run()

        # Verify message is a list with one dict
        assert isinstance(fv.message, list)
        assert len(fv.message) == 1

        msg = fv.message[0]

        # Verify required fields exist
        assert "path" in msg
        assert "valid_stac" in msg
        assert "stac_versions" in msg
        assert "schemas_checked" in msg
        assert "total_objects" in msg
        assert "valid_objects" in msg
        assert "invalid_objects" in msg
        assert "setup_time_ms" in msg
        assert "execution_time_ms" in msg
        assert "errors" in msg

        # Verify field types
        assert isinstance(msg["path"], str)
        assert isinstance(msg["valid_stac"], bool)
        assert isinstance(msg["stac_versions"], list)
        assert isinstance(msg["schemas_checked"], list)
        assert isinstance(msg["total_objects"], int)
        assert isinstance(msg["valid_objects"], int)
        assert isinstance(msg["invalid_objects"], int)
        assert isinstance(msg["setup_time_ms"], float)
        assert isinstance(msg["execution_time_ms"], float)
        assert isinstance(msg["errors"], list)

    def test_message_attribute_valid_items(self, valid_feature_collection):
        """Test message attribute for valid items."""
        fv = FastValidator(valid_feature_collection, quiet=True)
        fv.run()

        msg = fv.message[0]

        # For valid items
        assert msg["valid_stac"] is True
        assert msg["total_objects"] == 5
        assert msg["valid_objects"] == 5
        assert msg["invalid_objects"] == 0
        assert len(msg["errors"]) == 0

        # Verify versions and schemas are tracked
        assert len(msg["stac_versions"]) > 0
        assert len(msg["schemas_checked"]) > 0
        assert "1.0.0" in msg["stac_versions"]

    def test_message_attribute_invalid_items(self, tmp_path):
        """Test message attribute for invalid items."""
        fc_path = tmp_path / "invalid_fc.json"
        fc_data = {
            "type": "FeatureCollection",
            "features": [
                {
                    "stac_version": "1.0.0",
                    "type": "Feature",
                    "id": "item-1",
                    "geometry": None,
                    "properties": {"datetime": "2023-01-01T00:00:00Z"},
                    "links": [{"rel": "self", "href": "http://example.com"}],
                    "assets": {},
                },
                {
                    "stac_version": "1.0.0",
                    "type": "Feature",
                    "id": "item-2",
                    "geometry": None,
                    # Missing required 'properties' field
                    "links": [{"rel": "self", "href": "http://example.com"}],
                    "assets": {},
                },
            ],
        }
        fc_path.write_text(json.dumps(fc_data))

        fv = FastValidator(str(fc_path), quiet=True)
        fv.run()

        msg = fv.message[0]

        # For mixed valid/invalid items
        assert msg["valid_stac"] is False
        assert msg["total_objects"] == 2
        assert msg["valid_objects"] == 1
        assert msg["invalid_objects"] == 1
        assert len(msg["errors"]) > 0

        # Verify error structure
        for error in msg["errors"]:
            assert "error_message" in error
            assert "affected_items" in error
            assert "count" in error
            assert isinstance(error["affected_items"], list)
            assert error["count"] == len(error["affected_items"])


def _item_schema_uri(version):
    return f"https://schemas.stacspec.org/v{version}/item-spec/json-schema/item.json"


def _prefill_item_schema(version):
    fast_validator.SCHEMA_CACHE[_item_schema_uri(version)] = {
        "type": "object",
        "required": ["id"],
    }


def _run_in_threads(targets):
    """Run each callable in its own thread; return its result or the exception it raised."""
    results = [None] * len(targets)

    def run(index, target):
        try:
            results[index] = target()
        except Exception as e:
            results[index] = e

    # Daemon threads and one shared deadline: a stuck waiter fails the test, not the run.
    threads = [
        threading.Thread(target=run, args=(index, target), daemon=True)
        for index, target in enumerate(targets)
    ]
    for thread in threads:
        thread.start()
    deadline = time.monotonic() + 30
    for thread in threads:
        thread.join(max(0, deadline - time.monotonic()))
    assert not any(thread.is_alive() for thread in threads), "worker threads hung"
    return results


@pytest.fixture
def fake_version():
    """Return unique fake STAC versions and drop their cached schemas and validators."""
    versions = []

    def make(name):
        version = f"0.0.0-singleflight-{name}"
        versions.append(version)
        return version

    yield make
    for version in versions:
        fast_validator.SCHEMA_CACHE.pop(_item_schema_uri(version), None)
        fast_validator.VALIDATOR_CACHE.pop(("Item", version, ()), None)


class TestGetValidatorConcurrency:
    """Concurrent cold get_validator calls build each cache key once."""

    def test_get_validator_compiles_once_under_concurrency(
        self, fake_version, monkeypatch
    ):
        version = fake_version("same-key")
        _prefill_item_schema(version)
        compile_calls = []
        original_compile = fast_validator.compile_unrolled_schema

        def counting_compile(schema, quiet=False):
            compile_calls.append(schema)
            time.sleep(0.05)  # widen the race window
            return original_compile(schema, quiet=quiet)

        monkeypatch.setattr(fast_validator, "compile_unrolled_schema", counting_compile)
        start = threading.Barrier(20)

        def call():
            start.wait(timeout=5)
            validator, was_cached = fast_validator.get_validator(
                "Item", version, [], quiet=True
            )
            validator({"id": "x"})
            return validator, was_cached

        results = _run_in_threads([call] * 20)

        assert [r for r in results if isinstance(r, Exception)] == []
        assert len(compile_calls) == 1
        assert len({id(validator) for validator, _ in results}) == 1
        assert [was_cached for _, was_cached in results].count(False) == 1
        with pytest.raises(FastSTACMultiValidationError):
            results[0][0]({})

    def test_get_validator_compiles_different_keys_in_parallel(
        self, fake_version, monkeypatch
    ):
        versions = [fake_version("parallel-a"), fake_version("parallel-b")]
        for version in versions:
            _prefill_item_schema(version)
        both_compiling = threading.Event()
        rendezvous = threading.Barrier(2, action=both_compiling.set)
        original_compile = fast_validator.compile_unrolled_schema

        def compile_together(schema, quiet=False):
            # Tier 1's fallback swallows a BrokenBarrierError, so the event is the check.
            rendezvous.wait(timeout=5)
            return original_compile(schema, quiet=quiet)

        monkeypatch.setattr(fast_validator, "compile_unrolled_schema", compile_together)

        results = _run_in_threads(
            [
                lambda v=version: fast_validator.get_validator(
                    "Item", v, [], quiet=True
                )
                for version in versions
            ]
        )

        assert [r for r in results if isinstance(r, Exception)] == []
        assert both_compiling.is_set()

    def test_get_validator_shares_build_failure_then_retries(
        self, fake_version, monkeypatch
    ):
        version = fake_version("failure")
        workers = 20
        arrived = threading.Condition()
        arrivals = 0
        fetch_calls = []

        def arrive():
            nonlocal arrivals
            with arrived:
                arrivals += 1
                arrived.notify_all()

        class CountingFuture(Future):
            def result(self, timeout=None):
                arrive()
                return super().result(timeout=10)

        def failing_fetch(uri, quiet=False):
            fetch_calls.append(uri)
            arrive()
            # Fail only once every worker is either fetching or waiting on the build.
            with arrived:
                arrived.wait_for(lambda: arrivals == workers, timeout=5)
            raise RuntimeError("schema fetch failed")

        # get_validator creates in-flight builds from this module-level name.
        monkeypatch.setattr(fast_validator, "Future", CountingFuture)
        monkeypatch.setattr(fast_validator, "fetch_schema", failing_fetch)
        start = threading.Barrier(workers)

        def call():
            start.wait(timeout=5)
            return fast_validator.get_validator("Item", version, [], quiet=True)

        results = _run_in_threads([call] * workers)

        assert all(
            isinstance(r, RuntimeError) and str(r) == "schema fetch failed"
            for r in results
        ), results
        assert len(fetch_calls) == 1
        assert fast_validator.VALIDATOR_BUILDS == {}

        monkeypatch.undo()
        _prefill_item_schema(version)
        validator, was_cached = fast_validator.get_validator(
            "Item", version, [], quiet=True
        )
        assert was_cached is False
        validator({"id": "x"})

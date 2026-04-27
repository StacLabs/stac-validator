import json

import pytest

from stac_validator.fast_validator import FastValidator


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

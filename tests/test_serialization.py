"""
Tests for serialization (to_dict) and round-trip (from_dict -> to_dict)
behavior across all models.
"""

import json
from decimal import Decimal as PyDecimal
from pathlib import Path

from l9format import (
    Certificate,
    DatasetSummary,
    GeoLocation,
    GeoPoint,
    L9Event,
    L9HttpEvent,
    L9LeakEvent,
    L9ServiceEvent,
    Network,
    Software,
    SoftwareModule,
)
from l9format.l9format import Decimal as DecimalField

TESTS_DIR = Path(__file__).parent


class TestDecimalField:
    """Test the custom Decimal field serialize/deserialize paths."""

    def test_serialize_without_resolution(self) -> None:
        field = DecimalField()
        assert field.serialize(PyDecimal("1.5")) == "1.5"

    def test_serialize_with_resolution(self) -> None:
        field = DecimalField(resolution=6)
        assert field.serialize(PyDecimal("1.5")) == "1.500000"

    def test_serialize_rounds_to_resolution(self) -> None:
        field = DecimalField(resolution=2)
        assert field.serialize(PyDecimal("1.555")) == "1.56"

    def test_deserialize_without_resolution(self) -> None:
        field = DecimalField()
        result = field.deserialize("1.5")
        assert result == PyDecimal("1.5")

    def test_deserialize_with_resolution(self) -> None:
        field = DecimalField(resolution=6)
        result = field.deserialize("1.5")
        assert result == PyDecimal("1.500000")

    def test_deserialize_from_int(self) -> None:
        field = DecimalField()
        result = field.deserialize(42)
        assert result == PyDecimal("42")

    def test_deserialize_from_float(self) -> None:
        field = DecimalField()
        result = field.deserialize(1.5)
        assert result == PyDecimal("1.5")

    def test_round_trip_with_resolution(self) -> None:
        field = DecimalField(resolution=6)
        original = "1.500000"
        deserialized = field.deserialize(original)
        serialized = field.serialize(deserialized)
        assert serialized == original

    def test_round_trip_without_resolution(self) -> None:
        field = DecimalField()
        original = "3.14159"
        deserialized = field.deserialize(original)
        serialized = field.serialize(deserialized)
        assert serialized == original


class TestGeoPointRoundTrip:
    """Test GeoPoint serialization and round-trip."""

    def test_to_dict(self) -> None:
        gp = GeoPoint.from_dict({"lat": "1.5", "lon": "2.5"})
        d = gp.to_dict()
        assert d["lat"] == "1.5"
        assert d["lon"] == "2.5"

    def test_round_trip(self) -> None:
        data = {"lat": "48.8566", "lon": "2.3522"}
        assert GeoPoint.from_dict(data).to_dict() == data

    def test_round_trip_zero(self) -> None:
        data = {"lat": "0", "lon": "0"}
        assert GeoPoint.from_dict(data).to_dict() == data

    def test_round_trip_negative(self) -> None:
        data = {"lat": "-33.8688", "lon": "-151.2093"}
        assert GeoPoint.from_dict(data).to_dict() == data


class TestNetworkRoundTrip:
    """Test Network serialization and round-trip."""

    def test_to_dict(self) -> None:
        net = Network.from_dict(
            {
                "organization_name": "Test Org",
                "asn": 12345,
                "network": "1.0.0.0/8",
            }
        )
        d = net.to_dict()
        assert d["organization_name"] == "Test Org"
        assert d["asn"] == 12345
        assert d["network"] == "1.0.0.0/8"

    def test_round_trip(self) -> None:
        data = {
            "organization_name": "Test Org",
            "asn": 12345,
            "network": "1.0.0.0/8",
        }
        assert Network.from_dict(data).to_dict() == data


class TestCertificateRoundTrip:
    """Test Certificate serialization and round-trip."""

    def test_to_dict(self) -> None:
        data = {
            "cn": "example.com",
            "domain": ["a.example.com", "b.example.com"],
            "fingerprint": "abc123",
            "key_algo": "RSA",
            "key_size": 2048,
            "issuer_name": "Test CA",
            "not_before": "2024-01-01T00:00:00+00:00",
            "not_after": "2024-12-31T23:59:59+00:00",
            "valid": True,
        }
        cert = Certificate.from_dict(data)
        d = cert.to_dict()
        assert d["cn"] == "example.com"
        assert d["domain"] == ["a.example.com", "b.example.com"]
        assert d["key_size"] == 2048
        assert d["valid"] is True

    def test_round_trip(self) -> None:
        data = {
            "cn": "example.com",
            "domain": ["a.example.com"],
            "fingerprint": "abc123",
            "key_algo": "RSA",
            "key_size": 2048,
            "issuer_name": "Test CA",
            "not_before": "2024-01-01T00:00:00+00:00",
            "not_after": "2024-12-31T23:59:59+00:00",
            "valid": True,
        }
        assert Certificate.from_dict(data).to_dict() == data

    def test_round_trip_null_domain_omitted(self) -> None:
        """serde omits None-valued optional fields from to_dict()."""
        data = {
            "cn": "example.com",
            "domain": None,
            "fingerprint": "abc123",
            "key_algo": "RSA",
            "key_size": 2048,
            "issuer_name": "Test CA",
            "not_before": "2024-01-01T00:00:00+00:00",
            "not_after": "2024-12-31T23:59:59+00:00",
            "valid": True,
        }
        result = Certificate.from_dict(data).to_dict()
        assert "domain" not in result


class TestHttpEventRoundTrip:
    """Test L9HttpEvent serialization and round-trip."""

    def test_round_trip(self) -> None:
        data = {
            "root": "/",
            "url": "/index.html",
            "status": 200,
            "length": 1024,
            "header": {"Content-Type": "text/html"},
            "title": "Welcome",
            "favicon_hash": "abc123",
        }
        assert L9HttpEvent.from_dict(data).to_dict() == data

    def test_round_trip_null_header_omitted(self) -> None:
        """serde omits None-valued optional fields from to_dict()."""
        data = {
            "root": "/",
            "url": "/",
            "status": 0,
            "length": 0,
            "header": None,
            "title": "",
            "favicon_hash": "",
        }
        result = L9HttpEvent.from_dict(data).to_dict()
        assert "header" not in result


class TestSoftwareRoundTrip:
    """Test Software and SoftwareModule serialization."""

    def test_software_module_round_trip(self) -> None:
        data = {"name": "PHP", "version": "8.2.0", "fingerprint": "php-8-2-0"}
        assert SoftwareModule.from_dict(data).to_dict() == data

    def test_software_with_modules_round_trip(self) -> None:
        data = {
            "name": "Apache",
            "version": "2.4.52",
            "os": "Ubuntu",
            "modules": [
                {"name": "PHP", "version": "8.2.0", "fingerprint": "php-8-2-0"}
            ],
            "fingerprint": "apache-2-4-52",
        }
        assert Software.from_dict(data).to_dict() == data

    def test_software_null_modules_omitted(self) -> None:
        """serde omits None-valued optional fields from to_dict()."""
        data = {
            "name": "nginx",
            "version": "1.24.0",
            "os": "",
            "modules": None,
            "fingerprint": "nginx-1-24-0",
        }
        result = Software.from_dict(data).to_dict()
        assert "modules" not in result
        assert result["name"] == "nginx"


class TestLeakEventRoundTrip:
    """Test L9LeakEvent and DatasetSummary serialization."""

    def test_dataset_summary_round_trip(self) -> None:
        data = {
            "rows": 100,
            "files": 5,
            "size": 65536,
            "collections": 3,
            "infected": False,
            "ransom_notes": ["Pay up"],
        }
        assert DatasetSummary.from_dict(data).to_dict() == data

    def test_dataset_summary_null_ransom_notes_omitted(self) -> None:
        """serde omits None-valued optional fields from to_dict()."""
        data = {
            "rows": 100,
            "files": 5,
            "size": 65536,
            "collections": 3,
            "infected": False,
            "ransom_notes": None,
        }
        result = DatasetSummary.from_dict(data).to_dict()
        assert "ransom_notes" not in result

    def test_leak_event_round_trip(self) -> None:
        data = {
            "stage": "open",
            "type": "database",
            "severity": "high",
            "dataset": {
                "rows": 1000,
                "files": 0,
                "size": 1048576,
                "collections": 10,
                "infected": True,
                "ransom_notes": ["Pay up"],
            },
        }
        assert L9LeakEvent.from_dict(data).to_dict() == data


class TestGeoLocationRoundTrip:
    """Test GeoLocation serialization with nested GeoPoint."""

    def test_round_trip_with_location(self) -> None:
        data = {
            "continent_name": "Europe",
            "region_iso_code": "FR-IDF",
            "city_name": "Paris",
            "country_iso_code": "FR",
            "country_name": "France",
            "region_name": "Ile-de-France",
            "location": {"lat": "48.8566", "lon": "2.3522"},
        }
        assert GeoLocation.from_dict(data).to_dict() == data

    def test_round_trip_all_null_omitted(self) -> None:
        """serde omits None-valued optional fields from to_dict()."""
        data = {
            "continent_name": None,
            "region_iso_code": None,
            "city_name": None,
            "country_iso_code": None,
            "country_name": None,
            "region_name": None,
            "location": None,
        }
        result = GeoLocation.from_dict(data).to_dict()
        assert len(result) == 0


class TestServiceEventRoundTrip:
    """Test L9ServiceEvent serialization."""

    def test_round_trip(self) -> None:
        data = {
            "credentials": {
                "noauth": True,
                "username": "",
                "password": "",
                "key": "",
                "raw": "dGVzdA==",
            },
            "software": {
                "name": "Apache",
                "version": "2.4.52",
                "os": "Ubuntu",
                "modules": [
                    {
                        "name": "PHP",
                        "version": "8.2.0",
                        "fingerprint": "php-8-2-0",
                    }
                ],
                "fingerprint": "apache-2-4-52",
            },
        }
        assert L9ServiceEvent.from_dict(data).to_dict() == data

    def test_round_trip_null_optionals_omitted(self) -> None:
        """serde omits None-valued optional fields from to_dict()."""
        data = {
            "credentials": {
                "noauth": False,
                "username": "",
                "password": "",
                "key": "",
                "raw": None,
            },
            "software": {
                "name": "nginx",
                "version": "1.24.0",
                "os": "",
                "modules": None,
                "fingerprint": "nginx-1-24-0",
            },
        }
        result = L9ServiceEvent.from_dict(data).to_dict()
        assert "raw" not in result["credentials"]
        assert "modules" not in result["software"]


class TestL9EventRoundTrip:
    """Test full L9Event round-trip from reference JSON.

    The reference JSON uses raw types (numeric lat/lon, Z-suffix
    datetimes) that differ from the serialized form (string decimals,
    +00:00 datetimes). A true round-trip asserts idempotency:
    serialize(deserialize(x)) produces a stable output that survives
    another cycle unchanged.
    """

    def test_round_trip_from_reference(self) -> None:
        path = TESTS_DIR / "l9event.json"
        with open(path) as f:
            data = json.load(f)
        first = L9Event.from_dict(data).to_dict()
        second = L9Event.from_dict(first).to_dict()
        assert first == second

    def test_round_trip_ip4scout(self) -> None:
        ip4scout_files = [
            f
            for f in Path.iterdir(TESTS_DIR)
            if Path.is_file(f) and "ip4scout" in f.name
        ]
        for path in ip4scout_files:
            with open(path) as f:
                data = json.load(f)
            first = L9Event.from_dict(data).to_dict()
            second = L9Event.from_dict(first).to_dict()
            assert first == second

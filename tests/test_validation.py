"""
Tests for validation behavior on malformed input, missing fields,
and edge cases.

These tests document and verify the expected behavior when the schema
encounters invalid or edge-case input data.
"""

import json
from pathlib import Path

import pytest
from serde import ValidationError

from l9format import (
    Certificate,
    DatasetSummary,
    GeoLocation,
    GeoPoint,
    L9Event,
    L9HttpEvent,
    Network,
)

TESTS_DIR = Path(__file__).parent


class TestMissingRequiredFields:
    """Test behavior when required fields are missing."""

    def test_geopoint_missing_lat(self) -> None:
        with pytest.raises(ValidationError):
            GeoPoint.from_dict({"lon": "1.0"})

    def test_geopoint_missing_lon(self) -> None:
        with pytest.raises(ValidationError):
            GeoPoint.from_dict({"lat": "1.0"})

    def test_network_missing_organization_name(self) -> None:
        with pytest.raises(ValidationError):
            Network.from_dict({"asn": 12345, "network": "1.0.0.0/8"})

    def test_network_missing_asn(self) -> None:
        with pytest.raises(ValidationError):
            Network.from_dict(
                {"organization_name": "Test Org", "network": "1.0.0.0/8"}
            )

    def test_network_missing_network(self) -> None:
        with pytest.raises(ValidationError):
            Network.from_dict({"organization_name": "Test Org", "asn": 12345})

    def test_certificate_missing_cn(self) -> None:
        with pytest.raises(ValidationError):
            Certificate.from_dict(
                {
                    "fingerprint": "abc123",
                    "key_algo": "RSA",
                    "key_size": 2048,
                    "issuer_name": "Test CA",
                    "not_before": "2024-01-01T00:00:00Z",
                    "not_after": "2024-12-31T23:59:59Z",
                    "valid": True,
                }
            )

    def test_l9event_missing_required_fields(self) -> None:
        with pytest.raises(ValidationError):
            L9Event.from_dict(
                {
                    "event_source": "test",
                    "ip": "127.0.0.1",
                    "port": "80",
                    "host": "example.com",
                    "reverse": "ptr.example.com",
                    "protocol": "http",
                    "summary": "test",
                    "time": "2024-01-01T00:00:00Z",
                }
            )


class TestExtraUnknownFields:
    """Extra fields are silently ignored (default serde behavior)."""

    def test_geopoint_extra_field_ignored(self) -> None:
        gp = GeoPoint.from_dict(
            {"lat": "1.5", "lon": "2.5", "unknown_field": "value"}
        )
        assert gp.lat == 1.5
        assert gp.lon == 2.5
        assert not hasattr(gp, "unknown_field")

    def test_network_extra_field_ignored(self) -> None:
        net = Network.from_dict(
            {
                "organization_name": "Test Org",
                "asn": 12345,
                "network": "1.0.0.0/8",
                "extra_field": "should be ignored",
            }
        )
        assert net.organization_name == "Test Org"
        assert net.asn == 12345
        assert not hasattr(net, "extra_field")


class TestNullValues:
    """Test behavior when null values are provided."""

    def test_geopoint_null_lat(self) -> None:
        with pytest.raises(ValueError, match="invalid decimal"):
            GeoPoint.from_dict({"lat": None, "lon": "1.0"})

    def test_geopoint_null_lon(self) -> None:
        with pytest.raises(ValueError, match="invalid decimal"):
            GeoPoint.from_dict({"lat": "1.0", "lon": None})

    def test_network_null_organization_name(self) -> None:
        with pytest.raises(ValidationError):
            Network.from_dict(
                {
                    "organization_name": None,
                    "asn": 12345,
                    "network": "1.0.0.0/8",
                }
            )

    def test_network_null_asn(self) -> None:
        with pytest.raises(ValidationError):
            Network.from_dict(
                {
                    "organization_name": "Test Org",
                    "asn": None,
                    "network": "1.0.0.0/8",
                }
            )

    def test_optional_field_allows_null(self) -> None:
        geo = GeoLocation.from_dict(
            {
                "continent_name": None,
                "region_iso_code": None,
                "city_name": None,
                "country_iso_code": None,
                "country_name": None,
                "region_name": None,
                "location": None,
            }
        )
        assert geo.continent_name is None
        assert geo.location is None


class TestEmptyStrings:
    """Test behavior when empty strings are provided."""

    def test_geopoint_empty_string_lat(self) -> None:
        with pytest.raises(ValueError, match="invalid decimal"):
            GeoPoint.from_dict({"lat": "", "lon": "1.0"})

    def test_geopoint_empty_string_lon(self) -> None:
        with pytest.raises(ValueError, match="invalid decimal"):
            GeoPoint.from_dict({"lat": "1.0", "lon": ""})

    def test_network_accepts_empty_strings(self) -> None:
        net = Network.from_dict(
            {"organization_name": "", "asn": 12345, "network": ""}
        )
        assert net.organization_name == ""
        assert net.network == ""


class TestBoundaryIntegers:
    """Test behavior with boundary integer values.

    The schema performs no range validation on integers.
    """

    def test_network_zero_asn(self) -> None:
        net = Network.from_dict(
            {"organization_name": "Test", "asn": 0, "network": "1.0.0.0/8"}
        )
        assert net.asn == 0

    def test_network_negative_asn(self) -> None:
        net = Network.from_dict(
            {"organization_name": "Test", "asn": -1, "network": "1.0.0.0/8"}
        )
        assert net.asn == -1

    def test_network_large_asn(self) -> None:
        net = Network.from_dict(
            {
                "organization_name": "Test",
                "asn": 2**31 - 1,
                "network": "1.0.0.0/8",
            }
        )
        assert net.asn == 2147483647

    def test_http_event_negative_status(self) -> None:
        http = L9HttpEvent.from_dict(
            {
                "root": "/",
                "url": "/test",
                "status": -1,
                "length": 0,
                "title": "",
                "favicon_hash": "",
            }
        )
        assert http.status == -1

    def test_dataset_summary_negative_values(self) -> None:
        ds = DatasetSummary.from_dict(
            {
                "rows": -1,
                "files": -1,
                "size": -1,
                "collections": -1,
                "infected": False,
            }
        )
        assert ds.rows == -1
        assert ds.files == -1
        assert ds.size == -1


class TestMalformedDatetimes:
    """Test behavior with malformed datetime strings."""

    def test_certificate_invalid_datetime(self) -> None:
        with pytest.raises(ValidationError):
            Certificate.from_dict(
                {
                    "cn": "example.com",
                    "fingerprint": "abc123",
                    "key_algo": "RSA",
                    "key_size": 2048,
                    "issuer_name": "Test CA",
                    "not_before": "invalid-datetime",
                    "not_after": "2024-12-31T23:59:59Z",
                    "valid": True,
                }
            )

    def test_certificate_empty_datetime(self) -> None:
        with pytest.raises(ValidationError):
            Certificate.from_dict(
                {
                    "cn": "example.com",
                    "fingerprint": "abc123",
                    "key_algo": "RSA",
                    "key_size": 2048,
                    "issuer_name": "Test CA",
                    "not_before": "",
                    "not_after": "2024-12-31T23:59:59Z",
                    "valid": True,
                }
            )

    def test_certificate_date_only(self) -> None:
        cert = Certificate.from_dict(
            {
                "cn": "example.com",
                "fingerprint": "abc123",
                "key_algo": "RSA",
                "key_size": 2048,
                "issuer_name": "Test CA",
                "not_before": "2024-01-01",
                "not_after": "2024-12-31T23:59:59Z",
                "valid": True,
            }
        )
        assert cert.not_before.year == 2024
        assert cert.not_before.month == 1
        assert cert.not_before.day == 1


class TestMalformedDecimals:
    """Test behavior with malformed decimal values."""

    def test_geopoint_non_numeric(self) -> None:
        with pytest.raises(ValueError, match="invalid decimal"):
            GeoPoint.from_dict({"lat": "not-a-number", "lon": "1.0"})

    def test_geopoint_infinity(self) -> None:
        gp = GeoPoint.from_dict({"lat": "Infinity", "lon": "1.0"})
        assert str(gp.lat) == "Infinity"

    def test_geopoint_nan(self) -> None:
        gp = GeoPoint.from_dict({"lat": "NaN", "lon": "1.0"})
        assert str(gp.lat) == "NaN"

    def test_geopoint_scientific_notation(self) -> None:
        gp = GeoPoint.from_dict({"lat": "1.5e2", "lon": "2.5E-1"})
        assert gp.lat == 150
        assert gp.lon == 0.25

    def test_geopoint_negative_values(self) -> None:
        gp = GeoPoint.from_dict({"lat": "-1.5", "lon": "-2.5"})
        assert gp.lat == -1.5
        assert gp.lon == -2.5

    def test_geopoint_round_trip_preserves_value(self) -> None:
        """Regression: normalize() used to strip trailing zeros."""
        gp = GeoPoint.from_dict({"lat": "1.000000", "lon": "2.500000"})
        serialized = gp.to_dict()
        gp2 = GeoPoint.from_dict(serialized)
        assert gp2.lat == gp.lat
        assert gp2.lon == gp.lon


class TestComplexNestedValidation:
    """Test validation behavior with complex nested structures."""

    def test_l9event_invalid_nested_decimal(self) -> None:
        path = TESTS_DIR / "l9event.json"
        with open(path) as f:
            data = json.load(f)
        data["geoip"]["location"] = {"lat": "invalid", "lon": "1.0"}
        with pytest.raises(ValueError, match="invalid decimal"):
            L9Event.from_dict(data)

    def test_l9event_missing_nested_required_field(self) -> None:
        path = TESTS_DIR / "l9event.json"
        with open(path) as f:
            data = json.load(f)
        del data["network"]["asn"]
        with pytest.raises(ValidationError):
            L9Event.from_dict(data)

    def test_certificate_with_domain_list(self) -> None:
        cert = Certificate.from_dict(
            {
                "cn": "example.com",
                "domain": ["site1.example.com", "site2.example.com"],
                "fingerprint": "abc123",
                "key_algo": "RSA",
                "key_size": 2048,
                "issuer_name": "Test CA",
                "not_before": "2024-01-01T00:00:00Z",
                "not_after": "2024-12-31T23:59:59Z",
                "valid": True,
            }
        )
        assert cert.domain == ["site1.example.com", "site2.example.com"]

    def test_certificate_with_empty_domain_list(self) -> None:
        cert = Certificate.from_dict(
            {
                "cn": "example.com",
                "domain": [],
                "fingerprint": "abc123",
                "key_algo": "RSA",
                "key_size": 2048,
                "issuer_name": "Test CA",
                "not_before": "2024-01-01T00:00:00Z",
                "not_after": "2024-12-31T23:59:59Z",
                "valid": True,
            }
        )
        assert cert.domain == []

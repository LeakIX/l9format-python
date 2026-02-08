import json
from pathlib import Path

import pytest

from l9format import L9Event

TESTS_DIR = Path(__file__).parent

IP4SCOUT_FILES = sorted(
    f for f in TESTS_DIR.iterdir() if f.is_file() and "ip4scout" in f.name
)


def test_l9event_json_from_reference_repository() -> None:
    path = TESTS_DIR / "l9event.json"
    with open(path) as f:
        c = json.load(f)
    event = L9Event.from_dict(c)
    assert event.event_type == "leak"
    assert event.event_source == "DotEnvConfigPlugin"
    assert event.ip == "127.0.0.1"
    assert event.port == "8080"
    assert event.host == "site1.example.com"
    assert event.reverse == "ptr1.example.com"
    assert event.protocol == "https"
    assert event.summary == "GET /... qwerqwer"
    assert event.http.root == "/site1"
    assert event.http.url == "/site1/.env"
    assert event.http.status == 200
    assert event.http.length == 12423
    assert event.http.title == "Apache welcome page"
    assert event.ssl.detected is True
    assert event.ssl.enabled is True
    assert event.ssl.version == "TLSv1.3"
    assert event.ssl.certificate.cn == "example.com"
    assert event.ssl.certificate.key_algo == "RSA"
    assert event.ssl.certificate.key_size == 2048
    assert event.service.software.name == "Apache"
    assert event.service.software.version == "2.2.4"
    assert event.service.credentials.noauth is True
    assert event.leak.stage == "open"
    assert event.leak.type == "configuration"
    assert event.leak.severity == "medium"
    assert event.leak.dataset.rows == 4
    assert event.leak.dataset.files == 1
    assert event.network.asn == 0
    assert event.tags == ["plc"]
    assert event.transport == ["tcp", "tls", "http"]
    assert event.event_pipeline == [
        "ip4scout",
        "l9tcpid",
        "l9explore",
        "DotEnvConfigPlugin",
    ]


@pytest.mark.parametrize("path", IP4SCOUT_FILES, ids=lambda p: p.name)
def test_l9events_from_ip4scout(path: Path) -> None:
    with open(path) as f:
        c = json.load(f)
    event = L9Event.from_dict(c)
    assert event.event_source == "ip4scout"
    assert event.event_type == "synack"
    assert isinstance(event.ip, str)
    assert len(event.ip) > 0
    assert isinstance(event.port, str)
    assert len(event.port) > 0


def test_iso8601_nanosecond_parsing() -> None:
    """
    Test ISO8601 datetime parsing with nanosecond precision.

    serde 0.9.0+ uses Python stdlib iso8601 support which handles nanoseconds
    correctly in Python 3.11+.
    """
    path = TESTS_DIR / "l9event.json"
    with open(path) as f:
        c = json.load(f)
    # Use a timestamp with nanosecond precision (9 decimal places)
    c["time"] = "2023-10-05T23:30:36.823867784Z"
    event = L9Event.from_dict(c)
    assert event.time.year == 2023
    assert event.time.month == 10
    assert event.time.day == 5
    assert event.time.hour == 23
    assert event.time.minute == 30
    assert event.time.second == 36


def test_all_models_importable_from_package() -> None:
    """Verify all public models are importable from the l9format package."""
    import l9format

    expected_models = [
        "Certificate",
        "DatasetSummary",
        "GeoLocation",
        "GeoPoint",
        "L9Aggregation",
        "L9AMQPEvent",
        "L9DNSEvent",
        "L9Event",
        "L9FTPEvent",
        "L9HttpEvent",
        "L9LDAPEvent",
        "L9LeakEvent",
        "L9MemcachedEvent",
        "L9MongoDBEvent",
        "L9MySQLEvent",
        "L9PostgreSQLEvent",
        "L9RDPEvent",
        "L9RedisEvent",
        "L9RTSPEvent",
        "L9ServiceEvent",
        "L9SIPEvent",
        "L9SMTPEvent",
        "L9SSHEvent",
        "L9SSLEvent",
        "L9TelnetEvent",
        "L9VNCEvent",
        "Network",
        "ServiceCredentials",
        "Software",
        "SoftwareModule",
    ]
    for name in expected_models:
        assert hasattr(l9format, name), f"{name} not importable from l9format"

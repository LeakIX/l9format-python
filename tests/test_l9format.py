import json
import os
from pathlib import Path

from l9format import L9Event

TESTS_DIR = Path(os.path.dirname(__file__))

IP4SCOUT_FILES = [
    f
    for f in Path.iterdir(TESTS_DIR)
    if Path.is_file(f) and "ip4scout" in f.name
]


def test_l9event_json_from_reference_repository():
    path = TESTS_DIR / "l9event.json"
    c = json.load(open(str(path), "r"))
    L9Event.from_dict(c)


def test_l9events_from_ip4scout():
    for path in IP4SCOUT_FILES:
        c = json.load(open(str(path), "r"))
        L9Event.from_dict(c)


def test_iso8601_nanosecond_parsing():
    """
    Test ISO8601 datetime parsing with nanosecond precision.

    serde 0.9.0+ uses Python stdlib iso8601 support which handles nanoseconds
    correctly in Python 3.11+.
    """
    path = TESTS_DIR / "l9event.json"
    c = json.load(open(str(path), "r"))
    # Use a timestamp with nanosecond precision (9 decimal places)
    c["time"] = "2023-10-05T23:30:36.823867784Z"
    event = L9Event.from_dict(c)
    assert event.time.year == 2023
    assert event.time.month == 10
    assert event.time.day == 5
    assert event.time.hour == 23
    assert event.time.minute == 30
    assert event.time.second == 36


def test_all_models_importable_from_package():
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

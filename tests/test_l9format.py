from l9format import l9format
from pathlib import Path
import os
import json

TESTS_DIR = Path(os.path.dirname(__file__))

IP4SCOUT_FILES = [
    f for f in Path.iterdir(TESTS_DIR) if Path.is_file(f) and "ip4scout" in f.name
]


def test_l9event_json_from_reference_repository():
    path = TESTS_DIR / "l9event.json"
    c = json.load(open(str(path), "r"))
    l9format.L9Event.from_dict(c)


def test_l9events_form_ip4scout():
    for path in IP4SCOUT_FILES:
        c = json.load(open(str(path), "r"))
        l9format.L9Event.from_dict(c)

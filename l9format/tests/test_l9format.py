from l9format import l9format
from pathlib import Path
import os
import json

TESTS_DIR = Path(os.path.dirname(__file__))


def test_l9event_json():
    path = TESTS_DIR / "l9event.json"
    c = json.load(open(str(path), "r"))
    l9format.L9Event.from_dict(c)

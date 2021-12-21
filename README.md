l9format python
===================

l9format is a schema declaration targeted at interoperability between network
recon tools used at LeakIX.

This library is equivalent to [l9format](https://github.com/leakix/l9format)
which provides a Go implementation.

## Run the tests


```
poetry install
poetry run pytest l9format/tests/test_l9format.py
```

## Install

Use main branch for the moment:
```
poetry add https://github.com/leakix/l9format-python#main
```

## Documentation

```
from l9format import l9format
l9format.L9Event.from_dict(res)
```

## Versioning

The versions will be synced with [l9format](https://github.com/leakix/l9format),
suffixed by a number for bug fixes in the python implementation specifically.
For instance, `1.3.1-0` will be the first version for `1.3.1` and follow
https://github.com/LeakIX/l9format/releases/tag/v1.3.1. If a change is required
for the Python package, but is the same specification than the Go
implementation, the next release will be `1.3.1-1`.

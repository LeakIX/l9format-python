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

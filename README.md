l9format python
===================

[![PyPI](https://img.shields.io/pypi/v/l9format)](https://pypi.org/project/l9format/)
[![GitHub Release](https://img.shields.io/github/v/release/LeakIX/l9format-python)](https://github.com/LeakIX/l9format-python/releases/latest)

l9format is a schema declaration targeted at interoperability between network
recon tools used at LeakIX.

This library is equivalent to [l9format](https://github.com/leakix/l9format)
which provides a Go implementation.

## Tools and Usage

### Running Tests

We use `pytest` for testing. Run the tests with:

```bash
poetry run pytest
```

### Code Formatting

We use `black` for code formatting. To format the code, run:

```bash
poetry run black .
```

### Import Sorting

We use `isort` to sort imports. To sort imports, run:

```bash
poetry run isort .
```

### Code Linting

We use `ruff` for linting. Run:

```bash
poetry run ruff check .
```

## Install

```bash
pip install l9format
```

Or with a specific version:

```bash
pip install l9format==1.4.0
```

See [PyPI](https://pypi.org/project/l9format/) and
[GitHub releases](https://github.com/LeakIX/l9format-python/releases/latest)
for all available versions.

## Documentation

```python
from l9format import l9format
l9format.L9Event.from_dict(res)
```

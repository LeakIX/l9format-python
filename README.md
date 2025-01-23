l9format python
===================

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

See [releases](https://github.com/LeakIX/l9format-python/releases/) for the
different versions.
The release `1.3.1-0` will be mapped to `1.3.1.post0`.

## Documentation

```python
from l9format import l9format
l9format.L9Event.from_dict(res)
```

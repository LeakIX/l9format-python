# l9format

`l9format` is a schema declaration targeted at interoperability between the
network reconnaissance tools used at [LeakIX](https://leakix.net). This
package is the Python implementation: typed dataclass models with
serialization, deserialization, and validation.

## Install

```bash
uv add l9format
```

The package has no runtime dependencies.

## Usage

```python
from l9format import L9Event

event = L9Event.from_json(raw_json)
print(event.to_dict())
```

Models support `from_dict` / `to_dict` and `from_json` / `to_json`, with
validation of required fields and optional (`X | None`) handling.

See the [API reference](reference.md) for the full model set.

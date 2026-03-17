# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.1] - 2026-03-17

### Changed

- Use explicit include lists instead of exclude lists for hatch build targets
  (sdist and wheel) in `pyproject.toml` ([953d604], [#67])

### Infrastructure

- CI: move shellcheck into its own dedicated workflow, separate from changelog
  checks ([72bf877], [#65])
- CI: bump astral-sh/setup-uv from 6 to 7 ([c9216ba], [#64])

## [2.0.0] - 2026-03-16

### Changed

- **BREAKING**: Replace `serde` dependency with Python stdlib `dataclasses`.
  The `serde` library is unmaintained. All models now use `@dataclass` with a
  custom `Model` base class that provides the same `from_dict()`/`to_dict()`
  API. `ValidationError` is now exported from `l9format` directly instead of
  `serde`.
- Remove `Decimal` custom field class (was a `serde.fields.Instance` subclass).
  Decimal serialization/deserialization is now handled internally by the `Model`
  base class.

### Infrastructure

- CI: add Python 3.14 to test matrix
- Remove serde-specific mypy overrides from `pyproject.toml`

## [1.4.1] - 2026-03-16

### Infrastructure

- CI: bump actions/checkout from 4 to 6 ([6c9eecd], [#49])
- Bump ruff dev dependency from `^0.14.14` to `>=0.14.14,<0.16.0` ([ac8a1db], [#50])
- Bump isort dev dependency from `^7.0.0` to `>=7,<9` to allow isort 8.x
  ([4464bfd], [#51])
- Migrate from Poetry to uv: update `pyproject.toml` to PEP 621 format with
  `hatchling` build backend, replace `poetry run` with `uv run` in Makefile,
  and switch CI to `astral-sh/setup-uv` ([5f4fc51], [#56])
- CI: add per-commit workflow triggered by `ci:per-commit` label for easier
  bisect and revert ([bc4872d], [#59])
- CI: use Makefile targets in workflows and add sequential per-commit testing
  ([fa582dc], [#62])
- CI: bump astral-sh/setup-uv from 6 to 7 ([961f9ee], [#58])

## [1.4.0] - 2026-02-09

### Added

- Add 16 protocol-specific event types: `L9SSHEvent`, `L9VNCEvent`,
  `L9FTPEvent`, `L9SMTPEvent`, `L9TelnetEvent`, `L9RedisEvent`,
  `L9MySQLEvent`, `L9PostgreSQLEvent`, `L9MongoDBEvent`, `L9MemcachedEvent`,
  `L9AMQPEvent`, `L9LDAPEvent`, `L9SIPEvent`, `L9RDPEvent`, `L9DNSEvent`,
  `L9RTSPEvent` ([8f45e82], [#18])
- Extend `L9SSHEvent` with enumeration fields for host keys, algorithms, and
  KEX methods ([8f45e82], [#18])
- Add 32 round-trip and serialization tests covering `to_dict()`, `Decimal`
  field serialize/deserialize, and serde `None`-omission behavior
  ([d554f1e], [#24])
- Add `py.typed` marker for PEP 561 compliance ([7f49ff5], [#31])
- Add field-level assertions to deserialization tests ([cbea4fc], [#26])
- Add 34 edge-case and validation tests covering missing fields, null values,
  empty strings, boundary integers, malformed datetimes/decimals, and nested
  validation ([1ca6e4d], [#33])

### Changed

- Bump minimum Python version from 3.13 to 3.11 for `datetime.fromisoformat`
  UTC suffix support ([82245e9], [#18])
- Version bump to 1.4.0 ([8f45e82], [#18])
- Use `importlib.metadata.version()` for `__version__`, single source of truth
  in `pyproject.toml` ([3547e22], [#22])
- Re-export all public models from `__init__.py` and define `__all__`
  ([1dcfbef], [#21])
- Tests now import from `l9format` package directly instead of
  `l9format.l9format` ([e8aef2e], [#21])
- Use `pytest.mark.parametrize` for ip4scout tests so each file is a distinct
  test case ([ac4744e], [#32])

### Fixed

- Fix leaked file handles in tests using context managers ([b66a6f5], [#25])
- Fix `Decimal.normalize()` stripping trailing zeros, breaking round-trip
  serialization; add regression test ([28c76f1], [0130743], [#28])
- Add return type annotations to test functions for mypy compliance
  ([cd74b55], [#43])
- Fix typo in test name: `test_l9events_form_ip4scout` ->
  `test_l9events_from_ip4scout` ([0d8736e], [#27])

### Infrastructure

- CI: drop Python 3.10 from test matrix ([82245e9], [#18])
- Add mypy type checking with serde-compatible configuration
  ([fac243d], [#16])
- Add `.editorconfig` for consistent editor settings ([fac243d], [#16])
- Add Dependabot configuration for pip and GitHub Actions ([2144fb2], [#12])
- Expand Makefile with self-documenting help and additional targets
  ([fac243d], [#16])
- Add explicit tool configuration for ruff, black, isort in pyproject.toml
  ([fac243d], [#16])
- Fix type annotations in `Decimal` class and improve exception handling
  ([fac243d], [#16])
- CI: bump actions/checkout from 4 to 6 ([138b369], [#14])
- CI: bump actions/setup-python from 5 to 6 ([2c42bd0], [#15])
- CI: add typecheck step to workflow ([fac243d], [#16])
- CI: update to Python 3.13, remove Python 3.14 due to serde compatibility
  ([17402be], [#13])
- CI: enforce CHANGELOG.md changes are in dedicated commits
  ([d30efd2], [#35])

## [1.3.2] - 2025-01-23

### Changed

- Bump version to 1.3.2 ([5887f5e], [#10])
- README: remove versioning section ([f2694d7], [#10])

### Infrastructure

- CI: add format, lint, and import sort checks ([f3f9ebd], [#8])
- Add Makefile with standard targets ([7be8625], [#8])
- Update development dependencies ([60ee697], [#8])
- Update README with current usage instructions ([269c004], [#9])

## [1.3.1-1] - 2025-01-23

### Added

- L9Event: add missing field `port` ([03d6655], [#6])

### Changed

- Bump minimum Python version to 3.9 ([577774e], [#7])
- Use `Exception` instead of undefined `ValidationError` ([285fe96])

### Infrastructure

- CI: drop Python 3.7 and 3.8 support ([66faa74], [de5aae6], [#7])
- CI: add Python 3.12 support ([ba3b5a5], [#7])
- CI: use Poetry 1.8.5 ([635b24c], [#7])
- CI: update to ubuntu 22.04 ([afdbe95])
- CI: update CI configuration and fix variable name ([61683cb], [8612f13],
  [#4], [#5])

## [1.3.1-0] - 2021-12-21

### Added

- Add `L9Aggregation` model ([4807f73])
- Add `record_age` as optional field ([0d91cab])
- Add `__init__.py` with `__version__` for version verification ([897bd6c])
- Add Decimal fields for `lat` and `lon` in GeoPoint ([dad2666])
- Add more tests with ip4scout outputs ([5102665])
- Add mypy for type checking ([cd75682])

### Changed

- Make `leak` field optional in L9Event ([25d841e])
- Make some fields optional in models ([4807f73])
- Use `DateTime` instead of `Time` for time fields ([20d4b1d], [#3])
- Empty lists are returned as None ([4a58022], [#2])
- Move tests to the root directory ([b7eecf6], [#2])
- Remove decimal dependency ([094ddd2])

### Infrastructure

- Complete pyproject.toml configuration ([d7f8696])
- Add poetry build in CI ([325581f])
- Check format in CI and move black to dev deps ([2a33ed0])
- Use Poetry 1.1.11 ([259a81b])

## [1.0.0] - 2021-05-23

### Added

- Initial release based on l9format Go implementation ([67cc265], [#1])
- L9Event model with HTTP, SSL, SSH, Service, Leak, GeoIP, and Network fields
- Basic serialization/deserialization using serde library

<!-- Version links -->

[Unreleased]: https://github.com/LeakIX/l9format-python/compare/v2.0.1...HEAD
[2.0.1]: https://github.com/LeakIX/l9format-python/compare/v2.0.0...v2.0.1
[2.0.0]: https://github.com/LeakIX/l9format-python/compare/v1.4.1...v2.0.0
[1.4.1]: https://github.com/LeakIX/l9format-python/compare/1.4.0...1.4.1
[1.4.0]: https://github.com/LeakIX/l9format-python/compare/1.3.2...1.4.0
[1.3.2]: https://github.com/LeakIX/l9format-python/compare/1.3.1-1...1.3.2
[1.3.1-1]: https://github.com/LeakIX/l9format-python/compare/1.3.1-0...1.3.1-1
[1.3.1-0]: https://github.com/LeakIX/l9format-python/compare/1.0.0...1.3.1-0
[1.0.0]: https://github.com/LeakIX/l9format-python/releases/tag/1.0.0

<!-- Commit links -->

[953d604]: https://github.com/LeakIX/l9format-python/commit/953d604
[72bf877]: https://github.com/LeakIX/l9format-python/commit/72bf877
[c9216ba]: https://github.com/LeakIX/l9format-python/commit/c9216ba
[fa582dc]: https://github.com/LeakIX/l9format-python/commit/fa582dc
[bc4872d]: https://github.com/LeakIX/l9format-python/commit/bc4872d
[6c9eecd]: https://github.com/LeakIX/l9format-python/commit/6c9eecd
[961f9ee]: https://github.com/LeakIX/l9format-python/commit/961f9ee
[5f4fc51]: https://github.com/LeakIX/l9format-python/commit/5f4fc51
[ac8a1db]: https://github.com/LeakIX/l9format-python/commit/ac8a1db
[4464bfd]: https://github.com/LeakIX/l9format-python/commit/4464bfd
[ac4744e]: https://github.com/LeakIX/l9format-python/commit/ac4744e
[d554f1e]: https://github.com/LeakIX/l9format-python/commit/d554f1e
[7f49ff5]: https://github.com/LeakIX/l9format-python/commit/7f49ff5
[cd74b55]: https://github.com/LeakIX/l9format-python/commit/cd74b55
[0130743]: https://github.com/LeakIX/l9format-python/commit/0130743
[28c76f1]: https://github.com/LeakIX/l9format-python/commit/28c76f1
[b66a6f5]: https://github.com/LeakIX/l9format-python/commit/b66a6f5
[cbea4fc]: https://github.com/LeakIX/l9format-python/commit/cbea4fc
[3547e22]: https://github.com/LeakIX/l9format-python/commit/3547e22
[1ca6e4d]: https://github.com/LeakIX/l9format-python/commit/1ca6e4d
[0d8736e]: https://github.com/LeakIX/l9format-python/commit/0d8736e
[d30efd2]: https://github.com/LeakIX/l9format-python/commit/d30efd2
[1dcfbef]: https://github.com/LeakIX/l9format-python/commit/1dcfbef
[e8aef2e]: https://github.com/LeakIX/l9format-python/commit/e8aef2e
[8f45e82]: https://github.com/LeakIX/l9format-python/commit/8f45e82
[82245e9]: https://github.com/LeakIX/l9format-python/commit/82245e9
[fac243d]: https://github.com/LeakIX/l9format-python/commit/fac243d
[2144fb2]: https://github.com/LeakIX/l9format-python/commit/2144fb2
[138b369]: https://github.com/LeakIX/l9format-python/commit/138b369
[2c42bd0]: https://github.com/LeakIX/l9format-python/commit/2c42bd0
[17402be]: https://github.com/LeakIX/l9format-python/commit/17402be
[5887f5e]: https://github.com/LeakIX/l9format-python/commit/5887f5e
[f2694d7]: https://github.com/LeakIX/l9format-python/commit/f2694d7
[f3f9ebd]: https://github.com/LeakIX/l9format-python/commit/f3f9ebd
[7be8625]: https://github.com/LeakIX/l9format-python/commit/7be8625
[60ee697]: https://github.com/LeakIX/l9format-python/commit/60ee697
[269c004]: https://github.com/LeakIX/l9format-python/commit/269c004
[03d6655]: https://github.com/LeakIX/l9format-python/commit/03d6655
[577774e]: https://github.com/LeakIX/l9format-python/commit/577774e
[285fe96]: https://github.com/LeakIX/l9format-python/commit/285fe96
[66faa74]: https://github.com/LeakIX/l9format-python/commit/66faa74
[de5aae6]: https://github.com/LeakIX/l9format-python/commit/de5aae6
[ba3b5a5]: https://github.com/LeakIX/l9format-python/commit/ba3b5a5
[635b24c]: https://github.com/LeakIX/l9format-python/commit/635b24c
[afdbe95]: https://github.com/LeakIX/l9format-python/commit/afdbe95
[61683cb]: https://github.com/LeakIX/l9format-python/commit/61683cb
[8612f13]: https://github.com/LeakIX/l9format-python/commit/8612f13
[4807f73]: https://github.com/LeakIX/l9format-python/commit/4807f73
[0d91cab]: https://github.com/LeakIX/l9format-python/commit/0d91cab
[897bd6c]: https://github.com/LeakIX/l9format-python/commit/897bd6c
[dad2666]: https://github.com/LeakIX/l9format-python/commit/dad2666
[5102665]: https://github.com/LeakIX/l9format-python/commit/5102665
[cd75682]: https://github.com/LeakIX/l9format-python/commit/cd75682
[25d841e]: https://github.com/LeakIX/l9format-python/commit/25d841e
[20d4b1d]: https://github.com/LeakIX/l9format-python/commit/20d4b1d
[4a58022]: https://github.com/LeakIX/l9format-python/commit/4a58022
[b7eecf6]: https://github.com/LeakIX/l9format-python/commit/b7eecf6
[094ddd2]: https://github.com/LeakIX/l9format-python/commit/094ddd2
[d7f8696]: https://github.com/LeakIX/l9format-python/commit/d7f8696
[325581f]: https://github.com/LeakIX/l9format-python/commit/325581f
[2a33ed0]: https://github.com/LeakIX/l9format-python/commit/2a33ed0
[259a81b]: https://github.com/LeakIX/l9format-python/commit/259a81b
[67cc265]: https://github.com/LeakIX/l9format-python/commit/67cc265

<!-- PR links -->

[#1]: https://github.com/LeakIX/l9format-python/pull/1
[#2]: https://github.com/LeakIX/l9format-python/pull/2
[#3]: https://github.com/LeakIX/l9format-python/pull/3
[#4]: https://github.com/LeakIX/l9format-python/pull/4
[#5]: https://github.com/LeakIX/l9format-python/pull/5
[#6]: https://github.com/LeakIX/l9format-python/pull/6
[#7]: https://github.com/LeakIX/l9format-python/pull/7
[#8]: https://github.com/LeakIX/l9format-python/pull/8
[#9]: https://github.com/LeakIX/l9format-python/pull/9
[#10]: https://github.com/LeakIX/l9format-python/pull/10
[#12]: https://github.com/LeakIX/l9format-python/pull/12
[#13]: https://github.com/LeakIX/l9format-python/pull/13
[#14]: https://github.com/LeakIX/l9format-python/pull/14
[#15]: https://github.com/LeakIX/l9format-python/pull/15
[#16]: https://github.com/LeakIX/l9format-python/pull/16
[#18]: https://github.com/LeakIX/l9format-python/pull/18
[#21]: https://github.com/LeakIX/l9format-python/issues/21
[#22]: https://github.com/LeakIX/l9format-python/issues/22
[#26]: https://github.com/LeakIX/l9format-python/issues/26
[#28]: https://github.com/LeakIX/l9format-python/issues/28
[#27]: https://github.com/LeakIX/l9format-python/issues/27
[#33]: https://github.com/LeakIX/l9format-python/issues/33
[#25]: https://github.com/LeakIX/l9format-python/issues/25
[#35]: https://github.com/LeakIX/l9format-python/issues/35
[#24]: https://github.com/LeakIX/l9format-python/issues/24
[#31]: https://github.com/LeakIX/l9format-python/issues/31
[#32]: https://github.com/LeakIX/l9format-python/issues/32
[#49]: https://github.com/LeakIX/l9format-python/pull/49
[#50]: https://github.com/LeakIX/l9format-python/pull/50
[#51]: https://github.com/LeakIX/l9format-python/pull/51
[#56]: https://github.com/LeakIX/l9format-python/pull/56
[#58]: https://github.com/LeakIX/l9format-python/pull/58
[#59]: https://github.com/LeakIX/l9format-python/issues/59
[#62]: https://github.com/LeakIX/l9format-python/pull/62
[#64]: https://github.com/LeakIX/l9format-python/pull/64
[#65]: https://github.com/LeakIX/l9format-python/pull/65
[#67]: https://github.com/LeakIX/l9format-python/pull/67
[#43]: https://github.com/LeakIX/l9format-python/issues/43

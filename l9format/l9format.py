import dataclasses
import decimal
import json
import types
import typing
from collections import OrderedDict
from datetime import datetime
from typing import Any, Union, get_args, get_origin


class ValidationError(Exception):
    """Raised when a required field is missing or a type check fails."""

    def __init__(self, message: str, value: object = None) -> None:
        super().__init__(message)
        self.message = message
        self.value = value


def round_decimal(
    decimal_obj: decimal.Decimal, num_of_places: int = 6
) -> decimal.Decimal:
    return decimal_obj.quantize(decimal.Decimal(10) ** -num_of_places)


def _is_optional(tp: Any) -> bool:
    """Check if a type annotation is Optional[X] or X | None."""
    if get_origin(tp) in (Union, types.UnionType):
        return type(None) in get_args(tp)
    return False


def _unwrap_optional(tp: Any) -> Any:
    """Extract X from Optional[X] or X | None."""
    if get_origin(tp) in (Union, types.UnionType):
        args = get_args(tp)
        for arg in args:
            if arg is not type(None):
                return arg
    return tp


def _deserialize_value(value: object, tp: Any) -> object:
    """Deserialize a value into the expected type."""
    if value is None:
        return None

    if _is_optional(tp):
        tp = _unwrap_optional(tp)

    origin = get_origin(tp)

    if origin is list:
        elem_type = get_args(tp)[0] if get_args(tp) else object
        if not isinstance(value, list):
            raise ValidationError(
                f"expected list, got {type(value).__name__}",
                value,
            )
        return [_deserialize_value(item, elem_type) for item in value]

    if origin is dict:
        args = get_args(tp)
        key_type = args[0] if args else object
        val_type = args[1] if len(args) > 1 else object
        if not isinstance(value, dict):
            raise ValidationError(
                f"expected dict, got {type(value).__name__}",
                value,
            )
        return {
            _deserialize_value(k, key_type): _deserialize_value(v, val_type)
            for k, v in value.items()
        }

    if isinstance(tp, type) and issubclass(tp, Model):
        if not isinstance(value, dict):
            raise ValidationError(
                f"expected dict for nested model, got {type(value).__name__}",
                value,
            )
        return tp.from_dict(value)

    if isinstance(tp, type) and issubclass(tp, datetime):
        if not isinstance(value, str):
            raise ValidationError(
                f"expected string for datetime, got {type(value).__name__}",
                value,
            )
        if not value:
            raise ValidationError("empty datetime string", value)
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as e:
            raise ValidationError(f"invalid datetime: {value}", value) from e

    if isinstance(tp, type) and issubclass(tp, decimal.Decimal):
        try:
            return decimal.Decimal(str(value))
        except decimal.DecimalException as e:
            raise ValueError(f"invalid decimal: {value}") from e

    return value


class Model:
    """Base model providing from_dict/to_dict with serde-compatible
    behavior."""

    __dataclass_fields__: dict[str, dataclasses.Field[Any]]

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Model":
        if not isinstance(d, dict):
            raise ValidationError(f"expected dict, got {type(d).__name__}", d)
        kwargs: dict[str, Any] = {}
        hints = cls._get_type_hints()
        for f in cls.__dataclass_fields__.values():
            name = f.name
            tp = hints.get(name, f.type)
            optional = _is_optional(tp)

            if name not in d:
                if optional:
                    kwargs[name] = None
                    continue
                raise ValidationError(f"missing required field: {name}")

            value = d[name]

            if value is None:
                if optional:
                    kwargs[name] = None
                    continue
                # Let the deserializer handle None for types that
                # produce their own errors (e.g. Decimal -> ValueError)
                inner = _unwrap_optional(tp) if optional else tp
                if isinstance(inner, type) and issubclass(
                    inner, (str, int, bool)
                ):
                    raise ValidationError(
                        f"field '{name}' is required but got None"
                    )

            kwargs[name] = _deserialize_value(value, tp)

        return cls(**kwargs)

    def to_dict(self) -> "OrderedDict[str, Any]":
        result: OrderedDict[str, Any] = OrderedDict()
        hints = self.__class__._get_type_hints()
        for f in self.__class__.__dataclass_fields__.values():
            value = getattr(self, f.name)
            tp = hints.get(f.name, f.type)
            optional = _is_optional(tp)
            if optional and value is None:
                continue
            result[f.name] = self._serialize_field(value, tp)
        return result

    def _serialize_field(self, value: object, _tp: Any) -> object:
        if value is None:
            return None
        if isinstance(value, Model):
            return value.to_dict()
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, decimal.Decimal):
            return f"{value:f}"
        if isinstance(value, list):
            return [self._serialize_field(item, object) for item in value]
        if isinstance(value, dict):
            return {
                k: self._serialize_field(v, object) for k, v in value.items()
            }
        return value

    @classmethod
    def _get_type_hints(cls) -> dict[str, Any]:
        return typing.get_type_hints(cls)

    def to_json(self, **kwargs: Any) -> str:
        return json.dumps(self.to_dict(), **kwargs)

    @classmethod
    def from_json(cls, s: str, **kwargs: Any) -> "Model":
        return cls.from_dict(json.loads(s, **kwargs))


# --- Base Models ---


@dataclasses.dataclass
class GeoPoint(Model):
    lat: decimal.Decimal
    lon: decimal.Decimal

    def __post_init__(self) -> None:
        if not isinstance(self.lat, decimal.Decimal):
            try:
                self.lat = decimal.Decimal(str(self.lat))
            except decimal.DecimalException as e:
                raise ValueError(f"invalid decimal: {self.lat}") from e
        if not isinstance(self.lon, decimal.Decimal):
            try:
                self.lon = decimal.Decimal(str(self.lon))
            except decimal.DecimalException as e:
                raise ValueError(f"invalid decimal: {self.lon}") from e


@dataclasses.dataclass
class GeoLocation(Model):
    continent_name: str | None = None
    region_iso_code: str | None = None
    city_name: str | None = None
    country_iso_code: str | None = None
    country_name: str | None = None
    region_name: str | None = None
    location: GeoPoint | None = None


@dataclasses.dataclass
class Network(Model):
    organization_name: str = ""
    asn: int = 0
    network: str = ""


@dataclasses.dataclass
class Certificate(Model):
    cn: str = ""
    domain: list[str] | None = None
    fingerprint: str = ""
    key_algo: str = ""
    key_size: int = 0
    issuer_name: str = ""
    not_before: datetime = None  # type: ignore[assignment]
    not_after: datetime = None  # type: ignore[assignment]
    valid: bool = False


@dataclasses.dataclass
class SoftwareModule(Model):
    name: str = ""
    version: str = ""
    fingerprint: str = ""


@dataclasses.dataclass
class Software(Model):
    name: str = ""
    version: str = ""
    os: str = ""
    modules: list[SoftwareModule] | None = None
    fingerprint: str = ""


@dataclasses.dataclass
class ServiceCredentials(Model):
    noauth: bool = False
    username: str = ""
    password: str = ""
    key: str = ""
    raw: str | None = None


@dataclasses.dataclass
class DatasetSummary(Model):
    rows: int = 0
    files: int = 0
    size: int = 0
    collections: int = 0
    infected: bool = False
    ransom_notes: list[str] | None = None


# --- Service Events ---


@dataclasses.dataclass
class L9HttpEvent(Model):
    root: str = ""
    url: str = ""
    status: int = 0
    length: int = 0
    header: dict[str, str] | None = None
    title: str = ""
    favicon_hash: str = ""


@dataclasses.dataclass
class L9SSLEvent(Model):
    detected: bool = False
    enabled: bool = False
    jarm: str = ""
    cypher_suite: str = ""
    version: str = ""
    certificate: Certificate = None  # type: ignore[assignment]


@dataclasses.dataclass
class L9ServiceEvent(Model):
    credentials: ServiceCredentials = None  # type: ignore[assignment]
    software: Software = None  # type: ignore[assignment]


@dataclasses.dataclass
class L9LeakEvent(Model):
    stage: str = ""
    type: str = ""
    severity: str = ""
    dataset: DatasetSummary = None  # type: ignore[assignment]


# --- Protocol Events ---


@dataclasses.dataclass
class L9SSHEvent(Model):
    fingerprint: str | None = None
    version: int | None = None
    banner: str | None = None
    motd: str | None = None
    key_type: str | None = None
    key: str | None = None
    kex_algorithms: list[str] | None = None
    host_key_algorithms: list[str] | None = None
    encryption_algorithms: list[str] | None = None
    mac_algorithms: list[str] | None = None
    compression_algorithms: list[str] | None = None
    auth_methods: list[str] | None = None


@dataclasses.dataclass
class L9VNCEvent(Model):
    version: str | None = None
    security_types: list[str] | None = None
    noauth: bool | None = None


@dataclasses.dataclass
class L9FTPEvent(Model):
    banner: str | None = None
    tls_supported: bool | None = None
    anonymous: bool | None = None


@dataclasses.dataclass
class L9SMTPEvent(Model):
    banner: str | None = None
    starttls: bool | None = None
    extensions: list[str] | None = None


@dataclasses.dataclass
class L9TelnetEvent(Model):
    banner: str | None = None
    options: list[str] | None = None
    auth_required: bool | None = None


@dataclasses.dataclass
class L9RedisEvent(Model):
    version: str | None = None
    mode: str | None = None
    os: str | None = None
    auth_required: bool | None = None


@dataclasses.dataclass
class L9MySQLEvent(Model):
    version: str | None = None
    protocol_version: int | None = None
    auth_plugin: str | None = None
    server_status: str | None = None


@dataclasses.dataclass
class L9PostgreSQLEvent(Model):
    version: str | None = None
    databases: list[str] | None = None
    ssl_enabled: bool | None = None
    auth_method: str | None = None
    server_encoding: str | None = None
    client_encoding: str | None = None
    timezone: str | None = None
    max_connections: int | None = None


@dataclasses.dataclass
class L9MongoDBEvent(Model):
    version: str | None = None
    databases: list[str] | None = None
    auth_required: bool | None = None
    wire_version: int | None = None


@dataclasses.dataclass
class L9MemcachedEvent(Model):
    version: str | None = None
    libevent: str | None = None
    curr_items: int | None = None
    total_items: int | None = None
    bytes: int | None = None
    max_bytes: int | None = None
    cmd_get: int | None = None
    cmd_set: int | None = None
    get_hits: int | None = None
    get_misses: int | None = None
    threads: int | None = None


@dataclasses.dataclass
class L9AMQPEvent(Model):
    protocol_major: int | None = None
    protocol_minor: int | None = None
    product: str | None = None
    version: str | None = None
    platform: str | None = None


@dataclasses.dataclass
class L9LDAPEvent(Model):
    naming_contexts: list[str] | None = None
    supported_versions: list[str] | None = None
    vendor_name: str | None = None
    vendor_version: str | None = None
    supported_sasl: list[str] | None = None
    anonymous_bind: bool | None = None
    can_enumerate: bool | None = None


@dataclasses.dataclass
class L9SIPEvent(Model):
    version: str | None = None
    user_agent: str | None = None
    server: str | None = None
    allow: list[str] | None = None
    supported: list[str] | None = None


@dataclasses.dataclass
class L9RDPEvent(Model):
    product_version: str | None = None
    nla_required: bool | None = None
    ssl_enabled: bool | None = None
    hostname: str | None = None


@dataclasses.dataclass
class L9DNSEvent(Model):
    software: str | None = None
    version: str | None = None
    recursion: bool | None = None
    dnssec: bool | None = None
    zone_transfer: bool | None = None
    nameservers: list[str] | None = None


@dataclasses.dataclass
class L9RTSPEvent(Model):
    server: str | None = None
    methods: list[str] | None = None


# --- Main Event ---


@dataclasses.dataclass
class L9Event(Model):
    event_type: str = ""
    event_source: str = ""
    event_pipeline: list[str] | None = None
    event_fingerprint: str | None = None
    ip: str = ""
    port: str = ""
    host: str = ""
    reverse: str = ""
    mac: str | None = None
    vendor: str | None = None
    transport: list[str] | None = None
    protocol: str = ""
    http: L9HttpEvent = None  # type: ignore[assignment]
    summary: str = ""
    time: datetime = None  # type: ignore[assignment]
    ssl: L9SSLEvent | None = None
    # Protocol-specific events
    ssh: L9SSHEvent | None = None
    vnc: L9VNCEvent | None = None
    ftp: L9FTPEvent | None = None
    smtp: L9SMTPEvent | None = None
    telnet: L9TelnetEvent | None = None
    redis: L9RedisEvent | None = None
    mysql: L9MySQLEvent | None = None
    postgresql: L9PostgreSQLEvent | None = None
    mongodb: L9MongoDBEvent | None = None
    memcached: L9MemcachedEvent | None = None
    amqp: L9AMQPEvent | None = None
    ldap: L9LDAPEvent | None = None
    sip: L9SIPEvent | None = None
    rdp: L9RDPEvent | None = None
    dns: L9DNSEvent | None = None
    rtsp: L9RTSPEvent | None = None
    # Service events
    service: L9ServiceEvent = None  # type: ignore[assignment]
    leak: L9LeakEvent | None = None
    tags: list[str] | None = None
    geoip: GeoLocation = None  # type: ignore[assignment]
    network: Network = None  # type: ignore[assignment]


# --- Aggregation ---


@dataclasses.dataclass
class L9Aggregation(Model):
    summary: str | None = None
    ip: str = ""
    resource_id: str = ""
    open_ports: list[str] = None  # type: ignore[assignment]
    leak_count: int = 0
    leak_event_count: int = 0
    events: list[L9Event] = None  # type: ignore[assignment]
    plugins: list[str] = None  # type: ignore[assignment]
    geoip: GeoLocation = None  # type: ignore[assignment]
    network: Network = None  # type: ignore[assignment]
    creation_date: datetime = None  # type: ignore[assignment]
    update_date: datetime = None  # type: ignore[assignment]
    fresh: bool = False

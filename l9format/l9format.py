import dataclasses
import decimal
from collections import OrderedDict
from datetime import datetime
from typing import Any, Optional


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
    """Check if a type annotation is Optional[X]."""
    from typing import Union, get_args, get_origin

    if get_origin(tp) is Union:
        args = get_args(tp)
        return type(None) in args
    return False


def _unwrap_optional(tp: Any) -> Any:
    """Extract X from Optional[X]."""
    from typing import Union, get_args, get_origin

    if get_origin(tp) is Union:
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

    from typing import get_args, get_origin

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
                f"expected dict for nested model, "
                f"got {type(value).__name__}",
                value,
            )
        return tp.from_dict(value)

    if isinstance(tp, type) and issubclass(tp, datetime):
        if not isinstance(value, str):
            raise ValidationError(
                f"expected string for datetime, " f"got {type(value).__name__}",
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
    def from_dict(cls, d: dict) -> "Model":
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

    def to_dict(self) -> OrderedDict:
        result: OrderedDict = OrderedDict()
        hints = self.__class__._get_type_hints()
        for f in self.__class__.__dataclass_fields__.values():
            value = getattr(self, f.name)
            tp = hints.get(f.name, f.type)
            optional = _is_optional(tp)
            if optional and value is None:
                continue
            result[f.name] = self._serialize_field(value, tp)
        return result

    def _serialize_field(self, value: object, tp: Any) -> object:
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
        import typing

        return typing.get_type_hints(cls)

    def to_json(self, **kwargs: Any) -> str:
        import json

        return json.dumps(self.to_dict(), **kwargs)

    @classmethod
    def from_json(cls, s: str, **kwargs: Any) -> "Model":
        import json

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
    continent_name: Optional[str] = None
    region_iso_code: Optional[str] = None
    city_name: Optional[str] = None
    country_iso_code: Optional[str] = None
    country_name: Optional[str] = None
    region_name: Optional[str] = None
    location: Optional[GeoPoint] = None


@dataclasses.dataclass
class Network(Model):
    organization_name: str = ""
    asn: int = 0
    network: str = ""


@dataclasses.dataclass
class Certificate(Model):
    cn: str = ""
    domain: Optional[list[str]] = None
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
    modules: Optional[list[SoftwareModule]] = None
    fingerprint: str = ""


@dataclasses.dataclass
class ServiceCredentials(Model):
    noauth: bool = False
    username: str = ""
    password: str = ""
    key: str = ""
    raw: Optional[str] = None


@dataclasses.dataclass
class DatasetSummary(Model):
    rows: int = 0
    files: int = 0
    size: int = 0
    collections: int = 0
    infected: bool = False
    ransom_notes: Optional[list[str]] = None


# --- Service Events ---


@dataclasses.dataclass
class L9HttpEvent(Model):
    root: str = ""
    url: str = ""
    status: int = 0
    length: int = 0
    header: Optional[dict[str, str]] = None
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
    fingerprint: Optional[str] = None
    version: Optional[int] = None
    banner: Optional[str] = None
    motd: Optional[str] = None
    key_type: Optional[str] = None
    key: Optional[str] = None
    kex_algorithms: Optional[list[str]] = None
    host_key_algorithms: Optional[list[str]] = None
    encryption_algorithms: Optional[list[str]] = None
    mac_algorithms: Optional[list[str]] = None
    compression_algorithms: Optional[list[str]] = None
    auth_methods: Optional[list[str]] = None


@dataclasses.dataclass
class L9VNCEvent(Model):
    version: Optional[str] = None
    security_types: Optional[list[str]] = None
    noauth: Optional[bool] = None


@dataclasses.dataclass
class L9FTPEvent(Model):
    banner: Optional[str] = None
    tls_supported: Optional[bool] = None
    anonymous: Optional[bool] = None


@dataclasses.dataclass
class L9SMTPEvent(Model):
    banner: Optional[str] = None
    starttls: Optional[bool] = None
    extensions: Optional[list[str]] = None


@dataclasses.dataclass
class L9TelnetEvent(Model):
    banner: Optional[str] = None
    options: Optional[list[str]] = None
    auth_required: Optional[bool] = None


@dataclasses.dataclass
class L9RedisEvent(Model):
    version: Optional[str] = None
    mode: Optional[str] = None
    os: Optional[str] = None
    auth_required: Optional[bool] = None


@dataclasses.dataclass
class L9MySQLEvent(Model):
    version: Optional[str] = None
    protocol_version: Optional[int] = None
    auth_plugin: Optional[str] = None
    server_status: Optional[str] = None


@dataclasses.dataclass
class L9PostgreSQLEvent(Model):
    version: Optional[str] = None
    databases: Optional[list[str]] = None
    ssl_enabled: Optional[bool] = None
    auth_method: Optional[str] = None
    server_encoding: Optional[str] = None
    client_encoding: Optional[str] = None
    timezone: Optional[str] = None
    max_connections: Optional[int] = None


@dataclasses.dataclass
class L9MongoDBEvent(Model):
    version: Optional[str] = None
    databases: Optional[list[str]] = None
    auth_required: Optional[bool] = None
    wire_version: Optional[int] = None


@dataclasses.dataclass
class L9MemcachedEvent(Model):
    version: Optional[str] = None
    libevent: Optional[str] = None
    curr_items: Optional[int] = None
    total_items: Optional[int] = None
    bytes: Optional[int] = None
    max_bytes: Optional[int] = None
    cmd_get: Optional[int] = None
    cmd_set: Optional[int] = None
    get_hits: Optional[int] = None
    get_misses: Optional[int] = None
    threads: Optional[int] = None


@dataclasses.dataclass
class L9AMQPEvent(Model):
    protocol_major: Optional[int] = None
    protocol_minor: Optional[int] = None
    product: Optional[str] = None
    version: Optional[str] = None
    platform: Optional[str] = None


@dataclasses.dataclass
class L9LDAPEvent(Model):
    naming_contexts: Optional[list[str]] = None
    supported_versions: Optional[list[str]] = None
    vendor_name: Optional[str] = None
    vendor_version: Optional[str] = None
    supported_sasl: Optional[list[str]] = None
    anonymous_bind: Optional[bool] = None
    can_enumerate: Optional[bool] = None


@dataclasses.dataclass
class L9SIPEvent(Model):
    version: Optional[str] = None
    user_agent: Optional[str] = None
    server: Optional[str] = None
    allow: Optional[list[str]] = None
    supported: Optional[list[str]] = None


@dataclasses.dataclass
class L9RDPEvent(Model):
    product_version: Optional[str] = None
    nla_required: Optional[bool] = None
    ssl_enabled: Optional[bool] = None
    hostname: Optional[str] = None


@dataclasses.dataclass
class L9DNSEvent(Model):
    software: Optional[str] = None
    version: Optional[str] = None
    recursion: Optional[bool] = None
    dnssec: Optional[bool] = None
    zone_transfer: Optional[bool] = None
    nameservers: Optional[list[str]] = None


@dataclasses.dataclass
class L9RTSPEvent(Model):
    server: Optional[str] = None
    methods: Optional[list[str]] = None


# --- Main Event ---


@dataclasses.dataclass
class L9Event(Model):
    event_type: str = ""
    event_source: str = ""
    event_pipeline: Optional[list[str]] = None
    event_fingerprint: Optional[str] = None
    ip: str = ""
    port: str = ""
    host: str = ""
    reverse: str = ""
    mac: Optional[str] = None
    vendor: Optional[str] = None
    transport: Optional[list[str]] = None
    protocol: str = ""
    http: L9HttpEvent = None  # type: ignore[assignment]
    summary: str = ""
    time: datetime = None  # type: ignore[assignment]
    ssl: Optional[L9SSLEvent] = None
    # Protocol-specific events
    ssh: Optional[L9SSHEvent] = None
    vnc: Optional[L9VNCEvent] = None
    ftp: Optional[L9FTPEvent] = None
    smtp: Optional[L9SMTPEvent] = None
    telnet: Optional[L9TelnetEvent] = None
    redis: Optional[L9RedisEvent] = None
    mysql: Optional[L9MySQLEvent] = None
    postgresql: Optional[L9PostgreSQLEvent] = None
    mongodb: Optional[L9MongoDBEvent] = None
    memcached: Optional[L9MemcachedEvent] = None
    amqp: Optional[L9AMQPEvent] = None
    ldap: Optional[L9LDAPEvent] = None
    sip: Optional[L9SIPEvent] = None
    rdp: Optional[L9RDPEvent] = None
    dns: Optional[L9DNSEvent] = None
    rtsp: Optional[L9RTSPEvent] = None
    # Service events
    service: L9ServiceEvent = None  # type: ignore[assignment]
    leak: Optional[L9LeakEvent] = None
    tags: Optional[list[str]] = None
    geoip: GeoLocation = None  # type: ignore[assignment]
    network: Network = None  # type: ignore[assignment]


# --- Aggregation ---


@dataclasses.dataclass
class L9Aggregation(Model):
    summary: Optional[str] = None
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

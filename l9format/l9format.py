import decimal

from serde import Model, fields


def round_decimal(
    decimal_obj: decimal.Decimal, num_of_places: int = 6
) -> decimal.Decimal:
    return decimal_obj.quantize(
        decimal.Decimal(10) ** -num_of_places
    ).normalize()


class Decimal(fields.Instance):
    """
    A `~decimal.Decimal` field.

    This field serializes `~decimal.Decimal` objects as strings and
    deserializes string representations of Decimals as `~decimal.Decimal`
    objects.

    The resolution of the decimal can be specified. When not specified,
    the number is not rounded. When it is specified, the decimal is rounded
    to this number of decimal places upon serialization and deserialization.

    Args:
        resolution (int | None): The number of decimal places to round to.
            When None, rounding is disabled.
        **kwargs: keyword arguments for the `Field` constructor.
    """

    ty = decimal.Decimal

    def __init__(self, resolution: int | None = None, **kwargs: object) -> None:
        super(Decimal, self).__init__(self.__class__.ty, **kwargs)
        self.resolution = resolution

    def serialize(self, value: decimal.Decimal) -> str:
        if self.resolution is not None:
            value = round_decimal(value, num_of_places=self.resolution)
        return "{0:f}".format(value)

    def deserialize(self, value: object) -> decimal.Decimal:
        try:
            if self.resolution is not None:
                return round_decimal(
                    decimal.Decimal(str(value)), num_of_places=self.resolution
                )
            return decimal.Decimal(str(value))
        except decimal.DecimalException as e:
            raise ValueError(f"invalid decimal: {value}") from e


# --- Base Models ---


class GeoPoint(Model):
    lat: Decimal()
    lon: Decimal()


class GeoLocation(Model):
    continent_name: fields.Optional(fields.Str())
    region_iso_code: fields.Optional(fields.Str())
    city_name: fields.Optional(fields.Str())
    country_iso_code: fields.Optional(fields.Str())
    country_name: fields.Optional(fields.Str())
    region_name: fields.Optional(fields.Str())
    location: fields.Optional(fields.Nested(GeoPoint))


class Network(Model):
    organization_name: fields.Str()
    asn: fields.Int()
    network: fields.Str()


class Certificate(Model):
    cn: fields.Str()
    domain: fields.Optional(fields.List(fields.Str()))
    fingerprint: fields.Str()
    key_algo: fields.Str()
    key_size: fields.Int()
    issuer_name: fields.Str()
    not_before: fields.DateTime()
    not_after: fields.DateTime()
    valid: fields.Bool()


class SoftwareModule(Model):
    name: fields.Str()
    version: fields.Str()
    fingerprint: fields.Str()


class Software(Model):
    name: fields.Str()
    version: fields.Str()
    os: fields.Str()
    modules: fields.Optional(fields.List(fields.Nested(SoftwareModule)))
    fingerprint: fields.Str()


class ServiceCredentials(Model):
    noauth: fields.Bool()
    username: fields.Str()
    password: fields.Str()
    key: fields.Str()
    raw: fields.Optional(fields.Str())


class DatasetSummary(Model):
    rows: fields.Int()
    files: fields.Int()
    size: fields.Int()
    collections: fields.Int()
    infected: fields.Bool()
    ransom_notes: fields.Optional(fields.List(fields.Str()))


# --- Service Events ---


class L9HttpEvent(Model):
    root: fields.Str()
    url: fields.Str()
    status: fields.Int()
    length: fields.Int()
    header: fields.Optional(fields.Dict(key=fields.Str(), value=fields.Str()))
    title: fields.Str()
    favicon_hash: fields.Str()


class L9SSLEvent(Model):
    detected: fields.Bool()
    enabled: fields.Bool()
    jarm: fields.Str()
    cypher_suite: fields.Str()
    version: fields.Str()
    certificate: fields.Nested(Certificate)


class L9ServiceEvent(Model):
    credentials: fields.Nested(ServiceCredentials)
    software: fields.Nested(Software)


class L9LeakEvent(Model):
    stage: fields.Str()
    type: fields.Str()
    severity: fields.Str()
    dataset: fields.Nested(DatasetSummary)


# --- Protocol Events ---


class L9SSHEvent(Model):
    fingerprint: fields.Optional(fields.Str())
    version: fields.Optional(fields.Int())
    banner: fields.Optional(fields.Str())
    motd: fields.Optional(fields.Str())
    key_type: fields.Optional(fields.Str())
    key: fields.Optional(fields.Str())
    kex_algorithms: fields.Optional(fields.List(fields.Str()))
    host_key_algorithms: fields.Optional(fields.List(fields.Str()))
    encryption_algorithms: fields.Optional(fields.List(fields.Str()))
    mac_algorithms: fields.Optional(fields.List(fields.Str()))
    compression_algorithms: fields.Optional(fields.List(fields.Str()))
    auth_methods: fields.Optional(fields.List(fields.Str()))


class L9VNCEvent(Model):
    version: fields.Optional(fields.Str())
    security_types: fields.Optional(fields.List(fields.Str()))
    noauth: fields.Optional(fields.Bool())


class L9FTPEvent(Model):
    banner: fields.Optional(fields.Str())
    tls_supported: fields.Optional(fields.Bool())
    anonymous: fields.Optional(fields.Bool())


class L9SMTPEvent(Model):
    banner: fields.Optional(fields.Str())
    starttls: fields.Optional(fields.Bool())
    extensions: fields.Optional(fields.List(fields.Str()))


class L9TelnetEvent(Model):
    banner: fields.Optional(fields.Str())
    options: fields.Optional(fields.List(fields.Str()))
    auth_required: fields.Optional(fields.Bool())


class L9RedisEvent(Model):
    version: fields.Optional(fields.Str())
    mode: fields.Optional(fields.Str())
    os: fields.Optional(fields.Str())
    auth_required: fields.Optional(fields.Bool())


class L9MySQLEvent(Model):
    version: fields.Optional(fields.Str())
    protocol_version: fields.Optional(fields.Int())
    auth_plugin: fields.Optional(fields.Str())
    server_status: fields.Optional(fields.Str())


class L9PostgreSQLEvent(Model):
    version: fields.Optional(fields.Str())
    databases: fields.Optional(fields.List(fields.Str()))
    ssl_enabled: fields.Optional(fields.Bool())
    auth_method: fields.Optional(fields.Str())
    server_encoding: fields.Optional(fields.Str())
    client_encoding: fields.Optional(fields.Str())
    timezone: fields.Optional(fields.Str())
    max_connections: fields.Optional(fields.Int())


class L9MongoDBEvent(Model):
    version: fields.Optional(fields.Str())
    databases: fields.Optional(fields.List(fields.Str()))
    auth_required: fields.Optional(fields.Bool())
    wire_version: fields.Optional(fields.Int())


class L9MemcachedEvent(Model):
    version: fields.Optional(fields.Str())
    libevent: fields.Optional(fields.Str())
    curr_items: fields.Optional(fields.Int())
    total_items: fields.Optional(fields.Int())
    bytes: fields.Optional(fields.Int())
    max_bytes: fields.Optional(fields.Int())
    cmd_get: fields.Optional(fields.Int())
    cmd_set: fields.Optional(fields.Int())
    get_hits: fields.Optional(fields.Int())
    get_misses: fields.Optional(fields.Int())
    threads: fields.Optional(fields.Int())


class L9AMQPEvent(Model):
    protocol_major: fields.Optional(fields.Int())
    protocol_minor: fields.Optional(fields.Int())
    product: fields.Optional(fields.Str())
    version: fields.Optional(fields.Str())
    platform: fields.Optional(fields.Str())


class L9LDAPEvent(Model):
    naming_contexts: fields.Optional(fields.List(fields.Str()))
    supported_versions: fields.Optional(fields.List(fields.Str()))
    vendor_name: fields.Optional(fields.Str())
    vendor_version: fields.Optional(fields.Str())
    supported_sasl: fields.Optional(fields.List(fields.Str()))
    anonymous_bind: fields.Optional(fields.Bool())
    can_enumerate: fields.Optional(fields.Bool())


class L9SIPEvent(Model):
    version: fields.Optional(fields.Str())
    user_agent: fields.Optional(fields.Str())
    server: fields.Optional(fields.Str())
    allow: fields.Optional(fields.List(fields.Str()))
    supported: fields.Optional(fields.List(fields.Str()))


class L9RDPEvent(Model):
    product_version: fields.Optional(fields.Str())
    nla_required: fields.Optional(fields.Bool())
    ssl_enabled: fields.Optional(fields.Bool())
    hostname: fields.Optional(fields.Str())


class L9DNSEvent(Model):
    software: fields.Optional(fields.Str())
    version: fields.Optional(fields.Str())
    recursion: fields.Optional(fields.Bool())
    dnssec: fields.Optional(fields.Bool())
    zone_transfer: fields.Optional(fields.Bool())
    nameservers: fields.Optional(fields.List(fields.Str()))


class L9RTSPEvent(Model):
    server: fields.Optional(fields.Str())
    methods: fields.Optional(fields.List(fields.Str()))


# --- Main Event ---


class L9Event(Model):
    event_type: fields.Str()
    event_source: fields.Str()
    event_pipeline: fields.Optional(fields.List(fields.Str()))
    event_fingerprint: fields.Optional(fields.Str())
    ip: fields.Str()
    port: fields.Str()
    host: fields.Str()
    reverse: fields.Str()
    mac: fields.Optional(fields.Str())
    vendor: fields.Optional(fields.Str())
    transport: fields.Optional(fields.List(fields.Str()))
    protocol: fields.Str()
    http: fields.Nested(L9HttpEvent)
    summary: fields.Str()
    time: fields.DateTime()
    ssl: fields.Optional(fields.Nested(L9SSLEvent))
    # Protocol-specific events
    ssh: fields.Optional(fields.Nested(L9SSHEvent))
    vnc: fields.Optional(fields.Nested(L9VNCEvent))
    ftp: fields.Optional(fields.Nested(L9FTPEvent))
    smtp: fields.Optional(fields.Nested(L9SMTPEvent))
    telnet: fields.Optional(fields.Nested(L9TelnetEvent))
    redis: fields.Optional(fields.Nested(L9RedisEvent))
    mysql: fields.Optional(fields.Nested(L9MySQLEvent))
    postgresql: fields.Optional(fields.Nested(L9PostgreSQLEvent))
    mongodb: fields.Optional(fields.Nested(L9MongoDBEvent))
    memcached: fields.Optional(fields.Nested(L9MemcachedEvent))
    amqp: fields.Optional(fields.Nested(L9AMQPEvent))
    ldap: fields.Optional(fields.Nested(L9LDAPEvent))
    sip: fields.Optional(fields.Nested(L9SIPEvent))
    rdp: fields.Optional(fields.Nested(L9RDPEvent))
    dns: fields.Optional(fields.Nested(L9DNSEvent))
    rtsp: fields.Optional(fields.Nested(L9RTSPEvent))
    # Service events
    service: fields.Nested(L9ServiceEvent)
    leak: fields.Optional(fields.Nested(L9LeakEvent))
    tags: fields.Optional(fields.List(fields.Str()))
    geoip: fields.Nested(GeoLocation)
    network: fields.Nested(Network)


# --- Aggregation ---


class L9Aggregation(Model):
    summary: fields.Optional(fields.Str())
    ip: fields.Str()
    resource_id: fields.Str()
    open_ports: fields.List(fields.Str())
    leak_count: fields.Int()
    leak_event_count: fields.Int()
    events: fields.List(fields.Nested(L9Event))
    plugins: fields.List(fields.Str())
    geoip: fields.Nested(GeoLocation)
    network: fields.Nested(Network)
    creation_date: fields.DateTime()
    update_date: fields.DateTime()
    fresh: fields.Bool()

from serde import Model, fields


class L9HttpEvent(Model):
    root: fields.Str()
    url: fields.Str()
    status: fields.Int()
    # FIXME: must be int64
    length: fields.Int()
    header: fields.Dict(key=fields.Str(), value=fields.Str())
    title: fields.Str()
    favicon_hash: fields.Str()


class ServiceCredentials(Model):
    noauth: fields.Bool()
    username: fields.Str()
    password: fields.Str()
    key: fields.Str()
    # Bytes
    raw: fields.Str()


class SoftwareModule(Model):
    name: fields.Str()
    version: fields.Str()
    fingerprint: fields.Str()


class Software(Model):
    name: fields.Str()
    version: fields.Str()
    os: fields.Str()
    modules: fields.List(fields.Nested(SoftwareModule))
    fingerprint: fields.Str()


class Certificate(Model):
    cn: fields.Str()
    domain: fields.List(fields.Str())
    fingerprint: fields.Str()
    key_algo: fields.Str()
    key_size: fields.Int()
    issuer_name: fields.Str()
    not_before: fields.Time()
    not_after: fields.Time()
    valid: fields.Bool()


class GeoPoint(Model):
    lat: fields.Float()
    lon: fields.Float()


class GeoLocation(Model):
    continent_name: fields.Str()
    region_iso_code: fields.Str()
    city_name: fields.Str()
    country_iso_code: fields.Str()
    country_name: fields.Str()
    region_name: fields.Str()
    location: fields.Nested(GeoPoint)

class L9SSHEvent(Model):
    fingerprint: fields.Str()
    version: fields.Int()
    banner: fields.Str()
    motd: fields.Str()


class DatasetSummary(Model):
    rows: fields.Int()
    files: fields.Int()
    size: fields.Int()
    collections: fields.Int()
    infected: fields.Bool()
    ransom_notes: fields.List(fields.Str())


class L9LeakEvent(Model):
    stage: fields.Str()
    type: fields.Str()
    severity: fields.Str()
    dataset: fields.Nested(DatasetSummary)


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


class Network(Model):
    organization_name: fields.Str()
    asn: fields.Int()
    network: fields.Str()


class L9Event(Model):
    event_type: fields.Str()
    event_source: fields.Str()
    event_pipeline: fields.List(fields.Str())
    event_fingerprint: fields.Optional(fields.Str())
    ip: fields.Str()
    host: fields.Str()
    reverse: fields.Str()
    mac: fields.Optional(fields.Str())
    vendor: fields.Optional(fields.Str())
    transport: fields.Optional(fields.List(fields.Str()))
    protocol: fields.Str()
    http: fields.Nested(L9HttpEvent)
    summary: fields.Str()
    time: fields.Time()
    ssl: fields.Nested(L9SSLEvent)
    ssh: fields.Nested(L9SSHEvent)
    service: fields.Nested(L9ServiceEvent)
    leak: fields.Nested(L9LeakEvent)
    tags: fields.List(fields.Str())
    geoip: fields.Nested(GeoLocation)
    network: fields.Nested(Network)

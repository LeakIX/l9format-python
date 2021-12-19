import decimal
from serde import Model, fields

# Import from https://github.com/rossmacarthur/serde/commit/304884bca3c80e8b9a22a054b64dd94e3324b593#diff-dd2f65f16516311f0183377201a3d0b7894438787da732fc2bbc9c28cbde9fb8
# A helper function...
def round_decimal(
    decimal_obj: decimal.Decimal, num_of_places: int = 6
) -> decimal.Decimal:
    return decimal_obj.quantize(decimal.Decimal(10) ** -num_of_places).normalize()


class Decimal(fields.Instance):
    """
    A `~decimal.Decimal` field.
    This field serializes `~decimal.Decimal` objects as strings and
    deserializes string representations of Decimals as `~decimal.Decimal`
    objects.
    The resolution of the decimal can be specified. When not specified, the number
    is not rounded. When it is specified, the decimal is rounded to this number of
    decimal places upon serialization and deserialization.
    Note: When float type numbers are not rounded before serialization,
    they will be serialized in exact form, which as they are floats,
    is almost never the exact intended value,
    e.g. 0.2 = 0.20000000000000000000023
    Args:
        resolution (Union[int, bool]): The number of decimal places to round to.
        When None, rounding is disabled.
        **kwargs: keyword arguments for the `Field` constructor.
    """

    ty = decimal.Decimal

    def __init__(self, resolution=None, **kwargs):
        super(Decimal, self).__init__(self.__class__.ty, **kwargs)
        self.resolution = resolution

    def serialize(self, value: decimal.Decimal) -> str:
        if self.resolution is not None:
            value = round_decimal(value, num_of_places=self.resolution)
        return "{0:f}".format(value)

    def deserialize(self, value) -> decimal.Decimal:
        try:
            if self.resolution is not None:
                return round_decimal(
                    decimal.Decimal(value), num_of_places=self.resolution
                )

            return decimal.Decimal(value)
        except decimal.DecimalException:
            raise ValidationError("invalid decimal", value=value)


class L9HttpEvent(Model):
    root: fields.Str()
    url: fields.Str()
    status: fields.Int()
    # FIXME: must be int64
    length: fields.Int()
    header: fields.Optional(fields.Dict(key=fields.Str(), value=fields.Str()))
    title: fields.Str()
    favicon_hash: fields.Str()


class ServiceCredentials(Model):
    noauth: fields.Bool()
    username: fields.Str()
    password: fields.Str()
    key: fields.Str()
    # Bytes
    raw: fields.Optional(fields.Str())


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


class GeoPoint(Model):
    lat: Decimal()
    lon: Decimal()


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
    ransom_notes: fields.Optional(fields.List(fields.Str()))


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
    event_pipeline: fields.Optional(fields.List(fields.Str()))
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
    time: fields.DateTime()
    ssl: fields.Nested(L9SSLEvent)
    ssh: fields.Nested(L9SSHEvent)
    service: fields.Nested(L9ServiceEvent)
    leak: fields.Nested(L9LeakEvent)
    tags: fields.Optional(fields.List(fields.Str()))
    geoip: fields.Nested(GeoLocation)
    network: fields.Nested(Network)

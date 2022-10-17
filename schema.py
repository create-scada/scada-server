from marshmallow import Schema, fields


class DisplayPointSchema(Schema):
    id = fields.Integer()
    name = fields.Str()


class AlarmSchema(Schema):
    id = fields.Integer()
    name = fields.Str()
    point = fields.Str()
    compare = fields.Str()
    value = fields.Str()
    is_triggered = fields.Boolean()
    data_type = fields.Str()


class DeviceSchema(Schema):
    id = fields.Integer()
    rtu_address = fields.Str()
    device_address = fields.Str()
    schema = fields.Str()
    point_data = fields.Str()
    x = fields.Float()
    y = fields.Float()
    width = fields.Float()
    height = fields.Float()
    rotation = fields.Float()
    image_path = fields.Str()
    alarms = fields.List(fields.Nested(AlarmSchema()))
    display_points = fields.List(fields.Nested(DisplayPointSchema()))


class LocationSchema(Schema):
    id = fields.Integer()
    name = fields.Str()
    image_data = fields.Str()

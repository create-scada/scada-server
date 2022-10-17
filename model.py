import peewee as pw
from playhouse.shortcuts import ThreadSafeDatabaseMetadata
import env


class BaseModel(pw.Model):
    class Meta:
        if env.mode == 'production':
            database = env.config['database']
        else:
            database = ThreadSafeDatabaseMetadata


class Location(BaseModel):
    name = pw.CharField()
    image_data = pw.TextField()


class Device(BaseModel):
    rtu_address = pw.CharField()
    device_address = pw.CharField()
    schema = pw.CharField()
    point_data = pw.CharField(default='{}')
    x = pw.FloatField(default=0)
    y = pw.FloatField(default=0)
    width = pw.FloatField(default=0)
    height = pw.FloatField(default=0)
    rotation = pw.FloatField(default=0)
    image_path = pw.TextField()
    location = pw.ForeignKeyField(Location, backref='devices')


class Alarm(BaseModel):
    name = pw.CharField()
    point = pw.CharField()
    compare = pw.CharField()
    value = pw.CharField()
    is_triggered = pw.BooleanField(default=False)
    data_type = pw.CharField()
    device = pw.ForeignKeyField(Device, backref='alarms')


class DisplayPoint(BaseModel):
    name = pw.CharField()
    device = pw.ForeignKeyField(Device, backref='display_points')


Tables = [Location, Device, Alarm, DisplayPoint]

if env.mode == 'production':
    env.config['database'].create_tables(Tables)

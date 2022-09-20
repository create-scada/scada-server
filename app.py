import threading
from flask import Flask, request, jsonify, send_file
import peewee as pw
from playhouse.shortcuts import ThreadSafeDatabaseMetadata
from marshmallow import Schema, fields
from flask_cors import CORS
import json
import datetime
import dateutil.parser
from pymongo import MongoClient
import csv
import tempfile
import random
import matplotlib.pyplot as plt
import uuid
import sys
import os

app = Flask(__name__)
CORS(app)

port = sys.argv[1]
mode = sys.argv[2]

DbConnections = {}
Config = {}
Config['database'] = None
Config['historical_database'] = None

if mode == 'production':
    Config['database'] = pw.SqliteDatabase('lumen-production.db')
    Config['historical_database'] = MongoClient()['lumen-production']['sensors']

# db = pw.SqliteDatabase(':memory:')
# db.bind([Location, Device, Alarm, DisplayPoint])


class BaseModel(pw.Model):
    class Meta:
        if mode == 'production':
            database = Config['database']
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


Tables = [Location, Device, Alarm, DisplayPoint]

@app.route('/')
def index():
    return jsonify({})


@app.route('/connection', methods=['GET'])
def create_connection():
    myid = str(uuid.uuid1())
    database = pw.SqliteDatabase(f'tmp/{myid}.db')
    database.bind(Tables)
    database.create_tables(Tables)
    historical_database = MongoClient()['lumen-other'][f'sensors{myid}']
    DbConnections[myid] = {'database': database, 'historical_database': historical_database}
    return jsonify({'connId': myid})

@app.before_request
def before_req():
    if 'ConnId' in request.headers and request.headers['ConnId'] != '':
        conn_id = request.headers['ConnId']
        if conn_id in DbConnections:
            Config['database'] = DbConnections[conn_id]['database']
            Config['database'].bind(Tables)
            Config['historical_database'] = DbConnections[conn_id]['historical_database']

@app.after_request
def after_request(response):
    response.headers.add('Allow', 'OPTIONS, GET, HEAD')
    response.headers.add('Access-Control-Allow-Origin','*')
    response.headers.add('Access-Control-Allow-Headers','*')
    response.headers.add('Access-Control-Allow-Methods','DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT')
    response.headers.add('Vary', 'Origin')
    return response

@app.route('/locations/<location_id>', methods=['GET'])
def get_single_location(location_id):
    location = Location.get_by_id(location_id)
    if location == None:
        return 'Location not found', 404
    schema = LocationSchema()
    location_dict = schema.dump(location)
    return jsonify(location_dict)


@app.route('/locations', methods=['GET'])
def get_locations():
    result = []
    schema = LocationSchema()
    for location in Location.select():
        location_dict = schema.dump(location)
        result.append(location_dict)
    return jsonify(result)


@app.route('/locations', methods=['POST'])
def create_location():
    data = request.get_json()
    location = Location.create(
        name=data['name'],
        image_data=data['image_data']
    )
    location.save()
    schema = LocationSchema()
    location_dict = schema.dump(location)
    return jsonify(location_dict)


@app.route('/locations/<location_id>/devices', methods=['GET'])
def get_devices(location_id):
    location = Location.get_by_id(location_id)
    if location == None:
        return 'Location not found', 404
    result = []
    schema = DeviceSchema()
    for device in Device.select().where(Device.location == location):
        device_dict = schema.dump(device)
        device_dict['point_data'] = json.loads(device_dict['point_data'])
        result.append(device_dict)
    return jsonify(result)


@app.route('/locations/<location_id>/devices/<device_id>')
def get_single_device(location_id, device_id):
    location = Location.get_by_id(location_id)
    if location == None:
        return 'Location not found', 404
    device = Device.get_by_id(device_id)
    if device == None:
        return 'Device not found', 404
    schema = DeviceSchema()
    result = schema.dump(device)
    return jsonify(result)


@app.route('/locations/<location_id>/devices', methods=['POST'])
def create_device(location_id):
    data = request.get_json()
    location = Location.get_by_id(location_id)
    if location == None:
        return 'Location not found', 404
    device = Device.create(
        rtu_address=data['rtu_address'],
        device_address=data['device_address'],
        schema=data['schema'],
        image_path=data['image_path'],
        location=location
    )
    device.save()
    for display_point in data['display_points']:
        dp = DisplayPoint.create(name=display_point['name'], device=device)
        dp.save()

    device = Device.get_by_id(device.id)

    schema = DeviceSchema()
    device_dict = schema.dump(device)
    return jsonify(device_dict)


@app.route('/locations/<location_id>/devices/<device_id>/canvas-parms', methods=['PUT'])
def update_device(location_id, device_id):
    location = Location.get_by_id(location_id)
    if location == None:
        return 'Location not found', 404
    device = Device.get_by_id(device_id)
    if device == None:
        return 'Device not found', 404
    data = request.get_json()
    device.x = data['x']
    device.y = data['y']
    device.width = data['width']
    device.height = data['height']
    device.rotation = data['rotation']
    device.save()
    schema = DeviceSchema()
    device_dict = schema.dump(device)
    return jsonify(device_dict)


@app.route('/locations/<location_id>/devices/<device_id>/alarms', methods=['GET'])
def get_alarms(location_id, device_id):
    location = Location.get_by_id(location_id)
    if location == None:
        return 'Location not found', 404
    device = Device.get_by_id(device_id)
    if device == None:
        return 'Device not found', 404
    result = []
    schema = AlarmSchema()
    for alarm in Alarm.select().where(Alarm.device == device):
        alarm_dict = schema.dump(alarm)
        result.append(alarm_dict)
    return jsonify(result)


@app.route('/locations/<location_id>/devices/<device_id>/alarms', methods=['POST'])
def create_alarm(location_id, device_id):
    data = request.get_json()
    location = Location.get_by_id(location_id)
    if location == None:
        return 'Location not found', 404
    device = Device.get_by_id(device_id)
    if device == None:
        return 'Device not found', 404
    alarm = Alarm.create(
        name=data['name'],
        point=data['point'],
        compare=data['compare'],
        value=data['value'],
        data_type=data['data_type'],
        device=device
    )
    alarm.save()
    _trigger_alarms_for_all_devices()
    result = {'id': alarm.id}
    return jsonify(result)


def _numeric_alarm_is_triggered(point_value, alarm_value, comparison_operator):
    if comparison_operator == 'gt':
        if point_value > alarm_value:
            return True
    elif comparison_operator == 'lt':
        if point_value < alarm_value:
            return True
    elif comparison_operator == 'eq':
        if point_value == alarm_value:
            return True
    return False


def _discrete_alarm_is_triggered(point_value, alarm_value, comparison_operator):
    if comparison_operator == 'eq':
        if point_value == alarm_value:
            return True
    return False


def _trigger_alarms(rtu_address, device_address, point_data):
    devices = Device.select().where(
        (Device.rtu_address == rtu_address) &
        (Device.device_address == device_address)
    )
    for device in devices:
        for alarm in device.alarms:
            if alarm.data_type == 'number':
                point_value = float(point_data[alarm.point])
                alarm_value = float(alarm.value)
                if _numeric_alarm_is_triggered(point_value, alarm_value, alarm.compare):
                    alarm.is_triggered = 1
                else:
                    alarm.is_triggered = 0
                alarm.save()
            elif alarm.data_type == 'discrete':
                point_value = point_data[alarm.point]
                alarm_value = alarm.value
                if _discrete_alarm_is_triggered(point_value, alarm_value, alarm.compare):
                    alarm.is_triggered = 1
                else:
                    alarm.is_triggered = 0
                alarm.save()


def _trigger_alarms_for_all_devices():
    devices = Device.select()
    for device in devices:
        point_data = json.loads(device.point_data)
        if point_data == {}:
            continue
        _trigger_alarms(device.rtu_address,
                        device.device_address,
                        point_data)


def _create_sensor_reading(data):

    point_data_str = json.dumps(data['point_data'])
    devices = Device.select().where(
        (Device.rtu_address == data['rtu_address']) &
        (Device.device_address == data['device_address'])
    )
    for device in devices:
        device.point_data = point_data_str
        device.save()

    Config['historical_database'].insert_one(data)

    _trigger_alarms(data['rtu_address'],
                    data['device_address'],
                    data['point_data'])


@app.route('/sensor-readings', methods=['POST'])
def create_sensor_reading():
    data = request.get_json()
    data['date'] = datetime.datetime.now()
    _create_sensor_reading(data)

    return '', 201


@app.route('/schema', methods=['GET'])
def get_schema():
    with open('schema.json') as f:
        return f.read()


@app.route('/simulator-labs', methods=['GET'])
def get_simulator_labs():
    with open('simulator.json') as f:
        data = json.load(f)
        return jsonify(data)


@app.route('/simulator-labs', methods=['POST'])
def run_simulator_step():
    data = request.get_json()
    filename = f"{data['lab']}/{data['step']}.json"
    with open(filename) as f:
        step = json.load(f)
        for reading in step:
            _create_sensor_reading(reading)

        return '', 201


def _get_historical_data_query(rtu_address, device_address):
    query = {
        'rtu_address': rtu_address,
        'device_address': device_address,
    }

    for arg in request.args:
        if len(request.args.get(arg)) > 0:
            value = request.args.get(arg)
            comparison, name = arg.split('_')
            if name == 'date':
                value = dateutil.parser.parse(value)
                if comparison == 'gt':
                    query['date'] = {'$gt': value}
                elif comparison == 'lt':
                    query['date'] = {'$lt': value}
            else:
                if comparison == 'eq':
                    query[f'point_data.{name}'] = {'$eq': value}
                elif comparison == 'gt':
                    query[f'point_data.{name}'] = {'$gt': float(value)}
                elif comparison == 'lt':
                    query[f'point_data.{name}'] = {'$lt': float(value)}
    return query


@app.route('/historian/rtu-address/<rtu_address>/device-address/<device_address>/point/<point>/plot', methods=['GET'])
def get_historical_plot(rtu_address, device_address, point):

    query = _get_historical_data_query(rtu_address, device_address)
    x = []
    y = []

    for record in Config['historical_database'].find(query):
        date = dateutil.parser.parse(record['date'])
        x.append(date)
        y.append(record['point_data'][point])

    plt.clf()
    fig, ax = plt.subplots()
    fig.set_size_inches(14, 8)
    ax.plot(x, y)
    ax.xaxis_date()     # interpret the x-axis values as dates
    fig.autofmt_xdate()  # make space for and rotate the x-axis tick labels
    handle, filename = tempfile.mkstemp(".png")
    plt.savefig(filename)
    return send_file(filename, mimetype='image/png')


@app.route('/historian/rtu-address/<rtu_address>/device-address/<device_address>', methods=['GET'])
def get_historical_data(rtu_address, device_address):

    query = _get_historical_data_query(rtu_address, device_address)
    result = []
    for record in Config['historical_database'].find(query):
        del record['_id']
        result.append(record)

    return jsonify(result)


@app.route('/historian-export/rtu-address/<rtu_address>/device-address/<device_address>', methods=['GET'])
def get_historical_data_send_csv(rtu_address, device_address):

    query = _get_historical_data_query(rtu_address, device_address)
    result = []
    for record in Config['historical_database'].find(query):
        point_data = record['point_data']
        del record['_id']
        del record['point_data']
        record.update(point_data)
        result.append(record)

    handle, filename = tempfile.mkstemp(".csv")
    keys = ['date']
    keys += [x for x in result[0].keys() if x != 'date']

    with open(filename, "w") as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(result)

    return send_file(filename)


if __name__ == '__main__':
    try:
        os.mkdir('tmp')
    except FileExistsError:
        pass
    if mode == 'production':
        Config['database'].create_tables(Tables)
    app.run(debug=True, host="127.0.0.1", port=port, threaded = False)
    #app.run(debug=True, host="0.0.0.0", port=8080)

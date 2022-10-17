import threading
from flask import Flask, request, jsonify, send_file
import peewee as pw
from playhouse.shortcuts import ThreadSafeDatabaseMetadata
from marshmallow import Schema, fields
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
import env

port = sys.argv[1]
mode = sys.argv[2]
env.mode = mode

DbConnections = {}
env.config['database'] = None
env.config['historical_database'] = None

if mode == 'production':
    env.config['database'] = pw.SqliteDatabase('lumen-production.db')
    env.config['historical_database'] = MongoClient()[
        'lumen-production']['sensors']

from locations import locations
from historian import historian
from schema import LocationSchema, DeviceSchema, AlarmSchema, DisplayPointSchema
from model import Location, Device, Alarm, DisplayPoint, Tables

app = Flask(__name__)
app.register_blueprint(locations)
app.register_blueprint(historian)

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
    DbConnections[myid] = {'database': database,
                           'historical_database': historical_database}
    return jsonify({'connId': myid})


@app.before_request
def before_req():
    if 'ConnId' in request.headers and request.headers['ConnId'] != '':
        conn_id = request.headers['ConnId']
        if conn_id in DbConnections:
            env.config['database'] = DbConnections[conn_id]['database']
            env.config['database'].bind(Tables)
            env.config['historical_database'] = DbConnections[conn_id]['historical_database']


@app.after_request
def after_request(response):
    response.headers.add('Allow', 'OPTIONS, GET, HEAD')
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods',
                         'DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT')
    response.headers.add('Vary', 'Origin')
    return response


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

    env.config['historical_database'].insert_one(data)

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




@app.route('/historian-export/rtu-address/<rtu_address>/device-address/<device_address>', methods=['GET'])
def get_historical_data_send_csv(rtu_address, device_address):

    query = _get_historical_data_query(rtu_address, device_address)
    result = []
    for record in env.config['historical_database'].find(query):
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

    app.run(debug=True, host="127.0.0.1", port=port, threaded=False)
    #app.run(debug=True, host="0.0.0.0", port=8080)

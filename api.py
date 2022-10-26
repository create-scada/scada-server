from flask import Blueprint, jsonify, request, send_file
import uuid
import env
import peewee as pw
from model import Tables
from pymongo import MongoClient
import connections
import datetime
import json
import tempfile
import csv
from utils import create_sensor_reading, get_historical_data_query
api = Blueprint('api', __name__)

@api.route('/')
def index():
    return jsonify({})


@api.route('/connection', methods=['GET'], strict_slashes=False)
def create_connection():
    myid = str(uuid.uuid1())
    database = pw.SqliteDatabase(f'tmp/{myid}.db')
    database.bind(Tables)
    database.create_tables(Tables)
    historical_database = MongoClient()['lumen-other'][f'sensors{myid}']
    connections.DbConnections[myid] = {'database': database,
                           'historical_database': historical_database}
    return jsonify({'connId': myid})

@api.route('/sensor-readings', methods=['POST'], strict_slashes=False)
def create_lab_sensor_reading():
    data = request.get_json()
    data['date'] = datetime.datetime.now()
    create_sensor_reading(data)

    return '', 201

@api.route('/schema', methods=['GET'], strict_slashes=False)
def get_schema():
    with open('schema.json') as f:
        return f.read()

@api.route('/simulator-labs', methods=['GET'], strict_slashes=False)
def get_simulator_labs():
    with open('simulator.json') as f:
        data = json.load(f)
        return jsonify(data)

@api.route('/simulator-labs', methods=['POST'], strict_slashes=False)
def run_simulator_step():
    data = request.get_json()
    filename = f"{data['lab']}/{data['step']}.json"
    with open(filename) as f:
        step = json.load(f)
        for reading in step:
            create_sensor_reading(reading)

        return '', 201

@api.route('/historian-export/rtu-address/<rtu_address>/device-address/<device_address>', methods=['GET'], strict_slashes=False)
def get_historical_data_send_csv(rtu_address, device_address):

    query = get_historical_data_query(rtu_address, device_address, request)
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


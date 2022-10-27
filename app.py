from flask import Flask, request, jsonify, send_file
import peewee as pw
from pymongo import MongoClient
import sys
import os
import env
import connections

port = sys.argv[1]
mode = sys.argv[2]
env.mode = mode




from api.locations import locations
from api.historian import historian
from api.misc import misc
from model import Tables




def create_app():
    app = Flask(__name__)
    if mode == 'production':
        env.config['database'] = pw.SqliteDatabase('lumen-production.db')
        env.config['historical_database'] = MongoClient()[
            'lumen-production']['sensors']

    @app.before_request
    def before_req():
     if 'ConnId' in request.headers and request.headers['ConnId'] != '':
        conn_id = request.headers['ConnId']
        if conn_id in connections.DbConnections:
            env.config['database'] = connections.DbConnections[conn_id]['database']
            env.config['database'].bind(Tables)
            env.config['historical_database'] = connections.DbConnections[conn_id]['historical_database']

    @app.after_request
    def after_request(response):
        response.headers.add('Allow', 'OPTIONS, GET, HEAD')
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods',
                         'DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT')
        response.headers.add('Vary', 'Origin')
        return response
    return app

app = create_app()
app.register_blueprint(locations)
app.register_blueprint(historian)
app.register_blueprint(misc)

if __name__ == '__main__':
    try:
        os.mkdir('tmp')
    except FileExistsError:
        pass

    app.run(debug=True, host="127.0.0.1", port=port, threaded=False)
    #app.run(debug=True, host="0.0.0.0", port=8080)

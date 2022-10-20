from flask import Blueprint, jsonify, send_file, request
import dateutil.parser
import env
from utils import get_historical_data_query
import matplotlib.pyplot as plt
import tempfile


historian = Blueprint('historian', __name__, url_prefix='/historian')

@historian.route('/rtu-address/<rtu_address>/device-address/<device_address>/point/<point>/plot', methods=['GET'], strict_slashes=False)
def get_historical_plot(rtu_address, device_address, point):

    query = get_historical_data_query(rtu_address, device_address, request)
    x = []
    y = []

    for record in env.config['historical_database'].find(query):
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



@historian.route('/rtu-address/<rtu_address>/device-address/<device_address>', methods=['GET'], strict_slashes=False)
def get_historical_data(rtu_address, device_address):

    query = get_historical_data_query(rtu_address, device_address, request)
    result = []
    for record in env.config['historical_database'].find(query):
        del record['_id']
        result.append(record)

    return jsonify(result)


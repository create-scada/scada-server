from flask import Blueprint, jsonify, request
import json
from model import Location, Device, Alarm, DisplayPoint
from schema import LocationSchema, DeviceSchema, AlarmSchema, DisplayPointSchema
from utils import trigger_alarms_for_all_devices

locations = Blueprint('locations', __name__, url_prefix='/locations')


@locations.route('/<location_id>', methods=['GET'], strict_slashes=False)
def get_single_location(location_id):
    location = Location.get_by_id(location_id)
    if location == None:
        return 'Location not found', 404
    schema = LocationSchema()
    location_dict = schema.dump(location)
    return jsonify(location_dict)


@locations.route('/', methods=['GET'], strict_slashes=False)
def get_locations():
    result = []
    schema = LocationSchema()
    for location in Location.select():
        location_dict = schema.dump(location)
        result.append(location_dict)
    return jsonify(result)


@locations.route('/', methods=['POST'], strict_slashes=False)
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


@locations.route('/<location_id>/devices', methods=['GET'], strict_slashes=False)
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


@locations.route('/<location_id>/devices/<device_id>', strict_slashes=False)
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


@locations.route('/<location_id>/devices', methods=['POST'], strict_slashes=False)
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


@locations.route('/<location_id>/devices/<device_id>/canvas-parms', methods=['PUT'], strict_slashes=False)
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


@locations.route('/<location_id>/devices/<device_id>/alarms', methods=['GET'], strict_slashes=False)
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


@locations.route('/<location_id>/devices/<device_id>/alarms', methods=['POST'])
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
    trigger_alarms_for_all_devices()
    result = {'id': alarm.id}
    return jsonify(result)

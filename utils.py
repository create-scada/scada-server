from model import Location, Device, Alarm, DisplayPoint
import env

import json
import datetime
import dateutil.parser

def get_historical_data_query(rtu_address, device_address, request):
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


def trigger_alarms_for_all_devices():
    devices = Device.select()
    for device in devices:
        point_data = json.loads(device.point_data)
        if point_data == {}:
            continue
        _trigger_alarms(device.rtu_address,
                        device.device_address,
                        point_data)


def create_sensor_reading(data):

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


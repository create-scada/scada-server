import pytest
from app import app, database, Location, Device, Alarm, DisplayPoint
import datetime


@pytest.fixture
def client():
    with app.test_client() as client:
        database.create_tables([Location, Device, Alarm, DisplayPoint])
        yield client


def test_index(client):
    rv = client.get('/')
    data = rv.get_json()
    assert data == {}


def test_get_location_expect_empty(client):
    rv = client.get('/locations')
    data = rv.get_json()
    assert data == []


def test_create_location_expect_id(client):
    location = {
        'name': 'mylocation',
        'image_data': 'imgdata'
    }
    rv = client.post('/locations', json=location)
    data = rv.get_json()
    assert data['id'] == 1


def test_get_location_expect_one(client):
    rv = client.get('/locations')
    data = rv.get_json()
    assert len(data) == 1
    assert data[0]['name'] == 'mylocation'


def test_get_single_location_expect_one(client):
    rv = client.get('/locations/1')
    data = rv.get_json()
    assert data['name'] == 'mylocation'


def get_single_location_expect_404(client):
    rv = client.get('/locations/2')
    assert rv.status_code == 404


def test_get_device_expect_empty(client):
    rv = client.get('/locations/1/devices')
    data = rv.get_json()
    assert data == []


def test_create_device_expect_id_and_data(client):
    device = {
        'rtu_address': 'rtu1',
        'device_address': 'inverter1',
        'schema': 'basic-inverter',
        'image_path': '/images/basic-inverter.png',
        'display_points': [
            {'name': 'power'},
            {'name': 'status'}
        ]
    }
    rv = client.post('/locations/1/devices', json=device)
    data = rv.get_json()
    assert data['id'] == 1
    assert data['rtu_address'] == 'rtu1'
    assert len(data['display_points']) > 0
    assert data['display_points'][0]['name'] == 'power'


def test_get_devices_expect_one_and_data(client):
    rv = client.get('/locations/1/devices')
    data = rv.get_json()
    assert len(data) == 1
    assert data[0]['rtu_address'] == 'rtu1'
    assert len(data[0]['display_points']) > 0
    assert data[0]['display_points'][0]['name'] == 'power'


def test_get_device_expect_one(client):
    rv = client.get('/locations/1/devices/1')
    data = rv.get_json()
    assert data['rtu_address'] == 'rtu1'
    assert len(data['display_points']) > 0
    assert data['display_points'][0]['name'] == 'power'


def test_update_device_canvas_parms_expect_updated(client):
    rv = client.get('/locations/1/devices')
    data = rv.get_json()[0]
    data['x'] = 10
    data['y'] = 10
    rv = client.put('/locations/1/devices/1/canvas-parms', json=data)
    data = rv.get_json()
    assert data['x'] == 10
    assert data['y'] == 10


def test_get_schema_expect_json(client):
    rv = client.get('/schema')
    data = rv.get_json()
    assert data != {}


def test_set_point_data_expect_201(client):
    sensor_data = {
        'rtu_address': 'rtu1',
        'device_address': 'inverter1',
        'schema': 'basic-inverter',
        'point_data': {
            'power': 12.1897,
            'status': 'charging'
        }
    }
    rv = client.post('/sensor-readings', json=sensor_data)
    assert rv.status_code == 201


def test_get_point_data_expect_power(client):
    rv = client.get('/locations/1/devices')
    data = rv.get_json()[0]
    point_data = data['point_data']
    assert point_data['power'] > 12.0
    assert point_data['power'] < 13.0


def test_get_alarm_expect_empty(client):
    rv = client.get('/locations/1/devices/1/alarms')
    data = rv.get_json()
    assert data == []


def test_create_alarm_expect_id(client):
    alarm = {
        'name': 'High Power',
        'point': 'power',
        'compare': 'gt',
        'value': '12.0',
        'data_type': 'number'
    }
    rv = client.post('/locations/1/devices/1/alarms', json=alarm)
    data = rv.get_json()
    assert data['id'] == 1


def test_get_alarm_expect_one(client):
    rv = client.get('/locations/1/devices/1/alarms')
    data = rv.get_json()
    assert len(data) == 1
    assert data[0]['name'] == 'High Power'


def test_get_point_data_expect_high_power_alarm(client):
    rv = client.get('/locations/1/devices')
    data = rv.get_json()[0]
    assert data['alarms'][0]['is_triggered'] == True


def test_get_simulator_labs_expect_labs(client):
    rv = client.get('/simulator-labs')
    data = rv.get_json()
    assert len(data) > 0
    assert 'LAB_1' in data
    assert data['LAB_1'][0] == 'STEP_1'


def test_run_simulator_step_expect_updated_point_data(client):
    step = {
        'lab': 'LAB_1',
        'step': 'STEP_2'
    }
    rv = client.post('/simulator-labs', json=step)
    rv = client.get('/locations/1/devices')
    data = rv.get_json()[0]
    point_data = data['point_data']
    assert point_data['power'] < 500.0


def test_search_historian_expect_data(client):
    rv = client.get('/historian/rtu-address/rtu1/device-address/inverter1')
    data = rv.get_json()
    assert len(data) > 0
    assert data[0]['rtu_address'] == 'rtu1'
    assert 'power' in data[0]['point_data']
    assert 'date' in data[0]


def test_search_historian_with_query_expect_result(client):
    rv = client.get(
        '/historian/rtu-address/rtu1/device-address/inverter1?eq_status=charging')
    data = rv.get_json()
    assert len(data) > 0
    assert data[0]['rtu_address'] == 'rtu1'
    assert 'power' in data[0]['point_data']
    assert 'date' in data[0]


def test_search_historian_with_query_expect_empty(client):
    rv = client.get(
        '/historian/rtu-address/rtu1/device-address/inverter1?eq_status=charging')
    data = rv.get_json()
    assert len(data) > 0
    assert data[0]['rtu_address'] == 'rtu1'
    assert 'power' in data[0]['point_data']
    assert 'date' in data[0]


def test_search_historian_expect_csv(client):
    rv = client.get(
        '/historian-export/rtu-address/rtu1/device-address/inverter1?eq_status=charging')
    data = rv.data
    with open('/tmp/output.csv', "wb") as f:
        f.write(data)
    assert len(data) > 0

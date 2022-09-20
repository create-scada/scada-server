from vedirect import Vedirect
import requests

if __name__ == '__main__':
    
    ve = Vedirect('/dev/ttyUSB0', 60)
    reading = ve.read_data_single()
    print(reading)

    pv_voltage = float(reading['VPV']) / 1000.0 
    pv_power = float(reading['PPV'])
    pv_current = pv_power / pv_voltage

    ld_current = float(reading['IL']) / 1000.0
    ld_voltage = float(reading['V']) / 1000.0
    ld_power = ld_current * ld_voltage

    bt_current = float(reading['I']) / 1000.0
    bt_voltage = float(reading['V']) / 1000.0
    bt_power = bt_current * bt_voltage

    data = {
        'rtu_address': 'rtu1',
        'device_address': 'controller1',
        'point_data': {
            'pv_voltage': pv_voltage,
            'pv_current': pv_current,
            'pv_power':   pv_power,
            'ld_current': ld_current,
            'ld_voltage': ld_voltage,
            'ld_power':   ld_power,
            'bt_current': bt_current,
            'bt_voltage': bt_voltage,
            'bt_power':   bt_power
        }
    }


    print(data)
    response = requests.post('http://localhost:6000/sensor-readings', json=data)
    print(response)

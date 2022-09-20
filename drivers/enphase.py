import requests
import sys
import argparse

parser=argparse.ArgumentParser()

parser.add_argument('--system_id', help='Enphase System ID', required=True)
parser.add_argument('--api_key', help='Enphase API key', required=True)
parser.add_argument('--user_id', help='Enphase User ID', required=True)
parser.add_argument('--dst_url', help='Lumen Destination URL', required=True)
parser.add_argument('--rtu', help='Lumen RTU', required=True)
parser.add_argument('--device_address', help='Lumen Device Address', required=True)


args=parser.parse_args()

system_id = args.system_id
api_key = args.api_key
user_id = args.user_id
dst_url = args.dst_url
rtu = args.rtu
device_address = args.device_address


base_url = f"https://api.enphaseenergy.com/api/v2/systems/{system_id}/summary?key={api_key}&user_id={user_id}"

res = requests.get(base_url)
data = res.json()

pv_power = data['current_power'] / 1000.0

data = {
    'rtu_address': rtu,
    'device_address': device_address,
    'point_data': {
        'pv_power': pv_power,
    }
}

response = requests.post(dst_url, json=data)

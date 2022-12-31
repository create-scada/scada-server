import requests
import sys
import argparse
import json

parser = argparse.ArgumentParser()

parser.add_argument('--site_id', help='SolarEdge Site ID', required=True)
parser.add_argument('--api_key', help='SolarEdge API key', required=True)
parser.add_argument('--dst_url', help='Lumen Destination URL', required=True)
parser.add_argument('--rtu', help='Lumen RTU', required=True)
parser.add_argument('--device_address',
                    help='Lumen Device Address', required=True)

args = parser.parse_args()

site_id = args.site_id
api_key = args.api_key
dst_url = args.dst_url
rtu = args.rtu
device_address = args.device_address

base_url = f"https://monitoringapi.solaredge.com/site/{site_id}/overview?api_key={api_key}"

res = requests.get(base_url)
data = res.json()
pv_power = data['overview']['currentPower']['power'] / 1000.0

data = {
    'rtuAddress': rtu,
    'deviceAddress': device_address,
    'pointData': {
        'pv_power': pv_power,
    }

}

# data['pointData'] = json.dumps(data['pointData'])

response = requests.post(dst_url, json=data)

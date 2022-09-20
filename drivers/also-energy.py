import requests
import sys
import argparse

parser=argparse.ArgumentParser()

parser.add_argument('--site_id', help='AlsoEnergy Site ID', required=True)
parser.add_argument('--username', help='AlsoEnergy Username', required=True)
parser.add_argument('--password', help='AlsoEnergy Password', required=True)
parser.add_argument('--dst_url', help='Lumen Destination URL', required=True)
parser.add_argument('--rtu', help='Lumen RTU', required=True)
parser.add_argument('--device_address', help='Lumen Device Address', required=True)


args=parser.parse_args()

site_id = args.site_id
username = args.username
password = args.password
dst_url = args.dst_url
rtu = args.rtu
device_address = args.device_address

base_url = 'https://api.alsoenergy.com'

data = {
    'grant_type': 'password',
    'username': username,
    'password': password 
}

res = requests.post(f'{base_url}/Auth/token', data=data)
if res.status_code != 200:
    print('AUTH FAILURE')
    sys.exit()

result = res.json()
token = result['access_token']

headers = {
    "Authorization": f"Bearer {token}"
}

    
url = f'{base_url}/Sites/{site_id}?includeProductionData=true'
res = requests.get(url, headers=headers)
data = res.json()
pv_power = data['productionData']['nowKw']

url = f'{base_url}/Sites/{site_id}/Weather?daysOfForecast=0'
res = requests.get(url, headers=headers)
data = res.json()
temp = data['currentTemperatureFarenheight']
condition = data['currentCondition']

data = {
    'rtu_address': rtu,
    'device_address': device_address,
    'point_data': {
        'pv_power': pv_power,
        'temp':     temp,
        'skies':    condition
    }
}

response = requests.post(dst_url, json=data)

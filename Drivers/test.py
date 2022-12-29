import requests

data = {
    "rtuAddress": "rtu1",
    "deviceAddress": "inverter1",
    "schema": "basic-inverter",
    "pointData": "{ \"power\": 799.8343047604222, \"fan\": 4975.52934369038, \"status\": \"charging\" }",
    "date": "2020-05-01T09:00:00Z"
}

response = requests.post(
    'https://localhost:7033/api/readings', json=data, verify=False)
print(response.content)

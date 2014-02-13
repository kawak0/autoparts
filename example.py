#!/usr/bin/env python3
import json
import requests


url = 'http://www.oscaro.es/Catalog/Vehicle/ModelsJson'
codigoSeat = 192
data =  {'idOscManufacturer': codigoSeat }
headers = {'content-type': 'application/json'}
#headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = requests.post(url, data=json.dumps(data), headers=headers)

print (response.json())

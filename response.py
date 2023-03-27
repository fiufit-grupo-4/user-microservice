import requests
import json


tizziana_res = requests.get('http://127.0.0.1:8000')
print(tizziana_res.text)
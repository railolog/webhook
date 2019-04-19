from db_cities import CITIES
from weather_parser import *
import json

ready_coords = json.loads(open('ready_coords.json', 'rb').read())

print(ready_coords['набережные челны'])

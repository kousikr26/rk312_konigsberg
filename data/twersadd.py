import pandas as pd
import numpy as np
import json
import requests
import urllib3

towers=pd.read_csv('./data/towers_min.csv')
print(len(towers.index))

def getAdd(cur_lat,cur_lon):
    req_json = requests.get('https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=18&addressdetails=1'.format(
            lat=cur_lat, lon=cur_lon)).json()
    add_string = ""
    add_string +=" ,".join(req_json['address'].values())
    return add_string
    
    
towers['Address'] = towers.apply(lambda row : getAdd(row['lat'], row['lon']), axis=1)
print(towers.head())
towers.to_csv('./data/towers_final.csv')
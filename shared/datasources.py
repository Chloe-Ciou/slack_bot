from os import listdir, path
import pandas as pd
import urllib3
import random
import requests
from pathlib import Path
from .constants import unsplash
import json
http = urllib3.PoolManager()


def get_photos():
    '''
    :return: photo paths from directory
    '''
    dir_path = path.join(Path(__file__).parent.absolute(), f'photos')
    list_files = listdir(dir_path)
    return list(map(lambda f: path.join(dir_path, f), list_files))

def get_photo():
    photos = get_photos()
    return photos[random.randint(0, len(photos) - 1)]

def get_photo_unsplash(type):
    photos = requests.get(f'https://api.unsplash.com/search/photos?query={type}', headers={"Authorization":f"Client-ID {unsplash['chloeClient']}"})
    photos = json.loads(photos.text)
    print(photos['results'][random.randint(0, len(photos['results']) - 1)])
    return photos['results'][random.randint(0, len(photos['results']) - 1)]['urls']['thumb']

def get_excel():
    path = Path(__file__).parent.absolute()
    return pd.read_excel(path.join(path, 'botData.xlsx'), 'Sheet1', index_col=None)

def write_excel(data):
    file_path = Path(__file__).parent.absolute()
    writer = pd.ExcelWriter(path.join(file_path, 'botData.xlsx'))
    data.to_excel(writer, 'Sheet1', index=False)
    writer.save()

'''
example : how to read and write from botData.xlsx

>> read
data = get_excel();

>> write
data = data.append({'fieldName': 'date'}, ignore_index=True)
write_excel(data)
'''
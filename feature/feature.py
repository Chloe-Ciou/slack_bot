import requests
import pyowm

def get_weather():
    owm = pyowm.OWM('7c5cab8b6fecc7f08c4b82804db9b001')
    observation = owm.weather_at_place('Toronto,CA')
    w = observation.get_weather()
    print(w)
from prometheus_client import start_http_server, Gauge
import requests
from furl import furl
import yaml
import os
from os.path import join
import time
import logging

API_KEY = None
latlonlist = []


BASE_URL = "http://api.openweathermap.org/data/2.5/"

PORT = 9104

metrics = {}

specifications = [
    {'json_key': 'current/sunrise',
     'prometheus_key': 'weather_sunrise',
     'description': 'Sunrise Today'
     },
    {'json_key': 'current/sunset', 
     'prometheus_key': 'weather_sunset',
     'description': 'Sunset Today'
     },
    {'json_key': 'current/temp',
     'prometheus_key': 'weather_current_temperature',
     'description': 'Current Temperature'
     },
     {'json_key': 'current/feels_like',
      'prometheus_key': 'weather_current_temperature_feels_like',
     'description': 'Current Feels Like Temperature'
     },
     {'json_key': 'current/clouds',
     'prometheus_key': 'weather_current_cloud_coverage',
     'description': 'Cloud coverage (%)'
     },
     {'json_key': 'current/visibility',
      'prometheus_key': 'weather_current_visibility',
     'description': 'Current visibility (m)'
     },
     {'json_key': 'current/wind_speed',
     'prometheus_key': 'weather_current_wind_speed',
     'description': 'Current Wind Speed'
     },
     {'json_key': 'current/wind_gust',
     'prometheus_key': 'weather_current_wind_gust',
     'description': 'Current Wind Gust'
     },
     {'json_key': 'current/wind_deg',
      'prometheus_key': 'weather_current_wind_degree',
      'description': 'Current Wind Degree'
      },
     {'json_key': 'current/rain/1h',
     'prometheus_key': 'weather_current_rain_last_hour',
     'description': 'Rain in the last hour (mm)'
     },
     {'json_key': 'current/snow/1h',
      'prometheus_key': 'weather_current_snow_last_hour',
      'description': 'Snow in the last hour (mm)'
      },
    {'json_key': 'minutely',
     'prometheus_key': 'weather_next_hour_precipitation',
     'description': 'Rain Amount in the next hour'
     }
]

if __name__ == '__main__':


    for specification in specifications:
        g = Gauge(specification['prometheus_key'], 
                specification['description'])
        metrics[specification.get('json_key')] = g

        # print(metrics)


    with open(join(os.path.dirname(os.path.realpath(__file__)), "config.yml") )as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)
        API_KEY = config.get("api_key")
        latlonlist += config.get("latlons")

    # Start up the server to expose the metrics.
    start_http_server(PORT)
    logging.info(f"Starting server on {PORT}")

    while True:
        for latlon in latlonlist:

            f = furl(BASE_URL)

            f /= "onecall"

            f.args['appid'] = API_KEY
            f.args['units'] = 'imperial'
            f.args['lat'] = latlon[0]
            f.args['lon'] = latlon[1]

            js = requests.get(f.url).json()

            for json_key_combo in metrics:
                gauge = metrics[json_key_combo]
                json_key_array = json_key_combo.split("/")

                cur_json = js
                valid_key = True
                for key in json_key_array:
                    if key in cur_json:
                        cur_json = cur_json[key]
                    else:    
                        valid_key = False
                        gauge.set(-1)
                        break
        
                #If minutely, parse the minutely array to determine amount of rain over the next hour
                if valid_key and json_key_array[0] == 'minutely':
                    sum = 0
                    for element in cur_json:
                        sum += element['precipitation']
                    
                    gauge.set(sum)
                elif valid_key:
                    gauge.set(cur_json)
                    # print(f"{json_key_combo}: {cur_json}")

            current_conditions_js = js['current']

        time.sleep(60*3) # Sleep 3 minutes



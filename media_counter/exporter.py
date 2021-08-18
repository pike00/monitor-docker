import os, os.path

# simple version for working with CWD

from prometheus_client import start_http_server, Gauge
import requests
import time
import logging

logging.basicConfig(level=logging.INFO)

PORT = 9106
# Gauge : pihole_key
metrics = []

specifications = [
    {'prometheus_key': 'number_movies_downloaded',
     'description': 'Gives number of movies currently downloaded and sorted on disk'
     },
    {'prometheus_key': 'number_shows_downloaded',
     'description': 'Gives number of tv shows currently downloaded and sorted on disk'
     }
]


if __name__ == '__main__':
    # Take specifications and create metrics
    for specification in specifications:
        # print(specification)
        prometheus_key = specification['prometheus_key']
        description = specification['description']

        g = Gauge(prometheus_key, description)
        metrics.append(g)

    # Start up the server to expose the metrics.
    start_http_server(PORT)
    logging.info(f"Starting server on {PORT}")

    #Generate some requests.
    while True:
        n_movies = len([name for name in os.listdir('/mnt/media_storage/movies')])
        metrics[0].set(n_movies)
        
        n_shows = len([name for name in os.listdir('/mnt/media_storage/tv_shows')])
        metrics[1].set(n_shows)
        
        time.sleep(5)

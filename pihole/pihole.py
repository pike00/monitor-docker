from prometheus_client import start_http_server, Gauge
import requests
import time
import logging

logging.basicConfig(level=logging.INFO)

PIHOLE_BASE_URL = "https://pihole.wpike.com"
PORT = 9101
# Gauge : pihole_key
metrics = {}

specifications = [
    {'pihole_key': 'dns_queries_today',
     'prometheus_key': 'pihole_dns_queries',
     'description': 'Number of DNS Queries through Pihole today'
     },
    {'pihole_key': 'ads_blocked_today',
     'prometheus_key': 'pihole_ads_blocked',
     'description': 'Number of Ads blocked through Pihole today'
     },
    {'pihole_key': 'ads_percentage_today',
     'prometheus_key': 'pihole_ads_percentage',
     'description': 'Percentage of DNS queries that were blocked today'
     },
    {'pihole_key': 'unique_domains',
     'prometheus_key': 'pihole_unique_domains',
     'description': 'Number of Unique domains seen today'
     }
]


if __name__ == '__main__':
    # Take specifications and create metrics
    for specification in specifications:
        # print(specification)
        prometheus_key = specification['prometheus_key']
        description = specification['description']

        g = Gauge(prometheus_key, description)
        metrics[g] = specification['pihole_key']

    # Start up the server to expose the metrics.
    start_http_server(PORT)
    logging.info(f"Starting server on {PORT}")

    #Generate some requests.
    while True:
        js = requests.get(f"{PIHOLE_BASE_URL}/admin/api.php?summary").json()

        for gauge, pihole_key in metrics.items():
            value = int(float(js[pihole_key]))
            gauge.set(value)

        time.sleep(1)

from prometheus_client import start_http_server, Gauge
import requests
import time

# Create a metric to track time spent and requests made.
DNS_QUERIES = Gauge('pihole_dns_queries', 'Number of DNS Queries through Pihole today')
ADS_BLOCKED = Gauge('pihole_ads_blocked', 'Number of Ads blocked through Pihole today')
ADS_PERCENTAGE = Gauge('pihole_ads_percentage', 'Percentage of DNS queries that were blocked today')
UNIQUE_DOMAINS = Gauge('pihole_unique_domains', 'Number of Unique domains seen today')


def parse_str(str):
    return int(float(str.replace(",","")))




if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(9101)
    # Generate some requests.
    while True:
        time.sleep(5)
        js = requests.get("http://127.0.0.1:8001/admin/api.php?summary").json()
        print(js)

        DNS_QUERIES.set(parse_str(js['dns_queries_today']))
        ADS_BLOCKED.set(parse_str(js['ads_blocked_today']))
        ADS_PERCENTAGE.set(parse_str(js['ads_percentage_today']))
        UNIQUE_DOMAINS.set(parse_str(js['unique_domains']))

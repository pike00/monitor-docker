import sys
from subprocess import Popen, PIPE

from prometheus_client import start_http_server, Gauge, Info
import requests
import time
import pandas as pd

# Create a metric to track wireguard peer count (total) and active peers
WG_PEER_COUNT = Gauge('wg_peer_count', 'Number of Wireguard Peers in config file')
WG_PEER_COUNT_ACTIVE = Gauge('wg_peer_count_active', 'Number of Actuve Wireguard Peers')


# WG_PEERS = Info('wg_peers', 'List of Peers in key:value pairs')


def parse_str(str):
    return int(float(str.replace(",", "")))


def parse_wireguard(raw):
    interface_dict = None
    peers_array = []

    raw = raw[:-1]

    groups = raw.split("\n\n")
    for group in groups:
        lines = group.split("\n")
        lines = [line.strip() for line in lines]
        lines = [line.split(": ") for line in lines]
        cur_data = {line[0]: line[1] for line in lines}
        if "interface" in cur_data:
            interface_dict = cur_data
        elif "peer" in cur_data:

            # Checks to see if peer is active
            total_seconds = 0
            if 'latest handshake' in cur_data:
                # Parsing time to seconds
                time_unparsed = cur_data['latest handshake']
                if 'Now' not in time_unparsed:

                    time = time_unparsed.replace(" ago", "").split(", ")
                    for time_part in time:
                        value = time_part.split(" ")[0]
                        time_unit = time_part.split(" ")[1]
                        if 'second' in time_unit:
                            multiplier = 1
                        elif 'minute' in time_unit:
                            multiplier = 60
                        elif 'hour' in time_unit:
                            multiplier = 3600
                        else:
                            multiplier = 3600

                        total_seconds += int(value) * multiplier

            if 'latest handshake' in cur_data and total_seconds < 60 * 5:
                cur_data["active"] = True
            else:
                cur_data["active"] = False
            peers_array.append(cur_data)
        else:
            raise NotImplementedError()

    peers_df = pd.DataFrame.from_dict(peers_array)
    return interface_dict, peers_df


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(9102)

    # Generate some requests.
    while True:
        process = Popen(['wg'], stdout=PIPE, stderr=PIPE)
        process.wait()
        stdout, stderr = process.communicate()
        stdout = stdout.decode("utf-8")
        interface, peers = parse_wireguard(stdout)

        WG_PEER_COUNT.set(peers.shape[0])
        WG_PEER_COUNT_ACTIVE.set(sum(peers['active'] == True))

        time.sleep(5)

import sys
import json
from subprocess import Popen, PIPE

from prometheus_client import start_http_server, Gauge, Info
import requests
import time
import pandas as pd

# Create a metric to track wireguard peer count (total) and active peers
WG_PEER_COUNT = Gauge('wg_peer_count', 'Number of Wireguard Peers in config file')
WG_PEER_COUNT_ACTIVE = Gauge('wg_peer_count_active', 'Number of Actuve Wireguard Peers')

WG_DEVICE_HERMES = Info('wg_device_hermes',"Hermes Laptop Data")

WG_DEVICE_WILL_LAPTOP = Info('wg_device_will_laptop',"Will's Laptop Data")
WG_DEVICE_WILL_PHONE = Info('wg_device_will_iphone',"Will's iPhone Data")
WG_DEVICE_WILL_IPAD = Info('wg_device_will_ipad',"Will's iPad Data")


IP_MAP = {
    "10.0.0.1": "Calypso",
    "10.0.0.2": "Hermes",
    "10.0.1.1": "laptop.will.device",
    "10.0.1.2": "phone.will.device",
    "10.0.1.3": "ipad.will.device",
    "10.0.2.1": "laptop.aleisha.device",
    "10.0.2.2": "ipad.aleisha.device",
    "10.0.2.3": "phone.aleisha.device",
}



# WG_PEERS = Info('wg_peers', 'List of Peers in key:value pairs')


def parse_str(str):
    return int(float(str.replace(",", "")))

def parse_wireguard(str):
    lines = str.split("\n")
    data = {}
    interface = lines[0].split("\t")
    peers_raw = lines[1:]

    wg0 = {}
    wg0['private_key'] = interface[1]
    wg0['public_key'] = interface[2]
    wg0['listen_port'] = interface[3]
    wg0['fwmark'] = interface[4]

    peers = []

    for peer_raw in peers_raw:
        if peer_raw == "": continue
        peer_str = peer_raw.split("\t")
        peer = {}
        
        peer['public_key'] = peer_str[1]
        peer['preshared_key'] = peer_str[2]
        peer['endpoint'] = peer_str[3]
        peer['allowed_ips'] = peer_str[4]
        peer['name'] = IP_MAP[peer['allowed_ips'].split("/")[0]]
        peer['latest_handshake'] = peer_str[5]
        peer['transfer_rx'] = peer_str[6]
        peer['transfer_tx'] = peer_str[7]
        peer['persistent_keepalive'] = peer_str[8]

        peers.append(peer)
    
    wg0['peers'] = peers

    return wg0
    


if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(9102)

    # Generate some requests.
    while True:
        process = Popen(['wg','show','all','dump'], stdout=PIPE, stderr=PIPE)
        process.wait()
        stdout, stderr = process.communicate()
        stdout = stdout.decode("utf-8")
        
        data = parse_wireguard(stdout)
        peers = data['peers']

        WG_PEER_COUNT.set(len(peers))

        WG_DEVICE_HERMES.info(
            list(filter(lambda x: x['name'] == 'Hermes', peers))[0])
        WG_DEVICE_WILL_LAPTOP.info(
            list(filter(lambda x: x['name'] == 'laptop.will.device', peers))[0])
        WG_DEVICE_WILL_PHONE.info(
            list(filter(lambda x: x['name'] == 'phone.will.device', peers))[0])
        WG_DEVICE_WILL_IPAD.info(
            list(filter(lambda x: x['name'] == 'ipad.will.device', peers))[0])
            
        # WG_PEER_COUNT_ACTIVE.set(sum(peers['active'] == True))

        time.sleep(1)

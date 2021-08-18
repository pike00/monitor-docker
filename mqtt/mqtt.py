import paho.mqtt.client as mqtt
import json
from prometheus_client import start_http_server, Gauge
import logging
import yaml
import os
import pathlib


os.chdir(pathlib.Path(__file__).parent.absolute())
print(os.getcwd())

PORT = 9101


metrics = {}

owntracks_keys = None
with open("owntrack_keys.json") as keys_file:
    owntracks_keys = json.load(keys_file)

# Generates key of the form owntracks_device/id_mqttkey
def get_prometheus_key(device_id, mqtt_key):
    return f"owntracks_{device_id.replace('/', '_')}_{mqtt_key}"


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))

    # Only subscribe to owntracks topics
    client.subscribe("owntracks/#")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    device_id = "/".join(msg.topic.split("/")[1:])
    js = json.loads(msg.payload.decode("utf-8"))

    # Iterate over the payload message as json
    for key, value in js.items():
        # Generate the prometheus key
        prometheus_key = get_prometheus_key(device_id, key)

        # If it doesn't exist in the metrics dictionary, create it
        if prometheus_key not in metrics:
            
            # Get the description, or "" if it doesn't exist
            description = next(iter([key_dict.get("description","") 
                            for key_dict 
                            in owntracks_keys 
                            if key_dict.get("mqtt_key") == key]), "")

            # Create the gauge and add it to the dictionary
            g = Gauge(prometheus_key, description)
            metrics[prometheus_key] = g
            
        
        if isinstance(value, list):
            value = "_".join(value)

        if isinstance(value, float) | isinstance(value, int):
            # Metric should exist by now
            metrics[prometheus_key].set(value)
    

if __name__ == '__main__':

    config = None
    with open("config.yml") as config_file:
        config = yaml.load(config_file, Loader=yaml.SafeLoader)

    # Start up the server to expose the metrics.
    start_http_server(PORT)
    logging.info(f"Starting server on {PORT}")


    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    client.username_pw_set(config['connection']['username'],
                           config['connection']['password'])
    client.tls_set()
    client.connect(host = config['connection']['uri'], 
                   port = config['connection']['port'])

    client.loop_forever()

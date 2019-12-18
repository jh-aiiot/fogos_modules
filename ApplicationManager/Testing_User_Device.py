import paho.mqtt.client as mqtt
import json
import random
import configparser
import time
import numpy as np

config = configparser.ConfigParser()
config.read('configuration.ini')
num_devices = int(config.get('Topology', 'num_devices'))
num_contents = int(config.get('Topology', 'num_contents'))
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected OK")
    else:
        print("Bad connection Returned code=", rc)

def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))

def on_publish(client, userdata, mid):
    print("In on_pub callback mid= ", mid)
	
client = mqtt.Client("User_Device")
client.connect('www.versatile-broker-2.com', 1883)
client.on_connect = on_connect
client.on_publish = on_publish
# client.loop_forever()

client.publish('/configuration/join', json.dumps({"dummy": "dummy"}), 2)
client.loop()
time.sleep(10)
deviceID = num_devices
contentID = random.randint(1000, 1000 + num_contents -1)
client.publish('/utilization/request', json.dumps({"service_type": "videostreaming", "device_ID": str(deviceID), "content_ID": str(contentID), "resolution": "240"}), 2)
client.loop()

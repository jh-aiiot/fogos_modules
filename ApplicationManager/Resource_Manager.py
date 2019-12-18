import paho.mqtt.client as mqtt
import json
import random
from Topology_Generator import Generate
import time



def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected OK")
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))

def on_publish(client, userdata, mid):
    print("In on_pub callback mid= ", mid)
	


client = mqtt.Client("Resource_Manager")
client.connect('www.versatile-broker-2.com', 1883)
client.on_connect = on_connect
client.on_publish = on_publish
Nodes, Links = Generate()

while True:
    client.publish('/configuration/topology', json.dumps({"nodes": Nodes, "links": Links}), 1)
    client.loop() 
    time.sleep(10)
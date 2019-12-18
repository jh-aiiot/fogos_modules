import paho.mqtt.client as mqtt
import json
import random
from Topology_Generator import Generate
import time
import datetime


Nodes = []
Links = []
Num_nodes = 1
Data = None

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected OK")
    else:
        print("Bad connection Returned code=", rc)
    # client.subscribe("/utilization/status")
    client.subscribe("/configuration/join")
    client.subscribe("/configuration/status")
    

def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))

def on_publish(client, userdata, mid):
    print("In on_pub callback mid= ", mid)

def on_message(client, userdata, msg):
    payload = json.loads(msg.payload)
    if msg.topic == "/configuration/join":
        Nodes = userdata[0]
        Links = userdata[1]
        userdata[2] += 1
        Nodes, Links, Data = Generate(Nodes, Links, userdata[2], 0)
        userdata[0] = Nodes
        userdata[1] = Links
        userdata[3] = Data
        client.publish('/configuration/topology', json.dumps({"nodes": Nodes, "links": Links}), 1)
        client.loop()
    else:
        Data = userdata[3]
        now=datetime.datetime.now()
        print (now)
        print (Data)

Nodes, Links, _ = Generate()
client = mqtt.Client("Resource_Manager", userdata = [Nodes, Links, Num_nodes, Data])
client.connect('www.versatile-broker-2.com', 1883)
client.on_connect = on_connect
client.on_publish = on_publish
client.on_message = on_message
# while True:
client.publish('/configuration/topology', json.dumps({"nodes": Nodes, "links": Links}), 1)
client.loop_forever()
# client.loop() 
    # time.sleep(10)
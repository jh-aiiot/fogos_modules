import paho.mqtt.client as mqtt
import json
import random

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected OK")
        client.subscribe("/utilization/response/target")
    else:
        print("Bad connection Returned code=", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print(str(rc))

def on_publish(client, userdata, mid):
    print("In on_pub callback mid= ", mid)
	
def on_message(client, userdata, msg) :
    if msg.topic == "/utilization/response/target":
        payload = json.loads(msg.payload)
        print ("--RESPONSE--")
        print ("Device ID: " + str(payload['device_ID']))
        print ("Target ID: " + str(payload['target_ID']))


num_deivces = 20
num_contents = 20

client = mqtt.Client("Target_Device")
client.connect('www.versatile-broker-2.com', 1883)
client.on_connect = on_connect
client.on_message =  on_message
client.on_publish = on_publish

client.loop_forever()

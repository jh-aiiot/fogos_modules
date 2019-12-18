import paho.mqtt.client as mqtt
from algo2019_interface import Match
import argparse
import time
import configparser
import numpy as np
import json
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

config = configparser.ConfigParser()
config.read('configuration.ini')

num_devices = config.get('Topology', 'num_devices')
num_contents = config.get('Topology', 'num_contents')

class interpretor(object):
    def __init__(self, name):
        self.client = None # mqtt client 
        self.config = None

        self.request_node = []
        self.request_link = []
        self.topology_node = []
        self.topology_link = []
        self.payloads = []

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("connected OK")
            client.subscribe("/configuration/topology")
            client.subscribe("/utilization/request")
        else:
            print("Bad connection Returned code=", rc)

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print("subscribed: " + str(mid) + " " + str(granted_qos))

    def message_to_vnr(self, payload):
        
        vnr_node = []
        vnr_link = []
        if payload['service_type'] == self.config['service_type']['type']:
            num_nodes = int(self.config['service_type']['node'])
            linkval = int(self.config['res'][payload['resolution']]) # 링크의 최소치 
            cpu_list = []
            for i in range (num_nodes):
                cpu_list.append(int(self.config['cpu'][str(i)]))
            vnr_node.append(cpu_list)
            cid_list = []
            cid_list.append(int(payload['device_ID']))
            cid_list.append(int(payload['content_ID']))            
            vnr_node.append(cid_list)
            for i in range (num_nodes):
                bw_list = []
                for j in range (num_nodes):
                    if i == j:
                        bw_list.append(0)
                    elif i < j:
                        bw_list.append(int(linkval))
                    else:
                        bw_list.append(vnr_link[j][i])
                vnr_link.append(bw_list)
            
        return vnr_node, vnr_link

    def on_message(self, client, userdata, msg) :

        if msg.topic == "/configuration/topology":
            payload = json.loads(msg.payload)
            self.topology_node = payload['nodes']
            self.topology_link = payload['links']
            num_accepts, num_requests, results = Match(self.topology_node, self.topology_link, self.request_node, self.request_link)
        elif msg.topic == "/utilization/request":
            deviceID = num_devices
            contentID = 1000
            request = json.dumps({"service_type": "videostreaming", "device_ID": str(deviceID), "content_ID": str(contentID), "resolution": "240"})
            payload = json.loads(request)
            
            self.payloads.append(payload)
            node, link = self.message_to_vnr(payload)
            self.request_node.append(node)
            self.request_link.append(link)
            num_accepts, num_requests, results = Match(self.topology_node, self.topology_link, self.request_node, self.request_link)
            print ("Total Requests:", num_requests)
            print ("Total Accepted:", num_accepts)
            if results[-1][1] == "Accepted":
                MQTT_MSG=json.dumps({"service_type": self.payloads[-1]['service_type'], "device_ID": str(results[-1][2]), "target_ID": str(results[-1][3]), "resolution": self.payloads[-1]['resolution']})
                client.publish("/utilization/response/user", MQTT_MSG)
                client.publish("/utilization/response/target", MQTT_MSG)
            elif results[-1][1] == "Rejected":
                MQTT_MSG=json.dumps({"service_type": self.payloads[-1]['service_type'], "device_ID": self.payloads[-1]['device_ID'], "target_ID": "None", "resolution": self.payloads[-1]['resolution']})
                client.publish("/utilization/response/user", MQTT_MSG)


        
    def clientconnect(self, broker_addr, port):
        self.client = mqtt.Client("Application Manager")
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe
        
        self.client.connect(broker_addr, port=port)

        self.client.loop_forever()

if __name__ == '__main__':
    
    intp = interpretor("interpretor")
    intp.config = configparser.ConfigParser()
    intp.config.read('service_type_lookup_table.ini')
    intp.clientconnect('www.versatile-broker-2.com', 1883)


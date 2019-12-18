# -*- coding: utf-8 -*-
from flask_restful import Resource, reqparse
from flask import request
from flask_api import status
import json
import paho.mqtt.publish as publish
import sys
sys.path.insert(0, '../')
sys.path.insert(0, '../util')

from util import netif_util, pubkey_util
import random, hashlib
import device_config_db
import sub_ack
import mqtt_config

#mqtt_broker_addr = "iot.eclipse.org"
mqtt_broker_addr = mqtt_config.mqtt_broker_addr
mqtt_port = mqtt_config.mqtt_port


def join(tempDeviceID, uniqueCodes, relay, neighbors, pubKey):
    topic = '/configuration/join'
    payload = {"uniqueCodes": uniqueCodes, "relay": relay, "neighbors": neighbors, "pubKey": pubKey}

    print('[join] making payload...')
    print(' -', payload)
    print(' - publishing payload to topic:', topic+'/'+tempDeviceID)

    # Debug for checking time
    device_config_db.save_time_of_action('publish_{}'.format(topic+"/"+tempDeviceID))
    publish.single(topic+"/"+tempDeviceID, json.dumps(payload), hostname=mqtt_broker_addr, port=mqtt_port)

def leave(device_id, relay):
    topic = '/configuration/leave'
    payload = {"relay": relay}

    print('[leave] making payload...')
    print(' -', payload)
    print(' - publishing payload to topic:', topic+'/'+device_id)

    # Debug for checking time
    device_config_db.save_time_of_action('publish_{}'.format(topic+'/'+device_id))
    publish.single(topic+"/"+device_id, json.dumps(payload), hostname=mqtt_broker_addr, port=mqtt_port)

def register(device_id, register_id, register_list, relay):
    topic = '/configuration/register'
    payload = {
        'registerID': register_id,
        'registerList': register_list,
        'relay': relay }

    print('[register] making payload...')
    print(' -', payload)
    print(' - publishing payload to topic:', topic+'/'+device_id)

    # Debug for checking time
    device_config_db.save_time_of_action('publish_{}'.format(topic+'/'+device_id))
    publish.single(topic+"/"+device_id, json.dumps(payload), hostname=mqtt_broker_addr, port=mqtt_port)


def update(device_id, update_id, attributes):
    topic = '/configuration/update'
    payload = {
        'updateID': update_id,
        'id': device_id,
        'deregister':'false',
        'attributes': attributes,
        'relay': 'none'}

    print('[update] making payload...')
    print(' -', payload)
    print(' - publishing payload to topic:', topic+'/'+device_id)

    # Debug for checking time
    device_config_db.save_time_of_action('publish_{}'.format(topic+'/'+device_id))
    publish.single(topic+"/"+device_id, json.dumps(payload), hostname=mqtt_broker_addr, port=mqtt_port)

class EdgeConfigJoin(Resource):
    def get(self):
        # uniqueCodes
        uniqueCodes = netif_util.get_unique_codes()

        # relay
        relay = 'none'
        # 2017.11.26. Relays are not added yet.

        # neighbors
        # 2017.11.26. Neighbors are not added yet.
        neighbors = []

        # pubKey and temp_device_id
        pubKey = pubkey_util.get_pubkey()
        rand_num = random.randrange(0,4294967295)
        temp_str = '{}{}'.format(pubKey, rand_num)
        m = hashlib.md5()
        m.update(temp_str.encode('utf-8'))
        temp_device_id = m.hexdigest()

        # Remember temp_device_id.
        device_config_db.set_temp_device_id(temp_device_id)

        # Subscribe join_ack with the temp_device_id.
        sub_ack.sub_client.subscribe("/configuration/join_ack/"+temp_device_id)

        # Internal function for the API request
        join(temp_device_id, uniqueCodes, relay, neighbors, pubKey)

        device_config_db.set_device_status('join')

        # return values
        return {'error':0, 'temp_device_id':temp_device_id}, status.HTTP_200_OK


class EdgeConfigLeave(Resource):
    def get(self):
        device_id = device_config_db.get_device_id()

        # Relay: not used yet (2017.11.30)
        relay = 'none'

        # Internal function for the API request
        leave(device_id, relay)

        device_config_db.set_device_status('leave')

        # return values
        return {'error':0}, status.HTTP_200_OK


class EdgeConfigRegister(Resource):
    def post(self):
        # Parse post arguments
        json_data = request.get_json(force=True)
        register_list = json_data['register_list']
        print('[EdgeConfigRegister] recv JSON Data from user/service:\n', json_data)

        device_id = device_config_db.get_device_id()

        # Get registration list
        register_id = device_config_db.get_register_id(register_list)
        #device_config_db.add_register_list(register_list)
        for reg in register_list:
            index = device_config_db.add_register(reg)
            reg['index'] = str(index)

        # Relay: not used yet (2017.11.30)
        relay = 'none'

        # Internal function for the API request
        register(device_id, register_id, register_list, relay)

        # return values
        return {'error':0}, status.HTTP_200_OK


class EdgeConfigUpdate(Resource):
    def get(self):
        device_id = device_config_db.get_device_id()

        # TODO: get resources
        resources = 'none'

        # Internal function for the API request
        update(device_id, resources)

        # return values
        return {'error':0}, status.HTTP_200_OK

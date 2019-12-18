# -*- coding: utf-8 -*-
from flask_restful import Resource, reqparse
from flask import request
from flask_api import status
import paho.mqtt.publish as publish
import json
import sys
sys.path.insert(0, '../')


import device_config_db
import mqtt_config

def send_query(device_id, query):
    print('send query:', query)
    topic = '/utilization/query'
    if(query is not None):
        payload = query
        print('[query] making payload...')
        print(' -', payload)
        print(' - publishing payload to topic:', topic+'/'+device_id)

        # Debug for checking time
        device_config_db.save_time_of_action('publish_{}'.format(topic+"/"+tempDeviceID))
        publish.single(topic+"/"+device_id, json.dumps(payload), hostname=mqtt_config.mqtt_broker_addr, port=mqtt_config.mqtt_port)

class EdgeUtilQuery(Resource):
    def post(self):
        # Parse post arguments
        json_data = request.get_json(force=True)
        print('[EdgeUtilQuery] recv query from user/service:\n', json_data)

        if('query' in json_data):
            query_index = device_config_db.add_query(json_data['query'])
            json_data['query']['queryID'] = str(query_index)
            device_id = ''
            if('DeviceID' in json_data):
                device_id = json_data['DeviceID']
            else:
                device_id = device_config_db.get_device_id()
            send_query(device_id, json_data['query'])

        # return values
        return {'error':0}, status.HTTP_200_OK

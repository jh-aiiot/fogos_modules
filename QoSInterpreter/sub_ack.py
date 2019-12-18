# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
import device_config_db
import mqtt_config

mqtt_broker_addr = mqtt_config.mqtt_broker_addr
mqtt_port = mqtt_config.mqtt_port
#mqtt_broker_addr = "iot.eclipse.org"
sub_client = mqtt.Client()        # MQTT Client 오브젝트 생성

def subscribe_temp_device_id(client, temp_device_id):
    print('## subscribing temp_device_id...')

def on_connect (client, userdata, flags, rc):
    device_id = device_config_db.get_device_id()
    print ("connected with result code " +str(rc))

def on_message(client, userdata, msg):
    print('topic: '+msg.topic + '\nMessage: ' + str(msg.payload))

    # Debug for checking time
    device_config_db.save_time_of_action('sub_recv_{}'.format(msg.topic))

    if('/configuration/join_ack/' in msg.topic):
        print(' ## join_ack')
        split_topic = msg.topic.split('/')
        topic_temp_device_id = split_topic[len(split_topic)-1]
        if(topic_temp_device_id == device_config_db.get_temp_device_id()):
            payload = json.loads(str(msg.payload.decode('utf-8')))
            device_id = payload['id']
            print('  - received device_id:', device_id)
            device_config_db.set_device_id(topic_temp_device_id, device_id)

            sub_client.subscribe("/configuration/leave_ack/"+device_id)
            sub_client.subscribe("/configuration/update_ack/"+device_id)
            sub_client.subscribe("/configuration/register_ack/"+device_id)
            sub_client.subscribe("/utilization/reply/"+device_id)

    if('/configuration/register_ack/' in msg.topic):
        print(' ## register_ack')
        payload = json.loads(str(msg.payload.decode('utf-8')))

        if('idList' in payload.keys()):
            for item in payload['idList']:
                for key, value in item.items():
                    device_config_db.set_register_flex_id(key, value)

    if('/configuration/leave_ack/' in msg.topic):
        print(' ## leave_ack')

    if('/configuration/update_ack/' in msg.topic):
        print(' ## update_ack')


def connect_to_msg_bus(temp):
    # debug
    print(' - Threading temp variable: ', temp)

    #sub_client = mqtt.Client()
    sub_client.on_connect = on_connect
    sub_client.on_message = on_message
    sub_client.connect(mqtt_broker_addr, mqtt_port, 60)
    sub_client.loop_forever()

#
# Debug: test code
#
if __name__ == '__main__':
    connect_to_msg_bus()

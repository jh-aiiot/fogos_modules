# -*- coding: utf-8 -*-
import paho.mqtt.client as mqtt

tempDevID = 1

def on_connect (client, userdata, flags, rc):
    print ("connected with result code " +str(rc))
    client.subscribe("/configuration/join/#")
    client.subscribe("/configuration/leave/#")
    client.subscribe("/configuration/update/#")

def on_message(client, userdata, msg):
    print('topic:'+msg.topic + '\nMessage:' + str(msg.payload))

    if('/configuration/join/' in msg.topic):
        print(' - handling join')
    elif('/configuration/leave/' in msg.topic):
        print(' - handling leave')
    elif('/configuration/leave/' in msg.topic):
        print(' - handling update')
    else:
        print(' - invalid topic: ', msg.topic)

def connect_to_msg_bus():
    client = mqtt.Client()        # MQTT Client 오브젝트 생성
    client.on_connect = on_connect     # on_connect callback 설정
    client.on_message = on_message   # on_message callback 설정
    client.connect("iot.eclipse.org", 1883, 60)   # MQTT 서버에 연결
    client.loop_forever()

#
# Debug: test code
#
if __name__ == '__main__':
    connect_to_msg_bus()

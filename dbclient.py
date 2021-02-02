#!/usr/bin/env python
# -*- coding: utf-8 -*-

import paho.mqtt.client as mqtt
import MySQLdb
import  sys
import time, datetime
import json


VER = '1.3.0014'

# Define Variables
MQTT_HOST = "localhost"
MQTT_PORT = 1883
MQTT_USERNAME = None
MQTT_PASSWORD = None
TOPIC = "/dbquery/#"

SQL_HOST = "localhost"
SQL_PORT = 3306
SQL_USERNAME = "root"
SQL_PASSWORD = ""
SQL_DB = "mydb"
SQL_TABLE = None

LOG_FILE = None

def log(msg):
   if LOG_FILE is not None:
      filename =     str(time.strftime(LOG_FILE, time.localtime()))
      #logfile = open(filename, "a")
      #logfile.write(strtime+': '+msg+'\n')
      #logfile.close()

def debuglog(dbglevel, msg):
   log(msg)

def on_connect(client, userdata, message, rc):
   client.subscribe(TOPIC, 0)

def on_message(client, userdata, message):
    topicList = message.topic.split('/')
    print("message : " + message.topic + " " + str(message.qos) + " " + str(message.payload))
    try:
        db = MySQLdb.connect(SQL_HOST, SQL_USERNAME, SQL_PASSWORD, SQL_DB)
        cursor = db.cursor(MySQLdb.cursors.DictCursor)
        try:
            if topicList[2] == "insert" :
                # INSERT data
                data = json.loads(message.payload.decode("utf-8"))
                SQL_TABLE = data['table']
                length = len(data['data'])
                for i in range(0, length) :
                    query = "INSERT INTO {0} SET ".format(SQL_TABLE)
                    for index, (col, value) in enumerate(data['data'][i].items()):
                        if isinstance(value, list) :
                            value = [v.encode('unicode_escape') for v in value]
                            value = str(value).replace("\'", "\\\'")
                        if index == 0 :
                            query = query + "{0} = '{1}'".format(col, value)
                        else :
                            query = query + ", "
                            query = query + "{0} = '{1}'".format(col, value)
                    print(query)
                    cursor.execute(query)
                db.commit()
                if topicList[4] :
                    client.publish("/dbquery/iack/" + topicList[3] + "/" + topicList[4], json.dumps({"error" : 0}, separators=(',', ':')), 0)
                else :
                    client.publish("/dbquery/iack/" + topicList[3] + "/", json.dumps({"error" : 0}, separators=(',', ':')), 0)

            # SELECT data
            elif topicList[2] == "select" :
                data = json.loads(message.payload.decode("utf-8"))
                SQL_TABLE = data['table']
                query = "SELECT * FROM {0} WHERE ".format(SQL_TABLE)
                for index, (col, value) in enumerate(data['data'][0].items()):
                    if index == 0 :
                        query = query + "{0} = '{1}'".format(col, value)
                    else :
                        query = query + " and "
                        query = query + "{0} = '{1}'".format(col, value)
                print(query)
                cursor.execute(query)
                if topicList[4] :
                    client.publish("/dbquery/sack/" + topicList[3] + "/" + topicList[4], json.dumps({"error" : 0, "data" : cursor.fetchall()}, separators=(',', ':')), 0)
                else :
                    client.publish("/dbquery/sack/" + topicList[3] + "/", json.dumps({"error" : 0, "data" : cursor.fetchall()}, separators=(',', ':')), 0)

            # UPDATE data
            elif topicList[2] == "update" :
                data = json.loads(message.payload.decode("utf-8"))
                SQL_TABLE = data['table']
                length = len(data['data'])
                for i in range(0, length) :
                    query = "UPDATE {0} SET ".format(SQL_TABLE)
                    for index, (col, value) in enumerate(data['sdata'][i].items()):
                        if isinstance(value, list) :
                            value = [v.encode('unicode_escape') for v in value]
                            value = str(value).replace("\'", "\\\'")
                        if index == 0 :
                            query = query + "{0} = '{1}'".format(col, value)
                        else :
                            query = query + ", "
                            query = query + "{0} = '{1}'".format(col,value)
                    for index, (col, value) in enumerate(data['wdata'][0].items()):
                        if index == 0 :
                            query = query + " WHERE {0} = '{1}'".format(col, value)
                        else :
                            query = query + " and "
                            query = query + "{0} = '{1}'".format(col, value)
                    print(query)
                    cursor.execute(query)
                db.commit()
                if topicList[4] :
                    client.publish("/dbquery/uack/" + topicList[3] + "/" + topicList[4], json.dumps({"error" : 0}, separators=(',', ':')), 0)
                else :
                    client.publish("/dbquery/uack/" + topicList[3] + "/", json.dumps({"error" : 0}, separators=(',', ':')), 0)

            # DELETE data
            elif topicList[2] == "delete" :
                data = json.loads(message.payload.decode("utf-8"))
                SQL_TABLE = data['table']
                length = len(data['data'])
                for i in range(0, length) :
                    query = "DELETE FROM {0} WHERE ".format(SQL_TABLE)
                    for index, (col, value) in enumerate(data['data'][i].items()):
                        if index == 0 :
                            query = query + "{0} = '{1}'".format(col, value)
                        if index > 0 :
                            query = query + " and "
                            query = query + "{0} = '{1}'".format(col, value)
                    print(query)
                    cursor.execute(query)
                db.commit()
                if topicList[4] :
                    client.publish("/dbquery/dack/" + topicList[3] + "/" + topicList[4], json.dumps({"error" : 0}, separators=(',', ':')), 0)
                else : 
                    client.publish("/dbquery/dack/" + topicList[3] + "/", json.dumps({"error" : 0}, separators=(',', ':')), 0)

        except MySQLdb.Error as e:
            try:
                log("MySQL Error [{}]: {}".format(e.args[0], e.args[1]))

            except IndexError:
                log("MySQL Error: {}".format(e))

            # Rollback in case there is any error
            db.rollback()
            print("error adding record to mysql")
            #log('ERROR adding record to MYSQL')
            if topicList[4] :
                if topicList[2] == "insert" :
                    client.publish("/dbquery/iack/" + topicList[3] + "/" + topicList[4], json.dumps({"error" : 1}, separators=(',', ':')), 0)
                elif topicList[2] == "select" :
                    client.publish("/dbquery/sack/" + topicList[3] + "/" + topicList[4], json.dumps({"error" : 1, "data" : cursor.fetchall()}, separators=(',', ':')), 0)
                elif topicList[2] == "update" :
                    client.publish("/dbquery/uack/" + topicList[3] + "/" + topicList[4], json.dumps({"error" : 1}, separators=(',', ':')), 0)
                elif topicList[2] == "delete" :
                    client.publish("/dbquery/dack/" + topicList[3] + "/" + topicList[4], json.dumps({"error" : 1}, separators=(',', ':')), 0)
            else :
                if topicList[2] == "insert" :
                    client.publish("/dbquery/iack/" + topicList[3], json.dumps({"error" : 1}, separators=(',', ':')), 0)
                elif topicList[2] == "select" :
                    client.publish("/dbquery/sack/" + topicList[3], json.dumps({"error" : 1, "data" : cursor.fetchall()}, separators=(',', ':')), 0)
                elif topicList[2] == "update" :
                    client.publish("/dbquery/uack/" + topicList[3], json.dumps({"error" : 1}, separators=(',', ':')), 0)
                elif topicList[2] == "delete" :
                    client.publish("/dbquery/dack/" + topicList[3], json.dumps({"error" : 1}, separators=(',', ':')), 0)

    except IndexError:
        log("MySQL Error: {}".format(e))

    db.close()


def on_publish(client, userdata, mid):
   print("publish")

def on_subscribe(client, userdata, mid, granted_qos):
   print("subscribe")

def exit(status=0, message="end"):
   log(message)
   sys.exit(status)

if __name__ == "__main__":

   # Create MQTT client and set callback handler
   mqttc = mqtt.Client()
   mqttc.on_connect = on_connect
   mqttc.on_message = on_message
   mqttc.on_publish = on_publish
   mqttc.on_subscribe = on_subscribe

   # Attempt to connect to broker. If this fails, issue CRITICAL
   try:
      mqttc.connect(MQTT_HOST, MQTT_PORT, 60)
   except Exception as e:
      exit(3, 'Connection to {}:{} failed: {}'.format(MQTT_HOST, MQTT_PORT, str(e)))

   # Main loop as long as no error occurs
   mqttc.loop_forever()

# -*- coding: utf-8 -*-
from flask import Flask, render_template, request
from flask_restful import Resource, Api, reqparse
from flask_api import status
import requests
import sys
import threading
import json

sys.path.insert(0, './Edge_Config_API')
sys.path.insert(0, './Edge_Util_API')
sys.path.insert(0, './QoS_Interpreter')

from edge_config_api import EdgeConfigJoin
from edge_config_api import EdgeConfigLeave
from edge_config_api import EdgeConfigRegister
from edge_config_api import EdgeConfigUpdate
from edge_util_api import EdgeUtilQuery
import sub_ack
import device_config_db
import qos_interpreter
from util import hash_util

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fogos'
api = Api(app)

server_port = 9090

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/config', methods=['GET'])
def view_edge_configuration():
    device_status = device_config_db.get_device_status()
    register_list = device_config_db.get_register_list()
    print('Device status: ', device_status)
    return render_template('edge_config.html',
                            device_status=device_status,
                            register_list=register_list)

@app.route('/config/join', methods=['GET'])
def join_and_view_edge_config():
    #request.form[]
    url = 'http://localhost:'+str(server_port)+'/api/configuration/join'
    response = requests.get(url)
    device_status = device_config_db.get_device_status()
    device_id = device_config_db.get_device_id()
    register_list = device_config_db.get_register_list()
    print('Device status: ', device_status)
    return render_template('edge_config.html',
                            device_status=device_status,
                            register_list=register_list)

@app.route('/config/leave', methods=['GET'])
def leave_and_view_edge_config():
    #request.form[]
    url = 'http://localhost:'+str(server_port)+'/api/configuration/leave'
    response = requests.get(url)
    device_status = device_config_db.get_device_status()
    device_id = device_config_db.get_device_id()
    print('Device status: ', device_status)
    return render_template('edge_config.html',
                            device_status=device_status,
                            register_list=None)

@app.route('/config/register', methods=['POST'])
def register_and_view_edge_config():
    register_type = request.form['register_type']
    category = request.form['category']
    attributes = request.form['attributes']
    cache = request.form['cache']
    segment = request.form['segment']
    collisionAvoid = request.form['collisionAvoid']

    str_to_hash = '{}{}{}'.format(register_type, category, attributes)
    register_hash = hash_util.get_hash(str_to_hash)

    url = 'http://localhost:'+str(server_port)+'/api/configuration/register'
    json_data = {
        'register_list':[
            {
                'index':1,
                'hash':register_hash,
                'registerType':register_type,
                'category':category,
                'attributes':attributes,
                'cache':cache,
                'segment':segment,
                'collisionAvoid':collisionAvoid
            }
        ]
    }

    response = requests.post(url, json=json_data)
    device_status = device_config_db.get_device_status()
    register_list = device_config_db.get_register_list()
    print('Device status: ', device_status)
    print('Register List in DB:',register_list)
    return render_template('edge_config.html',
                            device_status=device_status,
                            register_list=register_list)


@app.route('/util', methods=['GET'])
def view_edge_utilization():
    device_status = device_config_db.get_device_status()
    return render_template('edge_util.html',
                            device_status=device_status)

@app.route('/util/query', methods=['POST'])
def query_and_view_edge_util():
    queryType = request.form['queryType']
    category = request.form['category']
    order = request.form['order']
    desc = request.form['desc']
    limit = request.form['limit']
    requirements = request.form['requirements']
    additionalFields = request.form['additionalFields']

    device_id = device_config_db.get_device_id()

    url = 'http://localhost:'+str(server_port)+'/api/utilization/query'
    json_data = {
        'query':{
            'queryID':1,
            'queryType':queryType,
            'category':category,
            'order':order,
            'desc':desc,
            'limit':limit,
            'requirements':requirements,
            'additionalFields':additionalFields
        },
        'DeviceID':device_id
    }
    response = requests.post(url, json=json_data)

    device_status = device_config_db.get_device_status()
    return render_template('edge_util.html',
                            device_status=device_status)


@app.route('/interpret', methods=['GET'])
def view_qos_interpreter_form():
    device_status = device_config_db.get_device_status()
    print('Device status: ', device_status)
    return render_template('qos_interpreter.html',
                            interpreted=False,
                            device_status=device_status)

@app.route('/util/qos_interpretation', methods=['POST'])
def run_qos_interpreter_and_view_result():
    service_type = request.form['service_type']
    service_name = request.form['service_name']
    requirements = request.form['requirements']
    preferences = request.form['preferences']

    #Debug
    print(' ')

    json_data = {
        'service_type':service_type,
        'service_name':service_name,
        'requirements':json.loads(requirements),
        'preferences':json.loads(preferences)
    }


    device_id = device_config_db.get_device_id()
    device_status = device_config_db.get_device_status()

    temp_result = qos_interpreter.interpret(json_data)
    output_result = []

    #Debug
    print(' ')
    print('--------------------------------------------------------')
    print('* QoS Interpretation Result:')
    print(temp_result)
    print('--------------------------------------------------------')

    if('delay' in temp_result.keys()):
        output_result.append(temp_result['delay'])
    if('jitter' in temp_result.keys()):
        output_result.append(temp_result['jitter'])
    if('bandwidth' in temp_result.keys()):
        output_result.append(temp_result['bandwidth'])
    if('lossrate' in temp_result.keys()):
        output_result.append(temp_result['lossrate'])

    return render_template('qos_interpreter.html',
                            interpreted=True,
                            device_status=device_status,
                            input_desc=json_data,
                            output_result=output_result)



# List of REST APIs
api.add_resource(EdgeConfigJoin, '/api/configuration/join')
api.add_resource(EdgeConfigLeave, '/api/configuration/leave')
api.add_resource(EdgeConfigRegister, '/api/configuration/register')
api.add_resource(EdgeConfigUpdate, '/api/configuration/update')
api.add_resource(EdgeUtilQuery, '/api/utilization/query')

if __name__ == '__main__':
    # Reset database.
    device_config_db.create_db()

    # Thread for subscription
    th_sub = threading.Thread(target=sub_ack.connect_to_msg_bus, args=('test1',))
    th_sub.daemon = True
    th_sub.start()

    if(len(sys.argv) == 1):
        app.run(debug=True, host='0.0.0.0', port=9090, threaded=True)
    else:
        try:
            server_port = int(sys.argv[1])
            app.run(debug=True, host='0.0.0.0', port=server_port, threaded=True)
        except:
            print('[Error] Invalid port number! Pleack check the port number you typed: ', sys.argv[1])

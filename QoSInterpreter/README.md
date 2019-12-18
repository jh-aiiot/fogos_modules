# QoS Interpreter for KAIST FogOS Project

The main role of QoS Interpreter is to convert from service/user descriptions about a requesting service to a set of network QoS parameters.

## Prerequisites
* Python 3.x
* Flask (pip3 installation package: flask)
* Flask-RESTful (pip3 installation package: flask-restful)
* Flask-API (pip3 installation package: flask-api)
* requests (pip3 installation package: requests)
* paho-mqtt (pip3 installation package: paho-mqtt)
* OpenSSH (# apt-get install ssh): You should make a public key file (id_rsa.pub) in $HOME/.ssh/.

## Usage
Run 'main.py' with a port number as an argument.
```
$ python main.py [PORT]
```
If you do not specify the port number, it will run as a port 9090 open.
Port number below 1024 would ask you a root permission. It would rather set the number more than 1024.

## Note
All knowledge representation files (.csv) must be at the root directory, not in the QoS_Interpreter directory.

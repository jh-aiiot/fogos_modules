from nodes import *
import random
import tensorflow as tf
tf.logging.set_verbosity(tf.logging.ERROR)
import numpy as np
import matplotlib.pyplot as plt

node_num = 100

def set_cpu():
    cpu_list = [2.4, 3.6]
    s_cpu = random.choice(cpu_list)
    return s_cpu

def set_ram():
    ram_list = [2.0, 4.0, 8.0]
    s_ram = random.choice(ram_list)

    return s_ram

def set_storage():
    storage_list = [128.0, 256.0, 512.0, 1024.0]
    s_storage = random.choice(storage_list)

    return s_storage

def set_core():
    core = []
    cpu = set_cpu()
    ram = set_ram()
    storage = set_storage()

    core.append(cpu)
    core.append(ram)
    core.append(storage)

    return core

def init_information():
    state = []
    core = set_core()
    for c in range(len(core)):
        state.append(core[c])
    parse_information()
    return state


def parse_information(f=None):
    if f is None:
        for i in range(node_num):
            ClientNode().generate()
            ResourceNode().generate()

core = []
state = []

cpu_usage = None
memory_usage = None
storage_usage = None
client_num = None
network_status = None
service_num = None
location_info = None

init_information()

cpu_usage = np.array([n.cpu for n in resource_node_list])
memory_usage = np.array([n.memory for n in resource_node_list])
storage_usage = np.array([n.storage for n in resource_node_list])
client_num = np.array([n.client_num for n in resource_node_list])
network_status = np.array([n.network_status for n in resource_node_list])
service_num = np.array([n.service_num for n in client_node_list])
location = np.array([n.location for n in client_node_list])

throughput = np.array([random.randint(0, 50) for n in resource_node_list])

from sklearn.model_selection import train_test_split
X_train,X_test,y_train,y_test=train_test_split(client_num, network_status, random_state=42,
                                               train_size=0.8, test_size=0.2)

layer_0 = tf.keras.layers.Dense(units = 1, input_shape=[1])
model = tf.keras.Sequential([layer_0])
model = tf.keras.Sequential([tf.keras.layers.Dense(units=1, input_shape=[1])])
model.compile(loss='mean_squared_error', optimizer=tf.keras.optimizers.Adam(0.1))


#Training phase
trained_model = model.fit(X_train, y_train, epochs=1000, verbose=False)

print ("Training complete")

y_pred = model.predict(X_test)
print('Actual Values\tPredicted Values')
print(y_test,'   ',y_pred.reshape(1,-1))

from sklearn.metrics import r2_score
r2_score(y_test,y_pred)

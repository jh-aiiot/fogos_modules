# This file explains the class structure of nodes

import random

node_list = []
resource_node_list = []
client_node_list = []
def give_new_id():
    new = False
    while not new:
        node_id = random.randint(0,100000)
        new = True
        for n in node_list:
            if n.id == node_id:
                new = False
    return node_id

class Node:
    def __init__(self):
        self.id = give_new_id()
        node_list.append(self)

class ResourceNode(Node):
    def __init__(self, cpu_usage=None, memory_usage=None, storage_usage=None, client_num=None, network_status=None):
        Node.__init__(self)
        self.cpu = cpu_usage
        self.memory = memory_usage
        self.storage = storage_usage
        self.client_num = client_num
        self.network_status = network_status
        resource_node_list.append(self)
    def generate(self):
        self.cpu = random.randint(0, 100)
        self.memory = random.randint(0,100)
        self.storage = random.randint(0,100)
        self.client_num = random.randint(0, 100)
        self.network_status = random.randint(0,5)


class ClientNode(Node):
    def __init__(self, node_id=None, service_num=None, location_info=None):
        Node.__init__(self)
        self.id = node_id
        self.service_num = service_num
        self.location = location_info
        client_node_list.append(self)
    def generate(self):
        self.service_num = random.randint(0, 10)
        self.location = random.randint(0,100)

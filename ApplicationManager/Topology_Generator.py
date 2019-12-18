import random
import configparser
import pandas

config = configparser.ConfigParser()
config.read('configuration.ini')

num_devices = 1
num_contents = int(config.get('Topology', 'num_contents'))
random.seed(5)


def Generate(Nodes=[], Links=[], Num_nodes=1, flag=0):
    Att_list = ["ifaceType", "hwAddress", "ipv4", "CPU", "Memory"]
    Node_list = ["0xF681", "0x2A3B", "0x4723", "0xE889", "0x34C3", "0x8E2D", "0x5555"]
    Data_list = [["wifi", "62:f0:0c:47:25:10", "143.248.200.21","3.2", "2.2"],
                ["wifi", "c0:90:0b:d5:5e:b5", "143.248.200.13","3.2", "2.2"],
                ["wifi", "2b:36:41:c4:19:34", "143.248.200.2","3.2", "2.3"],
                ["wifi", "10:b7:48:02:70:8a", "143.248.200.62","3.2", "2.4"],
                ["wifi", "8d:b1:29:f5:0e:e7", "143.248.200.8","3.6", "29.8"],
                ["wifi", "1d:25:d4:7e:22:1f", "143.248.200.11","3.2", "17.7"],
                ["wifi", "ef:84:fd:f7:37:1d", "143.248.200.2","2.8", "12.4"]]
    substrate_data = pandas.DataFrame(Data_list, Node_list, Att_list)

    min_CPU = 70
    max_CPU = 100
    min_bandwidth = 300
    max_bandwidth = 500
    
    substrate_node = []
    substrate_link = []

    if len(Nodes):
        cpu_list = Nodes[0]
        cid_list = Nodes[1]
        
        # for cpu_index in range(num_devices):
        cpu = random
        cpu_list.append(random.randint(min_CPU, max_CPU))
        cid = random.sample(range(1000, num_contents + 1000), 5)
        cid.append(Num_nodes-1)
        cid_list.append(cid)

        substrate_node.append(cpu_list)
        substrate_node.append(cid_list)
    else:
        cpu_list = [] 
        cid_list = []
        for cpu_index in range(num_devices):
            if cpu_index < 2:
                cpu_list.append(cpu_index * 10 + 15)
            else:
                cpu_list.append(random.randint(min_CPU, max_CPU))
            cid = random.sample(range(1000, num_contents + 1000), 5)
            cid.append(cpu_index)
            cid_list.append(cid)
        
        substrate_node.append(cpu_list)
        substrate_node.append(cid_list)

    if len(Links):

        for bw_index1 in range(Num_nodes):
            bw_list = []
            for bw_index2 in range(Num_nodes):
                if bw_index1 < Num_nodes-1 and bw_index2 < Num_nodes-1:
                    bw_list.append(Links[bw_index1][bw_index2]) 
                elif bw_index1 == bw_index2:
                    bw_list.append(0)
                elif bw_index1 < bw_index2:
                    if bw_index1 < 2:
                        bw_list.append(random.randint(min_bandwidth, max_bandwidth))
                    else:
                        bw_list.append(0)
                else:
                    bw_list.append(substrate_link[bw_index2][bw_index1])
            substrate_link.append(bw_list)     
    else:    
        for bw_index1 in range(num_devices):
            bw_list = []
            for bw_index2 in range(num_devices):
                if bw_index1 == bw_index2:
                    bw_list.append(0)
                elif bw_index1 < bw_index2:
                    if bw_index1 + bw_index2 == 5:
                        bw_list.append(0)
                    else:
                        bw_list.append(random.randint(min_bandwidth, max_bandwidth))
                    # else:
                        # bw_list.append(0)
                else:
                    bw_list.append(substrate_link[bw_index2][bw_index1])
            substrate_link.append(bw_list)
    substrate_data = substrate_data[:Num_nodes]
    return substrate_node, substrate_link, substrate_data

if __name__ == '__main__':
    
    node, link, data = Generate()
    print (node)
    print (link)
    print (data)
from __future__ import division
import networkx as nx
import matplotlib.pyplot as plt
import string
from collections import deque
from itertools import islice
import time
import numpy
import random


def GenerateVN_Nodes(network, node_attributes):
    for node_index in range(len(node_attributes[0])):
        network.add_node(alphabet_dict[node_index + 1], cpu=node_attributes[0][node_index],
                         content=node_attributes[1][node_index])

def GenerateSN_Nodes(network, node_attributes):
    for node_index in range(len(node_attributes[0])):
        network.add_node(alphabet_dict[node_index + 1], cpu=node_attributes[0][node_index],
                         content=node_attributes[1][node_index])


def GenerateEdges(network, edge_attributes):
    for row in range(len(edge_attributes)):
        for column in range(len(edge_attributes[0])):
            if edge_attributes[row][column] > 0:
                network.add_edge(alphabet_dict[row + 1], alphabet_dict[column + 1], bw=edge_attributes[row][column])

def GetRevenue(vnr_list):
    for vnr_index in range(len(vnr_list)):
        revenue_components = []
        for node in vnr_list[vnr_index].nodes():
            revenue_components.append(vnr_list[vnr_index].nodes[node]['cpu'])  # change something here?????
            # revenue_components.append(vnr_list[vnr_index].nodes[node]['content'])

        for edge in vnr_list[vnr_index].edges():
            revenue_components.append(vnr_list[vnr_index].edges[edge]['bw'])
        vnr_list[vnr_index] = (vnr_list[vnr_index], sum(revenue_components))

    vnr_list.sort(key=lambda x:x[1], reverse=False)


# def GetAvailableNodes(sn, maximum_cpu, vnr_list):
#     match_SN_nodes = []
#     for vnr in vnr_list:
#         for node1 in vnr[0].nodes():
#             temp = []
#             for node in sn.nodes():
#                 if vnr[0].nodes[node1]['content'] in sn.nodes[node]['content']:
#                     temp.append(node)
#             match_SN_nodes.append(temp)

#     possible_sn_nodes = []
#     for node in sn.nodes():
#         if sn.nodes[node]['cpu'] >= maximum_cpu:
#             possible_sn_nodes.append(node)

#     rest_sn_nodes = []
#     for temp_i in match_SN_nodes:
#         sn_nodes_i = list(set(temp_i) & set(possible_sn_nodes))
#         rest_sn_nodes.append(sn_nodes_i)

#     return rest_sn_nodes

def GetAvailableNodes(sn, maximum_cpu):
	possible_sn_nodes = []
	for node in sn.nodes():
		if sn.nodes[node]['cpu'] >= maximum_cpu:
			possible_sn_nodes.append(node)
	return possible_sn_nodes


def GetMaxAvailableResources(sn, sn_subset):
    for node_index in range(len(sn_subset)):
        max_available_resources = 0
        for edge in sn.edges(sn_subset[node_index]):
            max_available_resources += sn.nodes[sn_subset[node_index]]['cpu'] * sn.edges[edge]['bw']
        sn_subset[node_index] = (sn_subset[node_index], max_available_resources, sn.nodes[sn_subset[node_index]]['content'])

    sn_subset.sort(key=lambda x:x[1], reverse=True)

def SortVnrNodes(vnr):
    cpu = []
    for node in vnr.nodes():
        cpu.append(vnr.nodes[node]['cpu'])
    if cpu[1:] == cpu[:-1]:
        return sorted(vnr.nodes(data=True))
    else:
        return sorted(vnr.nodes(data=True), key=lambda x: x[1]['cpu'], reverse=True)

def AddNodeMapping(node_mapping_list, vnr_id, vnr_node, sn_node):
    node_mapping_list.append((vnr_id, vnr_node, sn_node))

def SubtractCpuResource(sn, sn_node, vnr, vnr_node):
    sn.nodes[sn_node]['cpu'] -= vnr.nodes[vnr_node]['cpu']

def ReturnCpuResource(sn, vnr, node_mapping):
    sn.nodes[node_mapping[2]]['cpu'] += vnr.nodes[node_mapping[1]]['cpu']

def RemoveNodeMapping(sn, vnr, node_mapping):
    ReturnCpuResource(sn, vnr, node_mapping)
    node_mapping_list.remove(node_mapping)

def AddEdgeMapping(edge_mapping_list, vnr_id, vnr_edge, sn_path):
    edge_mapping_list.append((vnr_id, vnr_edge, sn_path))

def SubtractBwResource(sn, sn_edge, vnr, vnr_edge):
    sn.edges[sn_edge]['bw'] -= vnr.edges[vnr_edge]['bw']

def ReturnBwResource(sn, sn_edge, vnr, vnr_edge):
    sn.edges[sn_edge]['bw'] += vnr.edges[vnr_edge]['bw']

def GetSnNodeMapping(node_mapping_list, vnr_id, vnr_node):
    with_vnr_id = list(filter(lambda x: x[0] == vnr_id, node_mapping_list))
    with_sn_node = list(filter(lambda x: x[1] == vnr_node, with_vnr_id))

    return with_sn_node[0][2]

def GreedyNodeMapping(sn, vnr_list, node_mapping_list, request_queue):
    successful_node_mapping = []
    for vnr in vnr_list:
        maximum_cpu = max(vnr[0].nodes(data=True), key=lambda x: x[1]['cpu'])[1]['cpu']
        possible_sn_nodes = GetAvailableNodes(sn, maximum_cpu)
        GetMaxAvailableResources(sn, possible_sn_nodes)

        if vnr[0].number_of_nodes() > len(possible_sn_nodes):
            request_queue.append(vnr[0])
            continue

        else:
            selected_sn_nodes = []
            success_flag = True
            sorted_vnr_nodes = SortVnrNodes(vnr[0])
            # sorted_vnr_nodes = vnr[0]
            for node in sorted_vnr_nodes:
                for idx, sn_node in enumerate(possible_sn_nodes):
                    if (node[1]['content']) in sn_node[2]:
                        selected_sn_node = possible_sn_nodes.pop(idx)
                        selected_sn_nodes.append(selected_sn_node)
                        break
                    if idx == len(possible_sn_nodes) - 1:
                        success_flag = False
            if success_flag == False:
                request_queue.append(vnr[0])
                continue

            vnr[0].graph['node_mapping_status'] = 1

            for idx, node in enumerate(sorted_vnr_nodes):
                selected_sn_node = selected_sn_nodes.pop(0)
                AddNodeMapping(node_mapping_list, vnr[0].graph['id'], node[0], selected_sn_node[0])
                SubtractCpuResource(sn, selected_sn_node[0], vnr[0], node[0])
                if idx == 0:
                    vnr[0].graph['receiver'] = min(selected_sn_node[2])
                else:
                    vnr[0].graph['sender'] = min(selected_sn_node[2])



            

        if vnr[0].graph['node_mapping_status'] == 1:
            successful_node_mapping.append(vnr[0])

    return (successful_node_mapping)

def k_shortest_paths(G, source, target, k, weight=None):
    return list(islice(nx.shortest_simple_paths(G, source, target, weight=weight), k))

def UnsplittableLinkMapping(sn, vnr_list, node_mapping_list, edge_mapping_list, request_queue):
    for vnr in vnr_list:
        selected_paths = []
        for edge in sorted(vnr[0].edges()):
            sn_node1 = GetSnNodeMapping(node_mapping_list, vnr[0].graph['id'], edge[0])
            sn_node2 = GetSnNodeMapping(node_mapping_list, vnr[0].graph['id'], edge[1])
            for path in k_shortest_paths(sn, sn_node1, sn_node2, 100):
                edge_selected = 0
                for chosen_path in selected_paths:
                    for chosen_path_index in range(len(chosen_path)-1):
                        for edge_index in range(len(path)-1):
                            if (path[edge_index] == chosen_path[chosen_path_index] and path[edge_index+1] == chosen_path[chosen_path_index+1]) or (path[edge_index] == chosen_path[chosen_path_index+1] and path[edge_index+1] == chosen_path[chosen_path_index]):
                                edge_selected = 1
                if edge_selected == 0:
                    to_map = 1
                    for edge_index in range(len(path)-1):
                        if vnr[0].edges[edge]['bw'] > sn.edges[path[edge_index], path[edge_index+1]]['bw']:
                            to_map = -1
                            break
                if to_map == 1:
                    selected_paths.append(path)
                    break
        if (len(selected_paths) < vnr[0].number_of_edges()):
            for node_mapping in list(filter(lambda x: x[0] == vnr[0].graph['id'], node_mapping_list)):
                RemoveNodeMapping(sn, vnr[0], node_mapping)
            request_queue.append(vnr[0])
        else:
            vnr[0].graph['edge_mapping_status'] = 1
            for edge in sorted(vnr[0].edges()):
                path = selected_paths.pop(0)
                AddEdgeMapping(edge_mapping_list, vnr[0].graph['id'], edge, tuple(path))
                for edge_index in range(len(path)-1):
                    SubtractBwResource(sn, (path[edge_index], path[edge_index+1]), vnr[0], edge)


def Plotting(network):
    # Hard coded position just for illustrative purposes
    #pos = { 'A': (10,20), 'B': (30, 30), 'C': (40,30), 'D': (30,20), 'E': (50,20), 'F': (20,10), 'G': (30,10), 'H': (40,10), 'I': (50,10)}
    pos = nx.spring_layout(network, scale=2, seed=0)
    nx.draw_networkx_nodes(network, pos, nodelist=network.nodes(), node_color='b')
    nx.draw_networkx_edges(network, pos, nodelist=network.edges())
    network_node_labels = nx.get_node_attributes(network,"cpu")
    network_edge_labels = nx.get_edge_attributes(network,"bw")
    nx.draw_networkx_labels(network, pos, labels=network_node_labels)
    nx.draw_networkx_edge_labels(network, pos, with_labels=True, edge_labels=network_edge_labels)

def Match(asn, asl, cvn, cvl):

    # Substrate Network Input
    # asn, asl = get_sn_info(topology)

    # # For lettering purposes
    global alphabet_dict
    alphabet_dict = dict(zip(range(1,len(asl)+1), string.ascii_uppercase))

    # # Graph for Substrate Network
    sn = nx.Graph()
    GenerateSN_Nodes(sn, asn)
    GenerateEdges(sn, asl)

    plt.figure(figsize=(15,5))
    plt.subplot(131)
    # Plotting(sn)
    # plt.subplot(122)
    Plotting(sn)

    if not len(cvn):
        plt.show(block=False)
        plt.pause(0.1)
        plt.close()
        return 1, 1, 1

    # Virtual Network Requests
    # cvn, cvl = get_vnr_info(requests)

    vnr_graph_list = []
    for vnr_index in range(len(cvn)):
        vnr_graph_list.append(nx.Graph(id=vnr_index+1, node_mapping_status=0, edge_mapping_status=0, splittable=0, sender=0, receiver=0))
        GenerateVN_Nodes(vnr_graph_list[vnr_index], cvn[vnr_index])
        GenerateEdges(vnr_graph_list[vnr_index], cvl[vnr_index])
    global node_mapping_list
    node_mapping_list = []
    edge_mapping_list = []
    request_queue = deque()
    GetRevenue(vnr_graph_list)
    # Greedy Node Mapping
    successful_node_mapping = GreedyNodeMapping(sn, vnr_graph_list, node_mapping_list, request_queue)
    # k-Shortest Path Link Mapping
    unsplittable_vnr = []
    splittable_vnr = []

    for vnr in successful_node_mapping:
        if vnr.graph['splittable'] == 0:
            unsplittable_vnr.append(vnr)
        else:
            splittable_vnr.append(vnr)

    GetRevenue(unsplittable_vnr)
    GetRevenue(splittable_vnr)
    UnsplittableLinkMapping(sn, unsplittable_vnr, node_mapping_list, edge_mapping_list, request_queue)

    # Writing to Output File
    output_file = open('results.txt', 'w+')
    out = open('results_original_arrangement.txt', 'w+')
    accepted_count = 0
    results = []
    for vnr in vnr_graph_list:
        if vnr[0].graph['node_mapping_status'] == 1 and vnr[0].graph['edge_mapping_status'] == 1:
            results.append((vnr[0].graph['id'], "Accepted", vnr[0].graph['receiver'], vnr[0].graph['sender']))
            out.write("Result " + str(vnr[0].graph['id']) + ": Accepted\n")
            accepted_count += 1
        else:
            results.append((vnr[0].graph['id'], "Rejected"))
            out.write("Result " + str(vnr[0].graph['id']) + ": Rejected\n")

    for item in sorted(results, key=lambda x:x[0]):
        output_file.write("Result " + str(item[0]) + ": " + item[1] + "\n")

    output_file.write("Acceptance Ratio: " + str(accepted_count/len(vnr_graph_list)*100) + "%")
    out.write("Acceptance Ratio: " + str(accepted_count/len(vnr_graph_list)*100) + "%")
    # plt.close()
    # plt.subplot(121)
    # Plotting(sn)
    plt.subplot(132)
    Plotting(vnr_graph_list[0][0])
    plt.subplot(133)
    Plotting(sn)
    plt.show(block=False)
    plt.pause(0.1)
    plt.close()

    return accepted_count, len(vnr_graph_list), results

if __name__ == '__main__':
    current_time =  time.time()
    topology = open('substrate_network.txt').read()
    requests = open('virtual_network_requests.txt').read()
    accept, total = Match(topology, requests)
    print (time.time() - current_time)
    print (accept)
    print (total)


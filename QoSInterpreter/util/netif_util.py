# -*- coding: utf-8 -*-
import subprocess
#import netifaces

def get_unique_codes():
    uniqueCodes = []
    if_str = subprocess.check_output(['ifconfig']).decode('utf-8').lower()
    if_items = []
    idx_s = 0
    idx = if_str.find('\n\n')

    while(idx != -1):
        #print('s:{}, e:{}'.format(idx_s, idx))
        #print(if_str[idx_s:idx])
        if_items.append(if_str[idx_s:idx])
        idx_s = idx+2
        idx = if_str.find('\n\n', idx+1)

    for if_item in if_items:
        uniqueCode = {
                     'ifaceType': 'undefined',
                     'hwAddress': 'null',
                     'ipv4': 'null'
                 }


        #print(if_item)
        if_item_split = if_item.split()
        print(if_item_split[0])
        iface_name = if_item_split[0]
        if(iface_name == 'lo'):
            continue
            
        if('eth' in iface_name or 'br' in iface_name or iface_name.startswith('en')):
            uniqueCode['ifaceType'] = 'wired'
        elif('wlan' in iface_name):
            uniqueCode['ifaceType'] = 'wifi'
        elif('rmnet' in iface_name):
            uniqueCode['ifaceType'] = 'cellular'
        else:
            uniqueCode['ifaceType'] = 'undefined'

        idx_ipv4 = if_item.find('inet addr')
        if(idx_ipv4 != -1):
            inet_addr_split = if_item[idx_ipv4+10:].split()
            print(inet_addr_split[0])
            uniqueCode['ipv4'] = inet_addr_split[0]

        idx_hwaddr = if_item.find('hwaddr')
        if(idx_hwaddr != -1):
            hwaddr_split = if_item[idx_hwaddr+6:].split()
            print(hwaddr_split[0])
            uniqueCode['hwAddress'] = hwaddr_split[0]

        uniqueCodes.append(uniqueCode)

    # ifaces = netifaces.interfaces()
    #
    #
    # for iface in ifaces:
    #     if(iface == 'lo'):
    #         continue
    #     else:
    #         addrs = netifaces.ifaddresses(iface)
    #
    #         ifaceType = 'undefined'
    #         if('eth' in iface or 'br' in iface or iface.startswith('en')):
    #             ifaceType = 'wired'
    #         elif('wlan' in iface):
    #             ifaceType = 'wifi'
    #         else:
    #             ifaceType = 'undefined'
    #
    #         hwAddress = addrs[netifaces.AF_LINK][0]['addr']
    #         if('addr' in addrs[netifaces.AF_INET][0]):
    #             ipv4 = addrs[netifaces.AF_INET][0]['addr']
    #         else:
    #             ipv4 = 'null'
    #
    #         uniqueCode = {
    #             'ifaceType': ifaceType,
    #             'hwAddress': hwAddress,
    #             'ipv4': ipv4
    #         }
    #         uniqueCodes.append(uniqueCode)
    #         return uniqueCodes

    return uniqueCodes


#
# Debug: test code
#
if __name__ == '__main__':
    res = get_unique_codes()
    print(res)

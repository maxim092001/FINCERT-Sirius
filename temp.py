"""
This code was verified on Ubuntu 17.10, Windows 10(English), Mac OSX
"""

from scapy.all import *
import datetime

result = []
"""
    src = 95.142.205.117
    dst = 10.10.200.213

    src = 10.10.200.213
    dst = 95.142.205.117
    
    src = 163.172.173.40
    dst = 10.10.200.213
    
    src = 173.194.222.189
    dst = 10.10.200.213
    
    
    data = {'ip_get': ['95.142.205.117', '10.10.200.213', '163.172.173.40', '173.194.222.189'], 'ip_post': ['10.10.200.213', '95.142.205.117', '10.10.200.213', '10.10.200.213']}
"""


def pkt_callback(pkt, data):
    pkt.show()
    # for pack in pkt:
    #
    #     ip_source = pack[IP].src
    #     ip_destination = pack[IP].dst
    #
    #     tm = pack[IP].time
    #     value = datetime.datetime.fromtimestamp(tm)
    #     tm = value.strftime('%Y-%m-%d %H:%M:%S')
    #
    #     if ip_source in data['ip_get']:
    #         result.append({'ip': ip_source, 'time': tm, 'type': 'GET'})
    #
    #     if ip_destination in data['ip_post']:
    #         result.append({'ip': ip_destination, 'time': tm, 'type': 'POST'})


# В iface указывать имя своего WI-FI модуля.
# sniff(iface="en0", prn=pkt_callback, filter="tcp", store=0)


# sniff(prn=pkt_callback, filter="tcp", store=0) # Windows-style
data = {'ip_get': []}
sniff(prn=lambda x: pkt_callback(x, data), store=0)
print(result)




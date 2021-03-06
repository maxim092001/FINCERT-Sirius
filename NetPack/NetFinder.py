from utils.encryption import get_cred
from itertools import groupby
from scapy.all import *
import datetime
import socket

table = {0: 'HOPOPT', 1: 'ICMP', 2: 'IGMP', 3: 'GGP', 4: 'IPv4', 5: 'ST', 6: 'TCP', 7: 'CBT', 8: 'EGP',
         9: 'IGP',
         10: 'BBN-RCC-MON', 11: 'NVP-II', 12: 'PUP', 13: 'ARGUS (deprecated)', 14: 'EMCON', 15: 'XNET',
         16: 'CHAOS',
         17: 'UDP', 18: 'MUX', 19: 'DCN-MEAS', 20: 'HMP', 21: 'PRM', 22: 'XNS-IDP', 23: 'TRUNK-1',
         24: 'TRUNK-2',
         25: 'LEAF-1', 26: 'LEAF-2', 27: 'RDP', 28: 'IRTP', 29: 'ISO-TP4', 30: 'NETBLT', 31: 'MFE-NSP',
         32: 'MERIT-INP',
         33: 'DCCP', 34: '3PC', 35: 'IDPR', 36: 'XTP', 37: 'DDP', 38: 'IDPR-CMTP', 39: 'TP++', 40: 'IL',
         41: 'IPv6',
         42: 'SDRP', 43: 'IPv6-Route', 44: 'IPv6-Frag', 45: 'IDRP', 46: 'RSVP', 47: 'GRE', 48: 'DSR',
         49: 'BNA',
         50: 'ESP', 51: 'AH', 52: 'I-NLSP', 53: 'SWIPE (deprecated)', 54: 'NARP', 55: 'MOBILE',
         56: 'TLSP', 57: 'SKIP',
         58: 'IPv6-ICMP', 59: 'IPv6-NoNxt', 60: 'IPv6-Opts', 61: '', 62: 'CFTP', 63: '',
         64: 'SAT-EXPAK',
         65: 'KRYPTOLAN', 66: 'RVD', 67: 'IPPC', 68: '', 69: 'SAT-MON', 70: 'VISA', 71: 'IPCV',
         72: 'CPNX', 73: 'CPHB',
         74: 'WSN', 75: 'PVP', 76: 'BR-SAT-MON', 77: 'SUN-ND', 78: 'WB-MON', 79: 'WB-EXPAK',
         80: 'ISO-IP', 81: 'VMTP',
         82: 'SECURE-VMTP', 83: 'VINES', 84: 'IPTM', 85: 'NSFNET-IGP', 86: 'DGP', 87: 'TCF',
         88: 'EIGRP', 89: 'OSPFIGP',
         90: 'Sprite-RPC', 91: 'LARP', 92: 'MTP', 93: 'AX.25', 94: 'IPIP', 95: 'MICP (deprecated)',
         96: 'SCC-SP',
         97: 'ETHERIP', 98: 'ENCAP', 100: 'GMTP', 101: 'IFMP', 102: 'PNNI', 103: 'PIM', 104: 'ARIS',
         105: 'SCPS',
         106: 'QNX', 107: 'A/N', 108: 'IPComp', 109: 'SNP', 110: 'Compaq-Peer', 111: 'IPX-in-IP',
         112: 'VRRP',
         113: 'PGM', 115: 'L2TP', 116: 'DDX', 117: 'IATP', 118: 'STP', 119: 'SRP', 120: 'UTI',
         121: 'SMP',
         122: 'SM (deprecated)', 123: 'PTP', 124: 'ISIS over IPv4', 125: 'FIRE', 126: 'CRTP',
         127: 'CRUDP',
         128: 'SSCOPMCE', 129: 'IPLT', 130: 'SPS', 131: 'PIPE', 132: 'SCTP', 133: 'FC',
         134: 'RSVP-E2E-IGNORE',
         135: 'Mobility Header', 136: 'UDPLite', 137: 'MPLS-in-IP', 138: 'manet', 139: 'HIP',
         140: 'Shim6', 141: 'WESP',
         142: 'ROHC'}
res = {'format': [], 'non_format': []}

count_ip_source = dict()
count_ip_destination = dict()

used_source = dict()
used_destination = dict()


def pkt_callback(pkt, data, cb):
    global count_ip_source, count_ip_destination, used_source, used_destination
    for pack in pkt:
        try:
            ip_source = pack[IP].src
            ip_destination = pack[IP].dst
        except IndexError:
            continue

        tm = pack[IP].time
        tm_seconds = tm
        value = datetime.datetime.fromtimestamp(tm)
        tm = value.strftime('%Y-%m-%d %H:%M:%S')  # Time when packet came
        tp = table[int(pkt[IP].proto)].lower()

        if ip_source in data['ip']:
            if ip_source not in used_source:
                count_ip_source[ip_source] = 1
                used_source[ip_source] = tm_seconds
                s = 'Дата: {} -- [{}] {} -> {} '.format(tm, tp, ip_source, ip_destination)
                res['format'].append(s)
            else:
                if (tm_seconds - used_source[ip_source]) > 20:
                    used_source[ip_source] = tm_seconds
                    res['non_format'].append({'ip': ip_source, 'time': tm, 'type': tp + ' to'})
                    s = 'Найдено обращений: {}. [{}] {} -> {} '.format(count_ip_source[ip_source], tp,
                                                                       ip_source,
                                                                       ip_destination)
                    cb.log(s)
                    s = 'Дата: {} -- [{}] {} -> {} '.format(tm, tp, ip_source, ip_destination)
                    res['format'].append(s)
                    count_ip_source[ip_source] = 0
                else:
                    count_ip_source[ip_source] += 1
                    s = 'Дата: {} -- [{}] {} -> {} '.format(tm, tp, ip_source, ip_destination)
                    res['format'].append(s)

        if ip_destination in data['ip']:
            if ip_destination not in used_destination:
                count_ip_destination[ip_destination] = 1
                used_destination[ip_destination] = tm_seconds
                s = 'Дата: {} -- [{}] {} -> {} '.format(tm, tp, ip_source, ip_destination)
                res['format'].append(s)
            else:
                if (tm_seconds - used_destination[ip_destination]) > 20:
                    used_destination[ip_destination] = tm_seconds
                    res['non_format'].append({'ip': ip_destination, 'time': tm, 'type': tp + ' from'})
                    s = 'Найдено обращений: {}. [{}] {} -> {} '.format(
                        count_ip_destination[ip_destination],
                        tp, ip_source,
                        ip_destination)
                    cb.log(s)
                    s = 'Дата: {} -- [{}] {} -> {} '.format(tm, tp, ip_source, ip_destination)
                    res['format'].append(s)
                    count_ip_destination[ip_destination] = 0
                else:
                    count_ip_destination[ip_destination] += 1
                    s = 'Дата: {} -- [{}] {} -> {} '.format(tm, tp, ip_source, ip_destination)
                    res['format'].append(s)

        if ip_source in data['ip_url']:
            if ip_source not in used_source:
                count_ip_source[ip_source] = 1
                used_source[ip_source] = tm_seconds
                s = 'Дата: {} -- [{}] {} -> {} '.format(tm, tp, ip_source, ip_destination)
                res['format'].append(s)
            else:
                if (tm_seconds - used_source[ip_source]) > 20:
                    used_source[ip_source] = tm_seconds
                    res['non_format'].append({'ip': ip_source, 'time': tm, 'type': tp + ' to'})
                    s = 'Найдено обращений: {}. [{}] {}'.format(count_ip_source[ip_source], tp,
                                                                data['ip_url'][ip_source])
                    cb.log(s)
                    s = 'Дата: {} -- [{}] {} -> {} '.format(tm, tp, ip_source, ip_destination)
                    res['format'].append(s)
                    count_ip_source[ip_source] = 0
                else:
                    count_ip_source[ip_source] += 1
                    s = 'Дата: {} -- [{}] {} -> {} '.format(tm, tp, ip_source, ip_destination)
                    res['format'].append(s)

        if ip_destination in data['ip_url']:
            if ip_destination not in used_destination:
                count_ip_destination[ip_destination] = 1
                used_destination[ip_destination] = tm_seconds
                s = 'Дата: {} -- [{}] {} -> {} '.format(tm, tp, ip_source, ip_destination)
                res['format'].append(s)
            else:
                if (tm_seconds - used_destination[ip_destination]) > 20:
                    used_destination[ip_destination] = tm_seconds
                    res['non_format'].append({'ip': ip_source, 'time': tm, 'type': tp + ' from'})
                    s = 'Найдено обращений: {}. [{}] {}'.format(count_ip_destination[ip_destination],
                                                                tp, data['ip_url'][ip_destination])
                    cb.log(s)
                    s = 'Дата: {} -- [{}] {} -> {} '.format(tm, tp, ip_source, ip_destination)
                    res['format'].append(s)
                    count_ip_destination[ip_destination] = 0
                else:
                    count_ip_destination[ip_destination] += 1
                    s = 'Дата: {} -- [{}] {} -> {} '.format(tm, tp, ip_source, ip_destination)
                    res['format'].append(s)


def clear():
    res['format'] = []
    res['non_format'] = []


def postprocess_data():
    f = lambda x: x.split(' -- ')[1]
    return list(map(lambda x: (x[0], list(x[1])), groupby(sorted(res['format'], key=f), key=f)))


def find(data, cb):
    count_ip_source.clear()
    count_ip_destination.clear()
    used_source.clear()
    used_destination.clear()

    udata = get_cred()

    try:
        a = udata['snifftime']
        if int(a) <= 0: raise Exception
    except Exception:
        cb.toast_red("Ошибка анализа сети", "Время не настроено в разделе НАСТРОЙКИ")
    else:
        dt = ({'ip': data['ip'], 'time': udata['snifftime'], 'ip_url': {}})
        for i in data['url']:
            try:
                dt['ip_url'][socket.gethostbyname(i)] = i  # Get ip by host name
            except socket.gaierror:
                continue

        try:
            sniff(prn=lambda x: pkt_callback(x, dt, cb), store=0,
                  timeout=int(
                      dt[
                          'time']) * 60)  # Dt - database, Cb - callback, store=0 means that we won't store our res
        except PermissionError:
            cb.toast_red("Системная ошибка", "Анализ сети не разрешен")
        except Exception as ex:
            cb.toast_red("Ошибка анализа сети", ex)
    return postprocess_data()

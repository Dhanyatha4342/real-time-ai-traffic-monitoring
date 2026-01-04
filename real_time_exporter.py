from prometheus_client import start_http_server, Gauge
from scapy.all import sniff, IP, TCP, UDP
import threading
import time
from statistics import mean, stdev

# Prometheus metrics
flow_packets_per_sec = Gauge('flow_packets_per_sec', 'Packets per second per flow', ['flow_id'])
fwd_packets_per_sec = Gauge('fwd_packets_per_sec', 'Forward packets per second per flow', ['flow_id'])
bwd_packets_per_sec = Gauge('bwd_packets_per_sec', 'Backward packets per second per flow', ['flow_id'])
flow_duration_gauge = Gauge('flow_duration', 'Flow duration in seconds', ['flow_id'])
pkt_len_mean = Gauge('packet_length_mean', 'Mean of packet lengths', ['flow_id'])
pkt_len_std = Gauge('packet_length_std', 'Std dev of packet lengths', ['flow_id'])
flow_bytes_per_sec = Gauge('flow_bytes_per_sec', 'Bytes per second per flow', ['flow_id'])
packet_count = Gauge('packet_count', 'Total packet count', ['flow_id'])

# Flow tracking
flow_table = {}

def get_flow_id(pkt):
    if IP in pkt:
        ip = pkt[IP]
        proto = 'TCP' if TCP in pkt else 'UDP' if UDP in pkt else 'OTHER'
        sport = pkt.sport if hasattr(pkt, 'sport') else 0
        dport = pkt.dport if hasattr(pkt, 'dport') else 0

        key = sorted([(ip.src, sport), (ip.dst, dport)])
        return (key[0][0], key[1][0], key[0][1], key[1][1], proto)
    return None

def process_packet(pkt):
    flow_id = get_flow_id(pkt)
    if not flow_id:
        return

    now = time.time()
    pkt_len = len(pkt)
    src_ip = pkt[IP].src

    if flow_id not in flow_table:
        flow_table[flow_id] = {
            'start': now,
            'end': now,
            'packet_sizes': [pkt_len],
            'total_bytes': pkt_len,
            'total_packets': 1,
            'fwd_packets': 1,
            'bwd_packets': 0,
            'first_src': src_ip
        }
    else:
        flow = flow_table[flow_id]
        flow['end'] = now
        flow['packet_sizes'].append(pkt_len)
        flow['total_bytes'] += pkt_len
        flow['total_packets'] += 1

        if src_ip == flow['first_src']:
            flow['fwd_packets'] += 1
        else:
            flow['bwd_packets'] += 1

    flow = flow_table[flow_id]
    duration = flow['end'] - flow['start']
    fid_str = f"{flow_id[0]}:{flow_id[2]} <-> {flow_id[1]}:{flow_id[3]} ({flow_id[4]})"

    if duration > 0:
        packet_count.labels(flow_id=fid_str).set(flow['total_packets'])
        flow_packets_per_sec.labels(flow_id=fid_str).set(flow['total_packets'] / duration)
        fwd_packets_per_sec.labels(flow_id=fid_str).set(flow['fwd_packets'] / duration)
        bwd_packets_per_sec.labels(flow_id=fid_str).set(flow['bwd_packets'] / duration)
        flow_duration_gauge.labels(flow_id=fid_str).set(duration)
        flow_bytes_per_sec.labels(flow_id=fid_str).set(flow['total_bytes'] / duration)

        if len(flow['packet_sizes']) >= 2:
            pkt_len_mean.labels(flow_id=fid_str).set(mean(flow['packet_sizes']))
            pkt_len_std.labels(flow_id=fid_str).set(stdev(flow['packet_sizes']))
        else:
            pkt_len_mean.labels(flow_id=fid_str).set(flow['packet_sizes'][0])
            pkt_len_std.labels(flow_id=fid_str).set(0)

        # print(f"[{fid_str}] Packets/s: {flow['total_packets'] / duration:.2f}, Bytes/s: {flow['total_bytes'] / duration:.2f}")

def remove_flow_metrics(fid_str):
    for metric in [flow_packets_per_sec, fwd_packets_per_sec, bwd_packets_per_sec,
                   flow_duration_gauge, pkt_len_mean, pkt_len_std,
                   flow_bytes_per_sec, packet_count]:
        try:
            metric.remove(flow_id=fid_str)
        except:
            pass

def expire_flows():
    while True:
        now = time.time()
        expired = []

        for flow_id, data in list(flow_table.items()):
            if now - data['end'] > 10:
                expired.append(flow_id)

        for fid in expired:
            fid_str = f"{fid[0]}:{fid[2]} <-> {fid[1]}:{fid[3]} ({fid[4]})"
            remove_flow_metrics(fid_str)
            del flow_table[fid]

        time.sleep(5)

def start_sniffing():
    iface_name = "Wi-Fi"  # fixed interface
    print(f"Sniffing on interface: {iface_name}")
    sniff(prn=process_packet, store=False, iface=iface_name)

if __name__ == '__main__':
    start_http_server(8100)
    print("Exporter running at http://localhost:8100/metrics")

    sniff_thread = threading.Thread(target=start_sniffing)
    sniff_thread.start()

    expire_thread = threading.Thread(target=expire_flows)
    expire_thread.daemon = True
    expire_thread.start()

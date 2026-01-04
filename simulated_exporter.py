import requests
import time
import joblib
from prometheus_client import Gauge, start_http_server
import threading
import time
import logging


model = joblib.load("rf_model.joblib")
features_order = joblib.load("features_order.joblib")
label_encoder = joblib.load("label_encoder.joblib")

# Prometheus metric for traffic in Mbps
flow_packets_per_second = Gauge('flow_packets_per_second', 'Flow Packets per Second')
fwd_packets_per_second = Gauge('fwd_packets_per_second', 'Forward Packets per Second')
bwd_packets_per_second = Gauge('bwd_packets_per_second', 'Backward Packets per Second')
flow_duration = Gauge('flow_duration', 'Duration of Flow')
packet_length_mean = Gauge('packet_length_mean', 'Mean Length of Forward Packets')
packet_length_std = Gauge('packet_length_std', 'Standard Deviation of Forward Packet Length')
flow_bytes_per_second = Gauge('flow_bytes_per_second', 'Bytes per Second in Flow')




# Load artifacts
label_encoder = joblib.load("label_encoder.joblib")
ddos_label = label_encoder.transform(["DDoS"])[0]
features = joblib.load("features_order.joblib")
model = joblib.load("rf_model.joblib")

# Normal Traffic Sample (converted from your CSV row)
normal_example = {
    "Destination Port": 1,
    "Flow Duration": 58607,
    "Total Fwd Packets": 2,
    "Total Length of Fwd Packets": 59,
    "Fwd Packet Length Max": 53,
    "Fwd Packet Length Min": 6,
    "Fwd Packet Length Mean": 29.5,
    "Fwd Packet Length Std": 33.23401872,
    "Bwd Packet Length Max": 0,
    "Bwd Packet Length Min": 0,
    "Bwd Packet Length Mean": 0.0,
    "Bwd Packet Length Std": 0.0,
    "Flow Bytes/s": 59000000.0,
    "Flow Packets/s": 2000000.0,
    "Flow IAT Mean": 1.0,
    "Flow IAT Std": 0.0,
    "Flow IAT Max": 1,
    "Flow IAT Min": 1,
    "Fwd IAT Total": 1,
    "Fwd IAT Mean": 1.0,
    "Fwd IAT Std": 0.0,
    "Fwd IAT Max": 1,
    "Fwd IAT Min": 1,
    "Bwd IAT Total": 0,
    "Bwd IAT Mean": 0.0,
    "Bwd IAT Std": 0.0,
    "Bwd IAT Max": 0,
    "Bwd IAT Min": 0,
    "Fwd Header Length": 40,
    "Bwd Header Length": 0,
    "Fwd Packets/s": 2000000.0,
    "Bwd Packets/s": 0.0,
    "Min Packet Length": 6,
    "Max Packet Length": 53,
    "Packet Length Mean": 37.33333333,
    "Packet Length Std": 27.13546265,
    "Packet Length Variance": 736.3333333,
    "FIN Flag Count": 0,
    "PSH Flag Count": 0,
    "ACK Flag Count": 1,
    "Average Packet Size": 56.0,
    "Subflow Fwd Bytes": 59,
    "Init_Win_bytes_forward": 1026,
    "Init_Win_bytes_backward": -1,
    "act_data_pkt_fwd": 1,
    "min_seg_size_forward": 20,
    "Active Mean": 0.0,
    "Active Max": 0,
    "Active Min": 0,
    "Idle Mean": 0.0,
    "Idle Max": 0,
    "Idle Min": 0,
    "Attack Type": int(label_encoder.transform(["Normal Traffic"])[0])
}

# Simulated DDoS flow (already defined earlier)
ddos_example = {
    "Destination Port": 80,
    "Flow Duration": 1293792,
    "Total Fwd Packets": 3,
    "Total Length of Fwd Packets": 26,
    "Fwd Packet Length Max": 20,
    "Fwd Packet Length Min": 0,
    "Fwd Packet Length Mean": 8.666666667,
    "Fwd Packet Length Std": 10.26320288,
    "Bwd Packet Length Max": 5840,
    "Bwd Packet Length Min": 0,
    "Bwd Packet Length Mean": 1658.142857,
    "Bwd Packet Length Std": 2137.29708,
    "Flow Bytes/s": 8991.398927,
    "Flow Packets/s": 7.72921768,
    "Flow IAT Mean": 143754.6667,
    "Flow IAT Std": 430865.8067,
    "Flow IAT Max": 1292730,
    "Flow IAT Min": 2,
    "Fwd IAT Total": 747,
    "Fwd IAT Mean": 373.5,
    "Fwd IAT Std": 523.9661249,
    "Fwd IAT Max": 744,
    "Fwd IAT Min": 3,
    "Bwd IAT Total": 1293746,
    "Bwd IAT Mean": 215624.3333,
    "Bwd IAT Std": 527671.9348,
    "Bwd IAT Max": 1292730,
    "Bwd IAT Min": 2,
    "Fwd Header Length": 72,
    "Bwd Header Length": 152,
    "Fwd Packets/s": 2.318765304,
    "Bwd Packets/s": 5.410452376,
    "Min Packet Length": 0,
    "Max Packet Length": 5840,
    "Packet Length Mean": 1057.545455,
    "Packet Length Std": 1853.437529,
    "Packet Length Variance": 3435230.673,
    "FIN Flag Count": 0,
    "PSH Flag Count": 1,
    "ACK Flag Count": 0,
    "Average Packet Size": 1163.3,
    "Subflow Fwd Bytes": 26,
    "Init_Win_bytes_forward": 8192,
    "Init_Win_bytes_backward": 229,
    "act_data_pkt_fwd": 2,
    "min_seg_size_forward": 20,
    "Active Mean": 0.0,
    "Active Max": 0.0,
    "Active Min": 0.0,
    "Idle Mean": 0.0,
    "Idle Max": 0.0,
    "Idle Min": 0.0,
    "Attack Type": int(ddos_label)
}
bots_example = {
    "Destination Port": 8080,
    "Flow Duration": 60202640,
    "Total Fwd Packets": 9,
    "Total Length of Fwd Packets": 322,
    "Fwd Packet Length Max": 322,
    "Fwd Packet Length Min": 0,
    "Fwd Packet Length Mean": 35.77777778,
    "Fwd Packet Length Std": 107.3333333,
    "Bwd Packet Length Max": 256,
    "Bwd Packet Length Min": 0,
    "Bwd Packet Length Mean": 28.44444444,
    "Bwd Packet Length Std": 85.33333333,
    "Flow Bytes/s": 9.600907867,
    "Flow Packets/s": 0.29899021,
    "Flow IAT Mean": 3541331.765,
    "Flow IAT Std": 4901981.331,
    "Flow IAT Max": 10200000,
    "Flow IAT Min": 47,
    "Fwd IAT Total": 51200000,
    "Fwd IAT Mean": 6396441.875,
    "Fwd IAT Std": 5268489.909,
    "Fwd IAT Max": 10200000,
    "Fwd IAT Min": 234,
    "Bwd IAT Total": 60200000,
    "Bwd IAT Mean": 7518953.625,
    "Bwd IAT Std": 4645137.318,
    "Bwd IAT Max": 10300000,
    "Bwd IAT Min": 637,
    "Fwd Header Length": 296,
    "Bwd Header Length": 296,
    "Fwd Packets/s": 0.149495105,
    "Bwd Packets/s": 0.149495105,
    "Min Packet Length": 0,
    "Max Packet Length": 322,
    "Packet Length Mean": 30.42105263,
    "Packet Length Std": 91.78375297,
    "Packet Length Variance": 8424.25731,
    "FIN Flag Count": 0,
    "PSH Flag Count": 1,
    "ACK Flag Count": 0,
    "Average Packet Size": 32.11111111,
    "Subflow Fwd Bytes": 322,
    "Init_Win_bytes_forward": 29200,
    "Init_Win_bytes_backward": 110,
    "act_data_pkt_fwd": 1,
    "min_seg_size_forward": 32,
    "Active Mean": 63678.2,
    "Active Max": 103175,
    "Active Min": 50911,
    "Idle Mean": 10200000.0,
    "Idle Max": 10200000,
    "Idle Min": 10100000,
    "Attack Type": int(label_encoder.transform(["Bots"])[0])
}

brute_force_example = {
    "Destination Port": 21,
    "Flow Duration": 38,
    "Total Fwd Packets": 1,
    "Total Length of Fwd Packets": 0,
    "Fwd Packet Length Max": 0,
    "Fwd Packet Length Min": 0,
    "Fwd Packet Length Mean": 0.0,
    "Fwd Packet Length Std": 0.0,
    "Bwd Packet Length Max": 0,
    "Bwd Packet Length Min": 0,
    "Bwd Packet Length Mean": 0.0,
    "Bwd Packet Length Std": 0.0,
    "Flow Bytes/s": 0.0,
    "Flow Packets/s": 52631.57895,
    "Flow IAT Mean": 38.0,
    "Flow IAT Std": 0.0,
    "Flow IAT Max": 38,
    "Flow IAT Min": 38,
    "Fwd IAT Total": 0,
    "Fwd IAT Mean": 0.0,
    "Fwd IAT Std": 0.0,
    "Fwd IAT Max": 0,
    "Fwd IAT Min": 0,
    "Bwd IAT Total": 0,
    "Bwd IAT Mean": 0.0,
    "Bwd IAT Std": 0.0,
    "Bwd IAT Max": 0,
    "Bwd IAT Min": 0,
    "Fwd Header Length": 32,
    "Bwd Header Length": 32,
    "Fwd Packets/s": 26315.78947,
    "Bwd Packets/s": 26315.78947,
    "Min Packet Length": 0,
    "Max Packet Length": 0,
    "Packet Length Mean": 0.0,
    "Packet Length Std": 0.0,
    "Packet Length Variance": 0.0,
    "FIN Flag Count": 0,
    "PSH Flag Count": 0,
    "ACK Flag Count": 1,
    "Average Packet Size": 0.0,
    "Subflow Fwd Bytes": 0,
    "Init_Win_bytes_forward": 229,
    "Init_Win_bytes_backward": 227,
    "act_data_pkt_fwd": 0,
    "min_seg_size_forward": 32,
    "Active Mean": 0.0,
    "Active Max": 0,
    "Active Min": 0,
    "Idle Mean": 0.0,
    "Idle Max": 0,
    "Idle Min": 0,
    "Attack Type": int(label_encoder.transform(["Brute Force"])[0])
}

dos_example = {
    "Destination Port": 80,
    "Flow Duration": 3204769,
    "Total Fwd Packets": 2,
    "Total Length of Fwd Packets": 12,
    "Fwd Packet Length Max": 6,
    "Fwd Packet Length Min": 6,
    "Fwd Packet Length Mean": 6.0,
    "Fwd Packet Length Std": 0.0,
    "Bwd Packet Length Max": 11,
    "Bwd Packet Length Min": 0,
    "Bwd Packet Length Mean": 5.5,
    "Bwd Packet Length Std": 7.778174593,
    "Flow Bytes/s": 7.176804319,
    "Flow Packets/s": 1.248139882,
    "Flow IAT Mean": 1068256.333,
    "Flow IAT Std": 1849977.203,
    "Flow IAT Max": 3204426,
    "Flow IAT Min": 32,
    "Fwd IAT Total": 343,
    "Fwd IAT Mean": 343.0,
    "Fwd IAT Std": 0.0,
    "Fwd IAT Max": 343,
    "Fwd IAT Min": 343,
    "Bwd IAT Total": 3204737,
    "Bwd IAT Mean": 3204737.0,
    "Bwd IAT Std": 0.0,
    "Bwd IAT Max": 3204737,
    "Bwd IAT Min": 3204737,
    "Fwd Header Length": 40,
    "Bwd Header Length": 64,
    "Fwd Packets/s": 0.624069941,
    "Bwd Packets/s": 0.624069941,
    "Min Packet Length": 0,
    "Max Packet Length": 11,
    "Packet Length Mean": 5.8,
    "Packet Length Std": 3.898717738,
    "Packet Length Variance": 15.2,
    "FIN Flag Count": 1,
    "PSH Flag Count": 0,
    "ACK Flag Count": 0,
    "Average Packet Size": 7.25,
    "Subflow Fwd Bytes": 12,
    "Init_Win_bytes_forward": 0,
    "Init_Win_bytes_backward": 235,
    "act_data_pkt_fwd": 1,
    "min_seg_size_forward": 20,
    "Active Mean": 0.0,
    "Active Max": 0,
    "Active Min": 0,
    "Idle Mean": 0.0,
    "Idle Max": 0,
    "Idle Min": 0,
    "Attack Type": int(label_encoder.transform(["DoS"])[0])  # 🔥🧨 DoS
}

portscan_example = {
    "Destination Port": 80,
    "Flow Duration": 70,
    "Total Fwd Packets": 1,
    "Total Length of Fwd Packets": 0,
    "Fwd Packet Length Max": 0,
    "Fwd Packet Length Min": 0,
    "Fwd Packet Length Mean": 0.0,
    "Fwd Packet Length Std": 0.0,
    "Bwd Packet Length Max": 0,
    "Bwd Packet Length Min": 0,
    "Bwd Packet Length Mean": 0.0,
    "Bwd Packet Length Std": 0.0,
    "Flow Bytes/s": 0.0,
    "Flow Packets/s": 28571.42857,
    "Flow IAT Mean": 70.0,
    "Flow IAT Std": 0.0,
    "Flow IAT Max": 70,
    "Flow IAT Min": 70,
    "Fwd IAT Total": 0,
    "Fwd IAT Mean": 0.0,
    "Fwd IAT Std": 0.0,
    "Fwd IAT Max": 0,
    "Fwd IAT Min": 0,
    "Bwd IAT Total": 0,
    "Bwd IAT Mean": 0.0,
    "Bwd IAT Std": 0.0,
    "Bwd IAT Max": 0,
    "Bwd IAT Min": 0,
    "Fwd Header Length": 32,
    "Bwd Header Length": 32,
    "Fwd Packets/s": 14285.71429,
    "Bwd Packets/s": 14285.71429,
    "Min Packet Length": 0,
    "Max Packet Length": 0,
    "Packet Length Mean": 0.0,
    "Packet Length Std": 0.0,
    "Packet Length Variance": 0.0,
    "FIN Flag Count": 0,
    "PSH Flag Count": 0,
    "ACK Flag Count": 1,
    "Average Packet Size": 0.0,
    "Subflow Fwd Bytes": 0,
    "Init_Win_bytes_forward": 253,
    "Init_Win_bytes_backward": 243,
    "act_data_pkt_fwd": 0,
    "min_seg_size_forward": 32,
    "Active Mean": 0.0,
    "Active Max": 0,
    "Active Min": 0,
    "Idle Mean": 0.0,
    "Idle Max": 0,
    "Idle Min": 0,
    "Attack Type": int(label_encoder.transform(["Port Scanning"])[0])  # 🛰️🔍 Port Scanning
}


# Your traffic samples
traffic_sequence = [
    ("✅ Normal", normal_example),
    ("🚨 DDoS", ddos_example),
    ("✅ Normal", normal_example),
    ("🤖 Bots", bots_example),
    ("✅ Normal", normal_example),
    ("🔐🪓 Brute Force ", brute_force_example),
    ("✅ Normal", normal_example),
    ("🔥🧨 DoS ",dos_example),
    ("✅ Normal", normal_example),
    ("🛰️🔍 Port Scanning", portscan_example)
]

features = list(normal_example.keys())  # Ensure this is already defined

index = 0
interval_duration = 10  # 2 minutes

start_time = time.time()

def simulate_traffic():
    while True:
        try:
            elapsed = time.time() - start_time
            index = int(elapsed // interval_duration) % len(traffic_sequence)
            label, sample = traffic_sequence[index]

            # Metrics
            flow_packets_per_second.set(sample["Flow Packets/s"])
            fwd_packets_per_second.set(sample["Fwd Packets/s"])
            bwd_packets_per_second.set(sample["Bwd Packets/s"])
            flow_duration.set(sample["Flow Duration"])
            packet_length_mean.set(sample["Fwd Packet Length Mean"])
            packet_length_std.set(sample["Fwd Packet Length Std"])
            flow_bytes_per_second.set(sample["Flow Bytes/s"])

            # Prediction request
            response = requests.post("http://localhost:5000/predict-simulated", json=sample)
            logging.debug(f"{label} sent: {response.text}")

        except Exception as e:
            logging.exception(f"🚨 Simulated traffic error: {e}")

        time.sleep(3)


if __name__ == '__main__':
    # Start Prometheus metrics server FIRST
    start_http_server(9100)
    print("✅ Prometheus metrics server started on port 9100")
    
    # Then start traffic simulation in a separate thread
    traffic_thread = threading.Thread(target=simulate_traffic)
    traffic_thread.daemon = True
    traffic_thread.start()
    
    # Keep main thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
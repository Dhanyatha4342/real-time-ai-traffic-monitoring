import threading
import time
import os
import signal
import subprocess
import logging
import joblib
import pandas as pd
from flask import Flask, request, jsonify
from flask_cors import CORS
from scapy.all import sniff, IP, TCP
import sys
app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# ML Artifacts
model = joblib.load("rf_model.joblib")
features_order = joblib.load("features_order.joblib")
label_encoder = joblib.load("label_encoder.joblib")

# Global state
latest_prediction = "Loading..."
latest_simulated_payload = {}  # <-- fix: define it
exporter_process = None
current_mode = None
stop_event = threading.Event()


# --------- Feature Extraction ---------
def extract_features(packet):
    fwd_len = len(packet)
    features = {
        "Destination Port": packet[TCP].dport if TCP in packet else 0,
        "Flow Duration": 1000,
        "Total Fwd Packets": 1,
        "Total Length of Fwd Packets": fwd_len,
        "Fwd Packet Length Max": fwd_len,
        "Fwd Packet Length Min": fwd_len,
        "Fwd Packet Length Mean": fwd_len,
        "Fwd Packet Length Std": 0,
        "Bwd Packet Length Max": 0,
        "Bwd Packet Length Min": 0,
        "Bwd Packet Length Mean": 0,
        "Bwd Packet Length Std": 0,
        "Flow Bytes/s": fwd_len,
        "Flow Packets/s": 1.0,
        "Flow IAT Mean": 5000,
        "Flow IAT Std": 1000,
        "Flow IAT Max": 6000,
        "Flow IAT Min": 200,
        "Fwd IAT Total": 5000,
        "Fwd IAT Mean": 5000,
        "Fwd IAT Std": 0,
        "Fwd IAT Max": 6000,
        "Fwd IAT Min": 200,
        "Bwd IAT Total": 0,
        "Bwd IAT Mean": 0,
        "Bwd IAT Std": 0,
        "Bwd IAT Max": 0,
        "Bwd IAT Min": 0,
        "Fwd Header Length": len(packet[IP]) if IP in packet else 0,
        "Bwd Header Length": 0,
        "Fwd Packets/s": 1.0,
        "Bwd Packets/s": 0.0,
        "Min Packet Length": fwd_len,
        "Max Packet Length": fwd_len,
        "Packet Length Mean": fwd_len,
        "Packet Length Std": 0,
        "Packet Length Variance": 0,
        "FIN Flag Count": int('F' in str(packet[TCP].flags)) if TCP in packet else 0,
        "PSH Flag Count": int('P' in str(packet[TCP].flags)) if TCP in packet else 0,
        "ACK Flag Count": int('A' in str(packet[TCP].flags)) if TCP in packet else 0,
        "Average Packet Size": fwd_len,
        "Subflow Fwd Bytes": fwd_len,
        "Init_Win_bytes_forward": packet[TCP].window if TCP in packet else 0,
        "Init_Win_bytes_backward": 0,
        "act_data_pkt_fwd": 1,
        "min_seg_size_forward": 0,
        "Active Mean": 3000,
        "Active Max": 5000,
        "Active Min": 1000,
        "Idle Mean": 3000,
        "Idle Max": 5000,
        "Idle Min": 1000
    }
    return {key: features.get(key, 0) for key in features_order}


# --------- Real-time Sniffing ---------
def predict_from_packet(packet):
    global latest_prediction
    try:
        features = extract_features(packet)
        feature_vector = [float(features[feature]) for feature in features_order]
        df = pd.DataFrame([feature_vector], columns=features_order)
        prediction = model.predict(df)[0]
        decoded_label = label_encoder.inverse_transform([prediction])[0]
        latest_prediction = decoded_label
        logging.info(f"\U0001f4e1 Packet Predicted: {decoded_label}")
    except Exception as e:
        logging.error(f"Prediction error: {e}")

def sniff_packets():
    sniff(iface="Wi-Fi", prn=predict_from_packet, store=0)


# --------- Routes ---------
@app.route('/')
def health():
    return jsonify({"status": "Server is running"})


@app.route('/predict-simulated', methods=['POST'])
def predict_simulated():
    global latest_prediction, latest_simulated_payload
    try:
        data = request.json
        latest_simulated_payload = data
        feature_vector = [float(data.get(feature, 0.0)) for feature in features_order]
        df = pd.DataFrame([feature_vector], columns=features_order)
        prediction = model.predict(df)[0]
        decoded_label = label_encoder.inverse_transform([prediction])[0]
        latest_prediction = decoded_label

        logging.info(f"\U0001f3af Simulated Prediction: {decoded_label}")
        return jsonify({
            "predicted_class": decoded_label,
            "status": "attack" if decoded_label.lower() != "normal" else "normal"
        })
    except Exception as e:
        logging.error(f"\u274c Simulated Prediction Error: {e}")
        return jsonify({"error": str(e)}), 400


@app.route('/latest_prediction-simulated', methods=['GET'])
def latest_predict_simulated():
    global latest_simulated_payload, latest_prediction
    try:
        if not latest_simulated_payload:
            return jsonify({"error": "No simulated data available yet"}), 404

        feature_vector = [float(latest_simulated_payload.get(feature, 0.0)) for feature in features_order]
        df = pd.DataFrame([feature_vector], columns=features_order)
        prediction = model.predict(df)[0]
        decoded_label = label_encoder.inverse_transform([prediction])[0]
        latest_prediction = decoded_label

        return jsonify({"traffic_type": decoded_label})
    except Exception as e:
        logging.error(f"\u274c Error in latest_prediction-simulated: {e}")
        logging.error(f"Simulated prediction error: {e}")
        return jsonify({"traffic_type": latest_prediction})



@app.route('/predict', methods=['POST'])
def predict():
    global latest_prediction
    try:
        data = request.json
        feature_vector = [float(data.get(feature, 0.0)) for feature in features_order]
        input_df = pd.DataFrame([feature_vector], columns=features_order)
        prediction = model.predict(input_df)[0]
        decoded_label = label_encoder.inverse_transform([prediction])[0]
        latest_prediction = decoded_label

        logging.info(f"\U0001f50e Predicted class: {decoded_label}")
        return jsonify({
            "predicted_class": decoded_label,
            "status": "attack" if decoded_label.lower() != "normal" else "normal"
        })
    except Exception as e:
        logging.error(f"\u274c Error: {str(e)}")
        return jsonify({"error": str(e)}), 400


@app.route('/latest_prediction', methods=['GET'])
def get_latest_prediction():
    try:
        pkt = sniff(count=1, timeout=2)[0]
        features = extract_features(pkt)
        feature_vector = [float(features[feature]) for feature in features_order]
        df = pd.DataFrame([feature_vector], columns=features_order)
        prediction = model.predict(df)[0]
        decoded_label = label_encoder.inverse_transform([prediction])[0]
        return jsonify({"traffic_type": decoded_label})
    except Exception as e:
        logging.error(f"Real-time prediction error: {e}")
        return jsonify({"traffic_type": latest_prediction})



@app.route("/start_exporter", methods=["POST"])
def start_exporter():
    global exporter_process, current_mode

    data = request.get_json()
    mode = data.get("mode")

    if exporter_process and exporter_process.poll() is None:
        os.kill(exporter_process.pid, signal.SIGTERM)

    if mode == "real":
        exporter_script = "real_time_exporter.py"
        port = 8100
    elif mode == "simulated":
        exporter_script = "simulated_exporter.py"
        port = 9100
    else:
        return jsonify({"error": "Invalid mode"}), 400

    exporter_process = subprocess.Popen(
        [sys.executable, exporter_script],
        stdout=None,
        stderr=None
    )
    current_mode = mode
    logging.info(f"\U0001f680 Launched {exporter_script} with PID {exporter_process.pid}")

    return jsonify({"status": f"{mode} exporter started on port {port}"}), 200


# --------- Main Entrypoint ---------
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)

from http.server import BaseHTTPRequestHandler, HTTPServer
from http.server import ThreadingHTTPServer  # for concurrency
import joblib
import json
import numpy as np
import pandas as pd
import logging
import signal
import sys

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")

# Load model and required artifacts
model = joblib.load("rf_model.joblib")
features_order = joblib.load("features_order.joblib")
label_encoder = joblib.load("label_encoder.joblib")

# Signal handler for graceful shutdown
def signal_handler(sig, frame):
    print("\n❌ Server stopped.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

class RequestHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')  # Allow CORS
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write(json.dumps({"status": "Server is running"}).encode())

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        try:
            data = json.loads(post_data)
            feature_vector = [float(data[feature]) for feature in features_order]
            input_df = pd.DataFrame([feature_vector], columns=features_order)

            prediction = model.predict(input_df)[0]
            decoded_label = label_encoder.inverse_transform([prediction])[0]

            logging.info(f"🔎 Predicted class: {decoded_label}")

            response = {
                "predicted_class": decoded_label,
                "status": "attack" if decoded_label.lower() != "normal" else "normal"
            }

            if decoded_label.lower() == "ddos":
                logging.warning("🚨 DDoS Attack Detected!")
            elif decoded_label.lower() == "bots":
                logging.warning("🤖 Bot Attack Detected!")
            elif decoded_label.lower() == "normal traffic":
                logging.info("✅ Normal traffic")
            elif decoded_label.lower() == "brute force":
                logging.info("🔐🪓 Brute Force ")
            elif decoded_label.lower() == "dos":
                logging.info("🔥🧨 DoS ")
            elif decoded_label.lower() == "port scanning":
                logging.info("🛰️🔍 Port Scanning ")
            else:
                logging.warning(f"⚠️ {decoded_label} Attack Detected!")

            self._set_headers()
            self.wfile.write(json.dumps(response).encode())

        except Exception as e:
            logging.error(f"❌ Error: {str(e)}")
            self._set_headers(400)
            self.wfile.write(json.dumps({"error": str(e)}).encode())

def run(server_class=ThreadingHTTPServer, handler_class=RequestHandler, port=8000):
    server = server_class(('0.0.0.0', port), handler_class)
    logging.info(f"🚀 Real-time server started on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    run()

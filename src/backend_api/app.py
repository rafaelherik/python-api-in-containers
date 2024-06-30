import time
import random
import os
from flask import Flask

app = Flask(__name__)

external_integration_key = os.getenv("EXTERNAL_INTEGRATION_KEY")

if not external_integration_key:
    raise ValueError("EXTERNAL_INTEGRATION_KEY is not set")

def generate_log():
    logs = [
        "Success",
        "Created",
        "Failed",
    ]
    return random.choice(logs)

@app.route('/api_1')
def api_call():
    log_message = generate_log()
    print(f"Operation log: {log_message}")
    time.sleep(0.5)  # Wait for half a second
    return f"completed: {log_message}"

@app.route('/healthz')
def health_check():
    return f"healthy"

@app.route('/readyz')
def health_check():
    return f"ready"

@app.route('/download_external_logs')
def download_external_logs():
    return f"download_external_logs works! EXTERNAL_INTEGRATION_API_KEY is set"


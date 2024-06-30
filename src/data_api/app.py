import os
import time
import random
from flask import Flask

app = Flask(__name__)

def generate_log():
    logs = [
        "Processing request...",
        "Executing task...",
        "Preparing data...",
        "Performing operation..."
    ]
    return random.choice(logs)

def write_to_file(file_path, text):
    with open(file_path, 'a') as file:
        file.write(text + '\n')

@app.route('/healthz')
def health_check():
    return f"healthy"

@app.route('/readyz')
def health_check():
    return f"ready"

@app.route('/')
def process_api():
    time.sleep(3)  # Wait for 3 seconds
    log_message = generate_log()
    print(f"Log: {log_message}")  

    
    log_directory = '/var/data/logs'
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    
    randome_text = f"log_{time.time()}.txt"
    file_path = os.path.join(log_directory, randome_text)
    
    write_to_file(file_path, log_message)  # Write the log message to a file
    

    return f"Log: {log_message}"


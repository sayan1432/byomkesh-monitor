from flask import Flask, jsonify, render_template
import psutil
import requests
import threading
import time
from database import init_db, insert_data, get_last_50_data

app = Flask(__name__)
def collect_metrics():
    while True:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        try:
            requests.get("https://www.google.com", timeout=3)
            network = "Online"
        except:
            network = "Offline"

        insert_data(cpu, ram, disk, network)
        time.sleep(5)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    return jsonify(get_last_50_data())

@app.route('/status')
def status():
    services = {
        "AWS": "https://status.aws.amazon.com/",
        "Google": "https://www.google.com/",
        "GitHub": "https://www.githubstatus.com/"
    }
    status_data = {}
    for name, url in services.items():
        try:
            r = requests.get(url, timeout=3)
            status_data[name] = "Up" if r.status_code == 200 else "Down"
        except:
            status_data[name] = "Down"
    return jsonify(status_data)

if __name__!= '__main__':
    thread = threading.Thread(target=collect_metrics, daemon=True)
    thread.start()
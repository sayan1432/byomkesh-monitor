from flask import Flask, render_template, jsonify
import psutil
import socket
import shutil
import platform
import threading
import time
import requests
from database import init_db, insert_data, get_last_50_data

app = Flask(__name__)

latest_data = {"cpu": 0, "ram": 0, "disk": 0, "network": "Offline", "cloud_status": {}}

CLOUD_SERVICES = {
    "AWS": "https://status.aws.amazon.com",
    "Google": "https://www.google.com",
    "GitHub": "https://www.github.com"
}
def check_cloud_status():
    status = {}
    for name, url in CLOUD_SERVICES.items():
        try:
            requests.get(url, timeout=3)
            status[name] = "Online"
        except:
            status[name] = "Down"
    return status
def background_monitor():
    global latest_data
    while True:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent

        disk_total, disk_used, disk_free = shutil.disk_usage("C:\\")
        disk = round((disk_used / disk_total) * 100, 2)

        cloud_status = check_cloud_status()

        if cloud_status["AWS"] == "Online" and cloud_status["Google"] == "Online" and cloud_status["GitHub"] == "Online":
            network = "All Cloud Online"
        else:
            network = "Cloud Issue"

        latest_data = {"cpu": cpu, "ram": ram, "disk": disk, "network": network, "cloud_status": cloud_status}
        insert_data(cpu, ram, disk, network)
        time.sleep(10)

@app.route("/")
def dashboard():
    os_name = platform.system() + " "+ platform.release()
    return render_template("dashboard.html", os=os_name)

@app.route("/data")
def data():
    return jsonify(get_last_50_data())

@app.route("/status")
def status():
    alerts = []
    if latest_data["cpu"] > 90: alerts.append("High CPU Usage")
    if latest_data["ram"] > 90: alerts.append("High RAM Usage")
    if latest_data["disk"] > 90: alerts.append("High Disk Usage")
    if latest_data["network"] == "Cloud Issue": alerts.append("Cloud Service Down")

    return jsonify({"current": latest_data, "alerts": alerts})

if __name__ == "__main__":
    init_db()
    threading.Thread(target=background_monitor, daemon=True).start()
    app.run(host="0.0.0.0", port=5000, debug=False)
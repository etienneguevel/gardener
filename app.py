"""
Sensor Dashboard - local web interface for humidity & luminosity captors.

Run with:
    python app.py

Then open http://127.0.0.1:5000 in your browser (on the same computer),
or http://<this-computer-ip>:5000 from another device on your network.
"""

import time
from collections import deque
from datetime import datetime

import threading
from flask import Flask, jsonify, render_template

from gardener.sensors import read_captors

app = Flask(__name__)

# Keep the last N readings in memory for the history graph
HISTORY_LEN = 60
history_lock = threading.Lock()
history = deque(maxlen=HISTORY_LEN)


def poll_sensors_loop(interval_seconds: float = 2.0):
    """Background thread: reads sensors on a fixed interval and stores history."""
    while True:
        try:
            temperature, humidity, luminosity = read_captors()
            reading = {
                "time": datetime.now().strftime("%H:%M:%S"),
                "humidity": humidity,
                "luminosity": luminosity,
            }
            with history_lock:
                history.append(reading)
        except Exception as e:
            # Don't crash the polling loop if a sensor read fails momentarily
            print(f"[sensor read error] {e}")
        time.sleep(interval_seconds)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/current")
def api_current():
    with history_lock:
        if history:
            return jsonify(history[-1])
    return jsonify({"time": None, "humidity": None, "luminosity": None})


@app.route("/api/history")
def api_history():
    with history_lock:
        return jsonify(list(history))


if __name__ == "__main__":
    # Start the background polling thread
    t = threading.Thread(target=poll_sensors_loop, args=(2.0,), daemon=True)
    t.start()

    # host="0.0.0.0" makes it reachable from other devices on your network too
    app.run(host="0.0.0.0", port=5000, debug=False)
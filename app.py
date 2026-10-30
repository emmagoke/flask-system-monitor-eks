from flask import Flask, render_template, jsonify
import psutil

app = Flask(__name__)

THRESHOLD = 80

def get_metrics():
    cpu_metric = psutil.cpu_percent(interval=1)
    memory_metric = psutil.virtual_memory().percent

    message = None
    if cpu_metric > THRESHOLD or memory_metric > THRESHOLD:
        message = "High CPU or Memory Detected, scale up!!!"
    return {"cpu": cpu_metric, "mem": memory_metric, "message": message}

@app.route("/")
def home():

    return render_template("index.html", **get_metrics())

@app.route("/metrics")
def metrics():
    return jsonify(get_metrics())

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

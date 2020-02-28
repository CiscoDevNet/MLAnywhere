from flask import Flask, url_for, send_from_directory
import os
import json

app = Flask(__name__)


@app.route('/')
@app.route('/index.html')
def index():
    return send_from_directory('static','index.html')

@app.route('/static/<path:path>')
def serve_static():
    return send_from_directory('static',path)

@app.route('/status')
def get_status():
    with open("/usr/mnt/log.txt", "r+", encoding="utf-8") as f:
        return json.dumps(f.readlines())

@app.route('/examples/bolts_demo.zip')
def get_bolts_demo():
    return send_from_directory('static','bolts_demo.zip')


if __name__ == "__main__":
    app.run(host='0.0.0.0')
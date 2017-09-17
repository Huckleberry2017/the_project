from threading import Lock
import _thread as thread
import matplotlib.pyplot as plt
import matplotlib.cm as colormap
import numpy as np
import requests
from time import sleep

from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
app = Flask(__name__)
CORS(app)
sock = SocketIO(app)

from sweeppy import Sweep as sp
from breezyslam.components import Laser
from breezyslam.algorithms import RMHC_SLAM
import json
import sys

lidar = Laser(200, 500, 360, 40000, 0, 0)
slam = RMHC_SLAM(lidar, 800, 40)

share = {'stuff': []}
lock = Lock()

def send(stuff):
        sock.emit('data', stuff)
        print("sent")

def scan():
    with sp("/dev/tty.usbserial-DM00LDB3") as sweep:
        while True:
            if sweep.get_motor_ready():
                break
        print("READY")

        sweep.set_sample_rate(1000)
        sweep.set_motor_speed(5)

        sweep.start_scanning()
        samples = []

        for scan in sweep.get_scans():
            if len(scan.samples) >= 200:
                print("Scaned")
                for sample in scan.samples:
                    samples.append(sample.distance)
                slam.update(samples[:200])
                x, y, theta = slam.getpos()
                stuff = {'samples': [{'distance': s.distance, 'angle': s.angle} for s in scan.samples[:200]], 'actor': {'x': x, 'y': y, 'theta': theta}}
                sock.start_background_task(send, (stuff,))
            samples = []

sock.start_background_task(target=scan)

@app.route("/")
def index():
    return "<html><head><script src='https://cdnjs.cloudflare.com/ajax/libs/socket.io/2.0.3/socket.io.slim.js'></script></head><body></body></html>"

@app.route("/message")#, methods["POST"])
def mass_message():
    nums = ["15617583358",
            "14023099580"
            ]
    count = 0
    for num in nums:
        if count >= 3:
            #WAIT
            count = 0
        r = requests.post("https://rest.nexmo.com/sms/json", params={'api_key': '541f753d', 'api_secret': 'f8d5709228b03d79', 'to': num, 'from': '12016728883', 'text': 'EMERGEN C'})
        sleep(.3)
        count += 1
    return "DONE"

if __name__ == "__main__":
    SocketIO.run(app)

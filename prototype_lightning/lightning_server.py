#
#   Lightning server
#
from gevent import monkey, spawn

from prototype_lightning.get_distance import get_distance_with_geopy

monkey.patch_all()


import zmq.green as zmq
import json

airports = [
    {"id": 1, "name": "San Jose Airport", "lat": 37.36384485275424, "lon": -121.92911989199551},
    {"id": 2, "name": "San Francisco Airport", "lat": 37.62115141922509, "lon": -122.3788802999304},
]

context = zmq.Context()
logger_sender_socket = context.socket(zmq.PUSH)
logger_sender_socket.connect("ipc:///tmp/log.pipe")


socket = context.socket(zmq.PULL)
socket.bind("ipc:///tmp/test.pipe")


while True:
    #  Wait for next request from client
    message = socket.recv()

    obj = json.loads(message)
    # print(obj)

    spawn(get_distance_with_geopy, obj, airports, logger_sender_socket)
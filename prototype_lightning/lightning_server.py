#
#   Hello World server in Python
#   Binds REP socket to tcp://*:5555
#   Expects b"Hello" from client, replies with b"World"
#
from gevent import monkey, spawn
monkey.patch_all()


import zmq.green as zmq
import json
import logging
import time

formatter = logging.Formatter('%(asctime)s -%(name)s - %(levelname)s -- %(message)s')
log = logging.getLogger()
log.setLevel(logging.INFO)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)
log.addHandler(console_handler)

airports = [
    {"id": 1, "name": "San Jose Airport", "lat": 37.36384485275424, "lon": -121.92911989199551},
    {"id": 2, "name": "San Francisco Airport", "lat": 37.62115141922509, "lon": -122.3788802999304},
]

context = zmq.Context()
logger_sender_socket = context.socket(zmq.PUSH)
logger_sender_socket.connect("ipc:///tmp/log.pipe")


def get_distance(obj) -> float:
    """
    output distance in meters
    """

    from shapely.geometry import Point
    import geopandas as gpd

    for p in airports:
        points_df = gpd.GeoDataFrame(
            {'geometry': [Point(obj["lon"], obj["lat"]), Point(p["lon"], p["lat"])]},
            crs='EPSG:4326',
        )
        points_df = points_df.to_crs('EPSG:5234')
        points_df2 = points_df.shift()
        dist = points_df.distance(points_df2)

        logger_sender_socket.send_string("%.2f" % time.time())
        if dist.array[1] < 48280.3:  # 30 miles in m
            logger_sender_socket.send_string(f"Airport within 30 mile radius: {p}. Distance (m): {dist.array[1]}")
        else:
            logger_sender_socket.send_string(f"Airport outside 30 mile radius: {p}. Distance (m): {dist.array[1]}")



socket = context.socket(zmq.PULL)
socket.bind("ipc:///tmp/test.pipe")


# resi_buildings = []

while True:
    #  Wait for next request from client
    message = socket.recv()

    obj = json.loads(message)
    # print(obj)

    spawn(get_distance, obj)
#
#   Send the objects (comercial buildings in our prototype) through the pipes.
#   The pipe could go through airport listener, resi listener, etc.

import zmq
import json

context = zmq.Context()

#  Socket to talk to server
print("Connecting to lightning server...")
socket = context.socket(zmq.PUSH)
socket.connect("ipc:///tmp/test.pipe")

com_buildings = [
    {"id": 1, "lat": 37.3376839, "lon": -121.8370821, "name": "Andu"},
    {"id": 2, "lat": 37.45120771293968, "lon": -122.18680756130705, "name": "1C"},
]

#  Do 10 requests, waiting each time for a response
for count in range(100):
    print(count)
    for request in com_buildings:
        print(f"Sending request {request} ...")
        socket.send_string(json.dumps(request))
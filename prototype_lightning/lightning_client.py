#
#   Hello World client in Python
#   Connects REQ socket to tcp://localhost:5555
#   Sends "Hello" to server, expects "World" back
#

import zmq

context = zmq.Context()

#  Socket to talk to server
print("Connecting to hello world server...")
socket = context.socket(zmq.REQ)
socket.connect("ipc:///tmp/test.pipe")

com_buildings = [
    {"id": 1, "lat": 37.3376839, "lon": -121.8370821, "name": "Andu"},
    {"id": 2, "lat": 37.45120771293968, "lon": -122.18680756130705, "name": "1C"},
]

#  Do 10 requests, waiting each time for a response
for request in range(10):
    print(f"Sending request {request} ...")
    socket.send_string("Hello")

    #  Get the reply.
    message = socket.recv()
    print(f"Received reply {request} [ {message} ]")
from gevent import monkey, spawn
monkey.patch_all()


import zmq.green as zmq


context = zmq.Context()
socket = context.socket(zmq.PULL)
socket.bind("ipc:///tmp/log.pipe")


while True:
    #  Wait for next request from client
    message = socket.recv()

    spawn(print, message)
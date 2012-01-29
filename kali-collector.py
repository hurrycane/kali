import zmq
import re
import time
import threading

from msgpack import unpackb

context = zmq.Context()
socket = context.socket(zmq.REP)

socket.bind("tcp://*:56468")

#q = Queue.Queue()

def main():

  while True:
    message = socket.recv()
    try:
      metrics = unpackb(message)
      print len(metrics.keys())
    except:
      metrics = {}

    socket.send("OK")

if __name__ == "__main__":
  main()

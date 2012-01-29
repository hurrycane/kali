import zmq
import time
import string
import random

import threading

context = zmq.Context()
socket = context.socket(zmq.REQ)

def run():
  socket = context.socket(zmq.REQ)
  socket.connect("ipc:///tmp/metrics.pipe")

  N = 1
  
  loop_start = time.time()

  for x in range(N):

    bucket = ""
    for i in range(4):
      bucket += random.choice(string.letters)

    message = bucket + ":" + str(random.random()*1000) + "|ms"

    socket.send(message)
    message = socket.recv()

  loop_end = time.time()
  x = loop_end - loop_start

  print x
  print float(N) / x


threads = []
#for i in range(1):
#  t = threading.Thread(target=run)
#  t.start()

#[t.join() for t in threads]
run()

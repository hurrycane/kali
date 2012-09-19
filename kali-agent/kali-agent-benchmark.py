import zmq
import time
import string
import random

import threading

context = zmq.Context()
socket = context.socket(zmq.REQ)

semaphore = threading.BoundedSemaphore(50)

buckets = ["testing","ceva","chiuveta","lalele","franzele"]

def run():
  semaphore.acquire()

  socket = context.socket(zmq.REQ)
  socket.connect("ipc:///tmp/local.pipe")

  N = 100
  loop_start = time.time()

  #bucket = ""
  #for i in range(4):
  #  bucket += random.choice(string.letters)
  bucket = buckets[random.randint(0,4)]

  for x in range(N):

    message = bucket + ":" + str(random.random()*1000) + "|ms"

    socket.send(message)
    message = socket.recv()

  loop_end = time.time()
  x = loop_end - loop_start

  print x
  print float(N) / x

  semaphore.release()

while True:
  threads = []
  for i in range(10):
    t = threading.Thread(target=run)
    threads.append(t)
    t.start()
  [t.join() for t in threads]
  time.sleep(1)

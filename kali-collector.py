import zmq
import re
import time
import threading

import pymongo

import Queue

from msgpack import unpackb

import metrics_processing

context = zmq.Context()
socket = context.socket(zmq.REP)

socket.bind("tcp://*:56468")

q = Queue.Queue()

def server_thread():

  while True:
    message = socket.recv()
    try:
      print "Received"
      q.put(message)
      metrics = unpackb(message)
    except:
      metrics = {}

    socket.send("OK")

def storage_thread():
  while True:
    print "Storage"
    item = q.get()
    metrics = unpackb(item)

    # for each metric insert it
    print len(metrics.keys())

    # insert item into DB
    for metric in metrics.keys():
      # funny
      metrics_processing.process_metric(metric,metrics[metric])
    
    print "Thread"
    q.task_done()
    print "Done"

def main():
  threads = []
  t = threading.Thread(target=server_thread)
  threads.append(t)

  t = threading.Thread(target=storage_thread)
  threads.append(t)

  [t.start() for t in threads]
  [t.join() for t in threads]

if __name__ == "__main__":
  main()

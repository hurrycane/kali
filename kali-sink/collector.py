import zmq
from msgpack import unpackb

import logging
import Queue
import os
import sys

import time

import threading

current_path = os.path.realpath(__file__)
sys.path.append("/".join(current_path.split("/")[0:-2]))

from metric import *
from watchdog import *

# port 56468"
class Collector:
  def __init__(self,port,retention):
    self.port = port
    self.retention = retention

    self.q = Queue.Queue()

    # lock guarding storage structure
    self.rlock = threading.RLock()

    # storage for metrics as a dictionary of metrics
    # indexed by metric name
    self.storage = {}

  def start(self):
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.REP)
    self.socket.bind("tcp://*:" + str(self.port))
    
    logging.info('Listening for connections on %d ' % self.port)

    while True:
      print "Here"
      message = self.socket.recv()
      print "There!"
      logging.info('Payload received')
      try:
        self.q.put(message)
      except:
        metrics = {}
      finally:
        self.socket.send("OK")

  def ticker(self):
    """
      Watchdog thread. Manages thread that 
    """
    watchdog = Watchdog(self)
    watchdog.start()
    
  
  def store(self):
    logging.info("Storage thread started")
    while True:
      item = self.q.get()
      payload = unpackb(item)

      logging.info('Payload processes with %d metrics' % len(payload.keys()))
      for metric_name in payload.keys():
        # requires locking since it's querying and
        # updating the storage structure

        try:
          self.rlock.acquire()
          if metric_name not in self.storage:
            self.storage[metric_name] = Metric(metric_name,self.retention)
          # metric.addAll acquires a lock on Metric
          self.storage[metric_name].addAll(payload[metric_name])
        finally:
          self.rlock.release()

      self.q.task_done()

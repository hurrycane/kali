import threading
import zmq
import re
import time

from msgpack import packb

S_LEN = 5

class Agent():

  def __init__(self,local_pipe,collector_addr,collect_time):
    self.collector_addr = collector_addr
    self.local_pipe = local_pipe
    self.collect_time = collect_time

    self.lock = threading.RLock()
    self.metrics = {}

  """
    Listen to the local pipe for incoming metrics.
  """
  def start(self):
    self.context = zmq.Context()
    self.socket = self.context.socket(zmq.REP)
    self.socket.bind("ipc://" + self.local_pipe)

    while True:
      message = self.socket.recv()
      # for each received metric validate it and store it localy
      self.store_metric(message)
      self.socket.send("RESP")

  """
    Validate and store metric information.
    A metric that is received must be in the following format:
    <bucket> : <int/float value> | <type>
    where:
    bucket is the name of the metric it can be any alphanumeric string.
    value  is the value recorded by the metric it can be either int
           or float
    type   represents what type the metric is: It can be one of the
           following: c - counter, ms - time based series, g - gauges
           @<float> - samples with <float> representing the value of 
           the applied sampling
  """
  def store_metric(self,message):
    message = re.split('(\w+)\:([-+]?\d*\.\d+|\d+)\|(.+)',message)

    # after split exactly S_LEN pieces need to be present
    if len(message) == S_LEN:
      bucket = message[1]
      value = message[2]
      category = message[3]
    else:
      return 

    # TODO Refactor verification to be included in regex
    categories = [ "c", "ms", "g" ]
    if category not in categories:
      return

    bucket = bucket + ":" + category

    try:
      self.lock.acquire()
      if bucket not in self.metrics:
        self.metrics[bucket] = []
      self.metrics[bucket].append({ 'v' : float(value), 't': time.time() })
    finally:
      self.lock.release()

  def collect(self):
    while True:
      time.sleep(self.collect_time)

      self.lock.acquire()
      if len(self.metrics.keys()) != 0:
        print "Metrics found"
        m = packb(self.metrics)
        self.metrics.clear()
      else:
        print "No metrics"
        m = None
      self.lock.release()

      if m != None:
        print "Sending metrics"
        self.send_to_collector(m)
  
  def nb_metrics(self):
    return len(self.metrics.keys())
  
  def get_data_points(self,bucket_name):
    return self.metrics[bucket_name]

  def send_to_collector(self,message):
    collector = self.context.socket(zmq.REQ)
    collector.connect("tcp://" + self.collector_addr)
    collector.send(message)
    collector.close()

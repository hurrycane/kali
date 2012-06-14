import blist
import threading

"""
.. moduleauthor:: Bogdan Gaza <bc.gaza@gmail.com>
"""
class Metric():
  """
    Metric: unit of work that publishes persistent data points.

    Internal structure:
    A Metric keeps a track of internal data points on which periodically
    computes a value and stores it (a persistent data point).

    The list of on internal data points is a blist.sortedlist.
    Insert time is O(logN) but we can do at any point in time queries
    about percentile information (tp50, tp90, tp99).
  """
  def __init__(self, name, retention):
    self.retention = retention
    self.name = name

    self.points = {}
    self.min_timestamp = {}

    self.rlock = threading.RLock()

    for period in self.retention:
      self.points[period] = []
      self.points[period].append(blist.sortedlist([]))

      self.min_timestamp[period] = False
  
  """
    Add an internal datapoint
  """
  def add(self, timestamp, value):
    try:
      self.rlock.acquire()

      for period in self.retention:
        # check if there is a min_timestamp
        if self.min_timestamp[period] != False:
          # check if current list has expired
          if timestamp > self.min_timestamp[period] + period:
            # if is expired add new list
            self.min_timestamp[period] = timestamp
            self.points[period].append(blist.sortedlist([]))
        else:
          # set min_timestamp 
          self.min_timestamp[period] = timestamp

        self.points[period][-1].add(value)
    finally:
      self.rlock.release()
  """
    Add a list of values to the roundlist. Value list can be either a list with
    two elements: the first one is the timestamp the other one is the value OR
    a dictionary indexed by t (timestamp) and v (value).
  """
  def addAll(self,value_list):
    for elem in value_list:
      if type([]) is type(elem):
        self.add(elem[0],elem[1])
      else:
        self.add(elem["t"],elem["v"])

  def size(self,period):
    return len(self.points[period][-1])
  
  """
    Switch buffer for a specific period
  """
  def tick(self,period,timestamp):
    try:
      self.rlock.acquire()
      self.min_timestamp[period] = timestamp
      self.points[period].append(blist.sortedlist([]))
    finally:
      self.rlock.release()

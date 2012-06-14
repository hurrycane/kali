import threading

"""
.. moduleauthor:: Bogdan Gaza <bc.gaza@gmail.com>
"""
class Metric():
  """
    Metric: unit of work that publishes persistent data points.

    Internal structure:

    A Metric keeps a track of internal data points.
    It periodically flushes them into a Redis instance.

    Storing in Redis is done in the following way:
    A metric has a name and some internal data points for a period of time (10s, 600s, etc).
    
    We keep in Redis the following key:

    "_".join([
    METRIC_PREFIX,
    TIMESTAMP,
    PERIOD])

    Metric Prefix is self explicatory the default is metric_
    Timestamp means the timestamp - timestamp % period,
              where period is an element of the retention variables.
              Ex: 1339705933 - 1339705933 % 10  = 1339705930
                  1339705933 - 1339705933 % 600 = 1339705800
    Period is one of the elements of the retantion array:
              Ex: 10, 600, 3600 etc.

    Future work:
    Compute percentile information for < 60s retention periods
    in memory instead of after redis storage.
  """
  def __init__(self, name, retention):
    self.retention = retention
    self.name = name

    self.points = {}
    self.min_timestamp = {}

    self.rlock = threading.RLock()

    # never flushed
    self.last_flushed = False

    for period in self.retention:
      self.points[period] = {}
  
  """
    Add an internal datapoint
  """
  def add(self, timestamp, value):
    try:
      self.rlock.acquire()

      for period in self.retention:
        t = timestamp - (timestamp % period)
        if t not in self.points[period]:
          self.points[period][t] = []
        
        self.points[period][t].append({'t' : timestamp, 'v' : value})
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

import threading
import os
import sys
import logging
import time
import math

import heapq

import redis
import publish

"""
  Watchdog

  The purpose of this module is to flush metric buffers
  to the redis database. So it keeps a minheap of the
  last time a metric has been flushed.
"""
class Watchdog():

  def __init__(self,collector):
    self.collector = collector

    # lock guaring the latest flushed heap
    self.h_lock = threading.RLock()

    # internal heap to store the oldest timestamp of a
    # flushed metric
    self.heap = []

    # redis connection
    # TODO Inject credentials
    self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
    self.publish = publish.Publish(self)

  """
    Start watch metrics and flush metrics threads
  """
  def start(self):
    logging.info("Watchdog started")

    threads = []
    t = threading.Thread(target=self.watch_metrics)
    threads.append(t)

    t = threading.Thread(target=self.flush_metrics)
    threads.append(t)

    t = threading.Thread(target=self.publish.publish_metrics)
    threads.append(t)

    [t.start() for t in threads]
    [t.join() for t in threads]

  def flush(self,elem):
    to_flush = heapq.heappop(self.heap)

    # update last flushed timestamp
    metric_name = to_flush[1]
    metric = self.collector.storage[metric_name]

    self.compute_persistent(metric)
    metric.last_flushed = math.trunc(time.time())

    # push metric with new timestamp back into the heap
    heapq.heappush(self.heap,(metric.last_flushed, metric_name))

  """
    The purpose is to flush the metrics from the in-memory
    store to Redis.

    It queries the min-heap for the minimum timestamp (the oldest
    flush timestamp) of the metrics and then it flushes the metric
    and updates the heap.
  """
  def flush_metrics(self):
    # sleep time is used to store the amount of sleep outside
    # the lock
    sleep_time = 0

    while True:
      if sleep_time != 0:
        time.sleep(sleep_time)

      try:
        sleep_time = 0
        # acq lock because we're modifying the heap
        self.h_lock.acquire()

        # if there is an element in the heap than try to process it
        if len(self.heap) > 0:
          elem = self.heap[0]

          # if since the last flush it has passed more than 11 seconds
          # then consider element
          if time.time() - elem[0] > 11:
            self.flush(elem)
          else:
            sleep_time = 11 + time.time() - elem[0]

        else:
          # sleep 5 maybe there are elements in the heap next time we look
          sleep_time = 5
      finally:
        # whatever happens release the lock
        self.h_lock.release()

  """
    Flush metrics to Redis
  """
  def compute_persistent(self,metric):
    # get curent timestamp to compute the last bucket of the
    # metric
    timestamp = math.trunc(time.time())
    # also prefetch the periods for computing metrics
    retention = self.collector.retention

    # keep and array of metrics that need to be flushed
    flushable = []

    # for every period
    for period in retention:
      # compute the latest bucket
      latest = timestamp - timestamp % period

      try:
        metric.rlock.acquire()
        # get the metric data points for the current period
        data_points = metric.points[period]

        # for every bucket in the current period
        for stamp in data_points.keys():
          # try to truncate the stamp
          stamp = math.trunc(stamp)

          if stamp + period + 11 <= timestamp:
            logging.info("Flushing %d data points for %s metric for period %s. At %s timestamp for the stamp %s" %
                        (len(data_points[stamp]),metric.name, str(period), str(time.time()), str(stamp)))

            flushable.append({ 'm' : metric,  'name' : metric.name + "_" + str(stamp) + "_" + str(period),
                               'v' : list(data_points[stamp]), 's': stamp, 'p': period})
            del metric.points[period][stamp]

      finally:
        metric.rlock.release()

    self.persist_metrics(flushable)

  def persist_metrics(self,flushable):
    # create redis pipeline
    pipe = self.redis.pipeline()
    """
      Flushable contains dicts with the following format:
      m = metric, name = metric name in redis, v = the value list,
      s = a timestamp from which the interval starts
      p = the period for that metric
    """
    for f in flushable:
      # for each flushable metric. Get the list of values
      for value in f['v']:
        pipe.zadd(f['name'],value['t'],value['v'])

      f['m'].processed_time = time.time()
      processed_key = max(long(f['s']) + long(f['p']) + 11,time.time())

      try:
        self.publish.p_lock.acquire()
        heapq.heappush(self.publish.flushed_heap,(processed_key, f))
      finally:
        self.publish.p_lock.release()

    # pipe flushing
    pipe.execute()

  """
    Watch Metrics
    Watch metrics purpose is to update the heap with the latests
    metric names collected by the service
  """
  def watch_metrics(self):
    logging.info("Watch metrics started")

    while True:
      # blocking wait to get a new metric_name
      metric_name = self.collector.nkeys.get()

      # get the metric
      metric = self.collector.storage[metric_name]
      # set it's last flushed time to now
      metric.last_flushed = math.trunc(time.time())

      try:
        self.h_lock.acquire()
        # push to heap new metric name is current last flushed timestamp
        heapq.heappush(self.heap,(metric.last_flushed, metric_name))
      finally:
        # release the lock and mark task as done
        self.h_lock.release()
        self.collector.nkeys.task_done()
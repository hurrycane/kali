import threading
import os
import sys
import logging
import time
import math

import heapq

S_LEN = 30

"""
  Watchdog

  The purpose of this module is to flush metric buffers
  to the redis database. So it keeps a minheap of the
  last time a metric has been flushed.
"""
class Watchdog():

  def __init__(self,collector):
    self.collector = collector

    # lock guaring the heap
    self.h_lock = threading.RLock()

    # internal heap to store the oldest timestamp of a
    # flushed metric
    self.heap = []

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
    
    [t.start() for t in threads]
    [t.join() for t in threads]

  """
    The purpose is to flush the metrics from the in-memory
    store to Redis.

    It queries the min-heap for the minimum timestamp (the oldest
    flush timestamp) of the metrics and then it flushes the metric
    and updates the heap.
  """
  def flush_metrics(self):
    sleep_time = 0
    
    while True:
      if sleep_time != 0:
        time.sleep(sleep_time)

      try:
        sleep_time = 0
        self.h_lock.acquire()

        if len(self.heap) > 0:
          elem= self.heap[0]

          # if since the last flush it has passed more than 11 seconds
          # then consider element
          if time.time() - elem[0] > 11:
            # flush metric into DB
            to_flush = heapq.heappop(self.heap)

            print "Flushed value"
            print to_flush

            metric_name = to_flush[1]
            metric = self.collector.storage[metric_name]
            metric.last_flushed = time.time()

            heapq.heappush(self.heap,(metric.last_flushed, metric_name))

          else:
            sleep_time = 11 + time.time() - elem[0]
        else:
          sleep_time = 5
      finally:
        self.h_lock.release()

  """
    Watch metrics purpose is to update the heap with the latests
    metric names collected by the service
  """
  def watch_metrics(self):
    logging.info("Watchdog started")

    while True:
      metric_name = self.collector.nkeys.get()

      metric = self.collector.storage[metric_name]
      metric.last_flushed = time.time()

      try:
        self.h_lock.acquire()
        heapq.heappush(self.heap,(metric.last_flushed, metric_name))
      finally:
        self.h_lock.release()
        self.collector.nkeys.task_done()

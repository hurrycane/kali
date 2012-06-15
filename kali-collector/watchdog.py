import threading
import os
import sys
import logging
import time
import math

import heapq

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
            # remove element from the heap
            to_flush = heapq.heappop(self.heap)

            print "Flushed value"
            print to_flush

            # update last flushed timestamp
            metric_name = to_flush[1]
            metric = self.collector.storage[metric_name]
            metric.last_flushed = time.time()

            # push metric with new timestamp back into the heap
            heapq.heappush(self.heap,(metric.last_flushed, metric_name))

          else:
            # sleep the exact amount of time needed before a metric expires
            sleep_time = 11 + time.time() - elem[0]
        else:
          # sleep 5 maybe there are elements in the heap next time we look
          sleep_time = 5
      finally:
        # whatever happens release the lock
        self.h_lock.release()

  """
    Watch metrics purpose is to update the heap with the latests
    metric names collected by the service
  """
  def watch_metrics(self):
    logging.info("Watchdog started")

    while True:
      # blocking wait to get a new metric_name
      metric_name = self.collector.nkeys.get()

      # get the metric
      metric = self.collector.storage[metric_name]
      # set it's last flushed time to now
      metric.last_flushed = time.time()

      try:
        self.h_lock.acquire()
        # push to heap new metric name is current last flushed timestamp
        heapq.heappush(self.heap,(metric.last_flushed, metric_name))
      finally:
        # release the lock and mark task as done
        self.h_lock.release()
        self.collector.nkeys.task_done()

import logging
import threading
import time
import math
import heapq
import redis

from pymongo import Connection

class Publish():

  def __init__(self,watchdog):
    # lock guaring the latest published heap
    self.p_lock = threading.RLock()
    self.flushed_heap = []
    
    self.watchdog = watchdog
    self.redis = redis.StrictRedis(host='localhost', port=6379, db=0)
    
    self.connection = Connection('localhost', 27017)
    self.db = self.connection.monitoring
    self.metrics = self.db.metrics

  def publish_metrics(self):
    logging.info("Publish metrics started")

    sleep_time = 0

    while True:
      if sleep_time != 0:
        time.sleep(sleep_time)

      try:
        sleep_time = 0
        # acq lock because we're modifying the heap
        self.p_lock.acquire()

        # if there is an element in the heap than try to process it
        if len(self.flushed_heap) > 0:
          elem = self.flushed_heap[0]
          # if since the last flush it has passed more than 11 seconds
          # then consider element
          timestamp = math.trunc(time.time())

          # if it's not in the future process it
          if elem[0] <= timestamp:
            to_flush = heapq.heappop(self.flushed_heap)
            # zcard  wFmQ:ms_1340024400_600
            self.persist_data_point(to_flush)
            # compute percentile information (get rank from redis + get element from redis)
          else:
            sleep_time = elem[0] - math.trunc(time.time())

        else:
          # sleep 5 maybe there are elements in the heap next time we look
          sleep_time = 5

      finally:
        self.p_lock.release()

  def persist_data_point(self,to_flush):
    redis_metric_name = to_flush[1]['name']
    period = to_flush[1]['p']
    stamp = to_flush[1]['s']

    p90 = self.compute_percentiles(redis_metric_name,9.0)
    p50 = self.compute_percentiles(redis_metric_name,5.0)
    minn = self.compute_percentiles(redis_metric_name,0.0)
    maxx = self.compute_percentiles(redis_metric_name,10.0)
    nn = self.redis.zcard(redis_metric_name)

    metric = {
      'name' : to_flush[1]['m'].name,
      'period' : period,
      'timestamp' : stamp,
      'stats' : {
        'p90' : p90,
        'p50' : p50,
        'min' : minn,
        'max' : maxx,
        'n'   : nn
      }
    }

    self.metrics.insert(metric)

  def compute_percentiles(self,metric_name,index):
    nb_points = self.redis.zcard(metric_name)

    if nb_points < 9:
      return None
    else:
      point = round(nb_points / 10.0 * index)
      if point > 0:
        point -= 1

      logging.info("Fetching index %d" % point)
      r = self.redis.zrange(metric_name,int(point),int(point),withscores=True)
      print r
      print r[0]

      if len(r) > 0:
        return r[0][0]
      else:
        return None
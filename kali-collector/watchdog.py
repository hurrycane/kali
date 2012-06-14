import threading
import os
import sys
import logging

import time
import math

current_path = os.path.realpath(__file__)
sys.path.append("/".join(current_path.split("/")[0:-2]))

S_LEN = 30

class Watchdog():

  def __init__(self,collector):
    self.collector = collector
    
    self.rlock = threading.RLock()
    self.nb_threads = 0
    self.threads = []

    self.watch = {}

  def start(self):
    idx = 0
    logging.info("Watchdog started")
    while True:
      if idx % 2 == 0:
        self.watch_storage()
      else:
        self.watch_tickers()

      idx = (idx + 1) % 2
      time.sleep(5)

  def watch_tickers(self):
    threads = []

    diff = self.nb_threads - len(self.threads)
    idx = len(self.threads)

    if diff > 0:
      c_threads = []
      for i in range(diff):
        thread = threading.Thread(target=self.watch_metrics, args=(idx+i,))
        self.threads.append(thread)
        c_threads.append(thread)

      [ t.start() for t in c_threads ]

  def watch_metrics(self,*args):
    first_run = 0

    diff = 10 - (math.trunc(time.time()) % 10)

    index = args[0]
    print "Current index is %d " % index

    while True:
      if first_run == 0:
        time.sleep(diff)
        first_run = 1
      else:
        time.sleep(10)

      try:
        self.rlock.acquire()
        watching = self.watch[index]
      finally:
        self.rlock.release()
        
      print "Watching"
      print watching

  def watch_storage(self):
    w = {}

    try:
      self.collector.rlock.acquire()
      keys = self.collector.storage.keys()
    finally:
      self.collector.rlock.release()

    logging.info("Managing %d metric" % len(keys))
    nb_threads = ( len(keys) / S_LEN ) + 1

    if (len(keys) % 2) == 0:
      nb_threads -= 1

    logging.info("%d threads are opened for processing" % nb_threads)

    nth_thread = 0
    for key in keys:
      if nth_thread not in w:
        w[nth_thread] = []

      w[nth_thread].append(key)
      if len(w[nth_thread]) > S_LEN:
        nth_thread += 1

    self.nb_threads = nb_threads

    try:
      self.rlock.acquire()
      self.watch = w
    finally:
      self.rlock.release()

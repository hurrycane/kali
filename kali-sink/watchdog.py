import threading
import os
import sys

import time

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
    while True:
      if idx % 2 == 0:
        self.watch_storage()
      else:
        self.update_threads()

      idx = (idx + 1) % 2
      time.sleep(5)

  def watch_tickers(self):
    diff = self.nb_threads - len(self.threads)
    if(diff > 0):
      for i in range(diff):
        thread = Thread(target=self.watch_metrics, args=())
        self.threads.append(thread)

  def watch_metrics(self,*args):

  def watch_storage(self):
    w = {}

    try:
      self.collector.rlock.acquire()
      keys = self.collector.storage.keys()
    finally:
      self.collector.rlock.release()

    nb_threads = len(keys) / S_LEN

    nth_thread = 0
    for key in keys:
      if nth_thread not in w:
        w[nth_thread] = []

      w[nth_thread].append(key)
      if len(w[nth_thread]) > S_LEN:
        nth_thread += 1

    self.nb_threads = nb_thread

    try:
      self.rlock.acquire()
      self.watch = w
    finally:
      self.rlock.release()

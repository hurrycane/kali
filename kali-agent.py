import zmq
import re
import time
import threading

from msgpack import packb

context = zmq.Context()
socket = context.socket(zmq.REP)

socket.bind("ipc:///tmp/metrics.pipe")

lock = threading.RLock()
metrics = {}
S_LEN = 5

# metric format is <bucket> : <int/float value> | <type>
# <type> can be:
# counter: c
# timer: ms
# sampled: @<float> were <float> means sampling radio
def storeMetric(message):
  global messages
  message = re.split('(\w+)\:([-+]?\d*\.\d+|\d+)\|(.+)',message)

  # after split exactly S_LEN pieces need to be present
  if len(message) == S_LEN:
    bucket = message[1]
    value = message[2]
    category = message[3]

    lock.acquire()
    if bucket in metrics:

      if category == "c":
        metrics[bucket] += value
      elif category == "ms" or category[0] == '@':
        metrics[bucket].append(value)

    else:

      if category == "c":
        metrics[bucket] = 0
        metrics[bucket] += value
      else:
        metrics[bucket] = []
        metrics[bucket].append(value)

    lock.release()

def server_thread():
  global metrics

  idx = 0
  while True:
    message = socket.recv()
    storeMetric(message)
    socket.send("RESP")

def send_to_collector():
  global metrics

  while True:
    # sleep for 10 seconds before sending metrics to
    # collector
    time.sleep(10)

    # pack metrics
    # this area needs locking because we're clearing
    # the metrics dictionary.
    print len(metrics.keys())
    lock.acquire()
    print len(metrics.keys())
    m = packb(metrics)
    metrics.clear()
    lock.release()
    print len(metrics.keys())

    # send them to collector
    collector = context.socket(zmq.REQ)
    collector.connect("tcp://localhost:56468")

    collector.send(m)

    collector.close()

def main():
  threads = []
  t = threading.Thread(target=server_thread)
  threads.append(t)

  t = threading.Thread(target=send_to_collector)
  threads.append(t)

  [t.start() for t in threads]
  [t.join() for t in threads]

if __name__ == "__main__":
  main()

import zmq
import re
import threading

context = zmq.Context()
socket = context.socket(zmq.REP)

socket.bind("ipc:///tmp/metrics.pipe")

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

def server_thread():
  idx = 0
  while True:
    message = socket.recv()
    storeMetric(message)
    idx += 1

    socket.send("RESP")

server_thread()

import logging
from agent import *

"""
  Kali Agent

  This agent runs on every node of your distributed system.
  Different clients post metrics through a local zmq pipe.
  At a specific period of time the agent forwards the stored
  metrics to a collector that computes data points and
  publishes them into mongodb.
"""

logging.basicConfig(filename='kali-agent.log',
                    format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')

# local pipe name
LOCAL_PIPE = "/tmp/local.pipe"
# central collector address
COLLECTOR_ADDR = "localhost:56468"
# delay at which kali-agent sends collected metrics to
# central collector
COLLECT_TIME = 10

agent = Agent(LOCAL_PIPE,COLLECTOR_ADDR,COLLECT_TIME)

# basic server thread for reading and storing metrics from clients
def server_thread():
  agent.start()

# collector thread that sends data to the collector once every 10s
def send_to_collector():
  agent.collect()

# entry point
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

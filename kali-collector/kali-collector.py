import threading
from collector import *

port = 56468
logging.basicConfig(filename='kali-sink.log',
                    format='%(asctime)s %(levelname)s %(message)s',
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')

PORT = 56468
RETENTION = [60,600,3600]

collector = Collector(PORT,RETENTION)

def server_thread():
  collector.start()

def storage_thread():
  collector.store()

def ticker_thread():
  collector.ticker()

def main():
  threads = []
  t = threading.Thread(target=server_thread)
  threads.append(t)

  t = threading.Thread(target=storage_thread)
  threads.append(t)

  t = threading.Thread(target=ticker_thread)
  threads.append(t)

  [t.start() for t in threads]
  [t.join() for t in threads]

if __name__ == "__main__":
  main()

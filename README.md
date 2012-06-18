# Kali

Kali is a very simple metrics gathering agent and collector.
The agent runs on every node of your infrastructure while the collector is used for storing and computing data based on the metrics published by the agents.

Kali is written and python and uses as data stores redis and mongodb. The networling later is based zeromq and messagepack.

* Arhichitecture

Each node has a publishing agent. You send metrics to the publishing agent via ZeroMQ IPC socks.
The agents handles pushing the metrics to a general collectors.

The Collector stores per metric agregation of data points (for 10s, 10mins and 1h) and stores into a sorted-set data-structure maintained
by Redis. Periodically it computes percentile information (easy to do so because of the sorted-set) and publishes it into a mongodb
instance.

Pre-alpha release

[Bogdan Gaza][hurrycane]

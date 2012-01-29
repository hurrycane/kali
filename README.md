# Kali-agent

Kali-agent is a very simple metrics gathering agent and collector.
The agent runs on every node of your infrastructure while the collector is used for storing and computing data based on the metrics published by the agents.

Kali-agent and collector are based on zeromq.

* Arhichitecture

Each node has a publishing agent. You send metrics to the publishing agent via ZeroMQ IPC socks.
The agents handles pushing the metrics to a general collectors.

The Collector computes percentile information and normalization and then stores the metrics in a MongoDb instance.

Pre-alpha release

[Bogdan Gaza][hurrycane]

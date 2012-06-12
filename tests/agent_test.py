import unittest
import random

import sys
import os

current_path = os.path.realpath(__file__)
sys.path.append("/".join(current_path.split("/")[0:-2]))

from agent import *

class AgentTest(unittest.TestCase):
  def setUp(self):
    self.agent = Agent("/tmp/test.pipe","localhost:12345",10)

  def test_storeMetricMalformed(self):
    self.agent.store_metric("asd")
    self.assertEqual(self.agent.nb_metrics(),0)

  def test_storeMetricMs(self):
    self.agent.store_metric("testbucket:2.3|ms")
    self.assertEqual(self.agent.nb_metrics(),1)

    data_point = self.agent.get_data_points("testbucket:ms")[0]
    self.assertEqual(data_point["v"],2.3)
  
if __name__ == '__main__':
    unittest.main()

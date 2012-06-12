import unittest
import random

import sys
import os

current_path = os.path.realpath(__file__)
sys.path.append("/".join(current_path.split("/")[0:-2]))

from metric import *

class MetricTest(unittest.TestCase):
  def setUp(self):
    self.metric = Metric("test_metric",[60,600,3600])
  
  def test_addOne(self):
    self.metric.add(1339254325,23.34)
    self.assertEqual(self.metric.size(60),1)
    self.assertEqual(self.metric.size(600),1)
    self.assertEqual(self.metric.size(3600),1)

  def test_addAllWithList(self):
    initial = 1339254325
    value_list = []
    for i in range(10):
      value_list.append([initial + i, random.random() * 100])

    self.metric.addAll(value_list)
    self.assertEqual(self.metric.size(60),10)
    self.assertEqual(self.metric.size(600),10)
    self.assertEqual(self.metric.size(3600),10)
    
  def test_addOutsideInterval(self):
    self.metric.add(1339254325,23.34)
    self.metric.add(1339254325+70,23.34)
    self.assertEqual(self.metric.size(60),1)
    self.assertEqual(self.metric.size(600),2)

if __name__ == '__main__':
    unittest.main()

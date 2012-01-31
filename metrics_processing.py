import pymongo
import time
import random

import math
import sys

connection = pymongo.Connection("localhost", 27017)
db = connection.metrics

raw = db.raw
tp50 = db.tp50
tp90 = db.tp90
tp99 = db.tp99
avg = db.avg
n = db.n

def percentile(N, percent, key = lambda x:x):
  k = (len(N)-1) * percent
  f = math.floor(k)
  c = math.ceil(k)
  if f == c:
    return key(N[int(k)])
  d0 = key(N[int(f)]) * (c-k)
  d1 = key(N[int(c)]) * (k-f)
  
  return d0+d1

def compute(metrics):
  k = lambda x : x["v"]
  at_tp50 = percentile(metrics,0.5,k)
  at_tp90 = percentile(metrics,0.9,k)
  at_tp99 = percentile(metrics,0.99,k)
  at_tp100 = percentile(metrics,1,k)

  s = 0
  for i in metrics:
    s += i["v"]

  at_avg = s / float(len(metrics))
  at_n = len(metrics)

  return { "tp50" : at_tp50, "tp90" : at_tp90, "tp99" : at_tp99, "avg" : at_avg, "n" : at_n}

def publish_stats(collection,name,stats,metric_type,afinity = None):
  if afinity == None:
    metric = collection.find_one({"name":name, "c" : metric_type})
  else:
    metric = collection.find_one({"name":name, "c" : metric_type, 'a' : afinity})


  if(metric != None):
    collection.update( { "name" : name}, { "$pushAll" : { "values" : stats }})
  else:
    if afinity == None:
      metric = { "name" : name, "values" : stats, "c" : metric_type }
    else:
      metric = { "name" : name, "values" : stats, "c" : metric_type, 'a' : afinity }

    collection.insert(metric)

def distribute_stats(stats,timestamp,metrics):
  for k in metrics:
    stats[k].append({ 'v' : metrics[k], 't' : timestamp })

# publish metrics need to put metrics in different buckets
# sort them and publish tps and other metrics
def publish_metric(name,bucket,ch,afinity):

  aggregated = {}
  stats = { "tp50" : [], "tp90" : [], "tp99" : [], "avg" : [], "n" : [] }

  for metric in bucket:
    # assign to index
    idx = ch(metric)

    if idx not in aggregated:
      aggregated[idx] = []

    aggregated[idx].append(metric)

  timestamps = aggregated.keys()
  if len(timestamps) != 1:
    timestamps.pop()

  for m in timestamps:
    s = sorted(aggregated[m],key = lambda x: x["v"])
    # compute stats for metric aggregation
    distribute_stats(stats,m,compute(s))

  publish_stats(tp50,name,stats["tp50"],"ms",afinity)
  publish_stats(tp90,name,stats["tp90"],"ms",afinity)
  publish_stats(tp99,name,stats["tp99"],"ms",afinity)
  publish_stats(avg,name,stats["avg"],"ms",afinity)
  publish_stats(n,name,stats["n"],"ms",afinity)

def compute_percentile_tbs(name,bucket):
  min_metric = min(bucket,key=lambda x: x["t"])

  # fetch the whole second metrics
  older = raw.find_one({"c" : "ms", "values" : { "$elemMatch" : { "t" : { "$gt" : int(min_metric["t"]) } } } } , { "values" : { "$slice" : -100 }})

  if older != None:
    # you need to search the metrics
    for v in older["values"]:
      if v["t"] > min_metric:
        bucket.append(v)

  # metrics for 1s
  publish_metric(name,bucket,lambda x: int(x["t"]),"1s")

  # metrics for 5s
  publish_metric(name,bucket,lambda x: min_metric["t"] if x["t"] < min_metric["t"] + 5 else min_metric["t"] + 5,"5s")

  # metrics for 10s
  publish_metric(name,bucket,lambda x: min_metric["t"],"10s")

def compute_percentile_ns():
  pass

def process_metric(bucket_name,bucket):
  # insert metrics in the raw collection
  (name,metric_type) = bucket_name.split(":")
  
  if metric_type == "ms":
    compute_percentile_tbs(name,bucket)
  else:
    compute_percentile_ns(name,bucket)

  publish_stats(raw,name,bucket,metric_type)

metrics = [ { "t" : time.time() + random.randint(0,10), "v" : random.random()*1000 } for i in range(30) ]
process_metric("whateverz:ms",metrics)

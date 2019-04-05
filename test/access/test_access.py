import sys
import argparse
import time
import os
from pyspark import SparkContext

parser = argparse.ArgumentParser(description='Process recharges data into a property graph')
parser.add_argument('--endpoint',help='The object storage endpoint')
parser.add_argument('--access-key',help='The API access key')
parser.add_argument('--secret-key',help='The API secret key')
parser.add_argument('--insecure',help='Use http instead of https',action='store_true',default=False)
parser.add_argument('urls',nargs='*')

# hack for spark-submit/k8s
parameters = None
if len(sys.argv)>1 and sys.argv[1].find(',')>0:
   parameters = sys.argv[1].split(',')
args = parser.parse_args(parameters)

sc = SparkContext(appName = "test_access")

if args.endpoint is not None:
   sc._jsc.hadoopConfiguration().set("fs.s3a.endpoint",args.endpoint)

if args.access_key is not None:
   sc._jsc.hadoopConfiguration().set("fs.s3a.access.key",args.access_key)

if args.secret_key is not None:
   sc._jsc.hadoopConfiguration().set("fs.s3a.secret.key",args.secret_key)

for url in args.urls:
   print(url)
   rdd = sc.textFile(url)
   print(rdd.take(10))

import sys
import argparse
from time import sleep
import os
from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.sql.types import StructType

parser = argparse.ArgumentParser(description='Process recharges data into a property graph')
parser.add_argument('--endpoint',help='The object storage endpoint')
parser.add_argument('--access-key',help='The API access key')
parser.add_argument('--secret-key',help='The API secret key')
parser.add_argument('source',nargs='?',default='s3a://amazon-reviews-pds/tsv/amazon_reviews_us_Digital_Video_Download_v1_00.tsv.gz')

# hack for spark-submit/k8s
parameters = None
if len(sys.argv)>1 and sys.argv[1].find(',')>0:
   parameters = sys.argv[1].split(',')
args = parser.parse_args(parameters)

sc = SparkContext(appName = "simple_read")

if args.endpoint is not None:
   sc._jsc.hadoopConfiguration().set("fs.s3a.endpoint",args.endpoint)

if args.access_key is not None:
   sc._jsc.hadoopConfiguration().set("fs.s3a.access.key",args.access_key)

if args.secret_key is not None:
   sc._jsc.hadoopConfiguration().set("fs.s3a.secret.key",args.secret_key)


spark = SparkSession(sc)

reviewsSchema = \
   StructType() \
      .add("marketplace", "string") \
      .add("customer_id", "integer") \
      .add("review_id", "string") \
      .add("product_id", "string") \
      .add("product_title", "string") \
      .add("product_category", "string") \
      .add("star_rating", "integer") \
      .add("helpful_votes", "integer") \
      .add("total_votes", "integer") \
      .add("vine", "boolean") \
      .add("verified_purchase", "boolean") \
      .add("review_headline", "string") \
      .add("review_body", "string") \
      .add("review_date", "date")

df = spark.read \
          .format('csv') \
          .option('sep','\t') \
          .option('header','true') \
          .option('schema',reviewsSchema) \
          .load(args.source)

df.createOrReplaceTempView("reviews")

spark.sql("select * from reviews limit 10").show()

spark.stop()

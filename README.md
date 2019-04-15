# Spark with S3 Support for Kubernetes

Sometimes it is a struggle to get all the parts and version aligned just so and
this is certainly the case with running Spark natively on Kubernetes along with
S3 support. To help ease this struggle, this project includes some documentation
and examples of packaging and using Spark with "S3 protocol" access along
with native support for Kubernetes.

The challenge for S3 support is that the Hadoop libraries must both match your
target distribution version and must also be after Hadoop 2.8.0. This is
due to dependencies on libraries introduced in the version from the Hadoop/AWS
integration. If you need to use a Hadoop version before 2.8.0, you are likely
unable to access S3 resources via urls within Spark computations.

## Building Spark

You must first start with a source distribution. One easy way to obtain
a source distribution is via [spark releases](https://github.com/apache/spark/releases)
on github. Just download a version subsequent to Spark 2.3 (the minimum for Kubenetes
support).

Once you have unpacked a distribution, you can build a distribution locally via:

```bash
./dev/make-distribution.sh --name hadoop-2.9 --pip --tgz -Phadoop-2.9 -Pyarn -Pkubernetes -Phadoop-cloud -Dhadoop.version=2.9.2
```

In the above command:

 * The `--name` parameter controls the suffix used to name the distribution
 * The `-Dhadoop.version=n.n.n` needs to match the target Hadoop version (2.8.0+)

This will build a distribution you can use to build base container images.

## Building Base Container Images

When you have unpacked the build distribution of Spark, you'll have a
dockerfiles for building spark container images. You can build an s3 compatible
spark image for your target languages (e.g., Java/Scala and Python), via the
following:

```bash
export OWNER=alexmilowski
export SPARK_VERSION=2.4.1
export HADOOP_VERSION=2.9.2
export IMAGE_VERSION=1
docker build -t ${OWNER}/s3-spark:${SPARK_VERSION}-${HADOOP_VERSION}-${IMAGE_VERSION} --no-cache -f kubernetes/dockerfiles/spark/Dockerfile .
docker build -t ${OWNER}/s3-pyspark:${SPARK_VERSION}-${HADOOP_VERSION}-${IMAGE_VERSION} --no-cache -f kubernetes/dockerfiles/spark/bindings/python/Dockerfile --build-arg base_img=alexmilowski/s3-spark:${SPARK_VERSION}-${HADOOP_VERSION}-${IMAGE_VERSION} .
```

For K8S you'll need to package your code using one of these base images.

### Testing S3 Access

You can build the access test via:

```bash
export OWNER=alexmilowski
export SPARK_VERSION=2.4.1
export HADOOP_VERSION=2.9.2
export IMAGE_VERSION=1
docker build -t ${OWNER}/s3-spark-test:${SPARK_VERSION}-${HADOOP_VERSION}-${IMAGE_VERSION} --no-cache -f test/access/Dockerfile --build-arg base_img=${OWNER}/s3-pyspark:${SPARK_VERSION}-${HADOOP_VERSION}-${IMAGE_VERSION} .
```

```bash
export ENDPOINT=...
export ACCESS_KEY=...
export SECRET_KEY=...
docker run -it ${OWNER}/s3-spark-test:${SPARK_VERSION}-${HADOOP_VERSION}-${IMAGE_VERSION} /opt/spark/bin/spark-submit --master local /app/test_access.py --endpoint ${ENDPOINT} --access-key ${ACCESS_KEY} --secret-key ${SECRET_KEY} s3a://code/test_access.py
```

### Testing via an Amazon Example

The [Amazon Customer Reviews Dataset](https://registry.opendata.aws/amazon-reviews/) contains over a 130+ million customer review. The various files vary in size but the default is the `amazon_reviews_us_Digital_Video_Download_v1_00.tsv.gz` file which is ~ 0.5GB in size and sufficient for testing access.

Build the testing image:

```bash
export OWNER=alexmilowski
export SPARK_VERSION=2.4.1
export HADOOP_VERSION=2.9.2
export IMAGE_VERSION=1
docker build -t ${OWNER}/s3-spark-amazon-reviews:${SPARK_VERSION}-${HADOOP_VERSION}-${IMAGE_VERSION} --no-cache -f examples/amazon-reviews/Dockerfile --build-arg base_img=${OWNER}/s3-pyspark:${SPARK_VERSION}-${HADOOP_VERSION}-${IMAGE_VERSION} .
```

Make sure you configure you AWS access (only once):

```bash
aws configure
```

Test Access:
```bash
docker run -it ${OWNER}/s3-spark-amazon-reviews:${SPARK_VERSION}-${HADOOP_VERSION}-${IMAGE_VERSION} /opt/spark/bin/spark-submit --master local /app/simple_read.py --access-key `grep aws_access_key_id ~/.aws/credentials | awk '{print $3}'` --secret-key "`grep aws_secret_access_key ~/.aws/credentials | awk '{print $3}'`"
```

## Running Spark via K8S

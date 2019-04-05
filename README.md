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

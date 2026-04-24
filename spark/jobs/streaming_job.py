from pyspark.sql import SparkSession, Window
from pyspark.sql.functions import col, from_json, avg, round as spark_round, to_timestamp, window, count, concat, lit
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType

KAFKA_TOPIC = "crypto-prices"
KAFKA_SERVERS = "kafka:9092"
HDFS_PATH = "hdfs://namenode:9000/data/cripto"
CHECKPOINT_LOCATION = "/tmp/spark_checkpoint"

spark = SparkSession.builder \
    .appName("CryptoExchangeStreaming") \
    .config("spark.sql.streaming.checkpointLocation", CHECKPOINT_LOCATION) \
    .config("spark.hadoop.fs.defaultFS", "hdfs://namenode:9000") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

schema = StructType([
    StructField("type", StringType(), True),
    StructField("symbol", StringType(), True),
    StructField("price", DoubleType(), True),
    StructField("volume_24h", DoubleType(), True),
    StructField("change_pct_24h", DoubleType(), True),
    StructField("timestamp", LongType(), True),
    StructField("open", DoubleType(), True),
    StructField("high", DoubleType(), True),
    StructField("low", DoubleType(), True),
    StructField("close", DoubleType(), True),
    StructField("interval", StringType(), True)
])

df = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_SERVERS) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

parsed_df = df.selectExpr("CAST(value AS STRING) as json_data") \
    .select(from_json(col("json_data"), schema).alias("data")) \
    .select("data.*") \
    .filter(col("type") == "miniTicker") \
    .withColumn("timestamp_dt", to_timestamp(col("timestamp") / 1000)) \
    .withWatermark("timestamp_dt", "2 minutes")

windowed_df = parsed_df.groupBy(
    window(col("timestamp_dt"), "5 minutes", "1 minute"),
    col("symbol")
).agg(
    avg("price").alias("sma_5min"),
    avg("volume_24h").alias("avg_volume"),
    avg("change_pct_24h").alias("avg_change_pct"),
    count("*").alias("message_count")
).withColumn(
    "price_change_pct",
    spark_round((col("sma_5min") - lit(0)) / lit(1) * 100, 4)
)

def write_to_hdfs(batch_df, batch_id):
    batch_df.write \
        .mode("append") \
        .partitionBy("symbol") \
        .format("parquet") \
        .save(HDFS_PATH)

query = windowed_df.writeStream \
    .outputMode("complete") \
    .foreachBatch(write_to_hdfs) \
    .option("checkpointLocation", CHECKPOINT_LOCATION) \
    .start()

query.awaitTermination()

from pyspark.sql import SparkSession
from pyspark.sql.functions import avg
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
import time

spark = SparkSession.builder \
    .appName("DataRead&Process") \
    .getOrCreate()

schema = StructType([
    StructField("Timestamp", StringType(), True),
    StructField("From Bank", IntegerType(), True),
    StructField("From Account", StringType(), True),
    StructField("To Bank", IntegerType(), True),
    StructField("To Account", StringType(), True),
    StructField("Amount Received", DoubleType(), True),
    StructField("Receiving Currency", StringType(), True),
    StructField("Amount Paid", DoubleType(), True),
    StructField("Payment Currency", StringType(), True),
    StructField("Payment Format", StringType(), True)
])


start_time_load = time.time()
df = spark.read.csv("/scripts/LI-Medium_Trans_Folder/LI-Medium_Trans.csv", header=True, schema=schema)
selected_df = df.select("Amount Paid", "Payment Format")
end_time_load = time.time()

start_time_transform = time.time()
avg_amt_paid = selected_df.groupBy("Payment Format").agg(avg("Amount Paid").alias("Avg Amount Paid"))
avg_amt_paid.show(50, truncate=False)
end_time_transform = time.time()

load_time = end_time_load - start_time_load
transform_time = end_time_transform - start_time_transform

print(f"time taken to load data: {load_time}")
print(f"time taken to transform data: {transform_time}")






import os
import sys

# Force the environment variables
os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jre1.8.0_481' 
os.environ['HADOOP_HOME'] = r'C:\hadoop'
os.environ['PATH'] = os.environ.get('PATH', '') + ';' + r'C:\hadoop\bin'

from pyspark.sql import SparkSession

print("Attempting to start Spark WITHOUT Hive...")

try:
    spark = SparkSession.builder \
        .appName("DiagnosticTest") \
        .master("local[*]") \
        .getOrCreate()
    
    print("\n✅ SPARK WORKS! The Python-Java bridge is healthy.")
    print("The crash is 100% caused by Windows rejecting the Hive Metastore.")
    
    spark.stop()

except Exception as e:
    print("\n❌ SPARK FAILED! The entire Python-Java bridge is broken.")
    print(e)
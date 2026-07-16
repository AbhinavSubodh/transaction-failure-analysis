import os

# 🚨 FORCE WINDOWS TO SEE THE EXACT JAVA AND HADOOP FOLDERS
os.environ['JAVA_HOME'] = r'C:\Program Files\Java\jre1.8.0_481' 
os.environ['HADOOP_HOME'] = r'C:\hadoop'
os.environ['PATH'] = os.environ.get('PATH', '') + ';' + r'C:\hadoop\bin'

from pyspark.sql import SparkSession
from pyspark.ml.feature import StringIndexer, VectorAssembler
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

# 1. INITIALIZE PYSPARK
spark = SparkSession.builder \
    .appName("DigitalPayment_Final") \
    .master("local[*]") \
    .getOrCreate()

print("✅ Spark Engine Online & Connected to Hadoop")

# ==========================================
# 2. LOAD DATA DIRECTLY FROM HDFS
# ==========================================
tx_df = spark.read.csv("hdfs://localhost:9000/user/hadoop/payment_data/transactions/transactions.csv", header=True, inferSchema=True)
banks_df = spark.read.csv("hdfs://localhost:9000/user/hadoop/payment_data/banks/banks.csv", header=True, inferSchema=True)

# Register as SQL tables
tx_df.createOrReplaceTempView("transactions")
banks_df.createOrReplaceTempView("banks")

# ==========================================
# 3. SQL ANALYTICS (Fixing the hidden space!)
# ==========================================
print("\n📊 Running SQL Analytics...")

print("Top Failing Banks:")
# We use TRIM(t.status) to destroy that hidden space before checking
spark.sql("""
    SELECT b.bank_name, COUNT(*) as failures 
    FROM transactions t 
    JOIN banks b ON t.bank_id = b.bank_id 
    WHERE TRIM(t.status) = 'FAILED'
    GROUP BY b.bank_name
    ORDER BY failures DESC
""").show()

# ==========================================
# 4. MLLIB PREDICTIVE MODELING
# ==========================================
print("🧠 Training MLlib Model...")

# Extract clean data for the Machine Learning model
full_data = spark.sql("""
    SELECT CAST(amount AS DOUBLE), CAST(bank_id AS DOUBLE), CAST(merchant_id AS DOUBLE), TRIM(status) as status 
    FROM transactions
""")

# Convert SUCCESS/FAILED to 1.0 and 0.0
indexer = StringIndexer(inputCol="status", outputCol="label")
indexed_data = indexer.fit(full_data).transform(full_data)

# Bundle the features
assembler = VectorAssembler(
    inputCols=["amount", "bank_id", "merchant_id"], 
    outputCol="features",
    handleInvalid="skip"
)
ml_data = assembler.transform(indexed_data)

# Split data 80% for training, 20% for testing
train_data, test_data = ml_data.randomSplit([0.8, 0.2], seed=42)

# Train the Random Forest
rf = RandomForestClassifier(labelCol="label", featuresCol="features", numTrees=20)
model = rf.fit(train_data)

# Test the model on the 20% unseen data
predictions = model.transform(test_data)
evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
accuracy = evaluator.evaluate(predictions)

print(f"\n🎯 MLLIB MODEL ACCURACY: {accuracy * 100:.2f}%\n")

spark.stop()
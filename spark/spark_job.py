from pyspark.sql import SparkSession

def main():
    """
    Main Spark job to analyze prediction data from HDFS.
    """
    spark = SparkSession.builder \
        .appName("Casting Defect Analysis") \
        .getOrCreate()

    hdfs_path = "hdfs://namenode:8020/predictions"

    try:
        # Read all JSON files from the HDFS directory
        df = spark.read.json(hdfs_path)

        # Perform analysis
        prediction_counts = df.groupBy("prediction").count()

        print("Prediction Analysis Results:")
        prediction_counts.show()

    except Exception as e:
        print(f"An error occurred: {e}")
        print(f"Please check if the directory '{hdfs_path}' exists and contains data.")

    finally:
        spark.stop()

if __name__ == "__main__":
    main()


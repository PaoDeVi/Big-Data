from pyspark.sql import SparkSession
from pyspark.sql.functions import split, col

KAFKA_BROKER = 'localhost:9092'
KAFKA_TOPIC = 'ferreteria'

def process_batch(spark, df, epoch_id):
    try:
        print(f"Processing batch with epoch ID: {epoch_id}")
        df.show(truncate=False)

        # Transformaciones y consulta sobre los datos
        df = df.selectExpr("CAST(value AS STRING) as message")
        df = df.withColumn("producto", split(df.message, "\|")[0])
        df = df.withColumn("cantidad", split(df.message, "\|")[1].cast("int"))
        df = df.withColumn("categoria", split(df.message, "\|")[2])
        df = df.withColumn("precio", split(df.message, "\|")[3].cast("float"))
        df = df.withColumn("fecha_venta", split(df.message, "\|")[4])
        df = df.withColumn("id_venta", split(df.message, "\|")[5])

        df.write.mode("append").saveAsTable("default.ventas")

    except Exception as e:
        print(f"Error processing batch: {str(e)}")

def main():
    # Crear la sesión global de Spark
    spark = SparkSession.builder.appName("FerreteriaStreamProcessing").config("spark.sql.warehouse.dir", "/user/hive/warehouse").config("hive.metastore.uris", "thrift://localhost:9083").enableHiveSupport().getOrCreate()

    # Configuración de lectura desde Kafka
    df = spark.readStream.format("kafka").option("kafka.bootstrap.servers", KAFKA_BROKER).option("subscribe", KAFKA_TOPIC).load()

    # Deserializar los datos de Kafka
    df = df.selectExpr("CAST(value AS STRING)")

    # Separar las columnas a partir de la cadena deserializada
    df = df.withColumn("producto", split(col("value"), "\|").getItem(0)).withColumn("cantidad", split(col("value"), "\|").getItem(1).cast("int")).withColumn("categoria", split(col("value"), "\|").getItem(2)).withColumn("precio", split(col("value"), "\|").getItem(3).cast("float")).withColumn("fecha_venta", split(col("value"), "\|").getItem(4)).withColumn("id_venta", split(col("value"), "\|").getItem(5))

    # Procesar cada batch de datos usando foreachBatch
    query = df.writeStream.foreachBatch(lambda df, epoch_id: process_batch(spark, df, epoch_id)).outputMode("append").option("checkpointLocation", "/tmp/checkpoints/ferreteria").start()

    # Esperar a que la aplicación termine
    query.awaitTermination()

if __name__ == "__main__":
    main()

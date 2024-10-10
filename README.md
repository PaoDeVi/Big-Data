<h2>PIPELINE</h2>

El proyecto consiste en la aplicación de Apache Kafka, Spark y HIVE para la implementación de un sistema de inventario de diferentes productos, los cuáles se pueden filtrar según diferentes criterios, cómo categorías, inventario actual, ventas por fecha, etc. Empleando Apache Kafka se crearán los tópicos de nuestros productos, a los cuáles los productores enviarán los detalles de cada producto y enviarán los detalles al consumidor suscrito, el cuál en base a sus necesidades, visualizará la información que necesite filtrada previamente por HIVE.

<h5>Comandos</h5>

```bash
    $ cd kafka/
    $bin/zookeeper-server-start.sh config/zookeeper.properties
```
## Broker:
```bash
$ cd kafka/
~/kafka$ bin/kafka-server-start.sh config/server.properties
```

## Hadoop:
```bash
~$ hdfs namenode -format
~$ start-dfs.sh
~$ hadoop fs -ls /
~$ hadoop fs -mkdir /test
~$ hadoop fs -mkdir -p /user/hive/warehouse
~$ hadoop fs -mkdir -p /tmp
~$ hadoop fs -chmod g+w /user/hive/warehouse
~$ hadoop fs -chmod g+w /tmp
```

## Kafka
```bash
~/kafka$ bin/kafka-topics.sh --list --bootstrap-server localhost:9092
~/kafka$ bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ferreteria
~/kafka$ bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic gaseosas
```
Note: Cuando recien instalas todo por primera vez:
```bash
~/hive$ mv lib/log4j-slf4j-impl-2.6.2.jar lib/log4j-slf4j-impl-2.6.2.jar.bak
```

## Para limpiar
```bash
rm /home/seed/metastore_db/db.lck
rm /home/seed/metastore_db/dbex.lck
rm -rf /home/seed/metastore_db

#Salir del localhost
ssh localhost
exit
```

## Database
```bash
~$ schematool -initSchema -dbType derby
~$ hive --service metastore &
```
En otra terminal:
```bash
~$ hive
hive> show databases;
```
Dará un error no te preocupes, realizá Ctrl+C en la terminal donde ejecutaste (hive --service metastore &). Ahora realiza la limpieza:
```bash
rm /home/seed/metastore_db/db.lck
rm /home/seed/metastore_db/dbex.lck
rm -rf /home/seed/metastore_db
```

Volverás a iniciarlizar:
```bash
~$ schematool -initSchema -dbType derby
~$ hive --service metastore &
```
Esto mostrará un mensaje con el símbolo [2]

## Hive
Abrimos la consola de hive con el siguiente comando:
```bash
hive> show databases;
hive> use default
```
Usaremos la base de datos llamada default.

Crearemos las tablas
```bash
hive> CREATE TABLE IF NOT EXISTS ventas (
     producto STRING,
      cantidad INT,
      categoria STRING,
      precio FLOAT,
       fecha_venta STRING,
       id_venta STRING
    )
    STORED AS PARQUET;

hive> CREATE TABLE IF NOT EXISTS gaseosas (
              producto STRING,
               cantidad INT,
               categoria STRING,
               precio FLOAT,
               fecha_venta STRING,
               id_venta STRING
          )
           STORED AS PARQUET;
```
Mostrará un mensaje de: OK Time taken: 0.44 seconds (esto puede variar según la máquina.

## Spark
Primero se ejecuta el stream y su productor correspondiente:
```bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0 herramientas_stream.py
python3 productor.py elementosFerreteria.txt
```

Realizamos lo mismo para el otro stream y su productor correspondiente:
```bash
spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.0 gaseosas_streaming.py
python3 productor2.py elementosGaseosas.txt
```

## Hive
Regresamos a la terminal de Hive y creamos la siguiente tabla:
```bash
hive> CREATE TABLE IF NOT EXISTS tiendas (
               item STRING,
               quantity INT,
               categoria STRING,
                precio FLOAT,
               fecha_venta STRING,
               id STRING
           )
          STORED AS PARQUET;
```
E insertamos los datos:
```bash
hive> INSERT INTO TABLE tiendas
    SELECT
        producto AS item,
        cantidad AS quantity,
        categoria,
        precio,
        fecha_venta,
        id_venta AS id
    FROM gaseosas;

hive> INSERT INTO TABLE tiendas
SELECT
    producto AS item,
    cantidad AS quantity,
    categoria,
    precio,
    fecha_venta,
    id_venta AS id
FROM ventas;
```


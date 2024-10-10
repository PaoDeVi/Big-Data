<h2>PIPELINE</h2>

Este proyecto implementa un sistema de inventario utilizando Apache Kafka, Spark y HIVE, permitiendo filtrar productos por diferentes criterios, como categorías, inventario actual, y ventas por fecha. A través de Kafka, se crean tópicos para los productos, a los cuales los productores enviarán detalles que serán procesados por los consumidores. La información se filtrará y se gestionará con HIVE para que los usuarios puedan visualizarla.


## Broker:
Este comando inicia el broker de Kafka, que maneja la comunicación entre los productores y los consumidores.
```bash
$ cd kafka/
~/kafka$ bin/kafka-server-start.sh config/server.properties
```

## Hadoop:
Hadoop Distributed File System (HDFS) es el sistema de archivos distribuido donde almacenaremos los datos. Estos comandos formatean el namenode, inician el sistema de archivos, y crean directorios necesarios.
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
Estos comandos configuran y crean los tópicos en Kafka, que serán usados para enviar y recibir información de productos.
```bash
~/kafka$ bin/kafka-topics.sh --list --bootstrap-server localhost:9092
~/kafka$ bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic ferreteria
~/kafka$ bin/kafka-topics.sh --create --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1 --topic gaseosas
```
Note: Si acabas de instalar Hive y Kafka por primera vez, deberás mover ciertos archivos para evitar errores relacionados con logging:
```bash
~/hive$ mv lib/log4j-slf4j-impl-2.6.2.jar lib/log4j-slf4j-impl-2.6.2.jar.bak
```

## Para limpiar
Si encuentras errores con la base de datos de metadatos de Hive, utiliza estos comandos para eliminar los archivos de bloqueo y limpiar el estado del sistema:
```bash
rm /home/seed/metastore_db/db.lck
rm /home/seed/metastore_db/dbex.lck
rm -rf /home/seed/metastore_db
```
## Salir localhost
Si estás conectado a un localhost, usa el siguiente comando para salir.
```bash
ssh localhost
exit
```

## Database
Este comando inicializa el esquema de la base de datos que Hive necesita para funcionar correctamente:
```bash
~$ schematool -initSchema -dbType derby
~$ hive --service metastore &
```
Abre otra terminal y verifica que la base de datos esté disponible:
```bash
~$ hive
hive> show databases;
```
Si ves algún error, realiza la limpieza nuevamente como se mencionó anteriormente y reinicia el metastore.
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
Esto mostrará un mensaje con el símbolo [2] indicando la cantidad de productos creados por kafka.

## Hive
Hive te permite almacenar los datos en formato estructurado. Aquí creamos las tablas para almacenar las ventas de ferretería y gaseosas.
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
Mostrará un mensaje de: OK Time taken: 0.44 seconds (esto puede variar según la máquina).

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
E insertamos los datos en las tablas creadas:
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
## Ejecución de la APP
La app fue realizada con Flask, al ejecutar el comando iniciará el servicio e indicará la dirección IP. Finalmente, copia y pega ese IP en tu browser para visualiar la aplicación.
```bash
python3 app.py
```

<h2>PIPELINE</h2>

El proyecto consiste en la aplicación de Apache Kafka, Spark y HIVE para la implementación de un sistema de inventario de diferentes productos, los cuáles se pueden filtrar según diferentes criterios, cómo categorías, inventario actual, ventas por fecha, etc. Empleando Apache Kafka se crearán los tópicos de nuestros productos, a los cuáles los productores enviarán los detalles de cada producto y enviarán los detalles al consumidor suscrito, el cuál en base a sus necesidades, visualizará la información que necesite filtrada previamente por HIVE.

<h5>COmandos</h5>

''' bash
$ cd kafka/
$ bin/zookeeper-server-start.sh config/zookeeper.properties
'''

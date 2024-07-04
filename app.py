from flask import Flask, render_template
from pyspark.sql import SparkSession

app = Flask(__name__)

# Configuración de Spark para usar Hive
spark = SparkSession.builder \
    .appName("Consulta de Hive desde Spark") \
    .config("spark.sql.warehouse.dir", "/user/hive/warehouse") \
    .config("hive.metastore.uris", "thrift://localhost:9083") \
    .enableHiveSupport() \
    .getOrCreate()

# Ruta raíz de la aplicación
@app.route('/')
def index():
    return render_template('index.html')

# Consulta 1: Mostrar todas las ventas
@app.route('/ventas')
def consultar_ventas():
    df = spark.sql("SELECT * FROM default.ventas")
    ventas_data = df.collect()  # Recolectar los datos en una lista de filas
    return render_template('tabla.html', titulo="Ventas", datos=ventas_data)

# Consulta 2: Mostrar todas las gaseosas
@app.route('/gaseosas')
def consultar_gaseosas():
    df = spark.sql("SELECT * FROM default.gaseosas")
    gaseosas_data = df.collect()  # Recolectar los datos en una lista de filas
    return render_template('tabla.html', titulo="Gaseosas", datos=gaseosas_data)

# Consulta 3: Mostrar todas las tiendas
@app.route('/tiendas')
def consultar_tiendas():
    query = """
        SELECT producto, cantidad, precio
        FROM default.ventas
        UNION ALL
        SELECT producto, cantidad, precio
        FROM default.gaseosas
    """
    df = spark.sql(query)
    tiendas_data = df.collect()  # Recolectar los datos en una lista de filas
    return render_template('tabla.html', titulo="Tiendas", datos=tiendas_data)

# Consulta 4: Ventas totales por categoría
@app.route('/ventas_por_categoria')
def ventas_por_categoria():
    query = """
    SELECT categoria, SUM(cantidad * precio) AS total_ventas
    FROM (
        SELECT categoria, cantidad, precio
        FROM default.ventas
        UNION ALL
        SELECT categoria, cantidad, precio
        FROM default.gaseosas
    ) AS todas_ventas
    GROUP BY categoria
    ORDER BY categoria
    """
    df = spark.sql(query)
    datos = df.collect()
    return render_template('tabla.html', titulo="Ventas por Categoría", datos=datos)

# Consulta 5: Ventas por mes
@app.route('/ventas_por_mes')
def ventas_por_mes():
    query = """
    SELECT mes, sum(total_ventas) as total_ventas
    FROM (
        SELECT fecha_venta AS mes, cantidad AS total_ventas
        FROM default.ventas
        UNION ALL
        SELECT fecha_venta AS mes, cantidad AS total_ventas
        FROM default.gaseosas
    ) ventas_por_mes
    GROUP BY mes
    ORDER BY mes
    """
    df = spark.sql(query)
    datos = df.collect()
    return render_template('tabla.html', titulo="Ventas por Mes", datos=datos)

# Consulta 6: Top 5 productos más vendidos
@app.route('/top_productos')
def top_productos():
    query = """
    SELECT producto, SUM(cantidad) AS total_vendido
    FROM (
        SELECT producto, cantidad
        FROM default.ventas
        UNION ALL
        SELECT producto, cantidad
        FROM default.gaseosas
    ) AS todos_productos
    GROUP BY producto
    ORDER BY total_vendido DESC
    LIMIT 5
    """
    df = spark.sql(query)
    datos = df.collect()
    return render_template('tabla.html', titulo="Top 5 Productos Más Vendidos", datos=datos)
    
# Consulta 7: Presupuesto de Ventas por Mes
@app.route('/presupuesto_de_ventas_por_mes')
def presupuesto_de_ventas_por_mes():
    query = """
    SELECT fecha_venta, SUM(cantidad * precio) AS presupuesto_ventas
	FROM default.ventas
	GROUP BY fecha_venta
	ORDER BY fecha_venta;
    """
    df = spark.sql(query)
    datos = df.collect()
    return render_template('tabla.html', titulo="Presupuesto de Ventas por Mes", datos=datos)

if __name__ == '__main__':
    app.run(debug=True)

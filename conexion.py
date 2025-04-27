import pymysql

conex = pymysql.connect(host = 'localhost', user = 'root', passwd = '', db = 'tiendapython_lp')
cur = conex.cursor()

def altaProducto(nombre,costo,cantidad):
    try:
        query = "INSERT INTO producto(nombreProducto, costoProducto, cantidadProducto) VALUES (%s, %s, %s)"
        valores = (nombre, costo, cantidad)

        cur.execute(query, valores)
        conex.commit()
    except pymysql.MySQLError as e:
        print(f"Error al insertar producto: {e}")

def eliminaProducto(id,nombre):
    try:
        query = "DELETE FROM producto WHERE idProducto = %s or nombreProducto = %s"
        valores = (id,nombre)

        cur.execute(query, valores)
        conex.commit()
    except pymysql.MySQLError as e:
        print(f"Error al eliminar producto: {e}")


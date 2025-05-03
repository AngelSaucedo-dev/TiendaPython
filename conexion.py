import pymysql

conex = pymysql.connect(host = 'localhost', user = 'root', passwd = '', db = 'tiendapython_lp')
cur = conex.cursor()

def altaProductoBD(nombre,costo,cantidad):
    try:
        query = "INSERT INTO producto(nombreProducto, costoProducto, cantidadProducto) VALUES (%s, %s, %s)"
        valores = (nombre, costo, cantidad)

        cur.execute(query, valores)
        conex.commit()
    except pymysql.MySQLError as e:
        print(f"Error al insertar producto: {e}")

def eliminaProductoBD(id):
    try:
        query = "DELETE FROM producto WHERE idProducto = %s"
        valores = (id)

        cur.execute(query, valores)
        conex.commit()
    except pymysql.MySQLError as e:
        print(f"Error al eliminar producto: {e}")

def tommaIdBD(nombre):
    try:
        query = "SELECT idProducto FROM producto WHERE nombreProducto = %s"
        cur.execute(query,nombre)

        resultado = cur.fetchone()

        if resultado:
            # Retornamos el idProducto si se encuentra
            return resultado[0]
        else:
            print("No existe el producto con ese nombre.")
            return None

    except pymysql.MySQLError as e:
        print(f"Error al tomar el Id: {e}")

def altaCompraCarritoBD(id,compra,fecha):
    try:
        queryCompra = "INSERT INTO compras(id_Producto, cantidadCompra, fechaCompra) VALUES (%s , %s , %s)"
        valoresCompra = (id,compra,fecha)
        cur.execute(queryCompra,valoresCompra)
        conex.commit()
        
        queryCantidad = "UPDATE producto SET cantidadProducto=cantidadProducto - %s WHERE idProducto = %s"
        valoresCantidad = (compra,id)
        cur.execute(queryCantidad,valoresCantidad)
        conex.commit()
    except pymysql.MySQLError as e:
        print(f"Error al comprar producto en BD:  {e}")

def modificaProductoBD(id,nombre,costo,cantidad):
    try:
        queryModifica = "UPDATE producto SET nombreProducto= %s ,costoProducto = %s,cantidadProducto = %s WHERE idProducto = %s"
        valoresModifica = (nombre,costo,cantidad,id)
        cur.execute(queryModifica,valoresModifica)
        conex.commit()
        
    except pymysql.MySQLError as e:
        print(f"Error al modificar producto en BD: {e}")
import flet as ft
from conexion import *

def admin_interface(page: ft.Page):
    page.title = "Punto de Venta - Cajero"
    page.window_maximized = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.clean()
    
    try:
        cur.execute("SELECT idProducto, nombreProducto, costoProducto, cantidadProducto FROM producto")
        resultado = cur.fetchall()

        productos = []

        for row in resultado:
            producto = {
                "id": str(row[0]).zfill(3),
                "nombre": row[1],
                "precio": float(row[2]),
                "cantidad": int(row[3])
            }
            productos.append(producto)

        print(productos) 

    except pymysql.MySQLError as e:
        print(f"Error al consultar producto: {e}")

    carrito = {}

    # Barra de navegación (siempre habilitada)
    navigation = ft.NavigationRail(
        destinations=[
            ft.NavigationRailDestination(icon=ft.Icons.SHOPPING_CART, label="Ventas"),
            ft.NavigationRailDestination(icon=ft.Icons.INVENTORY, label="Inventario"),
            ft.NavigationRailDestination(icon=ft.Icons.ANALYTICS, label="Reportes"),
        ],
        selected_index=0,
    )  
    # Payment Dialog
    pago_dialog = ft.AlertDialog(
        title=ft.Text("¡Venta exitosa!", text_align=ft.TextAlign.CENTER),
        content=ft.Text("Gracias por su compra", text_align=ft.TextAlign.CENTER),
    )
    
    # Payment Section
    forma_pago = ft.Dropdown(
        label="Forma de pago",
        options=[
            ft.dropdown.Option("Efectivo"),
            ft.dropdown.Option("Tarjeta")
        ],
        width=300,
        on_change=lambda e: actualizar_forma_pago()
    )
    
    cantidad_recibida = ft.TextField(
        label="Cantidad recibida", 
        keyboard_type=ft.KeyboardType.NUMBER, 
        width=300,
        on_change=lambda e: actualizar_cambio()
    )
    
    cambio_text = ft.Text("Cambio: $0.00", size=18, weight=ft.FontWeight.BOLD)
    total_text = ft.Text("Total: $0.00", size=18, weight=ft.FontWeight.BOLD)
    total_floating = ft.Container(
        content=ft.Text("Total: $0.00", size=28, weight=ft.FontWeight.BOLD),
        padding=15,
        right=20,
        bottom=20,
    )
    
    pago_section = ft.Container(
        content=ft.Column([
            ft.Container(width=1, height=1),  # Espacio para centrar el contenido
            forma_pago,
            cantidad_recibida,
            cambio_text,
            total_text,
            ft.Row([
                ft.ElevatedButton(
                    "Cancelar venta", 
                    icon=ft.Icons.CANCEL, 
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: cancelar_venta(),
                    icon_color=ft.Colors.WHITE
                ),
                ft.ElevatedButton(
                    "Finalizar venta", 
                    icon=ft.Icons.CHECK, 
                    bgcolor=ft.Colors.GREEN, 
                    color=ft.Colors.WHITE,
                    on_click=lambda e: finalizar_venta(),
                    icon_color=ft.Colors.WHITE
                )
            ], alignment=ft.MainAxisAlignment.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        visible=False,
        padding=20,
        border=ft.border.all(1, ft.Colors.OUTLINE),
        border_radius=10,
    )
    
    search_field = ft.TextField(label="Buscar producto", prefix_icon=ft.Icons.SEARCH, max_length=20)
    product_list = ft.ListView(expand=True, spacing=10)
    carrito_list = ft.ListView(expand=True, spacing=10)
    
    def actualizar_forma_pago():
        if forma_pago.value == "Tarjeta":
            cantidad_recibida.visible = False
            cambio_text.value = "Cambio: N/A"
        else:
            cantidad_recibida.visible = True
            cambio_text.value = "Cambio: $0.00"
        page.update()
    
    def actualizar_cambio():
        if forma_pago.value == "Efectivo" and cantidad_recibida.value:
            try:
                recibido = float(cantidad_recibida.value)
                total = sum(info["precio"] * info["cantidad"] for info in carrito.values())
                cambio = recibido - total
                cambio_text.value = f"Cambio: ${cambio:.2f}" if cambio >= 0 else "Cantidad insuficiente"
            except ValueError:
                cambio_text.value = "Cantidad inválida"
        page.update()
    
    def actualizar_lista():
        product_list.controls.clear()
        busqueda = search_field.value.strip().lower()

        if not busqueda:
            page.update()
            return  # No mostrar nada si está vacío

        for p in productos:
            if busqueda == p["id"].lower() or busqueda in p["nombre"].lower():
                product_list.controls.append(ft.ListTile(
                    title=ft.Text(f"{p['id']} - {p['nombre']} - ${p['precio']:.2f}"),
                    subtitle=ft.Text(f"Disponibles: {p['cantidad']}"),
                    trailing=ft.IconButton(ft.Icons.ADD, on_click=lambda e, p=p: agregar_al_carrito(p))
                ))
                break  # Solo mostrar el primero que coincide

        page.update()

    
    def agregar_al_carrito(producto):
        if producto["nombre"] in carrito:
            carrito[producto["nombre"]]["cantidad"] += 1
        else:
            carrito[producto["nombre"]] = {"precio": producto["precio"], "cantidad": 1}
        actualizar_carrito()
    
    def quitar_del_carrito(producto):
        if producto in carrito:
            if carrito[producto]["cantidad"] > 1:
                carrito[producto]["cantidad"] -= 1
            else:
                del carrito[producto]
        actualizar_carrito()
    
    def actualizar_carrito():
        carrito_list.controls.clear()
        for nombre, info in carrito.items():
            carrito_list.controls.append(ft.ListTile(
                title=ft.Row([
                    ft.Text(f"{nombre} - ${info['precio']:.2f}"),
                    ft.Container(expand=True),
                    ft.Text(f"{info['cantidad']}")
                ]),
                trailing=ft.IconButton(ft.Icons.REMOVE, on_click=lambda e, n=nombre: quitar_del_carrito(n))
            ))
        
        vaciar_carrito_btn.visible = len(carrito) > 0
        proceder_al_pago_btn.visible = len(carrito) > 0
        
        actualizar_total()
    
    def actualizar_total():
        total = sum(info["precio"] * info["cantidad"] for info in carrito.values())
        total_text.value = f"Total: ${total:.2f}"
        if total > 0 and navigation.selected_index == 0:  # Solo mostrar en vista de ventas
            total_floating.content.value = f"Total: ${total:.2f}"
            total_floating.visible = True
        else:
            total_floating.visible = False
        actualizar_cambio()
        page.update()
    
    def vaciar_carrito():
        carrito.clear()
        actualizar_carrito()
        page.update()
    
    def proceder_al_pago():
        if carrito:
            pago_section.visible = True
            vaciar_carrito_btn.visible = False
            proceder_al_pago_btn.visible = False
            total = sum(info["precio"] * info["cantidad"] for info in carrito.values())
            total_text.value = f"Total: ${total:.2f}"
            page.update()
    
    def cancelar_venta():
        pago_section.visible = False
        vaciar_carrito_btn.visible = len(carrito) > 0
        proceder_al_pago_btn.visible = len(carrito) > 0
        cantidad_recibida.value = ""
        forma_pago.value = None
        cambio_text.value = "Cambio: $0.00"
        page.update()
    
    def finalizar_venta():
        page.dialog = pago_dialog
        pago_dialog.open = True
        
        carrito.clear()
        pago_section.visible = False
        actualizar_carrito()
        cantidad_recibida.value = ""
        forma_pago.value = None
        cambio_text.value = "Cambio: $0.00"
        
        page.update()
    
    def ventas_view():
        global vaciar_carrito_btn, proceder_al_pago_btn
        
        vaciar_carrito_btn = ft.ElevatedButton(
            "Vaciar carrito",
            icon=ft.Icons.DELETE, 
            bgcolor=ft.Colors.RED, 
            color=ft.Colors.WHITE,
            on_click=lambda e: vaciar_carrito(),
            visible=False,
            icon_color=ft.Colors.WHITE
        )
        
        proceder_al_pago_btn = ft.ElevatedButton(
            "Proceder al pago", 
            icon=ft.Icons.PAYMENT, 
            bgcolor=ft.Colors.GREEN, 
            color=ft.Colors.WHITE,
            on_click=lambda e: proceder_al_pago(),
            visible=False,
            icon_color=ft.Colors.WHITE
        )
        
        return ft.Column([
            ft.Text("Ventas", size=24, weight=ft.FontWeight.BOLD),
            search_field,
            ft.ElevatedButton("Buscar", on_click=lambda e: actualizar_lista()),
            product_list,
            ft.Text("Carrito de compras", size=20, weight=ft.FontWeight.BOLD),
            carrito_list,
            ft.Row([
                vaciar_carrito_btn,
                proceder_al_pago_btn
            ], alignment=ft.MainAxisAlignment.CENTER),
            pago_section
        ])

    def inventario_view():
        # Botones principales
        importar_btn = ft.ElevatedButton("Importar Inventario", icon=ft.icons.DOWNLOAD)
        exportar_btn = ft.ElevatedButton("Exportar Inventario", icon=ft.icons.UPLOAD)
        agregar_btn = ft.ElevatedButton("Agregar Producto", icon=ft.icons.ADD)
        eliminar_btn = ft.ElevatedButton("Eliminar Producto", icon=ft.icons.DELETE)

        # Tabla de inventario
        table_columns = [
            ft.DataColumn(ft.Text("ID", width=100)),
            ft.DataColumn(ft.Text("Nombre", width=200)),
            ft.DataColumn(ft.Text("Precio", width=150)),
            ft.DataColumn(ft.Text("En existencia", width=150)),
        ]

        inventario_table = ft.DataTable(
            columns=table_columns,
            rows=[],
            column_spacing=20,
            horizontal_margin=10,
            divider_thickness=0.5,
            heading_row_color=ft.colors.GREY_200,
            heading_row_height=40,
            data_row_min_height=40,
        )

        def actualizar_tabla():
            inventario_table.rows.clear()
            try:
                cur.execute("SELECT idProducto, nombreProducto, costoProducto, cantidadProducto FROM producto")
                resultado = cur.fetchall()

                productos = []

                for row in resultado:
                    producto = {
                        "id": str(row[0]).zfill(3),
                        "nombre": row[1],
                        "precio": float(row[2]),
                        "cantidad": int(row[3])
                    }
                    productos.append(producto)

                print(productos) 

            except pymysql.MySQLError as e:
                print(f"Error al consultar producto: {e}")
            for p in productos:
                inventario_table.rows.append(
                    ft.DataRow(cells=[
                        ft.DataCell(ft.Text(p["id"])),
                        ft.DataCell(ft.Text(p["nombre"])),
                        ft.DataCell(ft.Text(f"${p['precio']:.2f}")),
                        ft.DataCell(ft.Text(str(p["cantidad"]))),
                    ])
                )
            page.update()

        # Controles para agregar producto
        #id_input = ft.TextField(label="ID del producto", width=200)
        nombre_input = ft.TextField(label="Nombre del producto", width=200, max_length=20)
        precio_input = ft.TextField(label="Precio", width=150, keyboard_type=ft.KeyboardType.NUMBER, max_length=6)
        existencia_input = ft.TextField(label="En existencia", width=150, keyboard_type=ft.KeyboardType.NUMBER, max_length=6)

        confirm_btn = ft.ElevatedButton("Confirmar", icon=ft.icons.CHECK_CIRCLE)

        formulario_container = ft.Column(
            controls=[
                ft.Row([
                    #id_input,
                    nombre_input,
                    precio_input,
                    existencia_input,
                    confirm_btn,
                ], spacing=10)
            ],
            visible=False
        )

        # Mostrar formulario al presionar agregar
        def mostrar_formulario(e):
            formulario_container.visible = not formulario_container.visible
            page.update()

        agregar_btn.on_click = mostrar_formulario

        # Confirmar producto
        def confirmar_agregado(e):
            try:
                valida_alta_productos(nombre_input.value, precio_input.value, existencia_input.value)
            except Exception as err:
                print("Error al agregar producto:", err)

        confirm_btn.on_click = confirmar_agregado

        actualizar_tabla()
        
        # Controles para eliminar producto
        eliminar_input = ft.TextField(label="ID o Nombre del producto a eliminar", width=300, max_length=20)
        eliminar_confirm_btn = ft.ElevatedButton("Eliminar", icon=ft.icons.DELETE_FOREVER)

        formulario_eliminar_container = ft.Column(
            controls=[
                ft.Row([
                    eliminar_input,
                    eliminar_confirm_btn,
                ], spacing=10)
            ],
            visible=False
        )

        #Validacion de productos
        def valida_alta_productos(nombre, precio, cantidad):
            existe = False
            valores = {"Nombre":nombre,"Precio":precio,"Cantidad":cantidad}
            vacio = []

            for valor in valores:
                print(valores[valor])
                if valores[valor] == "":
                    vacio.append(valor)
                    print(f"El campo {valor} esta vacio")
            print(vacio)
            if vacio:
                campos = ", ".join(vacio)
                print(campos)
                modal_productos_vacios(campos)
                return
            
            vacio = []  # Reiniciamos la lista vacíos

            if not validaFloat(precio):
                vacio.append("Precio")
            if not validarEnteros(cantidad):
                vacio.append("Cantidad")

            if vacio:
                campos = ", ".join(vacio)
                print(campos)
                modal_tipo_dato(campos)
                return

            for p in productos:
                print(f"Comparando {p['nombre'].lower()} con {nombre.lower()}")
                if p["nombre"].lower() == nombre.lower():
                    existe = True
                    break

            if existe:
                page.open(dlg_modal_validaNombre)
                return

            if not existe: 
                productos.append({
                    #"id": id_input.value,
                    "nombre": nombre_input.value,
                    "precio": float(precio_input.value),
                    "cantidad": int(existencia_input.value),
                })
                altaProducto(nombre,precio,cantidad)

            modal_nuevo_producto(nombre)

            # Limpiar campos
            #id_input.value = ""
            nombre_input.value = ""
            precio_input.value = ""
            existencia_input.value = ""
            
            formulario_container.visible = False
            actualizar_tabla()
        
        # Valida enteros
        def validarEnteros(enteros):
            try:
                numero = int(enteros)
                if numero > 0 and numero < 9999:
                    return True
                else:
                    return False
            except:
                return False

        # Valida flotantes
        def validaFloat(flotante):
            try:
                numero = float(flotante)
                if numero > 0 and numero < 9999:
                    return True
                else:
                    return False
            except:
                return False
            
        # Mostrar formulario al presionar eliminar
        def mostrar_formulario_eliminar(e):
            formulario_eliminar_container.visible = not formulario_eliminar_container.visible
            page.update()

        eliminar_btn.on_click = mostrar_formulario_eliminar

        # Eliminar producto por ID o nombre
        def confirmar_eliminacion(e):
            print("Pulsar boton eliminacion")
            criterio = eliminar_input.value.strip().lower()
            if not criterio:
                page.open(dlg_modal_CamposVaciosElimina)
                return

            original_len = len(productos)
            productos[:] = [
                p for p in productos
                if p["id"].lower() != criterio and p["nombre"].lower() != criterio
            ]

            if len(productos) < original_len:
                eliminar_input.value = ""
                formulario_eliminar_container.visible = False
                actualizar_tabla()
            else:
                page.open(dlg_modal_productoNoEncontrado)

            page.update()

        eliminar_confirm_btn.on_click = confirmar_eliminacion
        importar_btn = ft.ElevatedButton("Importar", icon=ft.icons.UPLOAD)

        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Gestión de Inventario", size=24, weight=ft.FontWeight.BOLD, expand=True),
                        agregar_btn,
                        eliminar_btn,
                        importar_btn,
                        exportar_btn
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
                formulario_container,
                formulario_eliminar_container,
                ft.Container(
                    content=ft.ListView(
                        controls=[inventario_table],
                        expand=True,
                        spacing=10,
                    ),
                    border=ft.border.all(1, ft.colors.GREY_300),
                    border_radius=10,
                    expand=True,
                    padding=10,
                )
            ],
            expand=True,
            spacing=20
        )


    def reportes_view():
        rango_selector = ft.Dropdown(
            label="Selecciona el rango de tiempo",
            options=[
                ft.dropdown.Option("Día"),
                ft.dropdown.Option("Semana"),
                ft.dropdown.Option("Mes"),
            ],
            value="Día",  # Valor por defecto
            width=300
        )

        formato_selector = ft.Dropdown(
            label="Selecciona el formato",
            options=[
                ft.dropdown.Option("PDF"),
                ft.dropdown.Option("Excel"),
            ],
            value="PDF",  # Valor por defecto
            width=300
        )

        resultado_texto = ft.Text("", size=16, color=ft.Colors.BLUE)

        def exportar_reporte(e):
            rango = rango_selector.value
            formato = formato_selector.value
            resultado_texto.value = f"Exportando reporte de {rango} en formato {formato}..."
            page.update()
            # Aquí iría la lógica real de exportación

        exportar_btn = ft.ElevatedButton(
            "Exportar Reporte",
            icon=ft.Icons.DOWNLOAD,
            on_click=exportar_reporte
        )

        return ft.Column([
            ft.Text("Reportes de Ventas", size=24, weight=ft.FontWeight.BOLD),
            rango_selector,
            formato_selector,
            exportar_btn,
            resultado_texto
        ], spacing=20)

    content = ft.Container(expand=True)

    def change_view(e):
        index = navigation.selected_index if e is None else e.control.selected_index
        if index == 0:
            content.content = ventas_view()
        elif index == 1:
            content.content = inventario_view()
        elif index == 2:
            content.content = reportes_view()
        
        # Ocultar total flotante cuando no está en ventas
        if index != 0:
            total_floating.visible = False
        page.update()

    navigation.on_change = change_view
    layout = ft.Row([navigation, ft.VerticalDivider(width=1), content], expand=True)
    
    # Agregar el contenedor flotante como overlay
    page.overlay.append(total_floating)

    # Definimos el modal en caso de repetir el nombre de un producto
    dlg_modal_validaNombre = ft.AlertDialog(
        modal=True,
        title=ft.Text(value="No se puede crear el producto",color="red"),
        content=ft.Text("Ya existe un producto con este nombre."),
        actions=[
            ft.TextButton("Aceptar", on_click=lambda e: page.close(dlg_modal_validaNombre)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    # Modal nuevo producto exitoso
    def modal_nuevo_producto(nombre):
        dlg_modal_nuevoProducto = ft.AlertDialog(
            modal=True,
            title=ft.Text(value="Producto creado correctamente",color="green"),
            content=ft.Text(f"Se creo correctamente el producto: {nombre}"),
            actions=[
                ft.TextButton("Aceptar", on_click=lambda e: page.close(dlg_modal_nuevoProducto)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(dlg_modal_nuevoProducto)

    #Definimos el modal para validar datos vacios
    def modal_productos_vacios(campos):
        dlg_modal_CamposVacios = ft.AlertDialog(
            modal=True,
            title=ft.Text(value="No se puede crear el producto",color="red"),
            content=ft.Text(f"Los siguientes campos estan vacios: {campos}"),
            actions=[
                ft.TextButton("Aceptar", on_click=lambda e: page.close(dlg_modal_CamposVacios)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(dlg_modal_CamposVacios)

    # Definimos el modal para validar el tipo de datos
    def modal_tipo_dato(campos):
        dlg_modal_TipoDato = ft.AlertDialog(
            modal=True,
            title=ft.Text(value="No se puede crear el producto",color="red"),
            content=ft.Text(f"Los siguientes campos tienen datos incorrectos: {campos}\nPosible error: Se agrego una cantidad o precio de 0 o se ingreso un tipo de dato incorrecto (solo entero o flotante)"),
            actions=[
                ft.TextButton("Aceptar", on_click=lambda e: page.close(dlg_modal_TipoDato)),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        page.open(dlg_modal_TipoDato)

    # Definimos el modal en caso de no encontrar el producto a eliminar
    dlg_modal_productoNoEncontrado = ft.AlertDialog(
        modal=True,
        title=ft.Text(value="No existe este producto",color="red"),
        content=ft.Text("Haz ingresado un id o producto que no existe"),
        actions=[
            ft.TextButton("Aceptar", on_click=lambda e: page.close(dlg_modal_productoNoEncontrado)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    #Definimos el modal para validar datos vacios al eliminar
    dlg_modal_CamposVaciosElimina = ft.AlertDialog(
        modal=True,
        title=ft.Text(value="No se ha eliminado el producto",color="red"),
        content=ft.Text("Haz dejado el campo del Id o nombre del producto vacio"),
        actions=[
            ft.TextButton("Aceptar", on_click=lambda e: page.close(dlg_modal_CamposVaciosElimina)),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    page.add(layout)
    change_view(None)  # Inicializar con la vista de ventas
    actualizar_lista()
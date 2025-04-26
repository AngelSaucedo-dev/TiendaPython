import flet as ft

def main_interface(page: ft.Page):
    page.title = "Punto de Venta - Cajero"
    page.window_maximized = True
    page.theme_mode = ft.ThemeMode.LIGHT
    page.clean()
    
    productos = [
        {"id": "001", "nombre": "Arroz", "precio": 20.0, "cantidad": 10},
        {"id": "002", "nombre": "Frijoles", "precio": 25.0, "cantidad": 15},
        {"id": "003", "nombre": "Aceite", "precio": 50.0, "cantidad": 8},
    ]
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
    
    search_field = ft.TextField(label="Buscar producto", prefix_icon=ft.Icons.SEARCH)
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
        # Botones de exportar
        exportar_btn = ft.ElevatedButton(
            "Exportar Inventario",
            icon=ft.icons.DOWNLOAD,
        )

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
            for p in productos:
                inventario_table.rows.append(ft.DataRow(
                    cells=[
                        ft.DataCell(ft.Text(p["id"])),
                        ft.DataCell(ft.Text(p["nombre"])),
                        ft.DataCell(ft.Text(f"${p['precio']:.2f}")),
                        ft.DataCell(ft.Text(str(p["cantidad"])))
                    ]
                ))
            page.update()

        actualizar_tabla()

        return ft.Column(
            controls=[
                ft.Row(
                    controls=[
                        ft.Text("Gestión de Inventario", size=24, weight=ft.FontWeight.BOLD, expand=True),
                        exportar_btn
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                ),
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
    
    page.add(layout)
    change_view(None)  # Inicializar con la vista de ventas
    actualizar_lista()

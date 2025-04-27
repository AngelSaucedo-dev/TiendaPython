import flet as ft
from main import main_interface
from admin import admin_interface

def login_view(page: ft.Page):
    page.title = "Login"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    user_field = ft.TextField(label="Usuario", bgcolor="white", color="black", border_radius=15, max_length=20)
    pass_field = ft.TextField(label="Contraseña", password=True, can_reveal_password=True, bgcolor="white", color="black", border_radius=15, max_length=20,)
    message = ft.Text("", color=ft.Colors.RED)

    def iniciar_sesion(e):
        usuario = user_field.value
        contraseña = pass_field.value

        if usuario == "Cajero1" and contraseña == "Cajero1":
            page.clean()
            main_interface(page)  # Interfaz de cajero
        elif usuario == "admin" and contraseña == "admin":
            page.clean()
            admin_interface(page)  # Interfaz de administrador
        else:
            message.value = "Credenciales incorrectas"
            page.update()

    login_button = ft.ElevatedButton(
        "Iniciar Sesión",
        height=40,
        width=200,
        on_click=iniciar_sesion,
        style=ft.ButtonStyle(
            bgcolor={"": "white", "hovered": "black"},
            color={"": "black", "hovered": "white"},
            shape=ft.RoundedRectangleBorder(radius=15),
            side={"": ft.BorderSide(color="black", width=2)}
        )
    )

    container = ft.Container(
        width=350,
        height=350,
        bgcolor="white",
        border_radius=20,
        padding=20,
        content=ft.Column(
            controls=[
                ft.Text("Bienvenido", size=20, weight=ft.FontWeight.BOLD, color="black"),
                user_field,
                pass_field,
                message,
                login_button
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10
        )
    )

    page.add(container)

# Este archivo sí debe tener la llamada a ft.app
ft.app(target=login_view)

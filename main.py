import flet as ft
from login import login_view

def main(page: ft.Page):
    login_view(page)

ft.app(target=main)
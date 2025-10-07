import flet as ft

def main(page: ft.Page):
    page.title = "Flet App de Prueba"
    page.add(ft.Text("¡Funciona Flet en escritorio!", size=30))

if __name__ == "__main__":
    ft.app(target=main, view=ft.FLET_APP)

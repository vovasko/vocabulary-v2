import flet as ft
from routes.settings_view import SettingsView
from routes.table_view import TableView
from services.DF_manager import DFManager
from components.appbar import AppBar

def home_view() -> ft.View:
    return ft.View(
        route="/",
        controls=[
            ft.Text("Home Page 2.0"),
            ft.ElevatedButton("Go to Settings", on_click=lambda e: e.page.go("/settings"), icon=ft.Icons.SETTINGS_ROUNDED),
            ft.ElevatedButton("Go to Table", on_click=lambda e: e.page.go("/table"))
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        appbar=AppBar(title="Home Page 2.0").build_home()
    )

def main(page: ft.Page):
    page.title = "Routing Demo"
    page.window.min_width = 700
    page.window.min_height = 650
    page.window.height = 650
    page.route_history = ["/"]
    page.df_manager = DFManager()

    page.fonts = {
        "Inter":"fonts/Inter-Regular.ttf",
        "Inter-Bold":"fonts/Inter-Bold.ttf",
        "Inter-Italic":"fonts/Inter-Italic.ttf",
        "Inter-SemiBold":"fonts/Inter-SemiBold.ttf"      
    }
    page.theme = ft.Theme(font_family="Inter")

    def route_change(e: ft.RouteChangeEvent):
        if page.route_history[-1] != page.route:
            page.route_history.append(page.route)
        page.views.clear()

        if page.route == "/":
            page.views.append(home_view())
        elif page.route == "/settings":
            page.views.append(SettingsView().fetch_view())
        elif page.route == "/table":
            page.views.append(TableView(page.df_manager).fetch_view())
        page.update()
        print(page.route_history)

    def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        top_view: ft.View = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main)

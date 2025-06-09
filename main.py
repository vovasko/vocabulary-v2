import flet as ft
from routes.settings_view import SettingsView
from routes.table_view import TableView

def home_view() -> ft.View:
    return ft.View(
        route="/",
        controls=[
            ft.Text("Home Page 2.0"),
            ft.ElevatedButton("Go to Settings", on_click=lambda e: e.page.go("/settings"), icon=ft.Icons.SETTINGS_ROUNDED),
            ft.ElevatedButton("Go to Table", on_click=lambda e: e.page.go("/table"))
        ],
        vertical_alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

def main(page: ft.Page):
    page.title = "Routing Demo"
    page.window.min_width = 500
    page.window.min_height = 500
    # page.show_semantics_debugger = True
    page.route_history = ["/"]

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
        print(page.route_history)
        page.views.clear()

        if page.route == "/":
            page.views.append(home_view())
        elif page.route == "/settings":
            # page.views.append(settings_view())
            page.views.append(SettingsView().fetch_view())
        elif page.route == "/table":
            page.views.append(TableView().fetch_view())
        page.update()

    def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        top_view: ft.View = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main)

import flet as ft
from routes.home_view import HomeView
from routes.settings_view import SettingsView
from routes.table_view import TableView
from routes.flash_view import FlashCardView
from routes.translation_view import TranslationView
from services.DF_manager import DFManager

def main(page: ft.Page):
    page.title = "Vocabulary Booster V2"
    page.window.min_width = 700
    page.window.min_height = 650
    page.window.height = 650
    page.route_history = ["/"]
    page.df_manager = DFManager()
    page.dialog_is_open = False
    page.bgcolor = ft.Colors.GREY_900
    # page.show_semantics_debugger = True
    page.home_view = HomeView(page.df_manager)

    page.fonts = {
        "Inter":"/fonts/Inter-Regular.ttf",
        "Inter-Bold":"/fonts/Inter-Bold.ttf",
        "Inter-Italic":"/fonts/Inter-Italic.ttf",
        "Inter-SemiBold":"/fonts/Inter-SemiBold.ttf"      
    }
    page.theme = ft.Theme(
        font_family="Inter",
        icon_button_theme=ft.IconButtonTheme(
            foreground_color=ft.Colors.WHITE70,
            hover_color=ft.Colors.WHITE10,
            disabled_foreground_color=ft.Colors.GREY
            ),
        filled_button_theme=ft.FilledButtonTheme(            
            foreground_color=ft.Colors.WHITE,
            bgcolor=ft.Colors.INDIGO_700,
            overlay_color=ft.Colors.BLACK,
            ),
        )
    
    def route_change(e: ft.RouteChangeEvent):
        if page.route_history[-1] != page.route:
            page.route_history.append(page.route)
        page.views.clear()

        if page.route == "/":
            page.views.append(page.home_view.fetch_view())
        elif page.route == "/settings":
            page.views.append(SettingsView().fetch_view())
        elif page.route == "/table":
            page.views.append(TableView(page.df_manager).fetch_view())
        elif page.route == "/flash":
            page.views.append(FlashCardView(page.df_manager).fetch_view())
        elif page.route == "/translation":
            page.views.append(TranslationView(page.df_manager).fetch_view())
        page.update()
        print(page.route_history)

    def view_pop(e: ft.ViewPopEvent):
        page.views.pop()
        top_view: ft.View = page.views[-1]
        page.go(top_view.route)

    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == "Escape":
            if len(page.route_history) > 1:
                page.route_history.pop()
                previous_route = page.route_history[-1]
                page.go(previous_route)
        elif e.key == "Backspace" and page.route == "/table" and not page.dialog_is_open:
            page.views[-1].controls[0].content.controls[2].delete_selected()
        elif e.key in ("Space", " ") and page.route == "/flash":
            page.views[-1].controls[0].flip_card()
        # print(f"Key: {e.key}, Shift: {e.shift}, Control: {e.ctrl}, Alt: {e.alt}, Meta: {e.meta}")
    
    page.on_keyboard_event = on_keyboard
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    page.go(page.route)

ft.app(target=main, assets_dir="assets")

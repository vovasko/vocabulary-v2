import flet as ft

class AppBar:
    def __init__(self, title: str, on_exit: callable = None):
        self.title = title
        self.on_exit = on_exit
        
        # Main buttons
        self.home_btn = ft.IconButton(ft.Icons.HOME, on_click=lambda e: e.page.go("/"))
        self.sett_btn = ft.IconButton(ft.Icons.SETTINGS, on_click=lambda e: e.page.go("/settings"))
        self.back_btn = ft.IconButton(ft.Icons.ARROW_BACK_IOS_ROUNDED, icon_size=30, scale=0.7)

        self.create_clicks()

    def create_clicks(self):
        def go_back(e: ft.ControlEvent):
            if self.on_exit:
                self.on_exit()
            if len(e.page.route_history) > 1:
                # Remove current route
                e.page.route_history.pop()
                # Go to previous route
                previous_route = e.page.route_history[-1]
                e.page.go(previous_route)
        self.back_btn.on_click = go_back

        def go_home(e: ft.ControlEvent):
            if self.on_exit:
                self.on_exit()
            e.page.route_history = ["/"]
            e.page.go("/")
        self.home_btn.on_click = go_home

    
    def build(self):    
        return ft.AppBar(
            title=ft.Text(self.title),
            actions=[
                self.home_btn,
                self.sett_btn
            ],
            center_title=True,
            leading=self.back_btn
        )

    def build_home(self):            
        return ft.AppBar(
            title=ft.Text(self.title),
            actions=[
                self.sett_btn
            ],
            center_title=True,
        )
    
    def build_settings(self):            
        return ft.AppBar(
            title=ft.Text(self.title),
            center_title=True,
            leading=self.back_btn
        )
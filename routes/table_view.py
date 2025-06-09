import flet as ft

class TableView(ft.Column):
    def __init__(self):
        super().__init__()

        self.spacing = 12
        self.scroll = "auto"
        self.width = 500
        self.expand = True
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.container_style = {
            "width" : self.width,
            "bgcolor" : ft.Colors.GREY_900,
            "border_radius" : ft.border_radius.all(12),
            "padding" : ft.padding.all(12),
            "margin" : ft.margin.only(12, 0, 12, 0)
        }

        self.create_title()

    def fetch_view(self):
        return ft.View(
            route="/table",
            horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            self.main_title,
                            # ft.Container(
                            #     content=self,
                            #     expand=True
                            # )
                        ]
                    ),
                    expand=True,
                )
            ]
        )
    
    def create_title(self):
        def go_back(e: ft.ControlEvent):
            if len(e.page.route_history) > 1:
                # Remove current route
                e.page.route_history.pop()
                # Go to previous route
                previous_route = e.page.route_history[-1]
                e.page.go(previous_route)
            
        self.main_title = ft.Container(
            content=ft.Stack(
                controls=[                    
                    ft.Container( # Center-aligned title
                        ft.Text("Table", style=ft.TextThemeStyle.HEADLINE_SMALL),
                        alignment=ft.alignment.center
                    ),  
                    ft.Container( # Left-aligned button
                        content=ft.Row(
                            controls=[                            
                                ft.ElevatedButton("Back", on_click=go_back, icon=ft.Icons.ARROW_BACK_IOS_ROUNDED),
                                ft.ElevatedButton(
                                    text="Settings",                            
                                    icon=ft.Icons.SETTINGS_ROUNDED,
                                    on_click=lambda e: e.page.go("/settings")
                                ),
                            ],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                        ),
                        alignment=ft.alignment.center_left,
                    ),
                ],
                height=40,
                width=500,
            ),
            padding=10
        )
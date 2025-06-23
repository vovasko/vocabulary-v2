import flet as ft
from components.appbar import AppBar

class HomeView(ft.Column):
    def __init__(self):
        super().__init__()

        self.container_style = {
            "bgcolor":ft.Colors.with_opacity(0.45, ft.Colors.GREY_800),
            "border_radius":12,
            "margin":ft.margin.only(50, 20, 50, 0),
        }

        self.create_word_card(word={"type":"der", "german":"Baum", "translation":"tree"})
        self.create_nav_card()
        self.create_stats_card()

        self.controls = [
            # ft.ElevatedButton("Go to Settings", on_click=lambda e: e.page.go("/settings"), icon=ft.Icons.SETTINGS_ROUNDED),
            # ft.Text("Hello from gg", size=30),
            # ft.Text("Hello from Inter", font_family="Inter", size=30),
            # ft.Text("Hello from Inter-Italic", font_family="Inter-Italic", size=30),
            # ft.Button("font", on_click=lambda e: print(e.page.theme)),
            self.word_card,
            self.nav_card,
            self.stats_card
        ]

    def fetch_view(self) -> ft.View:
        return ft.View(
            route="/",
            controls=self.controls,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            appbar=AppBar(title="Home Page 2.0").build_home(),
            padding=ft.padding.only(0, 10, 0, 10),
            scroll=ft.ScrollMode.HIDDEN
        )
    
    def create_nav_card(self):
        def nav_row(icon, label, on_click=None):
            return ft.Container(
                content=ft.Row([
                    ft.Icon(icon, size=22, color="white"),
                    ft.Text(label, size=16),
                    ft.Container(expand=True),
                    ft.Icon(ft.Icons.KEYBOARD_ARROW_RIGHT, size=20, color="grey")
                ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                padding=15,
                on_click=on_click,
                ink=True,
            )
        def divider():
            return ft.Divider(height=1, leading_indent=10, trailing_indent=15)
        
        self.nav_card = ft.Column(
            controls=[
                # ft.Container(
                #     ft.Text(value="Navigation Card"),
                #     margin=ft.margin.only(74, 12, 0, 0)
                # ),
                ft.Container(
                    content=ft.Column([
                        nav_row(ft.Icons.G_TRANSLATE_ROUNDED, "Translation master", lambda e: print("Translation clicked")),
                        divider(),
                        nav_row(ft.Icons.TABLE_ROWS_ROUNDED, "Records keeper", lambda e: e.page.go("/table")),
                        divider(),
                        nav_row(ft.Icons.AUTO_AWESOME_MOTION_ROUNDED, "Flash cards creator", lambda e: e.page.go("/flash")),
                    ], spacing=0),
                    **self.container_style
                )
            ]
        )
        
    def create_word_card(self, word: dict = None):
        def on_add(e: ft.ControlEvent):
            e.control.selected = True
            e.control.label.value = "Added to Vocabulary"
            e.control.disabled = True
            e.control.update()

        word_is_dummy = False
        if not isinstance(word, dict): # fill with dummy data
            word = {
                "german":"das Auto",
                "translation":"the car",
            }
            word_is_dummy = True
        elif word["type"] in ("der", "die", "das"):
            word["german"] = f"{word['type']} {word['german']}" 

        self.word_card = ft.Container(
            content=ft.Column([
                ft.Text("Word of the Day", size=16, weight="bold", color="white"),
                ft.Container(height=10), # spacing
                ft.Text(word["german"], size=28, weight="bold", color="white"),
                ft.Text(word["translation"], size=20, color="#AAAAAA"),
                ft.Container(height=10),  # spacing
                ft.Chip(
                    label = ft.Text("Add to Vocabulary"),
                    on_select=on_add,
                    disabled=word_is_dummy)
                ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER
            ),
            padding=20,
            **self.container_style
        )

    def create_stats_card(self):
        def mock_chart(label):
            return ft.Container(
                content=ft.Column([
                    ft.Text(label, size=14, color="white"),
                    ft.Container(
                        height=80,
                        width=80,
                        bgcolor="#3A3A3C",
                        border_radius=10
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=10
            )

        self.stats_card = ft.Column(
            controls=[
                # ft.Container(
                #     ft.Text(value="Stats Card"),
                #     margin=ft.margin.only(74, 12, 0, 0)
                # ),
                ft.Container(
                    content=ft.Column([
                        ft.Text("Your Learning Statistics", size=16, weight="bold", color="white"),
                        ft.Row([
                            mock_chart("Words learned"),
                            mock_chart("Review rate"),
                            mock_chart("Daily streak"),
                        ], alignment=ft.MainAxisAlignment.SPACE_EVENLY)
                    ]),
                    padding=20,
                    **self.container_style
                )
            ]
        )

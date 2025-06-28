import flet as ft
from components.appbar import AppBar
from components.buttons import RefreshButton
from services.home_helpers import DayWord
from services.DF_manager import DFManager

class HomeView(ft.Column):
    def __init__(self, df_manager: DFManager):
        super().__init__()

        self.container_style = {
            "bgcolor":ft.Colors.with_opacity(0.45, ft.Colors.GREY_800),
            "border_radius":12,
            "margin":ft.margin.only(50, 20, 50, 0),
        }

        self.day_word = DayWord()
        self.df_manager = df_manager

        self.create_word_card()
        self.create_nav_card()
        self.create_stats_card()

        self.controls = [
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
                ft.Container(
                    content=ft.Column([
                        nav_row(ft.Icons.G_TRANSLATE_ROUNDED, "Translation master", lambda e: e.page.go("/translation")),
                        divider(),
                        nav_row(ft.Icons.TABLE_ROWS_ROUNDED, "Records keeper", lambda e: e.page.go("/table")),
                        divider(),
                        nav_row(ft.Icons.AUTO_AWESOME_MOTION_ROUNDED, "Flash cards creator", lambda e: e.page.go("/flash")),
                    ], spacing=0),
                    **self.container_style
                )
            ]
        )
        
    def create_word_card(self):
        def on_add(e: ft.ControlEvent):
            # Add new word
            self.df_manager.create_new_record(self.day_word.word_data)
            self.day_word.on_word_added()
            # Adjust button
            e.control.selected = True
            e.control.label.value = "Added to Vocabulary"
            e.control.disabled = True
            e.control.update()

        def on_refresh(e: ft.ControlEvent):
            # self.refresh_btn.disabled = True
            # self.refresh_btn.update()
            self.day_word.get_word_data() # get new word
            self.word_card_refs["german"].current.value = get_display_word()
            self.word_card_refs["translation"].current.value =  self.day_word.word_data["translation"]
            self.word_card_refs["add_btn"].current.selected = False
            self.word_card_refs["add_btn"].current.disabled = False
            self.refresh_btn.disabled = False
            self.word_card.update()

        def get_display_word():
            if self.day_word.word_data["type"] in ("der", "die", "das"):
                return f"{self.day_word.word_data['type']} {self.day_word.word_data['german']}" 
            else: return self.day_word.word_data['german']
        
        self.word_card_refs = {
            "german": ft.Ref[ft.Text](),
            "translation": ft.Ref[ft.Text](),
            "add_btn": ft.Ref[ft.Chip](),
        }
        self.refresh_btn = RefreshButton(on_refresh)
        self.word_card = ft.Container(
            content=ft.Column([                
                ft.Row([
                    ft.Row(expand=True), # Filler
                    ft.Row([ft.Text("Word of the Day", size=16, weight="bold", color="white")], alignment="center", expand=True),
                    ft.Row([self.refresh_btn], alignment="end", expand=True)
                ], alignment="center"),
                ft.Container(height=10), # spacing
                ft.Text(get_display_word(), size=28, weight="bold", color="white", ref=self.word_card_refs["german"]),
                ft.Text(self.day_word.word_data["translation"], size=20, color=ft.Colors.WHITE70, ref=self.word_card_refs["translation"]),
                ft.Container(height=10),  # spacing
                ft.Chip(
                    label = ft.Text(value="Add to Vocabulary" if not self.day_word.saved else "Added to Vocabulary"),
                    on_select=on_add,
                    disabled=self.day_word.saved,
                    selected=self.day_word.saved,
                    ref=self.word_card_refs["add_btn"]
                    )
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

import flet as ft
from components.appbar import AppBar
from components.buttons import RefreshButton
from components.graphs import StatsPieChart
from services.home_helpers import DayWord, Statistics
from services.DF_manager import DFManager

class HomeView(ft.Column):
    def __init__(self, df_manager: DFManager):
        super().__init__()

        self.container_style = {
            "bgcolor":ft.Colors.with_opacity(0.45, ft.Colors.GREY_800),
            "border_radius":12,
            "margin":ft.margin.only(50, 20, 50, 0),
            "width":800,
        }

        self.df_manager = df_manager
        self.day_word = DayWord()
        self.statistics = Statistics(self.df_manager)

        self.create_integrity_flag()
        self.create_word_card()
        self.create_nav_card()
        self.create_stats_card()

        self.controls = [
            self.word_card,
            self.nav_card,
            self.stats_card,
            ft.Container(height=20) # Spacing
        ]

    def fetch_view(self) -> ft.View:
        return ft.View(
            route="/",
            controls=self.controls,
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            appbar=AppBar(title="Home Page").build_home(),
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
        def chart_layout(label, mode, color = None):
            text_ref = ft.Ref[ft.Text]()
            caption_text = ft.Text("", size=14, color="white", ref=text_ref)
            chart = StatsPieChart(self.statistics.get_stats(mode), color, text_ref)
            return ft.Container(
                content=ft.Column([
                    ft.Text(label, size=14, color="white", weight="bold"),
                    chart,
                    caption_text
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=10
            )

        self.stats_card = ft.Container(
                content=ft.Column([
                    ft.Row(controls=[
                        ft.Text("Your Learning Statistics", size=16, weight="bold", color="white"),
                        ft.Text(f"Vocabulary size - {self.statistics.words_count}")
                        ],alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Row([
                        chart_layout("Word Types", "type"),
                        chart_layout("Vocabulary Progress", "score", "DEEP_PURPLE"),
                        ft.Container(
                            content=ft.Column([
                                ft.Text("Integrity Check", size=14, color="white", weight="bold"),
                                self.integrity_icon,
                                self.integrity_caption
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                            padding=10
                        )
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                    spacing=10
                    )
                ]),
                padding=20,
                **self.container_style
            )
        
    def create_integrity_flag(self):
        text_ref = ft.Ref[ft.Text]()
        self.integrity_caption = ft.Text("", size=14, color="white", ref=text_ref)
        def update_caption(e: ft.ControlEvent):
            self.integrity_caption.value = e.control.data["caption"] if self.integrity_caption.value == "" else ""
            self.integrity_caption.update()
        
        def go_to_table(e: ft.ControlEvent):
            self.integrity_caption.value = ""
            e.page.go("/table")
        
        if self.statistics.bad_vals_flag: # Bad values present
            self.integrity_icon = ft.IconButton(
                icon=ft.Icons.ERROR_OUTLINE_ROUNDED,
                icon_color=ft.Colors.RED_300,
                icon_size=130,
                padding=10,
                data = {"caption": "Issues found!"},
                tooltip = f"Duplicates - {self.statistics.duplicates}\nNulls - {self.statistics.nulls}",
                style=ft.ButtonStyle(overlay_color=ft.Colors.with_opacity(0.0, "white")),
                on_hover=update_caption,
                on_click=go_to_table
            )
        else: 
            self.integrity_icon = ft.IconButton(
                icon=ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED,
                icon_size=130,
                icon_color=ft.Colors.GREEN_300,
                padding=10,
                data = {"caption":"All entries are valid"},
                on_hover=update_caption,
                style=ft.ButtonStyle(overlay_color=ft.Colors.with_opacity(0.0, "white")),
                mouse_cursor=ft.MouseCursor.BASIC
            )        
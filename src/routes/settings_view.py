import flet as ft
from services.settings import SettingsManager
from components.appbar import AppBar

class SettingsView(ft.Column):
    def __init__(self):
        super().__init__(spacing=12, scroll="auto", width=500, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
        self.container_style = {
            "width" : self.width,
            "bgcolor" : ft.Colors.GREY_900,
            "border_radius" : ft.border_radius.all(12),
            "padding" : ft.padding.all(12),
            "margin" : ft.margin.only(12, 0, 12, 0)
        }

        self.settings = SettingsManager()

        self.create_translation_layout()
        self.create_table_layout()
        self.create_flash_layout()

        self.controls = [            
            self.tr_layout,
            self.ta_layout,
            self.fl_layout,
        ]
    
    def fetch_view(self) -> ft.View:
        return ft.View(
            route="/settings",
            appbar=AppBar(title="Settings", on_exit=self.save_on_exit).build_settings(),
            horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Container(
                                content=self,
                                expand=True
                            )
                        ]
                    ),
                    expand=True,
                )
            ]
        )
    
    def save_on_exit(self):
        self.settings.save()
        
    def create_translation_layout(self):
        title = ft.Container(
            ft.Text(value="Translation Settings"),
            margin=ft.margin.only(24, 12, 0, 0)
        )
        container = ft.Container(
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text("Main Translation Language"),
                            self.create_lang_selector(main=True)
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Second Translation Language"),
                            self.create_lang_selector(main=False)
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN   
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Examples to include"),
                            self.create_segmented_btn(mode="examples")
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN   
                    ),
                    ft.Row(
                        controls=[
                            ft.Text("Meanings to include"),
                            self.create_segmented_btn(mode="meanings")
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN   
                    )
                ]
            ),
            **self.container_style,
        )

        self.tr_layout = ft.Column(
            controls=[
                title,
                container
            ]
        )
        
    def create_table_layout(self):
        title = ft.Container(
            ft.Text(value="Table display settings"),
            margin=ft.margin.only(24, 12, 0, 0)
        )
        controls = self.create_switch_controls(parent="columns")
        container = ft.Container(
            **self.container_style,
            content=ft.Row(
                controls=[
                    ft.Column(controls=controls[:3], expand=1, spacing=0),
                    ft.Column(controls=controls[3:], expand=1, spacing=0),
                ]
            ),
        )
        self.ta_layout = ft.Column(
            controls=[
                title,
                container
            ]
        )

    def create_flash_layout(self):
        title = ft.Container(
            ft.Text(value="Flash card settings"),
            margin=ft.margin.only(24, 12, 0, 0)
        )
        deck_settings = ft.Row(
            controls=[
                ft.Text("Cards in deck"),
                self.create_segmented_btn(mode="cards_in_deck")
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )
        header = ft.Row(
            controls=[ft.Text(value="Flash card content")],
            alignment=ft.MainAxisAlignment.CENTER
        )
        controls = self.create_switch_controls(parent="flashcards")
        columns = ft.Row(
            controls=[
                ft.Column(controls=controls[:3], expand=1, spacing=0),
                ft.Column(controls=controls[3:], expand=1, spacing=0),
            ]
        )
        container = ft.Container(
            **self.container_style,
            content=ft.Column(
                controls=[
                    deck_settings,
                    header,
                    columns
                ]
            )
        )
        self.fl_layout = ft.Column(
            controls=[
                title,
                container
            ]
        )

    def create_switch_controls(self, parent) -> list[ft.Row]:
        # Parent is name of a root setting for the nested one - ["columns", "flashcards"]
        def change(e: ft.ControlEvent):
            self.settings.set(
                key=e.control.label.value,
                value=e.control.value
            )

        controls = []
        
        for key,value in self.settings.get(parent, {}).items():
            if key == "german": continue
            row = ft.Row(
                spacing=0,
                controls=[
                    ft.Switch(
                        adaptive=True,
                        scale=0.7,
                        value=value,
                        label=ft.Text(
                            value=f"{parent}.{key}",
                            visible=False
                        ),
                        on_change=change
                    ),
                    ft.Text(value=key.replace('_', ' ').capitalize())
                ], 
            ) 
            controls.append(row)

        return controls
    
    def create_lang_selector(self, main: bool) -> ft.Row:
        lang_list = dict(self.settings.get_langs()) # Create main lang list
        if main: lang_var = "main_lang"
        else:
            lang_var = "second_lang"
            lang_list = {"nn": "None", **lang_list}

        def selected(e: ft.ControlEvent):
            lang_text.value = e.control.data["lang"]
            self.settings.set(lang_var, e.control.data)
            self.update()

        lang_text = ft.Text(value=self.settings.get(lang_var)["lang"], text_align=ft.TextAlign.END)
        row = ft.Row(
            controls=[
                lang_text,
                ft.PopupMenuButton(
                    items=[ft.PopupMenuItem(text=lang, data={"code":code, "lang":lang}, on_click=selected) for code, lang in lang_list.items()],
                    tooltip="Change Language",
                    height=28,
                    padding=0,
                )
            ],
            alignment=ft.MainAxisAlignment.END  ,
            height=30
        )
        return row
    
    def create_segmented_btn(self, mode) -> ft.CupertinoSlidingSegmentedButton:
        # Mode - [examples, meanings, cards_in_deck]
        options = []
        current_value = self.settings.get(mode)

        def on_change(e: ft.ControlEvent):
            selected = options[e.control.selected_index]
            self.settings.set(key=mode, value=selected)

        match mode:
            case "cards_in_deck": 
                options = ["5", "10", "20", "30", "All"]
                selected_index = options.index(str(current_value)) if str(current_value) in options else 0
            case _ : 
                options = [0, 1, 2]
                selected_index = options.index(current_value) if current_value in options else 0

        btn = ft.CupertinoSlidingSegmentedButton(
            controls=[ft.Text(opt) for opt in options],
            selected_index=selected_index,
            on_change=on_change
        )

        return btn
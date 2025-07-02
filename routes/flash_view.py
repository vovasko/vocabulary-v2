import flet as ft 
from services.settings import SettingsManager
from services.DF_manager import DFManager
from components.appbar import AppBar
from pandas import DataFrame, Series


class FlashCardView(ft.Column):
    def __init__(self, df_manager: DFManager):
        super().__init__(spacing=20, scroll="auto", horizontal_alignment=ft.CrossAxisAlignment.CENTER, alignment=ft.MainAxisAlignment.CENTER)

        self.side_index = 0  # 0=settings, 1=front, 2=back, 3=end screen, 4=info
        self.deck = DataFrame()
        self.deck_len = 1
        self.current_card_index = 0
        self.current_row = Series()

        self.settings = SettingsManager()
        self.df_manager = df_manager
        self.appbar = AppBar(title="Flash Cards Creator").build()

        self.card_style = {
            "alignment" : ft.alignment.center,        
            "border_radius" : ft.border_radius.all(12),
            "padding" : ft.padding.all(20),
            "expand" : True,
            "visible" : False,
        }
        self.card_elements = {
            "type":               ft.Text("NOUN", size=14, opacity=0.8), 
            "card_number":        ft.Text("Card 1/1", size=14),
            "card_number_back":   ft.Text("Card 1/1", size=14),
            "german":             ft.Text("Here goes German", size=24),
            "translation":        ft.Text("Here goes Translation", size=24, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
            "second_translation": ft.Text("Here goes Translation 2", size=24, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
            "example":            ft.Text("Here goes Example", size=18, max_lines=3, overflow=ft.TextOverflow.ELLIPSIS),
            "meaning":            ft.Text("Here goes meaning", size=18, max_lines=3, overflow=ft.TextOverflow.ELLIPSIS), 
            "score":              ft.Text("0", size=14)
        }

        self.create_card()
        self.create_buttons()
        self.controls = [self.card, self.btn_row]
    
    def fetch_view(self) -> ft.View:
        return ft.View(
            route="/flash",
            appbar=self.appbar,
            horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            vertical_alignment= ft.MainAxisAlignment.CENTER,
            controls=[self]
        )
    
    def create_card(self):
        # === SETTINGS VIEW === MARK: Setting view
        self.deck_choice = ft.Dropdown(
            label="Choose Deck",
            options=[
                ft.dropdown.Option(key="new", text="New cards"),
                ft.dropdown.Option(key="repeat", text="To repeat"),
                ft.dropdown.Option(key="nouns", text="Nouns"),
                ft.dropdown.Option(key="verbs", text="Verbs"),
                ft.dropdown.Option(key="adjectives", text="Adjectives"),
                ft.dropdown.Option(key="other", text="Other"),
            ],
            value="new",
        )

        self.start_btn = ft.ElevatedButton(content=ft.Text("Start", size=16, weight="bold"), on_click=self.start_game, width=150)
        self.settings_view = ft.Container(
            content=ft.Column([
                ft.Text("Flashcard Settings", size=24),
                self.deck_choice,
                self.start_btn
            ], horizontal_alignment="center", alignment="center", spacing=20),
            # bgcolor=ft.Colors.LIGHT_BLUE_700,
            bgcolor=ft.Colors.INDIGO_700,
            **self.card_style,
        )

        # === FRONT VIEW === MARK: Front view
        self.front_view = ft.Container(
            content=ft.Column(
                controls=[
                    self.card_elements["card_number"],
                    self.card_elements["german"],
                    self.card_elements["meaning"]
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            bgcolor=ft.Colors.LIGHT_BLUE_800,
            opacity=1.0,
            animate_opacity=ft.Animation(300, "easeInOut"),
            animate_offset=ft.Animation(300, "easeInOut"),
            offset=ft.Offset(0, 0),
            on_click=lambda e: self.flip_card(),
            **self.card_style
        )

        # === BACK VIEW === MARK: Back view
        self.back_view = ft.Container(
            content=ft.Column(
                controls=[
                    ft.Row([ft.Stack([
                            ft.Row([self.card_elements["type"],], alignment=ft.MainAxisAlignment.START, width=460),
                            ft.Row([self.card_elements["card_number_back"],], alignment=ft.MainAxisAlignment.CENTER, width=460),
                            ft.Row([self.card_elements["score"],], alignment=ft.MainAxisAlignment.END, width=460),
                        ]),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    ft.Column([
                        self.card_elements["translation"],
                        self.card_elements["second_translation"],
                    ], spacing=20, horizontal_alignment="center"),
                    self.card_elements["example"],
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN, 
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            ),
            bgcolor=ft.Colors.GREEN_800,
            opacity=0.0,
            animate_opacity=ft.Animation(300, "easeInOut"),
            animate_offset=ft.Animation(300, "easeInOut"),
            offset=ft.Offset(0.1, 0),
            on_click=lambda e: self.flip_card(),
            **self.card_style
        )

        # === END VIEW === MARK: End view
        self.back_to_settings_btn = ft.ElevatedButton(content=ft.Text("Back to settings", size=16, weight="bold"), on_click=lambda e: self.change_view(e, 0), width=180)
        self.end_screen = ft.Container(
            content=ft.Column([
                ft.Text("Session Completed!", size=24),
                # ft.Text(f"Correct Answers: {self.correct_answers}/{self.total_questions}", size=18),
                self.back_to_settings_btn
            ], horizontal_alignment="center", alignment="center", spacing=20),
            bgcolor=ft.Colors.INDIGO_700,
            **self.card_style
        )

        # === INFO VIEW === MARK: Info view
        self.info_view = ft.Container(
            content=ft.Column([
                ft.Text("There are no words to learn in this deck", size=24),
                self.back_to_settings_btn
            ], horizontal_alignment="center", alignment="center", spacing=20),
            bgcolor=ft.Colors.INDIGO_700,
            **self.card_style
        )

        # === STACK OF ALL VIEWS ===
        self.card_container = ft.Container(
            content=ft.Stack([
                self.settings_view,
                self.front_view,
                self.back_view,
                self.end_screen,
                self.info_view
            ]),
            width=500,
            height=300,
            border_radius=20,
            ink=True
        )
        
        self.settings_view.visible = True
        self.card = ft.Card(content=self.card_container, elevation=6)

        # Make some display data invisible according to user's preferences
        card_display_settings = self.settings.get("flashcards")
        for key, value in card_display_settings.items():
            if not value and key in ("example", "meaning"):
                self.card_elements[key].opacity = 0
                self.card_elements[key].max_lines = 1
            elif not value and key in ("type", "score", "translation", "second_translation"):
                self.card_elements[key].visible = False

    def create_buttons(self): # MARK: btn_row
        self.btn_row = ft.Row(
            controls=[
                ft.ElevatedButton("Repeat", on_click=lambda e: self.next_card(e, new_score=-1), width=80, height=40),
                ft.ElevatedButton("Hard",   on_click=lambda e: self.next_card(e, new_score=1), width=80, height=40),
                ft.ElevatedButton("Flip",   on_click=lambda e: self.flip_card(), width=100, height=40, icon=ft.Icons.AUTORENEW_ROUNDED),
                ft.ElevatedButton("Good",   on_click=lambda e: self.next_card(e, new_score=2), width=80, height=40),
                ft.ElevatedButton("Easy",   on_click=lambda e: self.next_card(e, new_score=3), width=80, height=40),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            width=500,
            height=40,
            disabled=True,
            opacity=0.0
        )

    def start_game(self, e: ft.ControlEvent):
        self.deck = self.df_manager.fetch_df(mode=self.deck_choice.value)
        if self.deck.shape[0] == 0:
            self.change_view(e, 4)
            return

        sample_amount = lambda shape: min(int(self.settings.get("cards_in_deck", default=20)), shape)
        self.deck = self.deck.sample(sample_amount(self.deck.shape[0]), weights=self.deck.score.apply(lambda x: 4-x))
        self.deck_len = self.deck.shape[0]
        self.deck.reset_index(inplace=True)

        self.current_card_index = 0

        self.next_card(e)
        self.change_view(e, 1)

    def flip_card(self):
        if self.side_index not in (1, 2):
            return 

        self.side_index = 2 if self.side_index == 1 else 1
        is_front: bool = self.side_index == 1
        if is_front:
            self.front_view.opacity = 1.0
            self.front_view.offset = ft.Offset(0, 0)
            self.back_view.opacity = 0.0
            self.back_view.offset = ft.Offset(0.1, 0)
        else:
            self.front_view.opacity = 0.0
            self.front_view.offset = ft.Offset(-0.1, 0)
            self.back_view.opacity = 1.0
            self.back_view.offset = ft.Offset(0, 0)

        self.update()

    def change_view(self, e: ft.ControlEvent, new_view_index: int):
        views = [self.settings_view, self.front_view, self.back_view, self.end_screen, self.info_view]
        if new_view_index == 1:
            self.front_view.visible = True
            self.back_view.visible = True
            self.btn_row.disabled = False
            self.btn_row.opacity = 1.0
        else:
            self.front_view.visible = False
            self.back_view.visible = False
            self.btn_row.disabled = True
            self.btn_row.opacity = 0.0
        if new_view_index == 3:
            self.save_scores()

        current = views[self.side_index]
        current.visible = False

        new_view = views[new_view_index]
        new_view.visible = True

        self.side_index = new_view_index
        e.page.update()

    def next_card(self, e: ft.ControlEvent, new_score: int = None):
        if new_score != None and self.current_card_index > 0:
            self.deck.at[self.current_card_index - 1, "score"] = new_score
            print(f"set new score ({new_score}) for {self.deck.at[self.current_card_index - 1, "german"]}")

        self.current_card_index += 1
        if self.current_card_index > self.deck_len:
            if self.side_index == 2: self.flip_card()
            self.change_view(e, 3)
            return
        
        self.current_row = self.deck.iloc[self.current_card_index - 1]
        
        if self.side_index == 2:
            self.back_view.content.visible = False  
            self.flip_card()
        
        self.card_elements["card_number"].value = f"Card {self.current_card_index}/{self.deck_len}"
        self.card_elements["card_number_back"].value = f"Card {self.current_card_index}/{self.deck_len}"
        self.card_elements["type"].value = "NOUN" if self.current_row.type in ("der", "die", "das") else self.current_row.type
        self.card_elements["german"].value = f"{self.current_row.type} {self.current_row.german}" if self.current_row.type in ("der", "die", "das") else self.current_row.german 
        self.card_elements["translation"].value = self.current_row.translation
        self.card_elements["second_translation"].value = self.current_row.second_translation
        self.card_elements["example"].value = self.current_row.example
        self.card_elements["meaning"].value = self.current_row.meaning
        self.card_elements["score"].value = self.current_row.score

        self.card.update()
        e.page.update()    
        self.back_view.content.visible = True    

    def save_scores(self):
        scores = self.deck[["rowid", "score"]]
        self.df_manager.update_scores(scores)
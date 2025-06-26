import flet as ft
from components.appbar import AppBar
from services.settings import SettingsManager
from services.DF_manager import DFManager
from services.translator import Translator
from routes.table_view import ListViewTable
import pandas as pd
import threading

class TranslationView(ft.Column):
    def __init__(self, df_manager: DFManager):
        super().__init__()

        self.settings = SettingsManager()
        self.df_manager = df_manager
        self.translator = Translator()

        # self.input_data = pd.DataFrame()
        self.table = ListViewTable(records=self.translator.data)
        self.progress_bar = ft.ProgressBar(visible=False)
        self.create_input_row()
        # self.create_filepicker()

        self.controls = [
            # ft.ElevatedButton("check dialog", on_click=lambda _: self.open_dialog(success=True, data={
            #     "success_count": 1,
            #     "words_count"  : 2,
            #     "failed_words" : ["auto ...", "baby ...", "Man ..."]
            # })),
            self.input_row,
            self.progress_bar,
            self.table,
            # self.file_picker
        ]

        self.dialog = ft.AlertDialog(
            open=False,
            on_dismiss=self.dialog_dismissed,
            content_padding=ft.padding.only(20, 20, 20, 0)
        )

        self.container_style = {
            "bgcolor":ft.Colors.with_opacity(0.45, ft.Colors.GREY_800),
            "border_radius":12,
            "margin":ft.margin.only(50, 20, 50, 0),
        }

    def fetch_view(self) -> ft.View:
        return ft.View(
            route="/translation",
            controls=[self],
            vertical_alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            appbar=AppBar(title="Translation Master").build(),
            padding=ft.padding.only(left=30, right=30, top=10, bottom=10),
        )

    def open_dialog(self, success: bool, data: dict):        
        if success and not data["failed_words"]:
            self.dialog.title = ft.Row(
                controls=[
                    ft.Icon(name="CHECK_CIRCLE_ROUNDED", color=ft.Colors.GREEN_300),
                    ft.Text("Translation Successful", color=ft.Colors.GREEN_300)
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
            self.dialog.content = ft.Row([
                ft.Text(f"Translated words: {data["success_count"]}/{data["words_count"]}", size=16)
                ], alignment=ft.MainAxisAlignment.CENTER
            )
        elif success and data["failed_words"]: 
            self.dialog.title = ft.Row(
                controls=[
                    ft.Icon(name="CHECK_CIRCLE_ROUNDED", color=ft.Colors.WHITE),
                    ft.Text("Translation Completed")
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
            self.dialog.content = ft.Column([
                ft.Text(f"Translated words: {data["success_count"]}/{data["words_count"]}", size=16),
                ft.Text("Translation failed for:", size=16),
                *[ft.Row([ft.Text(fail, size=16)], alignment="start") for fail in data["failed_words"]]
                ], 
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
            self.dialog.content.height = 34 * len(self.dialog.content.controls) - 10
        else:  # mode = error
            self.dialog.title = ft.Row(
                controls=[
                    ft.Icon(name="ERROR_ROUNDED", color=ft.Colors.RED_300),
                    ft.Text("Error", color=ft.Colors.RED_300)
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
            self.dialog.content = ft.Column([
                ft.Text("Translation Errors:", size=16),
                *[ft.Row([ft.Text(fail, size=16)], alignment="start") for fail in data["failed_words"]]
                ], 
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER
            )
            self.dialog.content.height = 34 * len(self.dialog.content.controls) - 10
        
        if self not in self.page.overlay:
            self.page.overlay.clear()
            self.page.overlay.append(self.dialog)
        self.dialog.open = True
        self.page.dialog_is_open = True
        self.page.update()
        print(f"Dialog called")
    
    def dialog_dismissed(self, e):
        e.control.open = False
        e.page.dialog_is_open = False
        e.page.update()

    def create_input_row(self):
        def change_layout(e: ft.ControlEvent):
            if e.control.selected: # File input mode
                self.input_field.label = "File path"
                self.input_field.disabled = True
                self.action_btn.disabled= True
                self.action_btn.text = "Select File"
                self.action_btn.on_click = lambda _: self.file_picker.pick_files(allow_multiple=False)
            else: # Word input mode
                self.input_field.label = "Input word"
                self.input_field.disabled = False
                self.action_btn.text = "Add"
                self.action_btn.on_click = self.add_to_input
            self.input_row.update()
        
        def input_len_check(e: ft.ControlEvent):
            if len(e.control.value) > 0:
                self.action_btn.disabled = False
            else: self.action_btn.disabled = True
            self.action_btn.update()

        self.input_field = ft.TextField(
            label="Input word",
            on_change=input_len_check
        )
        self.action_btn = ft.ElevatedButton(
            text="Add",
            on_click=self.add_to_input,
            disabled=True
        )
        self.translate_btn = ft.ElevatedButton(
            text="Translate", 
            icon=ft.Icons.G_TRANSLATE_ROUNDED, 
            disabled=True,
            on_click=self.translate
        )

        self.input_row = ft.Row(
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=20,
            controls=[
                self.translate_btn,
                self.input_field,
                self.action_btn,
                # ft.Chip(
                #     label=ft.Text("File Input"), 
                #     show_checkmark=False, 
                #     on_select=change_layout,
                # ),
            ]
        )

    def create_filepicker(self): # Not working because of ft.FilePicker
        def on_file_picked(e: ft.FilePickerResultEvent):
            if e.files:
                self.input_field.label = f"Picked file: {e.files[0].name}"
                e.page.update()

        self.file_picker = ft.FilePicker(on_result=on_file_picked)
    
    def call_filepicker(self, e: ft.ControlEvent): # Not working because of ft.FilePicker
        self.page.overlay.append(self.file_picker)
        self.file_picker.pick_files(allow_multiple=False)
        self.page.update()

    def add_to_input(self, e: ft.ControlEvent):
        self.translator.input_data = pd.Series([self.input_field.value])
        self.translator.clean_data()
        
        # Clear input field
        self.input_field.value = ""
        self.action_btn.disabled = True
        self.input_row.update()
        
        # Enable translate button
        if self.translator.data.shape[0] > 0: 
            self.translate_btn.disabled = False
            self.translate_btn.update()

        self.table.records = self.translator.data
        self.table.build_table()
        self.table.update()

    def translate(self, e: ft.ControlEvent):
        self.progress_bar.visible = True
        self.progress_bar.value = 0.0
        self.progress_bar.update()
        self.translate_btn.disabled = True
        self.translate_btn.update()
        threading.Thread(
            target=self.translator.get_netz_info, 
            args=(
                self.settings._data,
                self.progress_callback,
                self.translation_complete
                ), 
            daemon=True
        ).start()

    def progress_callback(self, current: int, all_vals: int):
        progress_value = current / all_vals
        self.progress_bar.value = progress_value
        self.progress_bar.update()

    def translation_complete(self, success: bool, data: dict):
        self.progress_bar.visible = False
        self.progress_bar.update()
        # call dialogs
        success_flag = False if data["success_count"] == 0 else success
        self.open_dialog(success_flag, data)

        if success_flag: 
            # update table
            self.table.records = self.translator.data
            self.table.build_table()
            self.table.update()
            # Add new data to db
            self.df_manager.add_translated_data(self.translator.data)
            # Clear translator dataframe for new words
            self.translator.data = pd.DataFrame()
        else:
            self.translator.data = self.translator.data[["type", "german"]]
            self.translate_btn.disabled = False
            self.translate_btn.update()
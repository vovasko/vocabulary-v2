import flet as ft
from services.settings import SettingsManager
from services.edit_dialog import EditDialog
from services.DF_manager import DFManager
from components.appbar import AppBar

class TableView(ft.Column):
    def __init__(self, df_manager: DFManager):
        super().__init__(spacing=12, scroll="auto", width=500, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.container_style = {
            "width" : self.width,
            "bgcolor" : ft.Colors.GREY_900,
            "border_radius" : ft.border_radius.all(12),
            "padding" : ft.padding.all(12),
            "margin" : ft.margin.only(12, 0, 12, 0)
        }
        self.settings = SettingsManager()
        self.df_manager = df_manager
        self.create_controls()

        self.appbar = AppBar(title="Table").build()
        self.table = ListViewTable(self.df_manager, self.update_buttons, self.settings)

    def fetch_view(self):
        return ft.View(
            route="/table",
            appbar=self.appbar,
            horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    self.delete_btn,
                                    self.edit_btn,
                                    self.sort_btn
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_AROUND
                            ),
                            self.table
                        ],
                        expand=True
                    ),
                    expand=True,
                )
            ],
            floating_action_button=self.add_btn
        )
    
    def create_controls(self):
        self.delete_btn = ft.ElevatedButton(
            "Delete",
            disabled=True,
            on_click=lambda e: self.table.delete_selected(),
            bgcolor=ft.Colors.RED_300,
            icon=ft.Icons.DELETE_FOREVER_ROUNDED,
            width=100
        )
        self.edit_btn = ft.ElevatedButton(
            "Edit",
            disabled=True,
            on_click=lambda e: self.table.call_dialog(e),
            bgcolor=ft.Colors.GREY_500,
            icon=ft.Icons.EDIT_ROUNDED,
            width=100
        )
        self.sort_btn = ft.ElevatedButton(
            "Sort",
            on_click=lambda e: self.table.sort(col_name="index"),
            bgcolor=ft.Colors.GREY_500,
            icon=ft.Icons.SORT_ROUNDED,
            width=100
        )
        self.add_btn = ft.FloatingActionButton(
            icon=ft.Icons.ADD, 
            on_click=lambda e: self.table.call_dialog(e, mode="new"),
            tooltip="Add new word",
        )
    
    def update_buttons(self, selected_count: int):
        self.delete_btn.disabled = selected_count == 0
        self.delete_btn.update()
        if selected_count == 1:
            self.edit_btn.disabled = False
            self.edit_btn.update()
        elif not self.edit_btn.disabled:
            self.edit_btn.disabled = True
            self.edit_btn.update()

class ListViewTable(ft.ListView):
    def __init__(self, df_manager: DFManager, on_selection_changed: callable, settings: SettingsManager):
        super().__init__(spacing=10, padding=20, auto_scroll=False, expand=True)
        self.df_manager = df_manager
        self.records = df_manager.data
        self.selected_refs: list[ft.Ref] = []
        self.on_selection_changed = on_selection_changed
        self.settings = settings
        self.last_sort = {}
        self.build_table()

    def build_table(self):
        self.controls.clear()
        self.last_sort = {"col": None, "asc": False}
        self.header = []
        self.column_flexes_dict = { "type": 2, "german": 4, "translation": 6,
            "second_translation": 6, "example": 8, "meaning": 8, "score": 1 }
        for col, value in self.settings.get("columns").items():
            if value: self.header.append(col)

        self.controls.append(self._build_row(self.header, is_header=True))
        self._build_content()
    
    def _build_content(self):
        self.controls = [self.controls[0]] # Delete all rows except header

        for row in self.records.itertuples():
            ref = ft.Ref[ft.Container]()
            container = self._build_row(row, ref=ref)
            self.controls.append(container)

    def _build_row(self, data: tuple | list[str], ref=None, is_header = False):  
        bgcolor = ft.Colors.GREY_700 if is_header else ft.Colors.GREY
        text_style = {
            "size":14,
            "overflow": ft.TextOverflow.ELLIPSIS, 
            "max_lines": 2
        }

        if is_header and isinstance(data, list):
            text_data = []
            for i, item in enumerate(data):
                match item:
                    case "second_translation": text_data.append("Translation 2")
                    case "score": text_data.append("Pt")
                    case _ : text_data.append(item.capitalize())
            bgcolor = ft.Colors.GREY_700
            controls_list = [
                ft.Container(
                    content=ft.Text(
                        value=col_text,                                        
                        text_align=ft.TextAlign.CENTER,
                        data={"col_name": col_name},
                        **text_style,
                    ),
                    expand=self.column_flexes_dict[col_name],
                    ink=True,
                    animate=ft.Animation(200, "easeInOut"),
                    on_click=lambda e: self.sort(e.control.content.data["col_name"]),
                    border_radius=12,
                    tooltip=f"Sort {col_text}"
                )
                for col_text, col_name in zip(text_data, data)
            ]
        else:
            ref = ft.Ref[ft.Text]()
            controls_list = [
                ft.Text(
                    value=getattr(data, col_name),
                    expand=self.column_flexes_dict[col_name],
                    ref=ref,
                    data={"ref":ref, "col":col_name},
                    **text_style
                )
                for col_name in self.header
            ]

        row = ft.Container(
            content=ft.Row(
                controls=controls_list,
                spacing=10,
                expand=True,
                alignment=ft.MainAxisAlignment.START
            ),
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            border_radius=12,
            bgcolor=bgcolor,
            ink=True,
            animate=ft.Animation(200, "easeInOut"),
            ref=ref,
            data={"ref": ref,"rowid": data.Index} if not is_header else None,
        )
        if not is_header:
            row.on_click = self.on_container_click
        return row

    def on_container_click(self, e: ft.ControlEvent):
        container = e.control
        ref = container.data["ref"]
        if not ref:
            return

        if ref in self.selected_refs:
            self.selected_refs.remove(ref)
            container.bgcolor = ft.Colors.GREY
        else:
            self.selected_refs.append(ref)
            container.bgcolor = ft.Colors.LIGHT_BLUE_100

        container.update()
        self.on_selection_changed(len(self.selected_refs))

    def delete_selected(self):
        rowids = []
        for ref in self.selected_refs:
            if ref.current and ref.current in self.controls:
                self.controls.remove(ref.current)
                rowids.append(ref.current.data["rowid"])
        self.selected_refs.clear()
        self.update()
        self.on_selection_changed(0)
        self.df_manager.delete_rows(rowids)

    def call_dialog(self, e, mode: str = "edit"):
        # mode = [edit, new]
        print(f"Dialog called")
        if mode == "new": 
            dialog = EditDialog(None, self.save_new_record) # Call New dialog
        else:
            dialog = EditDialog(self.selected_refs[0].current, self.save_updated_record) # Call Edit dialog
        
        if self not in e.page.overlay:
            e.page.overlay.append(dialog)
        dialog.open = True
        e.page.update()

    def save_updated_record(self):
        container = self.selected_refs[0].current
        self.df_manager.update_record(container)
        self.selected_refs.clear()
        self.on_selection_changed(0)
    
    def save_new_record(self, new_row: dict):
        self.df_manager.create_new_record(new_row)
        self.df_manager = DFManager()
        self.records = self.df_manager.data
        self._build_content()
        self.update()

    def sort(self, col_name: str):
        if self.last_sort["col"] == col_name:
            self.last_sort["asc"] = not self.last_sort["asc"]
        else: 
            self.last_sort["col"] = col_name
            self.last_sort["asc"] = True if col_name != "index" else False
        
        if col_name == "index":
            self.records.sort_index(inplace=True, ascending=self.last_sort["asc"])
        else:
            self.records.sort_values(by=col_name, inplace=True, ascending=self.last_sort["asc"], key=lambda col: col.str.lower())
        
        self._build_content()
        self.update()
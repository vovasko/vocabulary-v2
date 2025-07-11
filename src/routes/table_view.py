import flet as ft
from services.settings import SettingsManager
from services.edit_dialog import EditDialog
from services.DF_manager import DFManager
from components.appbar import AppBar
from components.buttons import StateButton
from pandas import DataFrame

class TableView(ft.Column):
    def __init__(self, df_manager: DFManager):
        super().__init__(spacing=12, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

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
        self.create_filter_controls()

        self.controls = [
            self.btn_row, 
            self.filter_row,
            self.table
        ]

    def fetch_view(self) -> ft.View:
        return ft.View(
            route="/table",
            appbar=self.appbar,
            horizontal_alignment = ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Container(
                    content=self,
                    expand=True,
                )
            ],
            padding=ft.padding.only(left=30, right=30, top=10, bottom=10)
        )
    
    def create_controls(self):
        self.appbar = AppBar(title="Records Keeper").build()
        self.table = ListViewTable(df_manager=self.df_manager, settings=self.settings, on_selection_changed=self.update_buttons)
        
        def delete_hover(e: ft.ControlEvent):
            if e.control.bgcolor == ft.Colors.RED_700: e.control.bgcolor = None
            else: e.control.bgcolor = ft.Colors.RED_700
            e.control.update()
        
        self.delete_btn = ft.FilledButton(
            "Delete",
            disabled=True,
            on_click=lambda e: self.table.delete_selected(),
            icon=ft.Icons.DELETE_FOREVER_ROUNDED,
            on_hover=delete_hover,
            expand=True
        )
        self.edit_btn = ft.FilledButton(
            "Edit",
            disabled=True,
            on_click=lambda e: self.table.call_dialog(e),
            icon=ft.Icons.EDIT_ROUNDED,
            expand=True
        )
        self.add_btn = ft.FilledButton(
            "Add word",            
            on_click=lambda e: self.table.call_dialog(e, mode="new"),
            icon=ft.Icons.ADD, 
            expand=True
        )
        self.sort_btn = StateButton(
            on_click=self.table.sort_index,
            text="Old first",
            icon=ft.Icons.SORT_ROUNDED,
            expand=True
        )
        self.filter_btn = StateButton(
            on_click=self.filter_toggle,
            text="Filter",
            icon=ft.Icons.FILTER_ALT_ROUNDED,
            expand=True
        )
        self.btn_row = ft.Row(
            controls=[
                self.delete_btn,
                self.edit_btn,
                self.add_btn,
                self.sort_btn,
                self.filter_btn
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN
        )        

    def create_filter_controls(self):
        self.filter_dropdown = ft.Dropdown(
            options=[
                ft.DropdownOption("Type"),
                ft.DropdownOption("Nouns"), 
                ft.DropdownOption("Score"),
                ft.DropdownOption("Problematic"),
            ], 
            on_change=self.on_filter_changed,
            border_color=ft.Colors.GREY
        )

        self.filter_row = ft.Row(
            controls=[self.filter_dropdown,],
            alignment=ft.MainAxisAlignment.START,
            visible=False
        )

    def on_filter_changed(self, e: ft.ControlEvent = None):
        def chip_selected(e: ft.ControlEvent):
            if not self.table.selected_filters:
                self.table.selected_filters = (e.control.data["column"], [])
            
            if e.control.selected:
                self.table.selected_filters[1].append(e.control.data["value"])
            else: 
                self.table.selected_filters[1].remove(e.control.data["value"])
            
            self.table.filter_selected()
            self.rows_count_txt.value = f"rows: {self.table.records.shape[0]}"
            self.rows_count_txt.update()

        selected = e.control.value if e is not None else self.filter_dropdown.value

        self.filter_row.controls = [self.filter_dropdown]
        self.table.selected_filters = ()

        match selected:
            case "Type":
                for chip in ["Noun", "Verb", "Adjective", "Other"]:
                    self.filter_row.controls.append(
                        ft.Chip(
                            label=ft.Text(chip),
                            on_select=chip_selected,
                            data={"column": "TYPE", "value": chip.lower()}
                        )
                    )
            case "Nouns":
                for chip in ["der", "die", "das"]:
                    self.filter_row.controls.append(
                        ft.Chip(
                            label=ft.Text(chip),
                            on_select=chip_selected,
                            data={"column": "type", "value": chip}
                        )
                    )
            case "Score":
                for chip in [-1, 0, 1, 2, 3]:
                    self.filter_row.controls.append(
                        ft.Chip(
                            label=ft.Text(chip),
                            on_select=chip_selected,
                            data={"column": "score", "value": chip}
                        )
                    )
            case "Problematic":
                for chip in ["Duplicates", "Nulls"]:
                    self.filter_row.controls.append(
                        ft.Chip(
                            label=ft.Text(chip),
                            on_select=chip_selected,
                            data={"column": "special", "value": chip.lower()}
                        )
                    )
        self.rows_count_txt = ft.Text(f"rows: {self.table.records.shape[0]}", expand=True, text_align="end")
        self.filter_row.controls.append(self.rows_count_txt)
        self.filter_row.update() 

    def filter_toggle(self, e: ft.ControlEvent = None):
        self.filter_row.controls = [self.filter_dropdown]
        self.filter_dropdown.value = "Type"
        self.on_filter_changed()
        self.filter_row.visible = not self.filter_row.visible
                
        self.table.selected_filters = ()
        self.table.filter_selected()

        self.update()

    def update_buttons(self, selected_count: int):
        def change_colors(btn):
            if btn.disabled:
                btn.bgcolor=ft.Colors.ON_SURFACE.with_opacity(0.18, "grey")
                btn.color=ft.Colors.ON_SURFACE.with_opacity(0.38, "white")
            else:
                btn.bgcolor = ft.Colors.INDIGO_700
                btn.color = ft.Colors.WHITE
            btn.update()

        self.delete_btn.disabled = selected_count == 0
        change_colors(self.delete_btn)

        if selected_count == 1:
            self.edit_btn.disabled = False
            change_colors(self.edit_btn)
        elif not self.edit_btn.disabled:
            self.edit_btn.disabled = True
            change_colors(self.edit_btn)

class ListViewTable(ft.ListView):
    def __init__(self, df_manager: DFManager = None, settings: SettingsManager = None, records: DataFrame = None, on_selection_changed: callable = None):
        super().__init__(spacing=5, auto_scroll=False, expand=True)
        self.df_manager = df_manager
        self.records = df_manager.data if self.df_manager != None else records
        self.selected_refs: list[ft.Ref] = []
        self.selected_filters: tuple[str, str|list] = ()
        self.on_selection_changed = on_selection_changed
        self.settings = settings
        self.last_sort = {}
        self.sort_old_first = False
        if isinstance(self.records, DataFrame): self.build_table()

    def build_table(self):
        self.controls.clear()
        self.last_sort = {"col": None, "asc": False}
        self.header_vals = []
        self.header_ref = ft.Ref[ft.Container]()
        self.column_flexes_dict = {"type": 2, "german": 4, "translation": 6,
            "second_translation": 6, "example": 8, "meaning": 8, "score": 1 }
        if self.settings != None:
            for col, value in self.settings.get("columns").items():
                if value: self.header_vals.append(col)
        else: 
            self.header_vals = list(self.records.columns)

        self.controls.append(self._build_row(self.header_vals, is_header=True, ref=self.header_ref))
        self._build_content()
    
    def _build_content(self, sorted = False):
        self.controls = [self.controls[0]] # Delete all rows except header
        if not sorted: self.records.sort_index(inplace=True, ascending=self.sort_old_first)

        for row in self.records.itertuples():
            ref = ft.Ref[ft.Container]()
            container = self._build_row(row, ref=ref)
            self.controls.append(container)

    def _build_row(self, data: tuple | list[str], ref=None, is_header = False):  
        default_bgcolor = ft.Colors.with_opacity(0.45, ft.Colors.GREY_800) if is_header else ft.Colors.GREY_700
        text_style = {
            "size":14,
            "overflow": ft.TextOverflow.ELLIPSIS, 
            "max_lines": 2
        }

        if is_header and isinstance(data, list):
            actions_table = self.df_manager != None
            text_data = []
            for item in data:
                match item:
                    case "second_translation": text_data.append("Translation 2")
                    case "score": text_data.append("Pt")
                    case _ : text_data.append(item.capitalize())
            controls_list = [
                ft.Container(
                    content=ft.Text(
                        value=col_text,                                        
                        text_align="center" if actions_table else "start",
                        data={"col_name": col_name},
                        **text_style,
                    ),
                    expand=self.column_flexes_dict.get(col_name, 2),
                    ink=True if actions_table else False,
                    animate=ft.Animation(200, "easeInOut"),
                    on_click=lambda e: self.sort(e.control.content.data["col_name"]) if actions_table else None,
                    border_radius=12,
                    tooltip=f"Sort {col_text}"
                )
                for col_text, col_name in zip(text_data, data)
            ]
        else:
            controls_list = [
                ft.Text(
                    value=getattr(data, col_name),
                    expand=self.column_flexes_dict.get(col_name, 2),
                    data={"col":col_name},
                    **text_style
                )
                for col_name in self.header_vals
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
            bgcolor=default_bgcolor,
            ink=True,
            animate=ft.Animation(200, "easeInOut"),
            ref=ref,
            data={"ref": ref,"rowid": data.Index} if not is_header else {"ref": ref},
        )
        if not is_header and self.df_manager != None:
            row.on_click = self.on_container_click
            row.on_long_press = self.on_container_long_press
        return row

    def on_container_click(self, e: ft.ControlEvent):
        container = e.control
        ref = container.data["ref"]
        if not ref:
            return

        if ref in self.selected_refs:
            self.selected_refs.remove(ref)
            container.bgcolor = ft.Colors.GREY_700
        else:
            self.selected_refs.append(ref)
            container.bgcolor = ft.Colors.INDIGO_500

        container.update()
        # print(f"{len(self.selected_refs)=}")
        if self.on_selection_changed: self.on_selection_changed(len(self.selected_refs))

    def on_container_long_press(self, e: ft.ControlEvent):
        container = e.control
        dialog = EditDialog(container, self.save_updated_record) # Call Edit dialog
        dialog.open_dialog(e)

    def delete_selected(self):
        if len(self.selected_refs) == 0:
            return # No selected refs
        rowids = []
        for ref in self.selected_refs:
            if ref.current and ref.current in self.controls:
                self.controls.remove(ref.current)
                rowids.append(ref.current.data["rowid"])
        self.selected_refs.clear()
        self.update()
        if self.on_selection_changed: self.on_selection_changed(0)
        self.df_manager.delete_rows(rowids)

    def call_dialog(self, e, mode: str = "edit"):
        # mode = [edit, new]
        if mode == "new": 
            dialog = EditDialog(None, self.save_new_record) # Call New dialog
        else:
            dialog = EditDialog(self.selected_refs[0].current, self.save_updated_record) # Call Edit dialog
        
        dialog.open_dialog(e)

    def save_updated_record(self, edited_container_ref: ft.Ref[ft.Container]):
        ref = edited_container_ref
        if ref in self.selected_refs:
            self.selected_refs.remove(ref)
            ref.current.bgcolor = ft.Colors.GREY_700
            ref.current.update()
            if self.on_selection_changed: self.on_selection_changed(len(self.selected_refs))
        
        container = ref.current
        container.update()
        self.df_manager.update_record(container)
    
    def save_new_record(self, new_row: dict):
        self.df_manager.create_new_record(new_row)
        self.records = self.df_manager.data
        if self.last_sort["col"] != None:
            col_name = self.last_sort["col"]
            self.last_sort["col"] = None
            self.sort(col_name)
        else: self._build_content()
        self.update()

    def sort(self, col_name: str):
        if self.records.shape[0] == 0: return # no records to sort
        if col_name != "index" and self.last_sort["col"] == "index" and self.last_sort["asc"] == True: return
        
        if self.last_sort["col"] == col_name:
            self.last_sort["asc"] = not self.last_sort["asc"]
        else: 
            self.last_sort["col"] = col_name
            self.last_sort["asc"] = True
        
        if col_name == "index":
            self.records.sort_index(inplace=True, ascending=self.last_sort["asc"])
        elif col_name == "score":
            self.records.sort_values(by=col_name, inplace=True, ascending=self.last_sort["asc"])
        else:
            self.records.sort_values(by=col_name, inplace=True, ascending=self.last_sort["asc"], key=lambda col: col.str.lower())
        
        if self.on_selection_changed: self.on_selection_changed(0)
        self.selected_refs.clear()
        self.highlight_col(col_name)
        self._build_content(sorted=True)
        self.update()

    def sort_index(self, e: ft.ControlEvent = None):
        self.sort_old_first = not self.sort_old_first
        self.sort("index")
        self.highlight_col("index", clean=True)

    def highlight_col(self, col_name: str, clean = False):
        if clean: 
            for container in self.header_ref.current.content.controls:
                container.bgcolor = None
                self.header_ref.current.update()
        
        if col_name == "index": return

        for container in self.header_ref.current.content.controls:
            if container.content.data["col_name"] == col_name: 
                container.bgcolor = ft.Colors.GREEN_300
            else: container.bgcolor = None

        self.header_ref.current.update()

    def filter_selected(self):
        if not self.selected_filters or not len(self.selected_filters[1]):
            self.records = self.df_manager.data
        else:
            self.records = self.df_manager.fetch_df("filter", self.selected_filters)
        
        self.highlight_col("none", True)
        self._build_content()
        self.update()
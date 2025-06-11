import flet as ft
from components.appbar import AppBar

class TableView(ft.Column):
    def __init__(self):
        super().__init__(spacing=12, scroll="auto", width=500, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER)

        self.container_style = {
            "width" : self.width,
            "bgcolor" : ft.Colors.GREY_900,
            "border_radius" : ft.border_radius.all(12),
            "padding" : ft.padding.all(12),
            "margin" : ft.margin.only(12, 0, 12, 0)
        }

        self.create_controls()
        self.fill_records()

        self.appbar = AppBar(title="Table").build()
        self.table = ListViewTable(self.records, self.update_buttons)

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
                                    self.edit_btn
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_AROUND
                            ),
                            self.table
                        ],
                        expand=True
                    ),
                    expand=True,
                )
            ]
        )
    
    def fill_records(self):
        self.records = [
            [f"type", f"Word number {i}", f"Here goes translation", "Here goes another translation", "Some long sentance goes here", "Some long sentance goes here", "0"]
            for i in range(20)
        ]
    
    def create_controls(self):
        self.delete_btn = ft.ElevatedButton(
            "Delete",
            disabled=True,
            on_click=self.delete_selected,
            bgcolor=ft.Colors.RED_300,
            icon=ft.Icons.DELETE_FOREVER_ROUNDED,
            width=100
        )
        self.edit_btn = ft.ElevatedButton(
            "Edit",
            disabled=True,
            on_click=self.edit_selected,
            bgcolor=ft.Colors.GREY_500,
            icon=ft.Icons.EDIT_ROUNDED,
            width=100
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

    def delete_selected(self, e):
        self.table.delete_selected()

    def edit_selected(self, e):
        self.table.edit_view()


class ListViewTable(ft.ListView):
    def __init__(self, items: list[list[str]], on_selection_changed: callable):
        super().__init__(spacing=10, padding=20, auto_scroll=False, expand=True)
        self.items = items
        self.selected_refs: list[ft.Ref] = []
        self.on_selection_changed = on_selection_changed
        self.build_table()

    def build_table(self):
        self.controls.clear()
        header = ["Type", "German", "Translation", "Translation_2", "Example", "Meaning", "#P"]

        self.controls.append(self._build_row(header, is_header=True))

        for row in self.items:
            ref = ft.Ref[ft.Container]()
            container = self._build_row(row, ref=ref)
            self.controls.append(container)

    def _build_row(self, data: list[str], ref=None, is_header=False):
        column_flexes = [2, 4, 6, 6, 8, 8, 1]
        bgcolor = ft.Colors.GREY_700 if is_header else ft.Colors.GREY
        row = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        value=cell,
                        size=14,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        expand=flex,
                        max_lines=2
                    )
                    for cell, flex in zip(data, column_flexes)
                ],
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
            data={"ref": ref} if ref else None,
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
        for ref in self.selected_refs:
            if ref.current and ref.current in self.controls:
                self.controls.remove(ref.current)
        self.selected_refs.clear()
        self.update()
        self.on_selection_changed(0)

    def edit_view(self):
        print("Edit view called")
        row_data = self.selected_refs[0].current.content.controls
        for cell in row_data:
            print(cell.value)
import flet as ft

class EditDialog(ft.AlertDialog):
    def __init__(self, container: ft.Container | None, on_save: callable = None):
        # If container is None - create Add New view, else - Edit View
        super().__init__(modal=True)
        self.is_edit = bool(container)
        print(self.is_edit)
        self.title = ft.Row(
            controls=[
                ft.Icon(name="EDIT_ROUNDED"),
                ft.Text("Edit record" if self.is_edit else "Create new record")
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        self.content_padding = 40
        self.original_container = container # for edit view case
        self.new_row = { # for new view case
            "type": "",
            "german": "",
            "translation": "",
            "second_translation": "",
            "example": "",
            "meaning": "",
            "score": "",
        }
        self.on_save = on_save

        self.score_options = [-1, 0, 1, 2, 3]
        self.score_btn = ft.CupertinoSlidingSegmentedButton(
            controls=[ft.Text(score) for score in self.score_options]
        )

        self.controls = []
        if self.is_edit: self.create_edit_controls()
        else: self.create_new_controls()
            
        self.content = ft.Column(
            controls=self.controls,
            tight=True,
            spacing=10,
            width=400
        )

        self.actions = [
            ft.TextButton("Cancel", on_click=self.close_dlg),
            ft.ElevatedButton("Save", on_click=self.save_data),
        ]
        self.actions_alignment = ft.MainAxisAlignment.END
        self.on_dismiss = lambda e: print("Modal dialog dismissed!")    

    def create_new_controls(self):
        for col_name in self.new_row.keys():
            if col_name == "score":  
                self.score_btn.selected_index = 1   
                self.controls.append(
                    ft.Row(
                        controls=[
                            ft.Text("Score:", size=18),
                            self.score_btn,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                )
            else:
                self.controls.append(
                    ft.TextField(
                        label=col_name.replace("_", " ").capitalize(),
                        value="", 
                        data={"col_name":col_name})
                )

    def create_edit_controls(self):
        for control in self.original_container.content.controls:
            if control.data["col"] == "score":  
                self.score_btn.selected_index = self.score_options.index(control.value)
                self.controls.append(
                    ft.Row(
                        controls=[
                            ft.Text("Score:", size=18),
                            self.score_btn,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN
                    )
                )
            else:
                self.controls.append(
                    ft.TextField(
                        label=control.data["col"].replace("_", " ").capitalize(), 
                        value=control.value
                    )
                )

    def open_dialog(self, e: ft.ControlEvent):
        if self not in e.page.overlay:
            e.page.overlay.append(self)
        self.open = True
        e.page.update()

    def close_dlg(self, e: ft.ControlEvent):
        self.open = False
        e.page.update()

    def save_data(self, e: ft.ControlEvent):
        if self.is_edit:
            self.save_updated_row()
        else:
            self.save_new_row()

        self.close_dlg(e)

    def save_updated_row(self):
        self.original_container.bgcolor = ft.Colors.GREY
        for original_control, new_control in zip(self.original_container.content.controls, self.controls):
            if isinstance(new_control, ft.Row):
                original_control.value = self.score_options[self.score_btn.selected_index]
            else: original_control.value = new_control.value

        self.original_container.update()
        if self.on_save:
            self.on_save()

    def save_new_row(self):
        for control in self.controls:
            if isinstance(control, ft.Row):
                self.new_row["score"] = self.score_options[self.score_btn.selected_index]
            else: 
                self.new_row[control.data["col_name"]] = control.value

        if self.on_save:
            self.on_save(self.new_row)                
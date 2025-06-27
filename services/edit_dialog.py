import flet as ft

class EditDialog(ft.AlertDialog):
    def __init__(self, container: ft.Container | None, on_save: callable = None):
        # If container is None - create Add New view, else - Edit View
        super().__init__(modal=True)
        self.is_edit = bool(container)
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

        self.alert_msg = ft.Text("Please fill all marked fields", color=ft.Colors.RED, visible=False)
            
        self.content = ft.Column(
            controls=[*self.controls, self.alert_msg,],
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
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        data={"col_name":"score"}
                    )
                )
            else:
                self.controls.append(
                    ft.TextField(
                        label=col_name.replace("_", " ").capitalize(),
                        value=None, 
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
                            self.score_btn
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                        data={"col_name":"score"}
                    )
                )
            else:
                self.controls.append(
                    ft.TextField(
                        label=control.data["col"].replace("_", " ").capitalize(), 
                        value=control.value,
                        data={"col_name":control.data["col"]}
                    )
                )

    def open_dialog(self, e: ft.ControlEvent):
        if self not in e.page.overlay:
            e.page.overlay.clear()
            e.page.overlay.append(self)
        self.open = True
        e.page.dialog_is_open = True
        e.page.update()
        print(f"Dialog called")

    def close_dlg(self, e: ft.ControlEvent):
        self.open = False
        e.page.dialog_is_open = False
        e.page.update()

    def save_data(self, e: ft.ControlEvent):
        if self.is_edit: saved = self.save_updated_row()
        else: saved = self.save_new_row()

        if saved: self.close_dlg(e)

    def save_updated_row(self) -> bool: # Returns save confirmation
        values = []
        for original_control, new_control in zip(self.original_container.content.controls, self.controls):
            if isinstance(new_control, ft.Row):
                original_control.value = self.score_options[self.score_btn.selected_index]
            else: 
                original_control.value = new_control.value
                if new_control.data["col_name"] in ("type", "german"): 
                    values.append(new_control.value)

        if not self.check_important_vals(values=values):
            self.highlight_important_vals()
            return False

        self.original_container.bgcolor = ft.Colors.GREY
        if self.on_save:
            self.on_save(self.original_container.data["ref"])
        return True

    def save_new_row(self) -> bool: # Returns save confirmation
        for control in self.controls:
            if isinstance(control, ft.Row):
                self.new_row["score"] = self.score_options[self.score_btn.selected_index]
            else: 
                self.new_row[control.data["col_name"]] = control.value
        
        if not self.check_important_vals(values=[self.new_row["type"], self.new_row["german"]]):
            self.highlight_important_vals()
            return False

        if self.on_save:
            self.on_save(self.new_row)
        return True

    def check_important_vals(self, values: list) -> bool:
        for value in values:
            if value in ("", " ", "-", None):
                return False
        return True
            
    def highlight_important_vals(self):
        for control in self.controls:
            if control.data["col_name"] in ("type", "german"):
                control.border_color = ft.Colors.RED
        self.alert_msg.visible = True
        self.update()
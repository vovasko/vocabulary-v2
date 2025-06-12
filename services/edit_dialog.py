import flet as ft

class EditDialog(ft.AlertDialog):
    def __init__(self, container: ft.Container, on_save: callable = None):
        super().__init__(modal=True)
        self.title = ft.Row(
            controls=[
                ft.Icon(name="EDIT_ROUNDED"),
                ft.Text("Edit record")
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
        self.content_padding = 40
        self.original_container = container
        self.on_save = on_save

        self.score_options = [-1, 0, 1, 2, 3]
        self.score_btn = ft.CupertinoSlidingSegmentedButton(
            controls=[ft.Text(score) for score in self.score_options]
        )

        self.controls = []
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

    def open_dialog(self, e: ft.ControlEvent):
        if self not in e.page.overlay:
            e.page.overlay.append(self)
        self.open = True
        e.page.update()

    def close_dlg(self, e: ft.ControlEvent):
        self.open = False
        e.page.update()

    def save_data(self, e: ft.ControlEvent):
        print("Saving record:")
        if self.on_save:
            self.on_save()
        self.original_container.bgcolor = ft.Colors.GREY
        for original_control, new_control in zip(self.original_container.content.controls, self.controls):
            if isinstance(new_control, ft.Row):
                original_control.value = self.score_options[self.score_btn.selected_index]
            else: original_control.value = new_control.value
        self.close_dlg(e)
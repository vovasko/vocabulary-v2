import flet as ft

class RefreshButton(ft.IconButton):
    def __init__(self, on_click=None, size=25):
        self._rotation = 0
        self._external_on_click = on_click

        super().__init__(
            icon=ft.Icons.REFRESH_ROUNDED,
            icon_size=size,
            tooltip="Refresh",
            rotate=0,
            animate_rotation=ft.Animation(500, "easeInOut"),
            on_click=self._handle_click
        )

    def _handle_click(self, e):
        self._rotation += 6.3
        self.rotate = self._rotation
        self.disabled = True
        self.update()
        if self._external_on_click:
            self._external_on_click(e)
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

class StateButton(ft.FilledButton):
    def __init__(self, on_click=None, on_click_args=None, active_bgcolor=ft.Colors.GREEN_700, active_color = None, **kwargs):
        # Extract and store user-provided on_click handler
        self._user_on_click = on_click
        self._on_click_args = None if on_click_args == None else on_click_args
        self._active_bgcolor = active_bgcolor
        self._active_color = active_color
        self.selected = False

        super().__init__(**kwargs)

        self._default_bgcolor = self.bgcolor
        self._default_color = self.color
        self.on_click = self._wrapped_on_click

    def _wrapped_on_click(self, e: ft.ControlEvent):
        self.selected = not self.selected
        # Toggle color
        self.bgcolor = self._active_bgcolor if self.selected else self._default_bgcolor
        if self._default_color:
            self.color = self._active_color if self.selected else self._default_color
        self.update()

        # Call the actual user-provided function with its arguments
        if self._user_on_click and self._on_click_args:
            self._user_on_click(e, *self._on_click_args)
        elif self._user_on_click:
            self._user_on_click(e)
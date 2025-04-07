import flet as ft
from models.models import Bank


class SDCardButton(ft.TextButton):
    def __init__(self, sd_dir_picker: ft.FilePicker, sd_path: dict):
        super().__init__(
            text="SD Card",
            width=170,
            height=45,
            tooltip=sd_path["path"],
            on_click=lambda _: sd_dir_picker.get_directory_path(),
            style=ft.ButtonStyle(
                text_style=ft.TextStyle(font_family="VT323", size=24),
                bgcolor={"": "transparent"},
                overlay_color="transparent",
                color={"": ft.Colors.GREY_500, "hovered": ft.Colors.WHITE},
                shadow_color={"hovered": None},
                elevation={"hovered": 2},
                animation_duration=200,
            ),
        )
        self.sd_path = sd_path

    def update_tooltip(self):
        self.tooltip = self.sd_path["path"]


class ExportButton(ft.TextButton):
    def __init__(self, on_click):
        super().__init__(
            text="СПАСИ И СОХРАНИ",
            style=ft.ButtonStyle(
                text_style=ft.TextStyle(font_family="RuslanDisplay", size=24),
                bgcolor={"": "transparent"},
                overlay_color="transparent",
                color={"": ft.Colors.GREY_500, "hovered": ft.Colors.WHITE},
                shadow_color={"hovered": None},
                elevation={"hovered": 2},
                animation_duration=200,
            ),
            width=350,
            height=50,
            on_click=on_click
        )


class BankDropdown(ft.DropdownM2):
    def __init__(self, ref, on_change):
        super().__init__(
            value=Bank.A.value,
            text_style=ft.TextStyle(font_family="VT323", size=24),
            ref=ref,
            border_color="transparent",
            focused_border_color=ft.Colors.GREY_300,
            filled=True,
            color=ft.Colors.GREY_500,
            fill_color="transparent",
            width=80,
            border_radius=5,
            options=[ft.dropdown.Option(b.value) for b in Bank],
            on_change=on_change,
        )
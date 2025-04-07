import flet as ft


def get_button(text: str, on_click_with_event):
    return ft.TextButton(
        text=text,
        width=160,
        height=45,
        on_click=on_click_with_event,
        style=ft.ButtonStyle(
            overlay_color="transparent",
            color={"": ft.Colors.GREY_500, "hovered": ft.Colors.WHITE},
            shadow_color={"hovered": None},
            elevation={"hovered": 2},
            animation_duration=200,
            text_style=ft.TextStyle(font_family="VT323", size=18)
        ),
    )


def alert_modal(page: ft.Page, msg: str, on_close_with_event):
    dlg = ft.CupertinoAlertDialog(
        modal=True,
        title=ft.Text(msg, size=14, text_align=ft.TextAlign.CENTER, font_family="VT323"),
        actions=[
            get_button("Понял", on_close_with_event)
        ]
    )
    return dlg


def confirm_delete_dialog(on_confirm_with_event, on_cancel_with_event, on_checkbox_change):
    return ft.CupertinoAlertDialog(
        modal=True,
        title=ft.Text("Очистить пэд?", size=24, text_align=ft.TextAlign.CENTER, font_family="VT323"),
        actions=[
            get_button("Да", on_confirm_with_event),
            get_button("Нет", on_cancel_with_event),
            ft.Row(
                controls=[
                    ft.Checkbox(
                        label="Я трезв (не спрашивать)",
                        value=False,
                        on_change=on_checkbox_change,
                        label_style=ft.TextStyle(font_family="VT323", size=16, color=ft.Colors.GREY_500),
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER
            )
        ]
    )
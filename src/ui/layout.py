import flet as ft
from core.controller import get_current_pad
from ui.pad import create_pad_ui


def build_pad_grid(pads: list[ft.Container]) -> ft.Column:
    # Построение грида с 4 строками по 4 пэда
    return ft.Column([
        ft.Row(pads[12:16]),
        ft.Row(pads[8:12]),
        ft.Row(pads[4:8]),
        ft.Row(pads[0:4]),
    ], alignment=ft.MainAxisAlignment.CENTER)


def refresh_pads(
    page: ft.Page,
    current_state: dict,
    pad_refs: list,
    pads: list,
    sd_path: dict,
    selected_pad_index: dict,
    confirm_dialog_state: dict,
    file_picker,
    audio_players,
    bank_dropdown,
    sd_folder_btn,
    export_loader,
    export_btn,
    call_alert_modal
):
    pad_refs.clear()
    pads.clear()
    for i in range(16):
        pad = get_current_pad(current_state["bank"], i + 1)
        pads.append(create_pad_ui(
            index=i,
            pad=pad,
            state={
                "confirm_dialog_state": confirm_dialog_state,
                "selected_pad_index": selected_pad_index,
                "sd_path": sd_path
            },
            handlers={
                "call_alert_modal": call_alert_modal,
                "refresh_pads": lambda: refresh_pads(
                    page, current_state, pad_refs, pads, sd_path, selected_pad_index,
                    confirm_dialog_state, file_picker, audio_players,
                    bank_dropdown, sd_folder_btn, export_loader, export_btn,
                    call_alert_modal
                )
            },
            refs={
                "page": page,
                "pad_refs": pad_refs,
                "audio_players": audio_players,
                "file_picker": file_picker
            }
        ))

    page.controls.clear()
    page.add(
        ft.Column([
            ft.Row([bank_dropdown, sd_folder_btn, export_loader]),
            build_pad_grid(pads),
            ft.Row([export_btn], alignment=ft.alignment.center)
        ], alignment=ft.MainAxisAlignment.CENTER),
    )

    page.update()
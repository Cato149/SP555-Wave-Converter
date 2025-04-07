import asyncio
from pathlib import Path

import flet as ft
from models.models import Bank
from core.bindings import scan_existing_bindings
from core.export import export_all_pads
from ui.layout import refresh_pads
from ui.controls import SDCardButton, ExportButton, BankDropdown
from ui.dialogs import alert_modal

def main(page: ft.Page):
    page.title = "The New SP-555 Wave Converter"
    page.fonts = {
        "VT323": "/fonts/Handjet-Regular.ttf",
        "Orbitron": "/fonts/Orbitron-Regular.ttf",
        "RuslanDisplay": "/fonts/RuslanDisplay-Regular.ttf"
    }
    page.window.resizable = False
    page.window.height = 525
    page.window.width = 370
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER

    # === Состояния приложения ===
    current_state = {"bank": Bank.A}
    selected_pad_index = {"index": None}
    confirm_dialog_state = {"show": True}
    sd_path = {"path": None}

    # === UI сущности ===
    file_picker = ft.FilePicker()
    sd_dir_picker = ft.FilePicker()
    export_loader = ft.ProgressRing(visible=False)
    pad_refs = []
    pads = []
    audio_players = {}

    # === Элементы управления ===
    bank_select = BankDropdown(ref=ft.Ref[ft.Dropdown](), on_change=lambda e: on_bank_change(e))
    sd_folder_btn = SDCardButton(sd_dir_picker, sd_path)
    export_btn = ExportButton(on_click=lambda e: convert_and_export(e))

    page.overlay.extend([file_picker, sd_dir_picker])

    # === Вспомогательные функции ===

    def call_alert_modal(e, msg: str):
        def close_alert(_):
            page.close(dlg_alert)

        dlg_alert = alert_modal(page, msg, on_close_with_event=close_alert)
        page.open(dlg_alert)

    def on_file_selected(e: ft.FilePickerResultEvent):
        if e.files and selected_pad_index["index"] is not None:
            from core.controller import get_current_pad
            pad_index = selected_pad_index["index"]
            pad = get_current_pad(current_state["bank"], pad_index + 1)
            pad.file_path = Path(e.files[0].path)
            pad.is_playing = False
            pad.special_marker = False
            refresh()

    file_picker.on_result = on_file_selected

    def on_sd_dir_selected(e: ft.FilePickerResultEvent):
        if e.path:
            sd_path["path"] = e.path
            refresh()

            async def delayed_scan():
                await asyncio.sleep(0.1)
                scan_existing_bindings(Path(e.path))
                refresh()

            page.run_task(delayed_scan)

        sd_folder_btn.update_tooltip()

    sd_dir_picker.on_result = on_sd_dir_selected

    def convert_and_export(e):
        if not sd_path["path"]:
            page.open(ft.SnackBar(
                ft.Text("Пожалуйста, выберите SD-карту перед экспортом",
                        color=ft.Colors.WHITE,
                        font_family="VT323",
                        size=18
                        ),
                bgcolor=ft.Colors.RED_900
            ))
            return

        export_loader.visible = True
        page.update()

        export_all_pads(Path(sd_path["path"]))

        export_loader.visible = False
        page.open(ft.SnackBar(
            ft.Text("Экспорт завершён ✅", color=ft.Colors.WHITE, font_family="VT323"),
            bgcolor=ft.Colors.BLACK
        ))
        page.update()

    def on_bank_change(e):
        current_state["bank"] = Bank(e.control.value)
        refresh()

    def refresh():
        refresh_pads(
            page=page,
            current_state=current_state,
            pad_refs=pad_refs,
            pads=pads,
            sd_path=sd_path,
            selected_pad_index=selected_pad_index,
            confirm_dialog_state=confirm_dialog_state,
            file_picker=file_picker,
            audio_players=audio_players,
            bank_dropdown=bank_select,
            sd_folder_btn=sd_folder_btn,
            export_loader=export_loader,
            export_btn=export_btn,
            call_alert_modal=call_alert_modal
        )

    # === Начальный рендер ===
    refresh()

ft.app(target=main, assets_dir="assets")

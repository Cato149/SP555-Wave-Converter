import asyncio
from pathlib import Path
import flet as ft
import re

from logic.audio_converter import convert_to_wav
from models.models import Pad, Bank
from ui.sampler import PadBank

pad_bank = {
    Bank.A: PadBank(),
    Bank.B: PadBank(),
    Bank.C: PadBank(),
    Bank.D: PadBank(),
    Bank.E: PadBank(),
    Bank.F: PadBank()
}

pad_refs_map = {bank: [ft.Ref[ft.Container]() for _ in range(16)] for bank in Bank}

def get_pad_by_global_id(global_id: int) -> tuple[Bank, Pad]:
    bank_index = (global_id - 1) // 16
    pad_index = (global_id - 1) % 16
    banks = [Bank.A, Bank.B, Bank.C, Bank.D, Bank.E, Bank.F]
    if 0 <= bank_index < len(banks):
        bank = banks[bank_index]
        pad = pad_bank[bank].get_pad(pad_index + 1)
        return bank, pad
    return None, None

def get_pad_by_wav_filename(filename: str) -> tuple[Bank, Pad]:
    match = re.match(r"(C|D|E|F)_(\d{2})\.WAV", filename.upper())
    if match:
        bank_char, pad_num = match.group(1), int(match.group(2))
        try:
            bank = Bank[bank_char]
            pad = pad_bank[bank].get_pad(pad_num)
            return bank, pad
        except:
            return None, None
    return None, None

def update_pad_ui(bank: Bank, pad_index: int):
    pad = pad_bank[bank].get_pad(pad_index + 1)
    ref = pad_refs_map[bank][pad_index]
    tooltip = str(pad.file_path.name) if pad.is_occupied else ""
    bgcolor = ft.Colors.ORANGE if getattr(pad, "special_marker", False) \
        else ft.Colors.RED_700 if pad.is_occupied \
        else ft.Colors.GREY_300
    if ref.current:
        ref.current.bgcolor = bgcolor
        ref.current.tooltip = tooltip
        ref.current.update()


def scan_existing_bindings(sd_path: Path):
    sp555_dir = sd_path / "ROLAND" / "SP555"

    for bank in pad_bank.values():
        for pad in bank.pads:
            pad.file_path = None
            pad.is_playing = False
            pad.special_marker = False

    if not sp555_dir.exists():
        return

    pattern_spd = re.compile(r"SMP(\d{4})([A-Z]*)\.SPD")
    wav_pattern = re.compile(r"(C|D|E|F)_\d{2}\.WAV", re.IGNORECASE)
    pad_flags = {}

    for file in sp555_dir.iterdir():
        if file.suffix.upper() == ".SPD":
            match = pattern_spd.match(file.name.upper())
            if match:
                number = int(match.group(1))
                pad_id = number
                bank, pad = get_pad_by_global_id(pad_id)
                print(bank, pad)
                if pad:
                    pad_flags.setdefault((bank, pad.pad_id), []).append(file)
        elif file.suffix.upper() == ".WAV" and wav_pattern.match(file.name):
            bank, pad = get_pad_by_wav_filename(file.name)
            if pad:
                pad.file_path = file
                pad.special_marker = False
                pad.is_playing = False
                update_pad_ui(bank, pad.pad_id - 1)

    for (bank, pad_id), files in pad_flags.items():
        pad = pad_bank[bank].get_pad(pad_id)
        if len(files) >= 2:
            pad.file_path = None
            pad.special_marker = True
            update_pad_ui(bank, pad.pad_id - 1)


def main(page: ft.Page):
    page.title = "The New SP-555 Wave Converter"
    page.fonts = {
        "VT323": ""
    }
    page.window.resizable = False
    page.window.height = 525
    page.window.width = 370
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.MainAxisAlignment.CENTER

    current_bank = ft.Ref[ft.Dropdown]()
    pad_refs = []
    pads = []
    current_state = {"bank": Bank.A}
    selected_pad_index = {"index": None}
    confirm_dialog_state = {"show": True}
    sd_path = {"path": None}
    file_picker = ft.FilePicker()
    sd_dir_picker = ft.FilePicker()
    export_loader = ft.ProgressRing(visible=False)
    audio_players = {}

    page.overlay.extend([file_picker, sd_dir_picker])

    def call_alert_modal(e, msg: str):
        dlg_alert = ft.CupertinoAlertDialog(
            modal=True,
            title=ft.Text(msg, size=14, text_align=ft.TextAlign.CENTER, font_family="VT323"),
            # bgcolor=ft.Colors.GREY_900,
            # actions_alignment=ft.MainAxisAlignment.CENTER,
            actions=[
                ft.TextButton(
                    text="Понял",
                    width=160,
                    height=45,
                    tooltip=sd_path["path"],
                    on_click=lambda _: page.close(dlg_alert),
                    style=ft.ButtonStyle(
                        overlay_color="transparent",  # отключаем ripple-эффект
                        color={
                            "": ft.colors.GREY_500,  # обычное состояние
                            "hovered": ft.colors.WHITE,  # светящийся цвет
                        },
                        shadow_color={"hovered": None},
                        elevation={"hovered": 2},
                        animation_duration=200,
                    ),
                )
            ]
        )
        page.open(dlg_alert)


    def get_current_pad(pad_id: int) -> Pad:
        return pad_bank[current_state["bank"]].get_pad(pad_id)

    def on_file_selected(e: ft.FilePickerResultEvent):
        if e.files and selected_pad_index["index"] is not None:
            pad_index = selected_pad_index["index"]
            pad = get_current_pad(pad_index + 1)
            pad.file_path = Path(e.files[0].path)
            pad.is_playing = False
            pad.special_marker = False
            refresh_pads()

    file_picker.on_result = on_file_selected

    def on_sd_dir_selected(e: ft.FilePickerResultEvent):
        if e.path:
            sd_path["path"] = e.path
            refresh_pads()

            async def delayed_scan():
                await asyncio.sleep(0.1)
                scan_existing_bindings(Path(e.path))
                refresh_pads()
                page.update()

            page.run_task(delayed_scan)

        sd_folder_btn.tooltip = sd_path["path"]
        sd_folder_btn.update()

    sd_dir_picker.on_result = on_sd_dir_selected

    def convert_and_export(e):
        if not sd_path["path"]:
            page.open(ft.SnackBar(
                ft.Text("Пожалуйста, выберите SD-карту перед экспортом", color=ft.Colors.WHITE, font_family="VT323"),
                bgcolor=ft.Colors.BLACK)
            )
            return

        export_dir = Path(sd_path["path"]) / "ROLAND" / "SP555"
        export_loader.visible = True
        page.update()

        for bank, bank_data in pad_bank.items():
            for pad in bank_data.pads:
                if pad.file_path and pad.file_path.exists():
                    filename = f"{bank.name}_{str(pad.pad_id).zfill(2)}.WAV"
                    output_path = export_dir / filename
                    try:
                        convert_to_wav(pad.file_path, output_path)
                    except Exception as ex:
                        print(f"Failed to convert {pad.pad_id}: {ex}")

        export_loader.visible = False
        page.open(ft.SnackBar(ft.Text(
                "Экспорт завершён ✅",
                color=ft.Colors.WHITE,
                font_family="VT323"),
            bgcolor=ft.Colors.BLACK))
        page.update()

    def refresh_pads():
        pads.clear()
        pad_refs.clear()
        for i in range(16):
            pads.append(create_pad_ui(i))

        page.controls.clear()
        page.add(
            ft.Column([
                ft.Row([current_bank.current, sd_folder_btn, export_loader]),
                ft.Row(pads[12:16]),
                ft.Row(pads[8:12]),
                ft.Row(pads[4:8]),
                ft.Row(pads[0:4]),
            ], alignment=ft.MainAxisAlignment.CENTER),
        )
        page.add(
            ft.Column([
                ft.Row([export_btn])
            ], alignment=ft.alignment.center)
        )
        page.update()

    def on_bank_change(e):
        current_state["bank"] = Bank(e.control.value)
        refresh_pads()

    def create_pad_ui(index: int):
        pad_ref = ft.Ref[ft.Container]()
        pad = get_current_pad(index + 1)

        def handle_close(e):
            page.close(dlg_delete)

        def confirm_delete(e):
            delete_pad(e)
            handle_close(e)

        dlg_delete = ft.CupertinoAlertDialog(
            modal=True,
            title=ft.Text("Очистить пэд?", size=14, text_align=ft.TextAlign.CENTER, font_family="VT323"),
            actions=[
                ft.CupertinoButton("Да", on_click=confirm_delete, color=ft.Colors.WHITE),
                ft.CupertinoButton("Нет", on_click=handle_close, color=ft.Colors.WHITE),
                ft.CupertinoCheckbox(
                    label="Я трезв (не спрашивать)",
                    value=False,
                    on_change=lambda e: confirm_dialog_state.update({"show": not e.control.value}))
            ]
        )

        def delete_pad(e):
            if pad.is_occupied or getattr(pad, "special_marker", False):
                pad.file_path = None
                pad.is_playing = False
                pad.special_marker = False
                if index in audio_players:
                    audio_players.pop(index)
                refresh_pads()

        def toggle_play_stop():
            if not pad.file_path or not pad.file_path.exists() or getattr(pad, "special_marker", False):
                return

            if pad.is_playing:
                player = audio_players.get(index)
                if player:
                    player.pause()
                pad.is_playing = False
            else:
                player = ft.Audio(src=str(pad.file_path), autoplay=True)
                audio_players[index] = player
                page.overlay.append(player)
                page.update()
                pad.is_playing = True

            refresh_pads()

        def on_click(e):
            if getattr(pad, "special_marker", False):
                return

            if not sd_path["path"]:
                call_alert_modal(e, "Карта памяти не выбрана")
                return

            if not pad.is_occupied:
                selected_pad_index["index"] = index
                file_picker.pick_files(
                    allow_multiple=False,
                    allowed_extensions=["wav", "mp3", "flac", "ogg", "aiff", "m4a"]
                )
            else:
                toggle_play_stop()

        def on_long_press(e):
            if confirm_dialog_state["show"] is False:
                delete_pad(e)
            if pad.is_occupied or getattr(pad, "special_marker", False):
                page.open(dlg_delete)
                page.update()

        tooltip = str(pad.file_path.name) if pad.is_occupied else ""
        bgcolor = ft.Colors.ORANGE_900 if getattr(pad, "special_marker", False) \
            else ft.Colors.RED_500 if pad.is_playing \
            else ft.Colors.RED_700 if pad.is_occupied \
            else ft.Colors.GREY_300

        shadow = ft.BoxShadow(
            spread_radius=3, blur_radius=8, color=ft.Colors.RED_400, offset=ft.Offset(0, 0)
        ) if pad.is_playing else None

        container = ft.Container(
            ref=pad_ref,
            content=ft.Text(str(pad.pad_id), size=20, color=ft.Colors.BLACK, font_family="Orbitron"),
            width=80,
            height=80,
            bgcolor=bgcolor,
            alignment=ft.alignment.center,
            border_radius=5,
            shadow=shadow,
            on_click=on_click,
            on_long_press=on_long_press,
            tooltip=tooltip,
        )

        pad_refs.append(pad_ref)

        return container

    bank_select = ft.Dropdown(
        value=Bank.A.value,
        trailing_icon=None,
        menu_width=80,
        focused_bgcolor=ft.colors.GREY_200,
        item_height=80,
        ref=current_bank,
        border_color=None,
        filled=True,
        alignment=ft.alignment.center,
        color=ft.Colors.BLACK,
        fill_color=ft.colors.GREY_300,
        width=80,
        border_radius=5,
        options=[
            ft.dropdown.Option(Bank.A.value),
            ft.dropdown.Option(Bank.B.value),
            ft.dropdown.Option(Bank.C.value),
            ft.dropdown.Option(Bank.D.value),
            ft.dropdown.Option(Bank.E.value),
            ft.dropdown.Option(Bank.F.value),
        ],
        on_change=on_bank_change
    )

    sd_folder_btn = ft.TextButton(
        text="SD Card",
        width=170,
        height=45,
        tooltip=sd_path["path"],
        on_click=lambda _: sd_dir_picker.get_directory_path(),
        style=ft.ButtonStyle(
            text_style=ft.TextStyle(font_family="VT323"),
            bgcolor={"": "transparent"},  # без фона
            overlay_color="transparent",  # отключаем ripple-эффект
            color={
                "": ft.colors.GREY_500,  # обычное состояние
                "hovered": ft.colors.WHITE,  # светящийся цвет
            },
            shadow_color={"hovered": None},
            elevation={"hovered": 2},
            animation_duration=200,
        ),
    )

    export_btn = ft.TextButton(
        text="СПАСИ И СОХРАНИ",
        style=ft.ButtonStyle(
            text_style=ft.TextStyle(font_family="RuslanDisplay"),
            bgcolor={"": "transparent"},  # без фона
            overlay_color="transparent",  # отключаем ripple-эффект
            color={
                "": ft.colors.GREY_500,  # обычное состояние
                "hovered": ft.colors.WHITE,  # светящийся цвет
            },
            shadow_color={"hovered": None},
            elevation={"hovered": 2},
            animation_duration=200,
        ),
        width=350,
        height=50,
        on_click=convert_and_export
    )

    refresh_pads()

    page.add(
        ft.Stack([
            # 1. Фон-картинка
            ft.Image(
                src="assets/bg.png",  # или путь в assets_dir
                width=page.width,
                height=page.height,
                fit=ft.ImageFit.COVER
            ),
            ft.Container(
                width=page.width,
                height=page.height,
                gradient=ft.LinearGradient(
                    begin=ft.alignment.top_center,
                    end=ft.alignment.bottom_center,
                    colors=[ft.colors.with_opacity(0.3, ft.colors.BLACK), ft.colors.with_opacity(0.6, ft.colors.BLACK)]
                ),
                blur=ft.Blur(5, 5),
            )
        ])
    )


ft.app(target=main, assets_dir="assets")

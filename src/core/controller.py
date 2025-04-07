import re
import flet as ft
from models.models import Bank, Pad
from ui.sampler import PadBank

# Глобальные банки
pad_bank = {bank: PadBank() for bank in Bank}
pad_refs_map = {bank: [ft.Ref[ft.Container]() for _ in range(16)] for bank in Bank}


def get_pad_by_global_id(global_id: int) -> tuple[Bank, Pad] | tuple[None, None]:
    bank_index = (global_id - 1) // 16
    pad_index = (global_id - 1) % 16
    banks = list(Bank)
    if 0 <= bank_index < len(banks):
        bank = banks[bank_index]
        pad = pad_bank[bank].get_pad(pad_index + 1)
        return bank, pad
    return None, None


def get_pad_by_wav_filename(filename: str) -> tuple[Bank, Pad] | tuple[None, None]:
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


def get_current_pad(bank: Bank, pad_id: int) -> Pad:
    return pad_bank[bank].get_pad(pad_id)

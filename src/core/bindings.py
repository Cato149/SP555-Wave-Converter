import re
from pathlib import Path
from core.controller import pad_bank, update_pad_ui, get_pad_by_global_id, get_pad_by_wav_filename

def scan_existing_bindings(sd_path: Path):
    sp555_dir = sd_path / "ROLAND" / "SP555"

    # Очистка всех пэдов перед сканированием
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
                bank, pad = get_pad_by_global_id(number)
                if pad:
                    pad_flags.setdefault((bank, pad.pad_id), []).append(file)

        elif file.suffix.upper() == ".WAV" and wav_pattern.match(file.name):
            bank, pad = get_pad_by_wav_filename(file.name)
            if pad:
                pad.file_path = file
                pad.special_marker = False
                pad.is_playing = False
                update_pad_ui(bank, pad.pad_id - 1)

    # Обработка конфликтов
    for (bank, pad_id), files in pad_flags.items():
        pad = pad_bank[bank].get_pad(pad_id)
        if len(files) >= 2:
            pad.file_path = None
            pad.special_marker = True
            update_pad_ui(bank, pad.pad_id - 1)
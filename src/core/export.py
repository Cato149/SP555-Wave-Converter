from pathlib import Path
from core.controller import pad_bank
from utils.audio_converter import convert_to_wav

def export_all_pads(sd_path: Path):
    export_dir = sd_path / "ROLAND" / "SP555"
    export_dir.mkdir(parents=True, exist_ok=True)

    for bank, bank_data in pad_bank.items():
        for pad in bank_data.pads:
            if pad.file_path and pad.file_path.exists():
                filename = f"{bank.name}_{str(pad.pad_id).zfill(2)}.WAV"
                output_path = export_dir / filename
                try:
                    convert_to_wav(pad.file_path, output_path)
                except Exception as ex:
                    print(f"[Export Error] Failed to convert pad {pad.pad_id}: {ex}")
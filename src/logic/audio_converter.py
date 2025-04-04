import json
import subprocess
import platform
from pathlib import Path

system = platform.system()
machine = platform.machine().lower()

BASE_DIR = Path(__file__).resolve().parent.parent
BIN_DIR = BASE_DIR / "bin"

if system == "Windows":
    FFMPEG_PATH = BIN_DIR / "ffmpeg.exe"
elif system == "Darwin":  # macOS
    if "arm" in machine or "apple" in machine:
        FFMPEG_PATH = BIN_DIR / "ffmpeg-macos-arm64"
    else:
        FFMPEG_PATH = BIN_DIR / "ffmpeg-macos-x86_64"
elif system == "Linux":
    FFMPEG_PATH = BIN_DIR / "ffmpeg"
else:
    raise RuntimeError("Unsupported OS for ffmpeg")


def get_audio_channels(input_path: Path) -> int:
    """Определяет количество каналов (1 = моно, 2 = стерео) через ffprobe"""
    try:
        result = subprocess.run(
            [str(FFMPEG_PATH).replace("ffmpeg", "ffprobe"),
             "-v", "error",
             "-select_streams", "a:0",
             "-show_entries", "stream=channels",
             "-of", "json",
             str(input_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True
        )
        info = json.loads(result.stdout)
        return info["streams"][0].get("channels", 2)
    except Exception as e:
        print(f"Failed to detect channels for {input_path}: {e}")
        return 2


def convert_to_wav(input_path: Path, output_path: Path):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    channels = get_audio_channels(input_path)
    subprocess.run([
        str(FFMPEG_PATH), "-y",
        "-i", str(input_path),
        "-ar", "44100",
        "-ac", str(channels),
        "-sample_fmt", "s16",
        str(output_path)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

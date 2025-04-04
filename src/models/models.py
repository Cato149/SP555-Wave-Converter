from pydantic import BaseModel
from typing import Optional
from pathlib import Path
from enum import Enum


class Bank(str, Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'
    F = 'F'


class Pad(BaseModel):
    special_marker: bool = False
    is_playing: bool = False
    pad_id: int
    file_path: Optional[Path] = None

    @property
    def is_occupied(self) -> bool:
        return self.file_path is not None

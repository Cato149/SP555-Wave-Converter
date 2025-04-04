from typing import List

from models.models import Pad


class PadBank:
    def __init__(self):
        self.pads: List[Pad] = [Pad(pad_id=i + 1) for i in range(16)]

    def get_pad(self, pad_id: int) -> Pad:
        pad = next((pad for pad in self.pads if pad.pad_id == pad_id), None)
        if pad is None:
            raise ValueError(f"Pad with id {pad_id} not found")
        return pad

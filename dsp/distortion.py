"""Distortion effect skeleton."""

from __future__ import annotations


class Distortion:
    """Soft clipping distortion processor."""

    def __init__(self, drive: float = 1.0) -> None:
        self.drive = drive

    def process_block(self, x):
        """Apply distortion to an input block."""
        return x

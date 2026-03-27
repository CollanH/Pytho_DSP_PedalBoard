"""Gain effect skeleton."""

from __future__ import annotations


class Gain:
    """Simple linear gain processor."""

    def __init__(self, gain: float = 1.0) -> None:
        self.gain = gain

    def process_block(self, x):
        """Apply gain to an input block."""
        return x * self.gain

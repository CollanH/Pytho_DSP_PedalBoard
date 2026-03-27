"""Core DSP processing engine interface."""

from __future__ import annotations


class DSPEngine:
    """Top-level DSP engine that processes audio blocks."""

    def __init__(self) -> None:
        self.enabled = True

    def process_block(self, x):
        """Process one block of audio samples.

        Args:
            x: Input block (typically 1-D or 2-D numeric array-like).

        Returns:
            Processed audio block with same shape as ``x``.
        """
        return x


def process_block(x):
    """Stable module-level DSP entry point for block processing."""
    return DSPEngine().process_block(x)

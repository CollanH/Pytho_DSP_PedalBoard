"""Core DSP processing engine interface."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any


Processor = Callable[[Any], Any]


class DSPEngine:
    """Top-level DSP engine that processes audio blocks."""

    def __init__(self, processor: Processor | None = None) -> None:
        self._processor = processor

    def set_processor(self, processor: Processor) -> None:
        """Inject a processing function used by :meth:`process_block`."""
        self._processor = processor

    def process_block(self, x: Any) -> Any:
        """Process one block of audio samples.

        Args:
            x: Input block (typically 1-D or 2-D numeric array-like).

        Returns:
            Processed audio block with the same shape contract as ``x``.
        """
        if self._processor is None:
            return x
        return self._processor(x)


_default_engine = DSPEngine()


def process_block(x: Any) -> Any:
    """Stable module-level DSP entry point for block processing."""
    return _default_engine.process_block(x)

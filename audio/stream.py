"""Audio streaming interfaces and callback contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class StreamConfig:
    """Configuration for opening an audio stream."""

    sample_rate: int
    block_size: int
    channels: int = 1


class StreamCallback(Protocol):
    """Callable audio callback contract.

    Implementations receive an input block and must return an output block with
    matching shape/dtype, suitable for low-latency real-time processing.
    """

    def __call__(self, input_block):
        """Process one audio block and return output samples."""


class AudioStream:
    """Minimal stream abstraction used by the DSP engine."""

    def __init__(self, config: StreamConfig, callback: StreamCallback) -> None:
        self.config = config
        self.callback = callback

    def start(self) -> None:
        """Start audio capture/playback."""

    def stop(self) -> None:
        """Stop audio capture/playback."""

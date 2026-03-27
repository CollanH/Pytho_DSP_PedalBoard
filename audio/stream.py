"""Audio streaming interfaces and callback contracts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True)
class StreamConfig:
    """Configuration for opening an audio stream."""

    sample_rate: int
    block_size: int
    input_channels: int = 1
    output_channels: int = 1


class StreamCallback(Protocol):
    """Real-time stream callback contract.

    The callback must be non-blocking and return a tuple with:
      - output_block: audio samples to write to output device
      - continue_stream: ``True`` to keep streaming, ``False`` to request stop
    """

    def __call__(
        self,
        input_block: Any,
        frame_count: int,
        time_info: dict[str, float] | None,
        status_flags: int,
    ) -> tuple[Any, bool]:
        """Process one audio block and indicate whether stream should continue."""


class AudioStream:
    """Minimal stream abstraction used by the DSP engine."""

    def __init__(self, config: StreamConfig, callback: StreamCallback) -> None:
        self.config = config
        self.callback = callback
        self.running = False

    def start(self) -> None:
        """Start audio capture/playback."""
        self.running = True

    def stop(self) -> None:
        """Stop audio capture/playback."""
        self.running = False

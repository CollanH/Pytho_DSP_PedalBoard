"""Audio device discovery and selection interfaces."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AudioDeviceInfo:
    """Information describing an input/output audio device."""

    name: str
    index: int
    max_input_channels: int
    max_output_channels: int


def list_devices() -> list[AudioDeviceInfo]:
    """Return available audio devices."""
    return []

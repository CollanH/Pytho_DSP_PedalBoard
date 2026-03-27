"""Waveform visualization skeleton."""

from __future__ import annotations


class WaveformView:
    """Render time-domain audio data."""

    def update(self, x) -> None:
        """Update waveform with latest audio samples."""

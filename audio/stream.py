"""Real-time sounddevice stream integration for ``dsp.engine.process_block``."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import numpy as np
import sounddevice as sd

from .device import validate_stream_config


@dataclass
class DSPAudioStream:
    """Bidirectional stream that processes input blocks through ``dsp.engine``."""

    dsp: Any
    blocksize: int
    input_channels: int = 1
    output_channels: int = 1
    samplerate: Optional[int] = None
    input_device: Optional[int | str] = None
    output_device: Optional[int | str] = None
    dtype: str = "float32"

    _stream: Optional[sd.Stream] = field(default=None, init=False, repr=False)
    _overflow_count: int = field(default=0, init=False)
    _underflow_count: int = field(default=0, init=False)

    def start(self) -> None:
        in_idx, out_idx, rate = validate_stream_config(
            input_device=self.input_device,
            output_device=self.output_device,
            input_channels=self.input_channels,
            output_channels=self.output_channels,
            samplerate=self.samplerate,
            dtype=self.dtype,
        )
        self.samplerate = rate

        self._stream = sd.Stream(
            samplerate=self.samplerate,
            blocksize=self.blocksize,
            dtype=self.dtype,
            channels=(self.input_channels, self.output_channels),
            device=(in_idx, out_idx),
            callback=self._callback,
        )
        self._stream.start()

    def stop(self) -> None:
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

    @property
    def xruns(self) -> tuple[int, int]:
        return self._overflow_count, self._underflow_count

    # NOTE: callback must remain realtime-safe:
    # - no plotting
    # - no blocking calls
    # - no per-block large allocations
    # - no prints/logging in callback path
    def _callback(
        self,
        indata: np.ndarray,
        outdata: np.ndarray,
        frames: int,
        _time: sd.CallbackFlags,
        status: sd.CallbackFlags,
    ) -> None:
        if status.input_overflow:
            self._overflow_count += 1
        if status.output_underflow:
            self._underflow_count += 1

        if frames != self.blocksize:
            # Avoid allocating in exceptional path where host blocksize differs.
            outdata.fill(0)
            return

        # Process block with user DSP engine.
        processed = self.dsp.engine.process_block(indata)

        # Copy into stream-owned output buffer without new large allocations.
        if processed is None:
            outdata.fill(0)
            return

        np.copyto(outdata, processed, casting="unsafe")

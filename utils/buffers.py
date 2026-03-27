"""Thread-safe audio snapshot buffers.

This module provides a lock-safe deque-based buffer for moving audio snapshots
from a real-time audio callback thread to a UI thread.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
import threading
from typing import Deque, Optional

import numpy as np


@dataclass(frozen=True)
class AudioSnapshot:
    """Container for a single audio snapshot."""

    samples: np.ndarray
    sample_rate: float


class AudioSnapshotBuffer:
    """Lock-safe bounded buffer for transferring audio snapshots.

    The audio thread should call :meth:`push` with a short NumPy array copy of
    the audio frame(s). The UI thread periodically calls :meth:`pop_latest` to
    consume only the most recent frame, naturally dropping stale snapshots when
    the UI cannot keep up.
    """

    def __init__(self, max_snapshots: int = 8) -> None:
        if max_snapshots <= 0:
            raise ValueError("max_snapshots must be > 0")
        self._buffer: Deque[AudioSnapshot] = deque(maxlen=max_snapshots)
        self._lock = threading.Lock()

    def push(self, samples: np.ndarray, sample_rate: float) -> None:
        """Push a snapshot into the buffer.

        Parameters
        ----------
        samples:
            Audio samples for one visualization frame. A copy is always made so
            the producer can safely reuse or mutate its source buffer.
        sample_rate:
            Sample rate in Hz used to derive axis values in the UI.
        """

        frozen = np.array(samples, dtype=np.float32, copy=True).reshape(-1)
        snapshot = AudioSnapshot(samples=frozen, sample_rate=float(sample_rate))
        with self._lock:
            self._buffer.append(snapshot)

    def pop_latest(self) -> Optional[AudioSnapshot]:
        """Pop and return the newest snapshot, dropping older buffered data."""

        with self._lock:
            if not self._buffer:
                return None
            latest = self._buffer[-1]
            self._buffer.clear()
            return latest

    def clear(self) -> None:
        """Remove all pending snapshots."""

        with self._lock:
            self._buffer.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._buffer)

"""Time-domain waveform visualization for audio snapshots."""

from __future__ import annotations

from typing import Optional

import numpy as np
import pyqtgraph as pg

from utils.buffers import AudioSnapshotBuffer

try:  # Qt binding compatibility
    from PySide6 import QtCore, QtWidgets
except ImportError:  # pragma: no cover
    try:
        from PyQt6 import QtCore, QtWidgets  # type: ignore
    except ImportError:  # pragma: no cover
        from PyQt5 import QtCore, QtWidgets  # type: ignore


class WaveformPlotWidget(pg.PlotWidget):
    """Plot widget that renders audio in the time domain."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)
        self.setBackground("k")
        self.showGrid(x=True, y=True, alpha=0.2)
        self.setLabel("left", "Amplitude")
        self.setLabel("bottom", "Time", units="s")
        self.setYRange(-1.05, 1.05)
        self._curve = self.plot(pen=pg.mkPen("#3daee9", width=2))

    def update_snapshot(self, samples: np.ndarray, sample_rate: float) -> None:
        """Render one audio snapshot."""

        if samples.size == 0 or sample_rate <= 0:
            self._curve.setData([], [])
            return
        x = np.arange(samples.size, dtype=np.float32) / float(sample_rate)
        self._curve.setData(x, samples)


class WaveformBufferUpdater(QtCore.QObject):
    """UI-thread updater that pulls snapshots from a shared buffer with QTimer."""

    def __init__(
        self,
        buffer: AudioSnapshotBuffer,
        widget: WaveformPlotWidget,
        interval_ms: int = 33,
        parent: Optional[QtCore.QObject] = None,
    ) -> None:
        super().__init__(parent)
        self._buffer = buffer
        self._widget = widget
        self._timer = QtCore.QTimer(self)
        self._timer.setInterval(int(interval_ms))
        self._timer.timeout.connect(self._on_timeout)

    def start(self) -> None:
        """Start periodic updates (runs in the UI thread)."""

        self._timer.start()

    def stop(self) -> None:
        """Stop periodic updates."""

        self._timer.stop()

    @QtCore.Slot()
    def _on_timeout(self) -> None:
        snapshot = self._buffer.pop_latest()
        if snapshot is None:
            return
        self._widget.update_snapshot(snapshot.samples, snapshot.sample_rate)

"""Frequency-domain magnitude spectrum visualization."""

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


class SpectrumPlotWidget(pg.PlotWidget):
    """Plot widget that renders FFT magnitude from audio snapshots."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent=parent)
        self.setBackground("k")
        self.showGrid(x=True, y=True, alpha=0.2)
        self.setLabel("left", "Magnitude", units="dB")
        self.setLabel("bottom", "Frequency", units="Hz")
        self.setLogMode(x=False, y=False)
        self._curve = self.plot(pen=pg.mkPen("#f0b429", width=2))

    def update_snapshot(self, samples: np.ndarray, sample_rate: float) -> None:
        """Compute and render FFT magnitude for one audio snapshot."""

        if samples.size == 0 or sample_rate <= 0:
            self._curve.setData([], [])
            return

        window = np.hanning(samples.size)
        windowed = samples * window
        spectrum = np.fft.rfft(windowed)
        mag = np.abs(spectrum)
        mag_db = 20.0 * np.log10(np.maximum(mag, 1.0e-12))
        freqs = np.fft.rfftfreq(samples.size, d=1.0 / float(sample_rate))
        self._curve.setData(freqs, mag_db)


class SpectrumBufferUpdater(QtCore.QObject):
    """UI-thread updater that pulls snapshots from a shared buffer with QTimer."""

    def __init__(
        self,
        buffer: AudioSnapshotBuffer,
        widget: SpectrumPlotWidget,
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

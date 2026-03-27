"""Application bootstrap for the Python DSP pedalboard UI."""

from __future__ import annotations

import logging
import os
import queue
import signal
import sys
from dataclasses import dataclass
from typing import Any, Protocol


class AudioStream(Protocol):
    """Minimal protocol for stream lifecycle management."""

    def start(self) -> None:
        """Start the audio stream."""

    def stop(self) -> None:
        """Stop the audio stream."""


class AudioEngine(Protocol):
    """Protocol for the runtime audio engine."""

    def open_stream(self, *, input_device: str | None, output_device: str | None) -> AudioStream:
        """Create an audio stream for the selected devices."""


@dataclass(frozen=True)
class AudioDeviceSelection:
    """Input/output device defaults used during startup."""

    input_device: str | None
    output_device: str | None


class BasicAudioStream:
    """Lightweight placeholder stream implementation."""

    def __init__(self) -> None:
        self._started = False

    def start(self) -> None:
        self._started = True
        logging.info("Audio stream started.")

    def stop(self) -> None:
        if self._started:
            logging.info("Audio stream stopped.")
        self._started = False


class BasicDSPEngine:
    """Simple DSP engine placeholder with stream construction."""

    def __init__(self, visualization_queue: queue.Queue[Any]) -> None:
        self.visualization_queue = visualization_queue
        logging.debug("DSP engine initialized with visualization queue id=%s", id(visualization_queue))

    def open_stream(self, *, input_device: str | None, output_device: str | None) -> AudioStream:
        logging.info(
            "Opening audio stream with devices (input=%r, output=%r).",
            input_device,
            output_device,
        )
        return BasicAudioStream()


class MainWindowProtocol(Protocol):
    """Protocol for methods used by bootstrap for main window."""

    def show(self) -> None:
        """Show the window."""


try:
    from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "PyQt6 is required to run this application. Install it with `pip install PyQt6`."
    ) from exc


class MainWindow(QMainWindow):
    """Minimal UI shell for the pedalboard app."""

    def __init__(self, visualization_queue: queue.Queue[Any]) -> None:
        super().__init__()
        self.visualization_queue = visualization_queue
        self.setWindowTitle("Python DSP Pedalboard")
        self.setCentralWidget(QLabel("DSP Pedalboard is running."))


def configure_logging() -> None:
    """Configure consistent, explicit startup logging."""

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )


def default_audio_devices() -> AudioDeviceSelection:
    """Resolve audio device defaults from environment variables."""

    return AudioDeviceSelection(
        input_device=os.getenv("DSP_INPUT_DEVICE"),
        output_device=os.getenv("DSP_OUTPUT_DEVICE"),
    )


def build_visualization_bridge() -> queue.Queue[Any]:
    """Build queue bridge between DSP thread and UI visualization layer."""

    return queue.Queue(maxsize=512)


def create_dsp_engine(visualization_queue: queue.Queue[Any]) -> AudioEngine:
    """Create the DSP engine instance."""

    return BasicDSPEngine(visualization_queue=visualization_queue)


def run() -> int:
    """Run application lifecycle and return process exit code."""

    configure_logging()
    logging.info("Bootstrapping Python DSP Pedalboard application.")

    try:
        devices = default_audio_devices()
        visualization_queue = build_visualization_bridge()
        dsp_engine = create_dsp_engine(visualization_queue)

        app = QApplication(sys.argv)
        window: MainWindowProtocol = MainWindow(visualization_queue)
        window.show()

        # Ensure stream only starts once UI has initialized and is visible.
        stream = dsp_engine.open_stream(
            input_device=devices.input_device,
            output_device=devices.output_device,
        )
        stream.start()

        def shutdown() -> None:
            logging.info("Application shutdown requested; stopping audio stream.")
            try:
                stream.stop()
            except Exception:
                logging.exception("Failed while stopping audio stream.")

        app.aboutToQuit.connect(shutdown)

        # Improve Ctrl+C behavior in terminal runs.
        signal.signal(signal.SIGINT, lambda *_: app.quit())

        logging.info("UI initialized and audio stream running.")
        return app.exec()

    except Exception:
        logging.exception("Startup failure: unable to initialize application.")
        return 1


if __name__ == "__main__":
    raise SystemExit(run())

"""Main UI window skeleton."""

from __future__ import annotations

from ui.controls import ControlPanel


class MainWindow:
    """Top-level application window."""

    def __init__(self) -> None:
        self.controls = ControlPanel()

    def show(self) -> None:
        """Display the main window."""

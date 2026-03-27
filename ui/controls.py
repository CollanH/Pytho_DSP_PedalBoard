"""UI control interfaces and parameter update hooks."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


ParameterUpdateHook = Callable[[str, float], None]


@dataclass
class ParameterBinding:
    """Mapping from a UI control to a DSP parameter."""

    control_id: str
    parameter_name: str


class ControlPanel:
    """Container for control widgets and update hook wiring."""

    def __init__(self, on_parameter_update: ParameterUpdateHook | None = None) -> None:
        self._on_parameter_update = on_parameter_update

    def set_parameter_update_hook(self, hook: ParameterUpdateHook) -> None:
        """Register callback receiving ``(parameter_name, value)`` updates."""
        self._on_parameter_update = hook

    def handle_control_change(self, parameter_name: str, value: float) -> None:
        """Bridge UI value changes into DSP parameter updates."""
        if self._on_parameter_update is not None:
            self._on_parameter_update(parameter_name, value)

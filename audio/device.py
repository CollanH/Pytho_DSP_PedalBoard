"""Device enumeration and stream configuration validation helpers."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import sounddevice as sd

DeviceSelector = Union[int, str]


def list_devices() -> List[Dict[str, Any]]:
    """Return all audio devices with index embedded in each record."""
    devices = sd.query_devices()
    return [{"index": idx, **dict(device)} for idx, device in enumerate(devices)]


def list_input_devices(min_channels: int = 1) -> List[Dict[str, Any]]:
    """Return input-capable devices supporting at least ``min_channels``."""
    return [
        device
        for device in list_devices()
        if int(device.get("max_input_channels", 0)) >= min_channels
    ]


def list_output_devices(min_channels: int = 1) -> List[Dict[str, Any]]:
    """Return output-capable devices supporting at least ``min_channels``."""
    return [
        device
        for device in list_devices()
        if int(device.get("max_output_channels", 0)) >= min_channels
    ]


def resolve_device(device: Optional[DeviceSelector], *, kind: str) -> int:
    """Resolve a device selector (index/name/default) to an integer device index."""
    if kind not in {"input", "output"}:
        raise ValueError("kind must be 'input' or 'output'")

    if device is None:
        default_in, default_out = sd.default.device
        selected = default_in if kind == "input" else default_out
        if selected is None or int(selected) < 0:
            raise RuntimeError(f"No default {kind} device configured")
        return int(selected)

    if isinstance(device, int):
        return device

    normalized = device.strip().lower()
    channel_field = "max_input_channels" if kind == "input" else "max_output_channels"
    for entry in list_devices():
        if int(entry.get(channel_field, 0)) <= 0:
            continue
        if normalized in str(entry.get("name", "")).lower():
            return int(entry["index"])

    raise LookupError(f"Could not resolve {kind} device from selector: {device!r}")


def _check_device_channels(device_index: int, channels: int, kind: str) -> None:
    if channels < 1:
        raise ValueError("channels must be >= 1")

    info = sd.query_devices(device_index)
    max_channels = int(
        info["max_input_channels"] if kind == "input" else info["max_output_channels"]
    )
    if max_channels < channels:
        raise ValueError(
            f"Device {device_index} supports {max_channels} {kind} channel(s), "
            f"requested {channels}"
        )


def _candidate_samplerates(device_index: int, explicit: Optional[Iterable[int]]) -> List[int]:
    if explicit:
        return [int(rate) for rate in explicit]

    default = int(sd.query_devices(device_index)["default_samplerate"])
    common = [44100, 48000, 88200, 96000]
    return [default] + [rate for rate in common if rate != default]


def validate_stream_config(
    input_device: Optional[DeviceSelector] = None,
    output_device: Optional[DeviceSelector] = None,
    input_channels: int = 1,
    output_channels: int = 1,
    samplerate: Optional[int] = None,
    sample_rates: Optional[Iterable[int]] = None,
    dtype: str = "float32",
) -> Tuple[int, int, int]:
    """Validate stream settings and return ``(input_idx, output_idx, samplerate)``.

    If ``samplerate`` is omitted, this helper picks the first compatible rate from
    ``sample_rates`` or from a small set of common defaults.
    """

    input_idx = resolve_device(input_device, kind="input")
    output_idx = resolve_device(output_device, kind="output")

    _check_device_channels(input_idx, input_channels, "input")
    _check_device_channels(output_idx, output_channels, "output")

    if samplerate is not None:
        sd.check_input_settings(
            device=input_idx,
            channels=input_channels,
            samplerate=int(samplerate),
            dtype=dtype,
        )
        sd.check_output_settings(
            device=output_idx,
            channels=output_channels,
            samplerate=int(samplerate),
            dtype=dtype,
        )
        return input_idx, output_idx, int(samplerate)

    for rate in _candidate_samplerates(output_idx, sample_rates):
        try:
            sd.check_input_settings(
                device=input_idx,
                channels=input_channels,
                samplerate=int(rate),
                dtype=dtype,
            )
            sd.check_output_settings(
                device=output_idx,
                channels=output_channels,
                samplerate=int(rate),
                dtype=dtype,
            )
            return input_idx, output_idx, int(rate)
        except Exception:
            continue

    raise RuntimeError("No compatible sample rate found for input/output device pair")


def pick_default_input_device(min_channels: int = 1) -> int:
    """Return default input device index (or first compatible fallback)."""
    try:
        return resolve_device(None, kind="input")
    except RuntimeError:
        candidates = list_input_devices(min_channels=min_channels)
        if not candidates:
            raise RuntimeError("No input-capable device found")
        return int(candidates[0]["index"])


def pick_default_output_device(min_channels: int = 1) -> int:
    """Return default output device index (or first compatible fallback)."""
    try:
        return resolve_device(None, kind="output")
    except RuntimeError:
        candidates = list_output_devices(min_channels=min_channels)
        if not candidates:
            raise RuntimeError("No output-capable device found")
        return int(candidates[0]["index"])

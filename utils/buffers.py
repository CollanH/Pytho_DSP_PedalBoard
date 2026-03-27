"""Buffer utilities including a stable ring buffer interface."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable
from typing import Generic, TypeVar


T = TypeVar("T")


class RingBuffer(Generic[T]):
    """Fixed-capacity FIFO ring buffer API.

    API:
    - ``write(items)``: append iterable items, dropping oldest if over capacity.
    - ``read(n)``: pop and return up to ``n`` oldest items.
    - ``peek(n)``: return up to ``n`` oldest items without removing.
    - ``clear()``: remove all buffered items.
    - ``available``: number of currently buffered items.
    - ``capacity``: maximum number of items retained.
    """

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be > 0")
        self._capacity = capacity
        self._buffer: deque[T] = deque(maxlen=capacity)

    @property
    def capacity(self) -> int:
        return self._capacity

    @property
    def available(self) -> int:
        return len(self._buffer)

    def write(self, items: Iterable[T]) -> None:
        self._buffer.extend(items)

    def read(self, n: int) -> list[T]:
        if n < 0:
            raise ValueError("n must be >= 0")
        return [self._buffer.popleft() for _ in range(min(n, len(self._buffer)))]

    def peek(self, n: int) -> list[T]:
        if n < 0:
            raise ValueError("n must be >= 0")
        return [self._buffer[i] for i in range(min(n, len(self._buffer)))]

    def clear(self) -> None:
        self._buffer.clear()

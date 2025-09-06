#!/usr/bin/env micropython
import time

from .task import TaskWatchdog


class WindowedTaskWatchdog(TaskWatchdog):
    def __init__(self, window_start, window_end):
        super().__init__(window_end)

        self.window_start = window_start

    def feed(self):
        if time.ticks_diff(time.ticks_ms(), self.last) <= self.window_start:
            self._starved = True  # overfed
        self.last = time.ticks_ms()

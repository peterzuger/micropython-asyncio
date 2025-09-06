#!/usr/bin/env micropython
import asyncio
import time


class TaskWatchdog:
    def __init__(self, timeout):
        self.timeout = timeout

        self.last = time.ticks_ms()
        self._starved = False

    def _check(self):
        self._starved |= time.ticks_diff(time.ticks_ms(), self.last) >= self.timeout

    def feed(self):
        self._check()
        self.last = time.ticks_ms()

    def __bool__(self):
        self._check()
        return not self._starved

    def is_starved(self):
        return self._starved

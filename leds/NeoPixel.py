#!/usr/bin/env micropython
import asyncio

import micropython

from . import _LedBase


class _Led(_LedBase):
    @_LedBase.color.setter
    def color(self, value):
        self._c = value
        self._m._recalc(self._i, self._b, self._c)

    @_LedBase.brightness.setter
    def brightness(self, value):
        self._b = value
        self._m._recalc(self._i, self._b, self._c)


class NeoPixel:
    MAX_BRIGHTNESS = 255

    def __init__(self, strip, pause=20):
        self.strip = strip
        self.pause = pause
        self.n = strip.n

        self.leds = [_Led(self, i) for i in range(self.n)]

        self._event = asyncio.Event()
        self._task = None

    @micropython.native
    def _recalc(self, n, b, c):
        self.strip[n] = tuple(int(led * b * self.MAX_BRIGHTNESS) for led in c)
        self._event.set()  # trigger change !

    def start(self):
        if not self._task:
            self._task = asyncio.create_task(self._run())

    def stop(self):
        if self._task:
            self._task.cancel()
            self._task = None

    async def _run(self):
        while True:
            await self._event.wait()
            self._event.clear()
            self.strip.write()
            await asyncio.sleep_ms(self.pause)

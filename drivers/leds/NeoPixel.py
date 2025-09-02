#!/usr/bin/env micropython
import asyncio

import micropython

from . import _LedBase


class _Led(_LedBase):
    def set_color(self, value):
        self._c = value
        self._m._recalc(self._i, self._b, self._c)
        self._m._event.set()  # trigger change !

    def _set_brightness(self, value):
        self._b = value
        self._m._recalc(self._i, self._b, self._c)
        self._m._event.set()  # trigger change !


class NeoPixel:
    def __init__(self, strip, pause=20):
        self.strip = strip
        self.pause = pause
        self.n = strip.n

        self.leds = [_Led(self, i) for i in range(self.n)]

        self._event = asyncio.Event()
        self._task = None

    @micropython.viper
    def _recalc(self, n: uint, b: uint, c: ptr8):
        buf = ptr8(self.strip.buf)
        order = ptr8(self.strip.ORDER)
        offset = uint(uint(self.strip.bpp) * n)
        buf[offset + order[0]] = ((c[0] * b) + 127) // 0xFF
        buf[offset + order[1]] = ((c[1] * b) + 127) // 0xFF
        buf[offset + order[2]] = ((c[2] * b) + 127) // 0xFF

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

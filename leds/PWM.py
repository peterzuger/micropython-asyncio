#!/usr/bin/env micropython
import asyncio

import machine
import micropython

from . import _LedBase


class _Led(_LedBase):
    @_LedBase.color.setter
    def color(self, value):
        self._c = value
        self._m._write(self._c, self._b)

    @_LedBase.brightness.setter
    def brightness(self, value):
        self._b = value
        self._m._write(self._c, self._b)


class PWMLed:
    MAX = 65535

    def __init__(self, r, g, b, freq=2000):
        self._r = machine.PWM(r, freq)
        self._g = machine.PWM(g, freq)
        self._b = machine.PWM(b, freq)

        self.leds = [_Led(self)]

    @micropython.native
    def _write(self, c, b):
        self._r.duty_u16(int(c.r * b * self.MAX))
        self._g.duty_u16(int(c.g * b * self.MAX))
        self._b.duty_u16(int(c.b * b * self.MAX))

    def start(self):
        pass

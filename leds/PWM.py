#!/usr/bin/env micropython
import machine
import micropython

from . import _LedBase


class _Led(_LedBase):
    def set_color(self, value):
        self._c = value
        self._m._write(self._c, self._b)

    def _set_brightness(self, value):
        self._b = value
        self._m._write(self._c, self._b)


@micropython.viper
def _calc(c: uint, b: uint) -> uint:
    _c = int((c * b) + 127) // 0xFF
    return uint(int((_c * 0xFFFF) + 127) // 0xFF)


class PWMLed:
    def __init__(self, r, g, b, freq=2000):
        self._r = machine.PWM(r, freq)
        self._g = machine.PWM(g, freq)
        self._b = machine.PWM(b, freq)

        self.leds = [_Led(self)]

    @micropython.native
    def _write(self, c, b):
        self._r.duty_u16(_calc(c.r, b))
        self._g.duty_u16(_calc(c.g, b))
        self._b.duty_u16(_calc(c.b, b))

    def start(self):
        pass

    def stop(self):
        pass

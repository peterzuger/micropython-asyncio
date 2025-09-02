#!/usr/bin/env micropython
import asyncio

from .color import RGB


class _LedBase:
    def __init__(self, m, i=0):
        self._m = m  # Led Driver reference
        self._i = i  # Driver specific Led reference
        self._c = RGB(0, 0, 0)  # color 0 - 255
        self._b = 255  # brightness 0 - 255
        self._effect = None

    def get_color(self):
        return self._c

    # def set_color(self, val):
    #     pass

    def get_brightness(self):
        return self._b / 255

    def set_brightness(self, val):
        self._set_brightness(int(val * 255))

    # implement in derived classes
    # def _set_brightness(self, val):
    #     pass

    def effect(self, effect=None):
        self.cancel()
        if effect is not None:
            self._effect = asyncio.create_task(effect.run(self))

    def cancel(self):
        if self._effect:
            self._effect.cancel()
            self._effect = None

    def done(self):
        return (self._effect is None) or self._effect.done()


class MultiLed:
    def __init__(self, leds):
        self.leds = leds
        self._effect = None

    def cancel_all(self):
        for led in self.leds:
            led.cancel()

    # not implemented because the underlying leds don't necessarily have the
    # same color/brightness and so the returned value would be ambiguous
    #
    # def get_color(self): pass
    #
    # def get_brightness(self):
    #     pass

    def set_color(self, v):
        for led in self.leds:
            led.set_color(v)

    def set_brightness(self, v):
        _v = int(v * 255)
        for led in self.leds:
            led._set_brightness(_v)

    def effect(self, effect=None):
        self.cancel()
        if effect is not None:
            self._effect = asyncio.create_task(effect.run(self))

    def cancel(self):
        if self._effect:
            self._effect.cancel()
            self._effect = None

    def done(self):
        return (self._effect is None) or self._effect.done()

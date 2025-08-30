#!/usr/bin/env micropython
import asyncio

from .effects import NoEffect
from .color import RGB


class _LedBase:
    def __init__(self, m, i=0):
        self._m = m  # Led Driver reference
        self._i = i  # Driver specific Led reference
        self._c = RGB(0, 0, 0)
        self._b = 1
        self._effect = None

    @property
    def color(self):
        return self._c

    @color.setter
    def color(self, _):
        raise NotImplementedError

    @property
    def brightness(self):
        return self._b

    @brightness.setter
    def brightness(self, _):
        raise NotImplementedError

    def effect(self, effect=NoEffect()):
        self.cancel()
        if isinstance(effect, tuple):
            self._effect = asyncio.create_task(
                asyncio.gather(*[e.run(self) for e in effect])
            )
        else:
            self._effect = asyncio.create_task(effect.run(self))

    def cancel(self):
        if self._effect:
            self._effect.cancel()

    def done(self):
        return self._effect.done()


class MultiLed:
    def __init__(self, leds):
        self.leds = leds
        self._effect = asyncio.create_task(NoEffect().run(None))

    def cancel_all(self):
        for led in self.leds:
            led.cancel()

    @property
    def color(self):
        raise AttributeError()

    @color.setter
    def color(self, value):
        for led in self.leds:
            led.color = value

    @property
    def brightness(self):
        raise AttributeError()

    @brightness.setter
    def brightness(self, value):
        for led in self.leds:
            led.brightness = value

    def effect(self, effect=NoEffect()):
        self._effect.cancel()
        if isinstance(effect, tuple):
            self._effect = asyncio.create_task(
                asyncio.gather(*[e.run(self) for e in effect])
            )
        else:
            self._effect = asyncio.create_task(effect.run(self))

    def cancel(self):
        self._effect.cancel()

    def done(self):
        return self._effect.done()

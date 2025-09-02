#!/usr/bin/env micropython
import asyncio
import math


class NoEffect:
    async def run(self, led):
        pass


class Set:
    def __init__(self, color, brightness):
        self.color = color
        self.brightness = brightness

    async def run(self, led):
        led.set_color(self.color)
        led.set_brightness(self.brightness)


class Color:
    def __init__(self, color):
        self.color = color

    async def run(self, led):
        led.set_color(self.color)


class Brightness:
    def __init__(self, brightness):
        self.brightness = brightness

    async def run(self, led):
        led.set_brightness(self.brightness)


class On:
    def __init__(self, time_ms=500, steps=16):
        self.delay = time_ms // steps
        self.steps = steps

    async def run(self, led):
        sb = led.get_brightness()
        bs = (1 - sb) / self.steps
        for step in range(self.steps):
            led.set_brightness(sb + (bs * step))
            await asyncio.sleep_ms(self.delay)
        led.set_brightness(1)  # because of FP errors


class Off:
    def __init__(self, time_ms=500, steps=16):
        self.delay = time_ms // steps
        self.steps = steps

    async def run(self, led):
        sb = led.get_brightness()
        bs = sb / self.steps
        for step in range(self.steps):
            led.set_brightness(sb - (bs * step))
            await asyncio.sleep_ms(self.delay)
        led.set_brightness(0)  # because of FP errors


class Sine:
    def __init__(self, step=4):
        self.step = step

    async def run(self, led):
        try:
            while True:
                for x in range(0, 180, self.step):
                    led.set_brightness(math.sin(math.radians(x)))
                    await asyncio.sleep_ms(20)
        finally:
            led.set_brightness(1)

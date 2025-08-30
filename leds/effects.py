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
        led.color = self.color
        led.brightness = self.brightness


class Color:
    def __init__(self, color):
        self.color = color

    async def run(self, led):
        led.color = self.color


class Brightness:
    def __init__(self, brightness):
        self.brightness = brightness

    async def run(self, led):
        led.brightness = self.brightness


class On:
    def __init__(self, time=0.5, steps=16):
        self.delay = int((time * 1000) / steps)
        self.steps = steps

    async def run(self, led):
        sb = led.brightness
        bs = (1 - sb) / self.steps
        for step in range(self.steps):
            led.brighness = sb + (bs * step)
            await asyncio.sleep_ms(self.delay)
        led.brighness = 1  # because of FP errors


class Off:
    def __init__(self, time=0.5, steps=16):
        self.delay = int((time * 1000) / steps)
        self.steps = steps

    async def run(self, led):
        sb = led.brightness
        bs = sb / self.steps
        for step in range(self.steps):
            led.brighness = sb - (bs * step)
            await asyncio.sleep_ms(self.delay)
        led.brighness = 0  # because of FP errors


class Sine:
    def __init__(self, step=4):
        self.step = step

    async def run(self, led):
        try:
            while True:
                for x in range(0, 180, self.step):
                    led.brightness = math.sin(math.radians(x))
                    await asyncio.sleep_ms(20)
        finally:
            led.brightness = 1

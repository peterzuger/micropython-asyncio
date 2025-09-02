#!/usr/bin/env micropython
import asyncio
import math

import machine
import neopixel

from drivers.leds.NeoPixel import NeoPixel
from drivers.leds.color import RGB


class LedColorChaserEffect:
    def __init__(self, leds):
        self.leds = leds

        n = len(leds)
        v = list(int(x * (255 / n)) for x in range(n))
        off1 = n // 3
        off2 = 2 * off1

        self._values = [
            RGB(v[i], v[(off1 + i) % n], v[(off2 + i) % n]) for i in range(n)
        ]

    async def run(self):
        n = len(self.leds)
        while True:
            for i in range(n):
                for j in range(n):
                    self.leds[j].set_color(self._values[(i + j) % n])
                await asyncio.sleep_ms(20)


class LedSineChaserEffect:
    def __init__(self, leds):
        self.leds = leds
        self.step = 180 / len(leds)

        # pre-calculate the sine steps
        self._values = [
            math.sin(math.radians(x)) for x in (n * self.step for n in range(len(leds)))
        ]

    async def run(self):
        n = len(self.leds)
        while True:
            for i in range(n):
                for j in range(n):
                    self.leds[j].set_brightness(self._values[(i + j) % n])
                await asyncio.sleep_ms(50)


async def main():
    # assumes that you have for example a seed studio 24 Led ring attached to
    # pin X1. The effects should work for any number of led's just change it
    # here.

    strip = NeoPixel(neopixel.NeoPixel(machine.Pin("X1"), 24))
    strip.start()

    chaser1 = LedSineChaserEffect(strip.leds)
    chaser2 = LedColorChaserEffect(strip.leds)

    await asyncio.gather(
        chaser1.run(),
        chaser2.run(),
    )


if __name__ == "__main__":
    asyncio.run(main())

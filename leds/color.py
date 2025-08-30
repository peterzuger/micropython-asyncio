#!/usr/bin/env micropython
from collections import namedtuple


class RGB(namedtuple("RGB", ["r", "g", "b"])):
    @classmethod
    def from_string(cls, val):
        v = val.lstrip("#")
        return cls(*tuple(int(v[i : i + 2], 16) / 255 for i in (0, 2, 4)))

    def __str__(self):
        return "#%02X%02X%02X" % tuple(int(c * 255) for c in self)

    def hsv(self):
        return HSV.from_rgb(self)


RGB.White = RGB(1, 1, 1)
RGB.Black = RGB(0, 0, 0)
RGB.Red = RGB(1, 0, 0)
RGB.Green = RGB(0, 1, 0)
RGB.Blue = RGB(0, 0, 1)


class HSV(namedtuple("HSV", ["h", "s", "v"])):
    @classmethod
    def from_rgb(cls, rgb):
        x_max = max(rgb)
        x_min = min(rgb)
        C = x_max - x_min

        if C == 0:
            return cls(0.0, 0.0, x_max)

        r, g, b = rgb
        if x_max == r:
            h = ((g - b) / C) % 6
        elif x_max == g:
            h = ((b - r) / C) + 2
        else:
            h = ((r - g) / C) + 4

        return cls(60 * h, C / x_max, x_max)

    def rgb(self):
        H = self.h / 60
        C = self.v * self.s
        X = C * (1 - abs((H % 2) - 1))

        r = g = b = 0
        if H < 1:
            r, g = (C, X)
        elif H < 2:
            r, g = (X, C)
        elif H < 3:
            g, b = (C, X)
        elif H < 4:
            g, b = (X, C)
        elif H < 5:
            r, b = (X, C)
        elif H < 6:
            r, b = (C, X)

        m = self.v - C
        return RGB(r + m, g + m, b + m)

#!/usr/bin/env micropython
import asyncio
import struct

import micropython

from . import _LedBase


class _Led(_LedBase):
    @_LedBase.color.setter
    def color(self, value):
        self._c = value
        self._m._write_color(self._i, value)

    @_LedBase.brightness.setter
    def brightness(self, value):
        self._b = value
        self._m._write_brightness(self._i, value)


class _LedBank(_LedBase):
    @_LedBase.color.setter
    def color(self, value):
        self._c = value
        self._m._write_bank_color(value)

    @_LedBase.brightness.setter
    def brightness(self, value):
        self._b = value
        self._m._write_bank_brightness(value)


class LP5024:
    LED_COUNT = 8

    DEVICE_CONFIG0 = 0x00
    DEVICE_CONFIG1 = 0x01
    LED_CONFIG0 = 0x02
    BANK_BRIGHTNESS = 0x03
    BANK_A_COLOR = 0x04
    BANK_B_COLOR = 0x05
    BANK_C_COLOR = 0x06
    LED0_BRIGHTNESS = 0x07
    OUT0_COLOR = 0x0F
    RESET = 0x27

    # DEVICE_CONFIG0
    CHIP_EN = 0x40

    # DEVICE_CONFIG1
    LOG_SCALE_EN = 0x20
    POWER_SAVE_EN = 0x10
    AUTO_INCR_EN = 0x08  # must be enabled for _write_color
    PWM_DITHERING_EN = 0x04
    MAX_CURRENT_OPTION = 0x02  # 25.5 or 35mA
    LED_GLOBAL_OFF = 0x01  # soft enable/disable

    # LED_CONFIG0
    LED0 = 0x01
    LED1 = 0x02
    LED2 = 0x04
    LED3 = 0x08
    LED4 = 0x10
    LED5 = 0x20
    LED6 = 0x40  # only on LP5024
    LED7 = 0x80  # only on LP5024

    def __init__(self, iface, enable, addr=40):
        self._iface = iface
        self._enable = enable
        self.addr = addr

        self.leds = [_Led(self, i) for i in range(self.LED_COUNT)]
        self.bank_led = _LedBank(self)  # must manually enable bank control

        self._task = None

    @micropython.native
    def _read(self, reg):
        return int.from_bytes(self._iface.readfrom_mem(self.addr, reg, 1))

    @micropython.native
    def _write(self, reg, val):
        _val = val.to_bytes(1)
        self._iface.writeto_mem(self.addr, reg, _val)
        return _val[0]

    # individual Led control
    @micropython.native
    def _write_color(self, led, c):
        r1 = self.OUT0_COLOR + 3 * led
        val = struct.pack("BBB", int(c.r * 255), int(c.g * 255), int(c.b * 255))
        self._iface.writeto_mem(self.addr, r1, val)

    @micropython.native
    def _write_brightness(self, led, b):
        self._write(self.LED0_BRIGHTNESS + led, int(b * 255))

    # BANK control
    @micropython.native
    def _write_bank_color(self, c):
        val = struct.pack("BBB", int(c.r * 255), int(c.g * 255), int(c.b * 255))
        self._iface.writeto_mem(self.addr, self.BANK_A_COLOR, val)

    @micropython.native
    def _write_bank_brightness(self, value):
        self._write(self.BANK_BRIGHTNESS, value)

    def enable_bank_control(self, val=0xFF):
        return self._write(self.LED_CONFIG0, val)

    def disable_bank_control(self, val=0xFF):
        _val = self._read(self.LED_CONFIG0) & ~val
        return self._write(self.LED_CONFIG0, _val)

    def start(self):
        if not self._task:
            self._task = asyncio.create_task(self._run())

        self._enable.high()

    def stop(self):
        if self._task:
            self._task.cancel()
            self._task = None

        self._enable.low()

    async def _run(self):
        await asyncio.sleep_ms(50)  # required for the LP50xx to be ready
        self.reset()
        self.enable()

    def reset(self):
        self._write(self.RESET, 0xFF)

    def enable(self):
        self._write(self.DEVICE_CONFIG0, self.CHIP_EN)

    def disable(self):
        self._write(self.DEVICE_CONFIG0, 0x00)


class LP5018(LP5024):
    LED_COUNT = 6

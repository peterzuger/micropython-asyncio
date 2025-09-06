#!/usr/bin/env micropython
import array
import asyncio

import micropython
from machine import Timer, Pin

PRESSED = micropython.const(1)
RELEASED = micropython.const(0)


class Button(Pin):
    def __init__(self, *args, invert=1, **kwargs):
        super().__init__(*args, mode=Pin.IN, **kwargs)

        self._invert = invert

        self.state = 0
        self.bounce = 0
        self.press_time = 0

        # TODO: asyncio.ThreadSafeFlag() can only be awaited by a single task
        self.pressed = asyncio.ThreadSafeFlag()
        self.released = asyncio.ThreadSafeFlag()

        if self._invert:
            self.value = self._value_n

    @micropython.native
    def _value_n(self):
        return not super().value()

    def irq(self, *args, **kwargs):
        return super().irq(
            *args,
            trigger=Pin.IRQ_FALLING if self._invert else Pin.IRQ_RISING,
            **kwargs,
        )

    # ThreadSafeFlag is self clearing, but we want to wait for a button press
    # NOW not in the past so we need to clear it first.

    def __enter__(self):
        self.pressed.clear()
        self.released.clear()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    async def press(self):
        await self.pressed.wait()

    async def long_press(self, time):
        try:
            await asyncio.wait_for(self.released.wait(), timeout=time)
        except TimeoutError:
            return True  # timed out before the button was released
        return False  # was a short press


_BITS = array.array("H", (1 << i for i in range(16)))


# count trailing zeroes
@micropython.asm_thumb
def ctz(r0) -> uint:
    rbit(r0, r0)
    clz(r0, r0)


class Buttons:
    def __init__(self, buttons: list[Button], period=25):
        self.buttons = [None] * 16
        for button in buttons:
            if self.buttons[button.pin()] is not None:
                raise ValueError("2 identical EXTI pins specified")
            self.buttons[button.pin()] = button

        self.period = period
        self.pressed = 0

    def start(self):
        for button in self.buttons:
            if button:
                button.irq(handler=self.button_irq)
        self.timer = Timer(period=self.period, callback=self.timer_irq)

    def button(self, name):
        for b in self.buttons:
            if b and name in b.names():
                return b
        return None

    @micropython.native
    def timer_irq(self, _):
        if self.pressed:  # anything to do ? No -> fast exit
            for _b in _BITS:  # well lets check all 16 bits
                if self.pressed & _b:
                    b = self.buttons[ctz(_b)]

                    if b.value():  # pressed
                        if not b.press_time:
                            b.state = PRESSED
                            b.pressed.set()
                        b.bounce = 1
                        b.press_time += self.period
                    else:  # not pressed
                        if not b.bounce:  # not pressed again
                            if b.state == PRESSED:
                                b.released.set()
                            b.state = RELEASED
                            b.press_time = 0
                            self.pressed &= ~_b  # clear the pressed bit
                        b.bounce = 0

    @micropython.native
    def button_irq(self, pin):
        # The button_irq only adds the button to the pressed buttons ensuring
        # no press event is missed everything else is done from the timer_irq
        self.pressed |= 1 << pin.pin()

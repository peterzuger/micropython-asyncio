#!/usr/bin/env micropython
import asyncio

import machine


class HardwareWatchdog:
    def __init__(self, timeout=4000, interval=2000):
        self.timeout = timeout
        self.interval = interval

        self.dogs = []
        self.add_watchdog = self.dogs.append
        self.remove_watchdog = self.dogs.remove

        self._wdt = None

    # check this every boot to ensure no reboot loop occurs
    def caused_last_reboot(self):
        return machine.reset_cause() == machine.WDT_RESET

    # pylint: disable=method-hidden
    def feed(self):
        pass

    # def add_watchdog(self, t):
    #     self.dogs.append(t)

    # def remove_watchdog(self, t):
    #     self.dogs.remove(t)

    def start(self):
        if self._wdt is None:
            self._wdt = machine.WDT(timeout=self.timeout)
            self.feed = self._wdt.feed
            asyncio.create_task(self._run())
            # not keeping a reference to this task as stopping it is useless

    # WDT cannot be stopped
    # def stop(self):
    #     if self._task:
    #         self._task.cancel()
    #         self._task = None

    async def _run(self):
        while True:
            if not all(self.dogs):
                return  # don't feed the hardware watchdog any more

            self.feed()
            await asyncio.sleep_ms(self.interval)

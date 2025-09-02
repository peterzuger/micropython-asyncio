#!/usr/bin/env micropython

_attrs = {
    "HardwareWatchdog": "hard",
    "TaskWatchdog": "task",
    "WindowedTaskWatchdog": "windowed",
}


# Lazy loader from micropython/asyncio
def __getattr__(attr):
    mod = _attrs.get(attr, None)
    if mod is None:
        raise AttributeError(attr)
    value = getattr(__import__(mod, None, None, True, 1), attr)
    globals()[attr] = value
    return value

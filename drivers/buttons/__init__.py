#!/usr/bin/env micropython
_port = None
try:
    from machine import Pin as _Pin

    if hasattr(_Pin, "pin"):
        _port = "stm32"
except ImportError:
    pass


# Lazy loader from micropython/asyncio
def __getattr__(attr):
    if _port is None:
        raise AttributeError(attr)
    value = getattr(__import__(_port, None, None, True, 1), attr)
    globals()[attr] = value
    return value

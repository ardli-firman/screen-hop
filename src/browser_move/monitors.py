from typing import List, Optional, Any


def get_monitors() -> List[Any]:
    try:
        from screeninfo import get_monitors

        return list(get_monitors())
    except ImportError:
        return []


def get_primary_monitor() -> Optional[Any]:
    for m in get_monitors():
        if m.is_primary:
            return m
    return None


def get_external_monitors() -> List[Any]:
    return [m for m in get_monitors() if not m.is_primary]


def select_external_monitor(monitors: List[Any]) -> Optional[Any]:
    if not monitors:
        return None
    return monitors[0]

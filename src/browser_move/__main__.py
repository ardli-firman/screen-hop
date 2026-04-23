"""Console entry point compatibility shim for ScreenHop."""

from __future__ import annotations

import sys
import types

import browser_move as _browser_move


def _register_legacy_namespace() -> None:
    """Expose the package under the legacy ``src.browser_move`` namespace."""
    src_package = sys.modules.get("src")
    if src_package is None:
        src_package = types.ModuleType("src")
        src_package.__path__ = []
        sys.modules["src"] = src_package

    setattr(src_package, "browser_move", _browser_move)
    sys.modules.setdefault("src.browser_move", _browser_move)


_register_legacy_namespace()

from browser_move.main import main


if __name__ == "__main__":
    raise SystemExit(main())

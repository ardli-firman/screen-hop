"""Shared UI tokens and helpers for ScreenHop windows."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

SURFACE = ("#f6f7f9", "#101418")
SURFACE_ALT = ("#ffffff", "#171c22")
SURFACE_MUTED = ("#edf1f5", "#20262d")
BORDER = ("#d6dce3", "#303943")
TEXT_MUTED = ("#5e6978", "#9aa6b5")
ACCENT = ("#2563eb", "#4f8cff")
ACCENT_HOVER = ("#1d4ed8", "#3b74db")
WARN = ("#b45309", "#f59e0b")
DANGER = ("#dc2626", "#ef4444")
SUCCESS = ("#168755", "#22c55e")
INFO = ("#2563eb", "#60a5fa")
DISABLED = ("#cbd5e1", "#2b3440")
CORNER_RADIUS = 8
INNER_RADIUS = 6
APP_GEOMETRY = "1120x700"
APP_MIN_SIZE = (1060, 640)
APP_CONTENT_MAX_WIDTH = 1088
MODAL_GEOMETRY = "720x640"
MODAL_MIN_SIZE = (720, 580)
MODAL_CONTENT_MAX_WIDTH = 700
PRESET_FORM_GEOMETRY = "780x760"
PRESET_FORM_MIN_SIZE = (760, 700)
PRESET_FORM_CONTENT_MAX_WIDTH = 740


def apply_base_theme(appearance_mode: str = "System") -> None:
    ctk.set_appearance_mode(appearance_mode)
    ctk.set_default_color_theme("blue")


def font(size: int, weight: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(size=size, weight=weight)


def style_card(widget: Any, **overrides: Any) -> None:
    widget.configure(
        fg_color=overrides.pop("fg_color", SURFACE_ALT),
        corner_radius=overrides.pop("corner_radius", CORNER_RADIUS),
        border_width=overrides.pop("border_width", 1),
        border_color=overrides.pop("border_color", BORDER),
        **overrides,
    )


def style_panel(widget: Any, **overrides: Any) -> None:
    widget.configure(
        fg_color=overrides.pop("fg_color", SURFACE),
        corner_radius=overrides.pop("corner_radius", CORNER_RADIUS),
        border_width=overrides.pop("border_width", 1),
        border_color=overrides.pop("border_color", BORDER),
        **overrides,
    )


def status_color(status_type: str) -> tuple[str, str]:
    palette = {
        "ready": SUCCESS,
        "running": WARN,
        "error": DANGER,
        "info": INFO,
    }
    return palette.get(status_type, INFO)

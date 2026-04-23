"""Shared UI tokens and helpers for ScreenHop windows."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

SURFACE = ("#f3f7fb", "#0f1724")
SURFACE_ALT = ("#ffffff", "#162033")
SURFACE_MUTED = ("#e6edf5", "#1e293b")
BORDER = ("#d5dee8", "#293548")
TEXT_MUTED = ("#5f6f85", "#91a4be")
ACCENT = ("#0f9d7a", "#10b981")
ACCENT_HOVER = ("#0a7a5f", "#059669")
WARN = ("#c97a17", "#f59e0b")
DANGER = ("#cf4c5b", "#ef4444")
SUCCESS = ("#1e8e5a", "#22c55e")
INFO = ("#2563eb", "#3b82f6")
CORNER_RADIUS = 18
INNER_RADIUS = 14
APP_GEOMETRY = "1120x720"
APP_MIN_SIZE = (920, 580)
MODAL_GEOMETRY = "760x680"
MODAL_MIN_SIZE = (700, 620)


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

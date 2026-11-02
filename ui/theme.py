"""
==============================================================================
StudySphere — UI Theme & Design System
==============================================================================
Author: Senior Python Mentor & Architect
Role: Defines the visual palette, fonts, padding constants, and widget styles
      for a sleek, modern, dark-mode productivity dashboard.
"""

import customtkinter as ctk

# Configure CustomTkinter Global Mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class Theme:
    """
    Central design tokens for StudySphere.
    Inspired by modern developer-focused productivity apps (Linear, Notion, GitHub Dark).
    """

    # Background Colors
    BG_WINDOW = "#0B0F19"       # Deep dark navy
    BG_SIDEBAR = "#0F172A"      # Slate navy sidebar
    BG_CONTENT = "#090D16"      # Main viewport background
    BG_CARD = "#1E293B"         # Standard elevated card surface
    BG_CARD_HOVER = "#273549"   # Card hover state
    BG_INPUT = "#0F172A"        # Input fields background
    BORDER = "#334155"          # Subtle border color
    BORDER_LIGHT = "#475569"    # Highlight border

    # Primary Brand Accents (Purple / Lavender)
    ACCENT_PRIMARY = "#8B5CF6"       # Vivid Purple
    ACCENT_PRIMARY_HOVER = "#7C3AED" # Darker Purple for Hover
    ACCENT_LIGHT = "#C4B5FD"         # Soft Lavender
    ACCENT_DARK = "#4C1D95"          # Deep Purple Container
    ACCENT_GRADIENT_START = "#7C3AED"
    ACCENT_GRADIENT_END = "#6366F1"

    # Secondary Accents
    ACCENT_BLUE = "#3B82F6"     # Information blue
    ACCENT_EMERALD = "#10B981"  # Success green
    ACCENT_AMBER = "#F59E0B"    # Warning amber
    ACCENT_ROSE = "#EF4444"     # Danger / Overdue red
    ACCENT_CYAN = "#06B6D4"     # Analytics cyan

    # Typography Colors
    TEXT_PRIMARY = "#F8FAFC"    # Crisp off-white
    TEXT_SECONDARY = "#94A3B8"  # Slate secondary text
    TEXT_MUTED = "#64748B"      # Darker muted labels
    TEXT_ACCENT = "#A78BFA"     # Lavender text highlight

    # Standard Fonts
    FONT_FAMILY = "Segoe UI"
    FONT_CODE = "Consolas"

    @classmethod
    def font_title(cls) -> tuple:
        return (cls.FONT_FAMILY, 22, "bold")

    @classmethod
    def font_h1(cls) -> tuple:
        return (cls.FONT_FAMILY, 18, "bold")

    @classmethod
    def font_h2(cls) -> tuple:
        return (cls.FONT_FAMILY, 14, "bold")

    @classmethod
    def font_h3(cls) -> tuple:
        return (cls.FONT_FAMILY, 12, "bold")

    @classmethod
    def font_body(cls) -> tuple:
        return (cls.FONT_FAMILY, 12)

    @classmethod
    def font_body_bold(cls) -> tuple:
        return (cls.FONT_FAMILY, 12, "bold")

    @classmethod
    def font_small(cls) -> tuple:
        return (cls.FONT_FAMILY, 10)

    @classmethod
    def font_small_bold(cls) -> tuple:
        return (cls.FONT_FAMILY, 10, "bold")

    @classmethod
    def font_timer(cls) -> tuple:
        return (cls.FONT_FAMILY, 64, "bold")

    @classmethod
    def font_stat_number(cls) -> tuple:
        return (cls.FONT_FAMILY, 26, "bold")

    @classmethod
    def font_code(cls) -> tuple:
        return (cls.FONT_CODE, 11)

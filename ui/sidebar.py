"""
==============================================================================
StudySphere — Sidebar Navigation Component
==============================================================================
Author: Senior Python Mentor & Architect
Role: Houses the primary navigation bar with active route highlighting,
      dynamic notification badge counters, and demo-seeding controls.
"""

import customtkinter as ctk
from ui.theme import Theme


class Sidebar(ctk.CTkFrame):
    """
    Vertical navigation bar providing seamless switching between application modules.
    """

    NAV_ITEMS = [
        ("dashboard", "📊", "Dashboard"),
        ("tasks", "✅", "Tasks"),
        ("subjects", "📚", "Subjects"),
        ("timer", "⏱️", "Focus Timer"),
        ("analytics", "📈", "Analytics"),
        ("quiz", "💡", "Quiz Zone"),
        ("notes", "📝", "Notes"),
        ("notifications", "🔔", "Notifications"),
    ]

    def __init__(self, master, on_navigate, on_load_demo, on_clear_data, **kwargs):
        super().__init__(
            master,
            width=230,
            corner_radius=0,
            fg_color=Theme.BG_SIDEBAR,
            border_color=Theme.BORDER,
            border_width=1,
            **kwargs
        )
        self.grid_propagate(False)

        self.on_navigate = on_navigate
        self.on_load_demo = on_load_demo
        self.on_clear_data = on_clear_data

        self.nav_buttons = {}
        self.active_route = "dashboard"

        self._build_header()
        self._build_nav_links()
        self._build_footer()

    def _build_header(self) -> None:
        """Renders brand logo, app title, and student badge."""
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.pack(fill="x", padx=18, pady=(24, 20))

        # Brand Icon & Title in horizontal alignment
        header_row = ctk.CTkFrame(brand_frame, fg_color="transparent")
        header_row.pack(fill="x")

        logo_label = ctk.CTkLabel(
            header_row,
            text="🪐",
            font=("Segoe UI Emoji", 24)
        )
        logo_label.pack(side="left", padx=(0, 10))

        title_col = ctk.CTkFrame(header_row, fg_color="transparent")
        title_col.pack(side="left")

        title_label = ctk.CTkLabel(
            title_col,
            text="StudySphere",
            font=Theme.font_h1(),
            text_color=Theme.TEXT_PRIMARY
        )
        title_label.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_col,
            text="Command Center",
            font=Theme.font_small(),
            text_color=Theme.TEXT_ACCENT
        )
        subtitle.pack(anchor="w")

        # Subtle divider
        divider = ctk.CTkFrame(self, height=1, fg_color=Theme.BORDER)
        divider.pack(fill="x", padx=16, pady=(0, 14))

    def _build_nav_links(self) -> None:
        """Generates navigation buttons."""
        self.nav_container = ctk.CTkFrame(self, fg_color="transparent")
        self.nav_container.pack(fill="both", expand=True, padx=12)

        for route_id, icon, label_text in self.NAV_ITEMS:
            display_text = f"  {icon}  {label_text}"
            btn = ctk.CTkButton(
                self.nav_container,
                text=display_text,
                font=Theme.font_body(),
                anchor="w",
                height=38,
                corner_radius=8,
                fg_color="transparent",
                text_color=Theme.TEXT_SECONDARY,
                hover_color=Theme.BG_CARD_HOVER,
                command=lambda r=route_id: self._handle_click(r)
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[route_id] = btn

        # Highlight default route
        self.set_active_route("dashboard")

    def _build_footer(self) -> None:
        """Renders portfolio helper controls (Load Demo, Clear) and version badge."""
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(fill="x", side="bottom", padx=12, pady=16)

        # Subtle divider
        divider = ctk.CTkFrame(footer_frame, height=1, fg_color=Theme.BORDER)
        divider.pack(fill="x", pady=(0, 12))

        # Demo Data Button
        demo_btn = ctk.CTkButton(
            footer_frame,
            text="⚡ Load Demo Data",
            font=Theme.font_small_bold(),
            height=30,
            corner_radius=6,
            fg_color=Theme.BG_CARD,
            hover_color=Theme.ACCENT_PRIMARY_HOVER,
            text_color=Theme.TEXT_PRIMARY,
            border_color=Theme.BORDER,
            border_width=1,
            command=self.on_load_demo
        )
        demo_btn.pack(fill="x", pady=(0, 6))

        # Reset Data Button
        clear_btn = ctk.CTkButton(
            footer_frame,
            text="🗑️ Reset Database",
            font=Theme.font_small(),
            height=26,
            corner_radius=6,
            fg_color="transparent",
            hover_color="#331B24",
            text_color=Theme.TEXT_MUTED,
            command=self.on_clear_data
        )
        clear_btn.pack(fill="x", pady=(0, 10))

        # Student Portfolio Tag
        badge_label = ctk.CTkLabel(
            footer_frame,
            text="B.Tech CSE (Data Science)\nPortfolio Project",
            font=Theme.font_small(),
            text_color=Theme.TEXT_MUTED,
            justify="center"
        )
        badge_label.pack()

    def _handle_click(self, route_id: str) -> None:
        """Updates UI state and triggers master navigation callback."""
        self.set_active_route(route_id)
        if self.on_navigate:
            self.on_navigate(route_id)

    def set_active_route(self, route_id: str) -> None:
        """Applies active highlight styling to selected button."""
        self.active_route = route_id
        for r_id, btn in self.nav_buttons.items():
            if r_id == route_id:
                btn.configure(
                    fg_color=Theme.ACCENT_PRIMARY,
                    text_color="#FFFFFF",
                    font=Theme.font_body_bold()
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=Theme.TEXT_SECONDARY,
                    font=Theme.font_body()
                )

    def update_notification_badge(self, count: int) -> None:
        """Updates the notification button label with pending alert count."""
        btn = self.nav_buttons.get("notifications")
        if btn:
            if count > 0:
                btn.configure(text=f"  🔔  Notifications ({count})")
            else:
                btn.configure(text="  🔔  Notifications")

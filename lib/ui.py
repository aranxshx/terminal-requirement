from __future__ import annotations

import os
from collections.abc import Callable

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont

from lib.app import WattzUpApplicationService, create_default_application_service
from util.config import (
    ACCENT_HOVER,
    ACCENT_MUTED,
    ACCENT_PRIMARY,
    BG_BASE,
    BG_ELEVATED,
    BG_SURFACE,
    BORDER_DEFAULT,
    STATUS_NOTSET,
    STATUS_OVER,
    STATUS_UNDER,
    TEXT_DISABLED,
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    USAGE_LEVELS,
)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

FONT_HEADING = ("Segoe UI", 16, "bold")
FONT_BODY = ("Segoe UI", 13)
FONT_CAPTION = ("Segoe UI", 11)


class WattzUpVisual(ctk.CTk):
    """CustomTkinter desktop application for WattzUp."""

    def __init__(self, application_service: WattzUpApplicationService | None = None) -> None:
        super().__init__()
        self._app = application_service or create_default_application_service()

        self.title("WattzUp | Home Energy Dashboard")
        self.geometry("1500x920")
        self.minsize(1260, 760)
        self.configure(fg_color=BG_BASE)
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        self._room_colors = {
            "Kitchen": "#ffb703",
            "Living Room": "#4caf82",
            "Bedroom": "#66a5ff",
            "Bathroom": "#7bc8f6",
            "Dining Area": "#ff8fab",
        }
        self._room_hotspots = {
            "Kitchen": (0.40, 0.48),
            "Living Room": (0.75, 0.65),
            "Bedroom": (0.48, 0.25),
            "Bathroom": (0.65, 0.35),
            "Dining Area": (0.32, 0.68),
        }
        self._room_icon_glyphs = {
            "Kitchen": "\U000F04B9",
            "Living Room": "\U000F04B8",
            "Bedroom": "\U000F02E3",
            "Bathroom": "\U000F09A0",
            "Dining Area": "\U000F0A70",
        }

        self._selected_room: str | None = None
        self._map_buttons: dict[str, ctk.CTkButton] = {}
        self._room_icon_images: dict[str, ctk.CTkImage] = {}
        self._map_label: ctk.CTkLabel | None = None

        self._map_source: Image.Image | None = None
        self._map_image: ctk.CTkImage | None = None
        self._map_size = (900, 620)

        self._user_value_label: ctk.CTkLabel | None = None
        self._cost_value_label: ctk.CTkLabel | None = None
        self._budget_value_label: ctk.CTkLabel | None = None
        self._appliance_rank_container: ctk.CTkScrollableFrame | None = None
        self._room_rank_container: ctk.CTkScrollableFrame | None = None
        self._panel_title_label: ctk.CTkLabel | None = None
        self._panel_tabview: ctk.CTkTabview | None = None
        self._manage_tab: ctk.CTkFrame | None = None
        self._appliance_tab: ctk.CTkFrame | None = None
        self._room_tab: ctk.CTkFrame | None = None
        self._room_name_value_label: ctk.CTkLabel | None = None
        self._appliance_menu_var: ctk.StringVar | None = None
        self._usage_menu_var: ctk.StringVar | None = None
        self._appliance_menu_widget: ctk.CTkOptionMenu | None = None
        self._room_records_container: ctk.CTkScrollableFrame | None = None
        self._tab_appliance_container: ctk.CTkScrollableFrame | None = None
        self._tab_room_container: ctk.CTkScrollableFrame | None = None
        self._panel_placeholder: ctk.CTkLabel | None = None

        self._load_assets()
        self._build_layout()
        self._center_main_window()

        if not self._startup_session_modal():
            self.destroy()
            return

        if self._selected_room is None:
            rooms = self._app.catalog.rooms()
            self._selected_room = rooms[0] if rooms else None

        self._refresh_all()

    # ---------- Build ----------
    def _load_assets(self) -> None:
        try:
            self._map_source = Image.open("Blueprint.png").convert("RGBA")
            self._map_image = ctk.CTkImage(
                light_image=self._map_source,
                dark_image=self._map_source,
                size=self._map_size,
            )
        except OSError:
            self._map_source = None
            self._map_image = None

        self._load_icon_images()

    def _load_icon_images(self) -> None:
        font_path = os.path.join("assets", "materialdesignicons-webfont.ttf")
        if not os.path.exists(font_path):
            return

        try:
            icon_font = ImageFont.truetype(font_path, 20)
        except OSError:
            return

        for room_name, glyph in self._room_icon_glyphs.items():
            canvas = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
            draw = ImageDraw.Draw(canvas)
            text_box = draw.textbbox((0, 0), glyph, font=icon_font)
            width = text_box[2] - text_box[0]
            height = text_box[3] - text_box[1]
            draw.text(
                ((24 - width) / 2 - text_box[0], (24 - height) / 2 - text_box[1]),
                glyph,
                font=icon_font,
                fill=(234, 234, 234, 255),
            )
            self._room_icon_images[room_name] = ctk.CTkImage(
                light_image=canvas,
                dark_image=canvas,
                size=(18, 18),
            )

    def _build_layout(self) -> None:
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_top_bar()
        self._build_body()

    def _build_top_bar(self) -> None:
        top = ctk.CTkFrame(self, fg_color=BG_ELEVATED, corner_radius=0, height=56)
        top.grid(row=0, column=0, sticky="ew")
        top.grid_propagate(False)
        top.grid_columnconfigure(0, weight=1)
        top.grid_columnconfigure(1, weight=0)
        top.grid_columnconfigure(2, weight=0)
        top.grid_columnconfigure(3, weight=0)
        top.grid_columnconfigure(4, weight=0)
        top.grid_columnconfigure(5, weight=0)

        ctk.CTkLabel(top, text="WattzUp", font=("Segoe UI", 18, "bold"), text_color=TEXT_PRIMARY).grid(
            row=0, column=0, padx=(20, 12), pady=10, sticky="w"
        )

        self._user_value_label = ctk.CTkLabel(top, text="User: -", font=FONT_BODY, text_color=TEXT_SECONDARY)
        self._user_value_label.grid(row=0, column=1, padx=(0, 16), pady=10, sticky="w")

        self._make_secondary_button(top, "Save", self._save_data).grid(row=0, column=2, padx=6, pady=10)
        self._make_secondary_button(top, "Budget", self._show_budget_modal).grid(row=0, column=3, padx=6, pady=10)
        self._make_secondary_button(top, "Logout", self._logout).grid(row=0, column=4, padx=(6, 16), pady=10)

    def _build_body(self) -> None:
        body = ctk.CTkFrame(self, fg_color=BG_BASE, corner_radius=0)
        body.grid(row=1, column=0, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=0)
        body.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(body, fg_color=BG_BASE, corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=(16, 16))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(0, weight=0)
        left.grid_rowconfigure(1, weight=0)
        left.grid_rowconfigure(2, weight=1)

        self._build_metrics_row(left)
        self._build_rankings_row(left)
        self._build_map_area(left)

        right = ctk.CTkFrame(
            body,
            fg_color=BG_SURFACE,
            width=420,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_DEFAULT,
        )
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=(16, 16))
        right.grid_propagate(False)
        right.grid_rowconfigure(2, weight=1)
        right.grid_columnconfigure(0, weight=1)

        self._panel_title_label = ctk.CTkLabel(right, text="Room: -", font=FONT_HEADING, text_color=TEXT_PRIMARY)
        self._panel_title_label.grid(row=0, column=0, padx=20, pady=(16, 8), sticky="w")

        self._room_name_value_label = ctk.CTkLabel(right, text="", font=FONT_CAPTION, text_color=TEXT_SECONDARY)
        self._room_name_value_label.grid(row=1, column=0, padx=20, pady=(0, 8), sticky="w")

        self._panel_tabview = ctk.CTkTabview(
            right,
            fg_color=BG_ELEVATED,
            segmented_button_selected_color=ACCENT_PRIMARY,
            segmented_button_selected_hover_color=ACCENT_HOVER,
            segmented_button_unselected_color=BG_SURFACE,
            segmented_button_unselected_hover_color=ACCENT_MUTED,
            text_color=TEXT_PRIMARY,
            corner_radius=10,
        )
        self._panel_tabview.grid(row=2, column=0, padx=14, pady=(0, 14), sticky="nsew")

        self._manage_tab = self._panel_tabview.add("Manage")
        self._appliance_tab = self._panel_tabview.add("Appliance Ranking")
        self._room_tab = self._panel_tabview.add("Room Ranking")

        self._panel_placeholder = ctk.CTkLabel(
            self._manage_tab,
            text="Select a room on the map to manage appliances.",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
        )
        self._panel_placeholder.grid(row=0, column=0, padx=16, pady=16, sticky="w")

        self._build_manage_tab()
        self._build_panel_ranking_tabs()

    def _build_metrics_row(self, parent: ctk.CTkFrame) -> None:
        row = ctk.CTkFrame(parent, fg_color=BG_BASE, corner_radius=0)
        row.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)

        cost_card = self._make_card(row)
        cost_card.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(cost_card, text="Estimated Monthly Cost", font=FONT_CAPTION, text_color=TEXT_SECONDARY).pack(
            anchor="w", padx=16, pady=(12, 4)
        )
        self._cost_value_label = ctk.CTkLabel(cost_card, text="P0.00", font=("Segoe UI", 20, "bold"), text_color=TEXT_PRIMARY)
        self._cost_value_label.pack(anchor="w", padx=16, pady=(0, 12))

        budget_card = self._make_card(row)
        budget_card.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(budget_card, text="Budget Status", font=FONT_CAPTION, text_color=TEXT_SECONDARY).pack(
            anchor="w", padx=16, pady=(12, 4)
        )
        self._budget_value_label = ctk.CTkLabel(budget_card, text="NOT SET", font=("Segoe UI", 20, "bold"), text_color=STATUS_NOTSET)
        self._budget_value_label.pack(anchor="w", padx=16, pady=(0, 12))

    def _build_rankings_row(self, parent: ctk.CTkFrame) -> None:
        row = ctk.CTkFrame(parent, fg_color=BG_BASE, corner_radius=0)
        row.grid(row=1, column=0, sticky="ew", pady=(0, 12))
        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=1)

        app_card = self._make_card(row)
        app_card.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ctk.CTkLabel(app_card, text="Top Appliance Ranking", font=FONT_HEADING, text_color=TEXT_PRIMARY).pack(
            anchor="w", padx=16, pady=(12, 8)
        )
        self._appliance_rank_container = ctk.CTkScrollableFrame(app_card, fg_color=BG_SURFACE, height=132)
        self._appliance_rank_container.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        room_card = self._make_card(row)
        room_card.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        ctk.CTkLabel(room_card, text="Top Room Ranking", font=FONT_HEADING, text_color=TEXT_PRIMARY).pack(
            anchor="w", padx=16, pady=(12, 8)
        )
        self._room_rank_container = ctk.CTkScrollableFrame(room_card, fg_color=BG_SURFACE, height=132)
        self._room_rank_container.pack(fill="both", expand=True, padx=12, pady=(0, 12))

    def _build_map_area(self, parent: ctk.CTkFrame) -> None:
        map_card = self._make_card(parent)
        map_card.grid(row=2, column=0, sticky="nsew")
        map_card.grid_rowconfigure(0, weight=1)
        map_card.grid_columnconfigure(0, weight=1)

        if self._map_image is None:
            ctk.CTkLabel(
                map_card,
                text="Map not available",
                font=FONT_HEADING,
                text_color=TEXT_SECONDARY,
            ).grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
            return

        self._map_label = ctk.CTkLabel(map_card, image=self._map_image, text="")
        self._map_label.grid(row=0, column=0, padx=14, pady=14, sticky="nsew")
        self._build_room_hotspots()

    def _build_manage_tab(self) -> None:
        if self._manage_tab is None:
            return

        self._manage_tab.grid_columnconfigure(0, weight=1)
        self._manage_tab.grid_rowconfigure(1, weight=1)

        add_card = ctk.CTkFrame(
            self._manage_tab,
            fg_color=BG_SURFACE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_DEFAULT,
        )
        add_card.grid(row=0, column=0, padx=10, pady=(10, 8), sticky="ew")
        add_card.grid_columnconfigure(0, weight=1)
        add_card.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(add_card, text="Add Appliance", font=FONT_HEADING, text_color=TEXT_PRIMARY).grid(
            row=0, column=0, columnspan=2, padx=12, pady=(10, 6), sticky="w"
        )

        ctk.CTkLabel(add_card, text="Room", font=FONT_CAPTION, text_color=TEXT_SECONDARY).grid(
            row=1, column=0, padx=12, pady=(0, 2), sticky="w"
        )
        ctk.CTkLabel(add_card, text="Usage", font=FONT_CAPTION, text_color=TEXT_SECONDARY).grid(
            row=1, column=1, padx=12, pady=(0, 2), sticky="w"
        )

        self._room_name_value_label = ctk.CTkLabel(add_card, text="-", font=FONT_BODY, text_color=TEXT_PRIMARY)
        self._room_name_value_label.grid(row=2, column=0, padx=12, pady=(0, 8), sticky="w")

        self._usage_menu_var = ctk.StringVar(value="Moderate")
        usage_menu = ctk.CTkOptionMenu(
            add_card,
            values=list(USAGE_LEVELS.keys()),
            variable=self._usage_menu_var,
            fg_color=BG_SURFACE,
            button_color=ACCENT_MUTED,
            button_hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            width=170,
        )
        usage_menu.grid(row=2, column=1, padx=12, pady=(0, 8), sticky="ew")

        ctk.CTkLabel(add_card, text="Appliance", font=FONT_CAPTION, text_color=TEXT_SECONDARY).grid(
            row=3, column=0, padx=12, pady=(0, 2), sticky="w"
        )
        self._appliance_menu_var = ctk.StringVar(value="")
        self._appliance_menu_widget = ctk.CTkOptionMenu(
            add_card,
            values=[""],
            variable=self._appliance_menu_var,
            fg_color=BG_SURFACE,
            button_color=ACCENT_MUTED,
            button_hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            width=220,
        )
        self._appliance_menu_widget.grid(row=4, column=0, columnspan=2, padx=12, pady=(0, 10), sticky="ew")

        self._make_primary_button(add_card, "Add Appliance", self._add_entry).grid(
            row=5, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="ew"
        )

        list_card = ctk.CTkFrame(
            self._manage_tab,
            fg_color=BG_SURFACE,
            corner_radius=10,
            border_width=1,
            border_color=BORDER_DEFAULT,
        )
        list_card.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        list_card.grid_columnconfigure(0, weight=1)
        list_card.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(list_card, text="Appliances In Room", font=FONT_HEADING, text_color=TEXT_PRIMARY).grid(
            row=0, column=0, padx=12, pady=(10, 8), sticky="w"
        )

        self._room_records_container = ctk.CTkScrollableFrame(list_card, fg_color=BG_SURFACE)
        self._room_records_container.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")

    def _build_panel_ranking_tabs(self) -> None:
        if self._appliance_tab is None or self._room_tab is None:
            return

        self._tab_appliance_container = ctk.CTkScrollableFrame(self._appliance_tab, fg_color=BG_SURFACE)
        self._tab_appliance_container.pack(fill="both", expand=True, padx=10, pady=10)

        self._tab_room_container = ctk.CTkScrollableFrame(self._room_tab, fg_color=BG_SURFACE)
        self._tab_room_container.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------- Helpers ----------
    def _make_card(self, parent: ctk.CTkBaseClass) -> ctk.CTkFrame:
        return ctk.CTkFrame(
            parent,
            fg_color=BG_SURFACE,
            corner_radius=12,
            border_width=1,
            border_color=BORDER_DEFAULT,
        )

    def _make_primary_button(self, parent: ctk.CTkBaseClass, text: str, command: Callable[[], None]) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            height=36,
            font=FONT_BODY,
        )

    def _make_secondary_button(self, parent: ctk.CTkBaseClass, text: str, command: Callable[[], None]) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            fg_color="transparent",
            border_width=1,
            border_color=BORDER_DEFAULT,
            hover_color=BG_SURFACE,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            height=36,
            width=92,
            font=FONT_BODY,
        )

    def _clear_container(self, container: ctk.CTkScrollableFrame | None) -> None:
        if container is None:
            return
        for widget in container.winfo_children():
            widget.destroy()

    def _build_room_hotspots(self) -> None:
        if self._map_label is None:
            return

        for room, (rel_x, rel_y) in self._room_hotspots.items():
            color = self._room_colors.get(room, ACCENT_PRIMARY)
            button = ctk.CTkButton(
                self._map_label,
                text=room,
                image=self._room_icon_images.get(room),
                compound="left",
                width=142,
                height=38,
                corner_radius=8,
                border_width=2,
                border_color=color,
                fg_color=BG_SURFACE,
                hover_color=ACCENT_MUTED,
                text_color=TEXT_PRIMARY,
                font=FONT_BODY,
                command=lambda room_name=room: self._on_room_click(room_name),
            )
            button.place(relx=rel_x, rely=rel_y, anchor="center")
            self._map_buttons[room] = button

    # ---------- Refresh ----------
    def _refresh_all(self) -> None:
        self._refresh_header()
        self._refresh_metrics()
        self._refresh_dashboard_rankings()
        self._refresh_panel()
        self._refresh_map_highlight()

    def _refresh_header(self) -> None:
        if self._user_value_label is not None:
            username = self._app.current_username or "-"
            self._user_value_label.configure(text=f"User: {username}")

    def _refresh_metrics(self) -> None:
        total = self._app.total_cost()
        budget_status = self._app.budget_status()

        if self._cost_value_label is not None:
            self._cost_value_label.configure(text=f"P{total:,.2f}")

        if self._budget_value_label is not None:
            status_color = STATUS_NOTSET
            if budget_status == "UNDER BUDGET":
                status_color = STATUS_UNDER
            elif budget_status == "OVER BUDGET":
                status_color = STATUS_OVER
            self._budget_value_label.configure(text=budget_status, text_color=status_color)

    def _refresh_dashboard_rankings(self) -> None:
        self._clear_container(self._appliance_rank_container)
        self._clear_container(self._room_rank_container)

        if self._appliance_rank_container is not None:
            ranked_appliances = self._app.ranked_appliances()[:3]
            if not ranked_appliances:
                ctk.CTkLabel(
                    self._appliance_rank_container,
                    text="Add appliances to see rankings.",
                    font=FONT_BODY,
                    text_color=TEXT_SECONDARY,
                ).pack(anchor="w", padx=6, pady=6)
            for idx, record in enumerate(ranked_appliances, start=1):
                ctk.CTkLabel(
                    self._appliance_rank_container,
                    text=f"{idx}. {record.appliance} ({record.room}) - P{record.monthly_cost:,.2f}",
                    font=FONT_BODY,
                    text_color=TEXT_PRIMARY,
                ).pack(anchor="w", padx=6, pady=2)

        if self._room_rank_container is not None:
            ranked_rooms = self._app.ranked_rooms()[:3]
            if not ranked_rooms:
                ctk.CTkLabel(
                    self._room_rank_container,
                    text="Add appliances to see rankings.",
                    font=FONT_BODY,
                    text_color=TEXT_SECONDARY,
                ).pack(anchor="w", padx=6, pady=6)
            for idx, (room, cost) in enumerate(ranked_rooms, start=1):
                ctk.CTkLabel(
                    self._room_rank_container,
                    text=f"{idx}. {room} - P{cost:,.2f}",
                    font=FONT_BODY,
                    text_color=TEXT_PRIMARY,
                ).pack(anchor="w", padx=6, pady=2)

    def _refresh_panel(self) -> None:
        room = self._selected_room
        has_room = room is not None

        if self._panel_title_label is not None:
            self._panel_title_label.configure(text=f"Room: {room if room else '-'}")
        if self._room_name_value_label is not None:
            self._room_name_value_label.configure(text=room if room else "-")

        if self._manage_tab is not None and self._panel_placeholder is not None:
            if has_room:
                self._panel_placeholder.grid_remove()
            elif not self._panel_placeholder.winfo_ismapped():
                self._panel_placeholder.grid()

        self._refresh_appliance_options()
        self._refresh_room_records()
        self._refresh_panel_rankings()

    def _refresh_appliance_options(self) -> None:
        if self._appliance_menu_widget is None or self._appliance_menu_var is None:
            return

        room = self._selected_room
        appliances = self._app.catalog.appliances_for_room(room) if room else []
        values = appliances or [""]
        self._appliance_menu_widget.configure(values=values)
        if appliances:
            if self._appliance_menu_var.get() not in appliances:
                self._appliance_menu_var.set(appliances[0])
        else:
            self._appliance_menu_var.set("")

    def _refresh_room_records(self) -> None:
        self._clear_container(self._room_records_container)
        if self._room_records_container is None:
            return

        room = self._selected_room
        if not room:
            ctk.CTkLabel(
                self._room_records_container,
                text="Select a room on the map to view records.",
                font=FONT_BODY,
                text_color=TEXT_SECONDARY,
            ).pack(anchor="w", padx=6, pady=6)
            return

        indexed_records = [(idx, rec) for idx, rec in enumerate(self._app.records) if rec.room == room]
        if not indexed_records:
            ctk.CTkLabel(
                self._room_records_container,
                text="No appliances added yet.",
                font=FONT_BODY,
                text_color=TEXT_SECONDARY,
            ).pack(anchor="w", padx=6, pady=6)
            return

        for idx, record in indexed_records:
            row = ctk.CTkFrame(
                self._room_records_container,
                fg_color=BG_ELEVATED,
                corner_radius=8,
                border_width=1,
                border_color=BORDER_DEFAULT,
            )
            row.pack(fill="x", padx=4, pady=4)
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=0)
            row.grid_columnconfigure(2, weight=0)

            ctk.CTkLabel(
                row,
                text=f"{record.appliance} | {record.usage_level} | P{record.monthly_cost:,.2f}",
                font=FONT_BODY,
                text_color=TEXT_PRIMARY,
            ).grid(row=0, column=0, padx=(10, 8), pady=8, sticky="w")

            self._make_secondary_button(row, "Edit", lambda i=idx: self._show_edit_modal(i)).grid(
                row=0, column=1, padx=(0, 6), pady=6
            )
            ctk.CTkButton(
                row,
                text="Delete",
                command=lambda i=idx: self._delete_record(i),
                fg_color="#7a1a2e",
                hover_color=ACCENT_PRIMARY,
                text_color=TEXT_PRIMARY,
                corner_radius=8,
                height=36,
                width=74,
                font=FONT_BODY,
            ).grid(row=0, column=2, padx=(0, 10), pady=6)

    def _refresh_panel_rankings(self) -> None:
        self._clear_container(self._tab_appliance_container)
        self._clear_container(self._tab_room_container)

        if self._tab_appliance_container is not None:
            ranked_appliances = self._app.ranked_appliances()
            if not ranked_appliances:
                ctk.CTkLabel(
                    self._tab_appliance_container,
                    text="Add appliances to see rankings.",
                    font=FONT_BODY,
                    text_color=TEXT_SECONDARY,
                ).pack(anchor="w", padx=6, pady=6)
            for idx, record in enumerate(ranked_appliances, start=1):
                ctk.CTkLabel(
                    self._tab_appliance_container,
                    text=f"{idx}. {record.appliance} ({record.room}) - P{record.monthly_cost:,.2f}",
                    font=FONT_BODY,
                    text_color=TEXT_PRIMARY,
                ).pack(anchor="w", padx=6, pady=2)

        if self._tab_room_container is not None:
            ranked_rooms = self._app.ranked_rooms()
            if not ranked_rooms:
                ctk.CTkLabel(
                    self._tab_room_container,
                    text="Add appliances to see rankings.",
                    font=FONT_BODY,
                    text_color=TEXT_SECONDARY,
                ).pack(anchor="w", padx=6, pady=6)
            for idx, (room, cost) in enumerate(ranked_rooms, start=1):
                ctk.CTkLabel(
                    self._tab_room_container,
                    text=f"{idx}. {room} - P{cost:,.2f}",
                    font=FONT_BODY,
                    text_color=TEXT_PRIMARY,
                ).pack(anchor="w", padx=6, pady=2)

    def _refresh_map_highlight(self) -> None:
        for room, button in self._map_buttons.items():
            accent = self._room_colors.get(room, ACCENT_PRIMARY)
            if room == self._selected_room:
                button.configure(fg_color=accent, hover_color=accent, text_color="#FFFFFF")
            else:
                button.configure(fg_color=BG_SURFACE, hover_color=ACCENT_MUTED, text_color=TEXT_PRIMARY)

    # ---------- Actions ----------
    def _on_room_click(self, room_name: str) -> None:
        self._selected_room = room_name
        self._refresh_all()

    def _add_entry(self) -> None:
        if self._selected_room is None or self._appliance_menu_var is None or self._usage_menu_var is None:
            return
        appliance = self._appliance_menu_var.get().strip()
        usage = self._usage_menu_var.get().strip()
        if not appliance:
            self._show_info_modal("Invalid Selection", "Please select an appliance.")
            return
        try:
            self._app.add_appliance_usage(self._selected_room, appliance, usage)
        except (ValueError, KeyError, RuntimeError) as exc:
            self._show_info_modal("Error", str(exc))
            return
        self._refresh_all()

    def _delete_record(self, index: int) -> None:
        accepted = self._show_confirm_dialog(
            "Delete Appliance",
            "Delete this appliance record?",
            destructive=True,
        )
        if not accepted:
            return
        try:
            self._app.delete_record_at(index)
        except (RuntimeError, IndexError) as exc:
            self._show_info_modal("Error", str(exc))
            return
        self._refresh_all()

    def _save_data(self) -> None:
        accepted = self._show_confirm_dialog("Save Session", "Save current records now?")
        if not accepted:
            return
        try:
            self._app.save_current_session()
        except RuntimeError as exc:
            self._show_info_modal("Error", str(exc))
            return
        self._show_info_modal("Saved", "Progress saved successfully.")

    def _logout(self) -> None:
        accepted = self._show_confirm_dialog(
            "Logout",
            "Logout current session?",
            destructive=True,
        )
        if not accepted:
            return
        self._app.current_username = None
        self._app.records = []
        self._app.budget = None
        self._selected_room = None
        if not self._startup_session_modal():
            self.destroy()
            return
        rooms = self._app.catalog.rooms()
        self._selected_room = rooms[0] if rooms else None
        self._refresh_all()

    # ---------- Modals ----------
    def _create_modal(self, title: str, width: int, height: int) -> ctk.CTkToplevel:
        modal = ctk.CTkToplevel(self)
        modal.title(title)
        modal.geometry(f"{width}x{height}")
        modal.resizable(False, False)
        modal.configure(fg_color=BG_ELEVATED)
        modal.transient(self)
        modal.grab_set()
        modal.focus_set()
        modal.bind("<Escape>", lambda _: modal.destroy())
        self._center_modal(modal)
        return modal

    def _center_modal(self, modal: ctk.CTkToplevel) -> None:
        modal.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - modal.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - modal.winfo_height()) // 2
        modal.geometry(f"+{x}+{y}")

    def _center_main_window(self) -> None:
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        if width <= 1 or height <= 1:
            # Fallback to requested defaults if actual size isn't ready yet.
            width, height = 1500, 920
        x = max(0, (self.winfo_screenwidth() - width) // 2)
        y = max(0, (self.winfo_screenheight() - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _show_confirm_dialog(self, title: str, message: str, destructive: bool = False) -> bool:
        modal = self._create_modal(title, 380, 190)
        result = {"ok": False}

        ctk.CTkLabel(modal, text=title, font=FONT_HEADING, text_color=TEXT_PRIMARY).pack(
            anchor="w", padx=20, pady=(18, 6)
        )
        ctk.CTkLabel(
            modal,
            text=message,
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            wraplength=330,
            justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 16))

        actions = ctk.CTkFrame(modal, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(0, 16))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        def cancel() -> None:
            modal.destroy()

        def confirm() -> None:
            result["ok"] = True
            modal.destroy()

        self._make_secondary_button(actions, "Cancel", cancel).grid(row=0, column=0, padx=(0, 6), sticky="ew")
        ctk.CTkButton(
            actions,
            text="Confirm",
            command=confirm,
            fg_color="#7a1a2e" if destructive else ACCENT_PRIMARY,
            hover_color=ACCENT_PRIMARY if destructive else ACCENT_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            height=36,
            font=FONT_BODY,
        ).grid(row=0, column=1, padx=(6, 0), sticky="ew")

        modal.wait_window()
        return bool(result["ok"])

    def _show_info_modal(self, title: str, message: str) -> None:
        modal = self._create_modal(title, 380, 180)
        ctk.CTkLabel(modal, text=title, font=FONT_HEADING, text_color=TEXT_PRIMARY).pack(
            anchor="w", padx=20, pady=(18, 6)
        )
        ctk.CTkLabel(
            modal,
            text=message,
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
            wraplength=330,
            justify="left",
        ).pack(anchor="w", padx=20, pady=(0, 16))

        self._make_primary_button(modal, "OK", modal.destroy).pack(fill="x", padx=20, pady=(0, 16))
        modal.wait_window()

    def _show_edit_modal(self, index: int) -> None:
        if index < 0 or index >= len(self._app.records):
            return
        record = self._app.records[index]

        modal = self._create_modal("Edit Appliance", 380, 230)
        ctk.CTkLabel(modal, text="Edit Appliance", font=FONT_HEADING, text_color=TEXT_PRIMARY).pack(
            anchor="w", padx=20, pady=(18, 8)
        )

        ctk.CTkLabel(modal, text=f"Appliance: {record.appliance}", font=FONT_CAPTION, text_color=TEXT_SECONDARY).pack(
            anchor="w", padx=20, pady=(0, 6)
        )

        usage_var = ctk.StringVar(value=record.usage_level)
        usage_menu = ctk.CTkOptionMenu(
            modal,
            values=list(USAGE_LEVELS.keys()),
            variable=usage_var,
            fg_color=BG_SURFACE,
            button_color=ACCENT_MUTED,
            button_hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            width=320,
        )
        usage_menu.pack(padx=20, pady=(0, 14), anchor="w")

        actions = ctk.CTkFrame(modal, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(0, 16))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        self._make_secondary_button(actions, "Cancel", modal.destroy).grid(row=0, column=0, padx=(0, 6), sticky="ew")

        def save_edit() -> None:
            try:
                self._app.update_record_usage_at(index, usage_var.get().strip())
            except (ValueError, IndexError) as exc:
                self._show_info_modal("Error", str(exc))
                return
            modal.destroy()
            self._refresh_all()

        self._make_primary_button(actions, "Save", save_edit).grid(row=0, column=1, padx=(6, 0), sticky="ew")
        modal.wait_window()

    def _show_budget_modal(self) -> None:
        modal = self._create_modal("Set Monthly Budget", 380, 230)
        ctk.CTkLabel(modal, text="Set Monthly Budget", font=FONT_HEADING, text_color=TEXT_PRIMARY).pack(
            anchor="w", padx=20, pady=(18, 8)
        )
        entry = ctk.CTkEntry(
            modal,
            placeholder_text="Enter amount in pesos",
            fg_color=BG_SURFACE,
            border_color=BORDER_DEFAULT,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            height=36,
            width=320,
        )
        entry.pack(anchor="w", padx=20, pady=(0, 4))

        error_label = ctk.CTkLabel(modal, text="", font=FONT_CAPTION, text_color=STATUS_OVER)
        error_label.pack(anchor="w", padx=20, pady=(0, 8))

        actions = ctk.CTkFrame(modal, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(0, 16))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        self._make_secondary_button(actions, "Cancel", modal.destroy).grid(row=0, column=0, padx=(0, 6), sticky="ew")

        def set_budget() -> None:
            raw = entry.get().replace(",", "").strip()
            try:
                value = float(raw)
                self._app.set_budget(value)
            except ValueError:
                error_label.configure(text="Please enter a valid number.")
                return
            modal.destroy()
            self._refresh_all()

        self._make_primary_button(actions, "Set Budget", set_budget).grid(row=0, column=1, padx=(6, 0), sticky="ew")
        modal.wait_window()

    def _startup_session_modal(self) -> bool:
        users = self._app.list_existing_users()
        modal = self._create_modal("Welcome to WattzUp", 420, 280)
        completed = {"ok": False}

        ctk.CTkLabel(modal, text="WattzUp", font=("Segoe UI", 20, "bold"), text_color=TEXT_PRIMARY).pack(
            pady=(20, 4)
        )
        ctk.CTkLabel(
            modal,
            text="Continue an existing session or create a new one.",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
        ).pack(pady=(0, 14))

        user_var = ctk.StringVar(value=users[0] if users else "")
        user_menu = ctk.CTkOptionMenu(
            modal,
            values=users if users else [""],
            variable=user_var,
            fg_color=BG_SURFACE,
            button_color=ACCENT_MUTED,
            button_hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            width=340,
        )
        user_menu.pack(pady=(0, 10))
        if not users:
            user_menu.configure(state="disabled")

        error_label = ctk.CTkLabel(modal, text="", font=FONT_CAPTION, text_color=STATUS_OVER)
        error_label.pack(pady=(0, 6))

        def continue_session() -> None:
            if not users:
                error_label.configure(text="No existing users found. Create a new session.")
                return
            try:
                self._app.continue_user_session(user_var.get())
            except ValueError as exc:
                error_label.configure(text=str(exc))
                return
            completed["ok"] = True
            modal.destroy()

        def create_session() -> None:
            modal.destroy()
            if self._show_create_user_modal():
                completed["ok"] = True

        actions = ctk.CTkFrame(modal, fg_color="transparent")
        actions.pack(fill="x", padx=24, pady=(4, 10))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        self._make_secondary_button(actions, "Continue", continue_session).grid(
            row=0, column=0, padx=(0, 6), sticky="ew"
        )
        self._make_primary_button(actions, "Create New Session", create_session).grid(
            row=0, column=1, padx=(6, 0), sticky="ew"
        )

        modal.protocol("WM_DELETE_WINDOW", lambda: (modal.destroy(), self.destroy()))
        modal.wait_window()
        return bool(completed["ok"])

    def _show_create_user_modal(self) -> bool:
        modal = self._create_modal("Create New Session", 400, 220)
        done = {"ok": False}

        ctk.CTkLabel(modal, text="Create New Session", font=FONT_HEADING, text_color=TEXT_PRIMARY).pack(
            anchor="w", padx=20, pady=(18, 8)
        )
        entry = ctk.CTkEntry(
            modal,
            placeholder_text="Enter username",
            fg_color=BG_SURFACE,
            border_color=BORDER_DEFAULT,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            width=340,
            height=36,
        )
        entry.pack(anchor="w", padx=20, pady=(0, 4))

        error_label = ctk.CTkLabel(modal, text="", font=FONT_CAPTION, text_color=STATUS_OVER)
        error_label.pack(anchor="w", padx=20, pady=(0, 8))

        actions = ctk.CTkFrame(modal, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(0, 16))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        self._make_secondary_button(actions, "Cancel", modal.destroy).grid(row=0, column=0, padx=(0, 6), sticky="ew")

        def create_now() -> None:
            try:
                self._app.create_new_user_session(entry.get().strip())
            except ValueError as exc:
                error_label.configure(text=str(exc))
                return
            done["ok"] = True
            modal.destroy()

        self._make_primary_button(actions, "Create", create_now).grid(row=0, column=1, padx=(6, 0), sticky="ew")
        modal.wait_window()
        return bool(done["ok"])

    # ---------- Window lifecycle ----------
    def _on_window_close(self) -> None:
        if self._app.records:
            accepted = self._show_confirm_dialog(
                "Exit WattzUp",
                "Save records before exiting?",
            )
            if accepted:
                try:
                    self._app.save_current_session()
                except RuntimeError:
                    pass
        self.destroy()


if __name__ == "__main__":
    app = WattzUpVisual()
    app.mainloop()

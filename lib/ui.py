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
    BORDER_FOCUS,
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

FONT_FAMILY_DISPLAY = "FunnelDisplay"
FONT_FAMILY_BODY = "FunnelSans"

FONT_HEADING = (FONT_FAMILY_DISPLAY, 16, "bold")
FONT_BODY = (FONT_FAMILY_BODY, 13)
FONT_CAPTION = (FONT_FAMILY_BODY, 11)
FONT_TITLE = (FONT_FAMILY_DISPLAY, 18, "bold")
FONT_METRIC_LARGE = (FONT_FAMILY_DISPLAY, 22, "bold")
FONT_METRIC_MEDIUM = (FONT_FAMILY_DISPLAY, 20, "bold")
FONT_CARD_HEADING = (FONT_FAMILY_DISPLAY, 16, "bold")
FONT_CARD_SUBHEADING = (FONT_FAMILY_DISPLAY, 15, "bold")
FONT_MODAL_BRAND = (FONT_FAMILY_DISPLAY, 20, "bold")
FIELD_BG = BG_ELEVATED
SIDEBAR_EXPANDED_WIDTH = 236
SIDEBAR_COLLAPSED_WIDTH = 76


class WattzUpVisual(ctk.CTk):
    """CustomTkinter desktop application for WattzUp."""

    def __init__(self, application_service: WattzUpApplicationService | None = None) -> None:
        super().__init__()
        self._app = application_service or create_default_application_service()
        self._register_custom_fonts()

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
        self._nav_icon_glyphs = {
            "save": "\U000F0193",
            "budget": "\U000F0114",
            "logout": "\U000F0343",
        }

        self._selected_room: str | None = None
        self._map_buttons: dict[str, ctk.CTkButton] = {}
        self._room_icon_images: dict[str, ctk.CTkImage] = {}
        self._nav_icon_images: dict[str, ctk.CTkImage] = {}
        self._map_label: ctk.CTkLabel | None = None
        self._map_back_button: ctk.CTkButton | None = None

        self._map_source: Image.Image | None = None
        self._map_image: ctk.CTkImage | None = None
        self._map_size = (900, 620)
        self._map_zoom_scale = 2.0
        self._map_zoomed_room: str | None = None
        self._map_view_box: tuple[float, float, float, float] | None = None
        self._startup_center_attempts = 0
        self._usage_display_map = {
            "Heavy": "\u26A1 Heavy",
            "Moderate": "\u25C9 Moderate",
            "Eco": "\U0001F343 Eco",
        }
        self._custom_usage_display = "\u23F1 Custom (hours/day)"
        self._usage_inverse_display_map = {display: raw for raw, display in self._usage_display_map.items()}

        self._user_value_label: ctk.CTkLabel | None = None
        self._left_sidebar: ctk.CTkFrame | None = None
        self._sidebar_title_label: ctk.CTkLabel | None = None
        self._sidebar_toggle_button: ctk.CTkButton | None = None
        self._sidebar_save_button: ctk.CTkButton | None = None
        self._sidebar_budget_button: ctk.CTkButton | None = None
        self._sidebar_logout_button: ctk.CTkButton | None = None
        self._sidebar_collapsed = True
        self._cost_value_label: ctk.CTkLabel | None = None
        self._cost_budget_suffix_label: ctk.CTkLabel | None = None
        self._budget_value_label: ctk.CTkLabel | None = None
        self._ranking_mode_var: ctk.StringVar | None = None
        self._ranking_mode_toggle: ctk.CTkSegmentedButton | None = None
        self._ranking_container: ctk.CTkScrollableFrame | None = None
        self._overview_cost_card: ctk.CTkFrame | None = None
        self._overview_budget_card: ctk.CTkFrame | None = None
        self._overview_rankings_card: ctk.CTkFrame | None = None
        self._panel_title_label: ctk.CTkLabel | None = None
        self._panel_tabview: ctk.CTkTabview | None = None
        self._manage_tab: ctk.CTkFrame | None = None
        self._appliance_tab: ctk.CTkFrame | None = None
        self._room_tab: ctk.CTkFrame | None = None
        self._body_frame: ctk.CTkFrame | None = None
        self._left_content_frame: ctk.CTkFrame | None = None
        self._right_sidebar: ctk.CTkFrame | None = None
        self._right_sidebar_visible = True
        self._room_name_value_label: ctk.CTkLabel | None = None
        self._appliance_menu_var: ctk.StringVar | None = None
        self._usage_menu_var: ctk.StringVar | None = None
        self._custom_usage_entry: ctk.CTkEntry | None = None
        self._appliance_menu_widget: ctk.CTkComboBox | None = None
        self._appliance_wattage_value_label: ctk.CTkLabel | None = None
        self._room_records_container: ctk.CTkScrollableFrame | None = None
        self._tab_appliance_container: ctk.CTkScrollableFrame | None = None
        self._tab_room_container: ctk.CTkScrollableFrame | None = None
        self._panel_placeholder: ctk.CTkLabel | None = None
        self._load_assets()
        self._build_layout()
        self._schedule_startup_centering()

        if not self._startup_session_modal():
            self.destroy()
            return

        self._refresh_all()
        self._schedule_startup_centering()

    def _register_custom_fonts(self) -> None:
        font_paths = (
            os.path.join("assets", "fonts", "FunnelDisplay.ttf"),
            os.path.join("assets", "fonts", "FunnelSans.ttf"),
        )
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    ctk.FontManager.load_font(font_path)
                except Exception:
                    # If font registration fails, tkinter will fall back to the next available family.
                    continue

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

        for key, glyph in self._nav_icon_glyphs.items():
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
            self._nav_icon_images[key] = ctk.CTkImage(
                light_image=canvas,
                dark_image=canvas,
                size=(16, 16),
            )

    def _build_layout(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self._build_left_sidebar()
        self._build_body()

    def _build_left_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(
            self,
            fg_color=BG_ELEVATED,
            width=SIDEBAR_COLLAPSED_WIDTH,
            corner_radius=0,
            border_width=1,
            border_color=BORDER_DEFAULT,
        )
        sidebar.grid(row=0, column=0, sticky="nsw")
        sidebar.grid_propagate(False)
        sidebar.grid_rowconfigure(4, weight=1)
        sidebar.grid_columnconfigure(0, weight=1)
        self._left_sidebar = sidebar

        header = ctk.CTkFrame(sidebar, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 8))
        header.grid_columnconfigure(0, weight=1)
        header.grid_columnconfigure(1, weight=0)

        self._sidebar_title_label = ctk.CTkLabel(
            header,
            text="\u26A1",
            font=(FONT_FAMILY_DISPLAY, 26, "bold"),
            text_color=ACCENT_PRIMARY,
        )
        self._sidebar_title_label.grid(row=0, column=0, sticky="w")

        self._sidebar_toggle_button = ctk.CTkButton(
            header,
            text="\u203A",
            command=self._toggle_left_sidebar,
            fg_color="transparent",
            border_width=1,
            border_color=BORDER_DEFAULT,
            hover_color=BG_SURFACE,
            text_color=TEXT_PRIMARY,
            width=30,
            height=30,
            corner_radius=8,
            font=FONT_BODY,
        )
        self._sidebar_toggle_button.grid(row=0, column=1, sticky="e")

        self._user_value_label = ctk.CTkLabel(sidebar, text="User: -", font=FONT_BODY, text_color=TEXT_SECONDARY)
        self._user_value_label.grid(row=1, column=0, padx=18, pady=(0, 14), sticky="w")

        self._sidebar_save_button = self._make_secondary_button(
            sidebar,
            "Save",
            self._save_data,
            icon=self._nav_icon_images.get("save"),
        )
        self._sidebar_save_button.grid(row=2, column=0, padx=14, pady=(8, 8), sticky="ew")
        self._sidebar_budget_button = self._make_secondary_button(
            sidebar,
            "Budget",
            self._show_budget_modal,
            icon=self._nav_icon_images.get("budget"),
        )
        self._sidebar_budget_button.grid(row=3, column=0, padx=14, pady=(0, 8), sticky="ew")
        self._sidebar_logout_button = self._make_secondary_button(
            sidebar,
            "Logout",
            self._logout,
            icon=self._nav_icon_images.get("logout"),
        )
        self._sidebar_logout_button.grid(row=5, column=0, padx=14, pady=(0, 14), sticky="ew")
        self._refresh_left_sidebar()

    def _build_body(self) -> None:
        body = ctk.CTkFrame(self, fg_color=BG_BASE, corner_radius=0)
        body.grid(row=0, column=1, sticky="nsew")
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=0)
        body.grid_rowconfigure(0, weight=1)
        self._body_frame = body

        left = ctk.CTkFrame(body, fg_color=BG_BASE, corner_radius=0)
        left.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=(16, 16))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(0, weight=0)
        left.grid_rowconfigure(1, weight=1)
        self._left_content_frame = left

        overview = ctk.CTkFrame(left, fg_color=BG_BASE, corner_radius=0)
        overview.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        overview.grid_columnconfigure(0, weight=1)
        overview.grid_columnconfigure(1, weight=1)
        overview.grid_rowconfigure(0, weight=1)
        overview.grid_rowconfigure(1, weight=1)

        self._build_metrics_row(overview)
        self._build_rankings_row(overview)

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
        self._right_sidebar = right

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
        cost_card = self._make_card(parent)
        cost_card.grid(row=0, column=0, sticky="ew")
        cost_card.grid_columnconfigure(0, weight=1)
        self._overview_cost_card = cost_card

        ctk.CTkLabel(cost_card, text="Estimated Monthly Cost", font=FONT_CAPTION, text_color=TEXT_SECONDARY).grid(
            row=0, column=0, padx=16, pady=(12, 2), sticky="w"
        )

        cost_stack = ctk.CTkFrame(cost_card, fg_color="transparent")
        cost_stack.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="w")
        self._cost_value_label = ctk.CTkLabel(
            cost_stack,
            text="P0.00",
            font=FONT_METRIC_LARGE,
            text_color=TEXT_PRIMARY,
        )
        self._cost_value_label.pack(side="left")
        self._cost_budget_suffix_label = ctk.CTkLabel(
            cost_stack,
            text=" / No budget",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
        )
        self._cost_budget_suffix_label.pack(side="left", padx=(8, 0), pady=(2, 0))

        budget_card = self._make_card(parent)
        budget_card.grid(row=1, column=0, sticky="ew", pady=(0, 0))
        budget_card.grid_columnconfigure(0, weight=1)
        self._overview_budget_card = budget_card

        ctk.CTkLabel(budget_card, text="Budget Status", font=FONT_CAPTION, text_color=TEXT_SECONDARY).grid(
            row=0, column=0, padx=16, pady=(12, 2), sticky="w"
        )

        self._budget_value_label = ctk.CTkLabel(
            budget_card,
            text="NOT SET",
            font=FONT_METRIC_MEDIUM,
            text_color=STATUS_NOTSET,
        )
        self._budget_value_label.grid(row=1, column=0, padx=16, pady=(0, 12), sticky="w")

    def _build_rankings_row(self, parent: ctk.CTkFrame) -> None:
        rankings_card = self._make_card(parent)
        rankings_card.grid(row=0, column=1, rowspan=2, sticky="nsew", padx=(12, 0))
        rankings_card.grid_columnconfigure(0, weight=1)
        rankings_card.grid_columnconfigure(1, weight=0)
        rankings_card.grid_rowconfigure(1, weight=1)
        self._overview_rankings_card = rankings_card

        ctk.CTkLabel(rankings_card, text="Top Rankings", font=FONT_HEADING, text_color=TEXT_PRIMARY).grid(
            row=0, column=0, padx=(16, 8), pady=(12, 8), sticky="w"
        )

        self._ranking_mode_var = ctk.StringVar(value="Appliance")
        self._ranking_mode_toggle = ctk.CTkSegmentedButton(
            rankings_card,
            values=["Appliance", "Room"],
            variable=self._ranking_mode_var,
            command=lambda _: self._refresh_dashboard_rankings(),
            selected_color=ACCENT_PRIMARY,
            selected_hover_color=ACCENT_HOVER,
            unselected_color=BG_SURFACE,
            unselected_hover_color=ACCENT_MUTED,
            text_color=TEXT_PRIMARY,
            font=FONT_CAPTION,
            corner_radius=8,
        )
        self._ranking_mode_toggle.grid(row=0, column=1, padx=(8, 14), pady=(12, 8), sticky="e")

        self._ranking_container = ctk.CTkScrollableFrame(rankings_card, fg_color=BG_SURFACE, height=132)
        self._ranking_container.grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="nsew")
        self.after(0, self._sync_overview_heights)

    def _sync_overview_heights(self) -> None:
        if (
            self._overview_cost_card is None
            or self._overview_budget_card is None
            or self._overview_rankings_card is None
        ):
            return

        self.update_idletasks()
        top = self._overview_cost_card.winfo_y()
        bottom = self._overview_budget_card.winfo_y() + self._overview_budget_card.winfo_height()
        target_height = max(120, bottom - top)

        self._overview_rankings_card.configure(height=target_height)
        self._overview_rankings_card.grid_propagate(False)

    def _build_map_area(self, parent: ctk.CTkFrame) -> None:
        map_card = self._make_card(parent)
        map_card.grid(row=1, column=0, sticky="nsew")
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
        self._map_label.bind("<Button-1>", self._on_map_background_click)

        self._map_back_button = self._make_secondary_button(
            map_card,
            "Back To Full View",
            self._reset_map_zoom,
        )
        self._map_back_button.place(x=24, y=22)
        self._map_back_button.place_forget()

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

        self._usage_menu_var = ctk.StringVar(value=self._usage_to_display("Moderate"))

        def on_usage_change(selected: str) -> None:
            self._set_custom_usage_state(selected == self._custom_usage_display)

        usage_menu = ctk.CTkComboBox(
            add_card,
            values=self._usage_display_values(),
            variable=self._usage_menu_var,
            command=on_usage_change,
            state="readonly",
            fg_color=FIELD_BG,
            border_color=BORDER_DEFAULT,
            button_color=ACCENT_MUTED,
            button_hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            width=170,
        )
        usage_menu.grid(row=2, column=1, padx=12, pady=(0, 8), sticky="ew")
        self._bind_field_focus_border(usage_menu)

        self._custom_usage_entry = ctk.CTkEntry(
            add_card,
            placeholder_text="Custom hours/day (1-24)",
            fg_color=FIELD_BG,
            border_color=BORDER_DEFAULT,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            width=170,
        )
        self._custom_usage_entry.grid(row=3, column=1, padx=12, pady=(0, 8), sticky="ew")
        self._bind_field_focus_border(self._custom_usage_entry)
        self._set_custom_usage_state(False)

        ctk.CTkLabel(add_card, text="Appliance", font=FONT_CAPTION, text_color=TEXT_SECONDARY).grid(
            row=4, column=0, padx=12, pady=(0, 2), sticky="w"
        )
        self._appliance_menu_var = ctk.StringVar(value="")
        self._appliance_menu_widget = ctk.CTkComboBox(
            add_card,
            values=[""],
            variable=self._appliance_menu_var,
            command=lambda _: self._refresh_selected_appliance_wattage(),
            state="readonly",
            fg_color=FIELD_BG,
            border_color=BORDER_DEFAULT,
            button_color=ACCENT_MUTED,
            button_hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            width=220,
        )
        self._appliance_menu_widget.grid(row=5, column=0, columnspan=2, padx=12, pady=(0, 10), sticky="ew")
        self._bind_field_focus_border(self._appliance_menu_widget)

        ctk.CTkLabel(add_card, text="Wattage", font=FONT_CAPTION, text_color=TEXT_SECONDARY).grid(
            row=6, column=0, padx=12, pady=(0, 2), sticky="w"
        )
        self._appliance_wattage_value_label = ctk.CTkLabel(
            add_card,
            text="-",
            font=FONT_BODY,
            text_color=TEXT_PRIMARY,
        )
        self._appliance_wattage_value_label.grid(row=6, column=1, padx=12, pady=(0, 8), sticky="w")

        self._make_primary_button(add_card, "Add Appliance", self._add_entry).grid(
            row=7, column=0, columnspan=2, padx=12, pady=(0, 12), sticky="ew"
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

    def _make_secondary_button(
        self,
        parent: ctk.CTkBaseClass,
        text: str,
        command: Callable[[], None],
        icon: ctk.CTkImage | None = None,
    ) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent,
            text=text,
            command=command,
            image=icon,
            compound="left",
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

    def _bind_field_focus_border(self, widget: ctk.CTkBaseClass) -> None:
        def on_focus_in(_: object) -> None:
            try:
                widget.configure(border_color=BORDER_FOCUS)
            except Exception:
                return

        def on_focus_out(_: object) -> None:
            try:
                widget.configure(border_color=BORDER_DEFAULT)
            except Exception:
                return

        widget.bind("<FocusIn>", on_focus_in, add="+")
        widget.bind("<FocusOut>", on_focus_out, add="+")

    def _clear_container(self, container: ctk.CTkScrollableFrame | None) -> None:
        if container is None:
            return
        for widget in container.winfo_children():
            widget.destroy()

    def _pack_subtle_divider(
        self,
        container: ctk.CTkScrollableFrame,
        padx: tuple[int, int] = (6, 6),
        pady: tuple[int, int] = (4, 4),
    ) -> None:
        ctk.CTkFrame(
            container,
            fg_color=BORDER_DEFAULT,
            height=2,
            corner_radius=0,
        ).pack(fill="x", padx=padx, pady=pady)

    def _build_room_hotspots(self) -> None:
        if self._map_label is None:
            return

        for room, (rel_x, rel_y) in self._room_hotspots.items():
            color = self._room_colors.get(room, ACCENT_PRIMARY)
            button = ctk.CTkButton(
                self._map_label,
                text=self._room_button_text(room, 0),
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
            self._map_buttons[room] = button

        self._refresh_map_view()

    def _refresh_map_view(self) -> None:
        if self._map_source is None or self._map_label is None:
            return

        source_w, source_h = self._map_source.size
        if self._map_zoomed_room is None or self._map_zoomed_room not in self._room_hotspots:
            self._map_view_box = (0.0, 0.0, float(source_w), float(source_h))
            visible_source = self._map_source
        else:
            rel_x, rel_y = self._room_hotspots[self._map_zoomed_room]
            center_x = rel_x * source_w
            center_y = rel_y * source_h

            view_w = source_w / self._map_zoom_scale
            view_h = source_h / self._map_zoom_scale

            left = max(0.0, min(center_x - (view_w / 2), source_w - view_w))
            top = max(0.0, min(center_y - (view_h / 2), source_h - view_h))
            right = left + view_w
            bottom = top + view_h
            self._map_view_box = (left, top, right, bottom)

            crop = self._map_source.crop((int(left), int(top), int(right), int(bottom)))
            resampling = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
            visible_source = crop.resize(self._map_size, resampling)

        self._map_image = ctk.CTkImage(light_image=visible_source, dark_image=visible_source, size=self._map_size)
        self._map_label.configure(image=self._map_image)
        self._reposition_room_hotspots()
        self._refresh_back_button_visibility()

    def _reposition_room_hotspots(self) -> None:
        if self._map_label is None or self._map_view_box is None:
            return

        left, top, right, bottom = self._map_view_box
        span_x = max(1.0, right - left)
        span_y = max(1.0, bottom - top)
        source_w, source_h = self._map_source.size if self._map_source is not None else (1, 1)

        for room, button in self._map_buttons.items():
            rel_x, rel_y = self._room_hotspots[room]
            source_x = rel_x * source_w
            source_y = rel_y * source_h
            mapped_x = (source_x - left) / span_x
            mapped_y = (source_y - top) / span_y

            if 0.0 <= mapped_x <= 1.0 and 0.0 <= mapped_y <= 1.0:
                button.place(relx=mapped_x, rely=mapped_y, anchor="center")
            else:
                button.place_forget()

    def _refresh_back_button_visibility(self) -> None:
        if self._map_back_button is None:
            return
        if self._map_zoomed_room is None:
            self._map_back_button.place_forget()
        else:
            self._map_back_button.place(x=24, y=22)

    def _reset_map_zoom(self) -> None:
        self._map_zoomed_room = None
        self._refresh_map_view()
        self._refresh_map_highlight()

    def _room_record_counts(self) -> dict[str, int]:
        counts = {room: 0 for room in self._room_hotspots.keys()}
        for record in self._app.records:
            counts[record.room] = counts.get(record.room, 0) + 1
        return counts

    @staticmethod
    def _room_button_text(room: str, count: int) -> str:
        return f"{room} [{count}]"

    def _usage_display_values(self) -> list[str]:
        values = [self._usage_to_display(usage) for usage in USAGE_LEVELS.keys()]
        values.append(self._custom_usage_display)
        return values

    def _usage_to_display(self, usage: str) -> str:
        if usage.startswith("Custom ("):
            return usage
        return self._usage_display_map.get(usage, usage)

    def _usage_to_raw(self, usage_or_display: str) -> str:
        return self._usage_inverse_display_map.get(usage_or_display, usage_or_display)

    @staticmethod
    def _usage_icon(usage_level: str) -> str:
        if usage_level.startswith("Custom ("):
            return "\u23F1"
        mapping = {
            "Heavy": "\u26A1",
            "Moderate": "\u25C9",
            "Eco": "\U0001F343",
        }
        return mapping.get(usage_level, "\u25C9")

    def _set_custom_usage_state(self, enabled: bool) -> None:
        if self._custom_usage_entry is None:
            return
        if enabled:
            self._custom_usage_entry.grid()
            self._custom_usage_entry.configure(state="normal")
        else:
            self._custom_usage_entry.delete(0, "end")
            self._custom_usage_entry.configure(state="disabled")
            self._custom_usage_entry.grid_remove()

    def _refresh_selected_appliance_wattage(self) -> None:
        if self._appliance_wattage_value_label is None or self._appliance_menu_var is None:
            return
        room = self._selected_room
        appliance = self._appliance_menu_var.get().strip()
        if not room or not appliance:
            self._appliance_wattage_value_label.configure(text="-")
            return
        try:
            wattage = self._app.catalog.wattage_for(room, appliance)
        except KeyError:
            self._appliance_wattage_value_label.configure(text="-")
            return
        self._appliance_wattage_value_label.configure(text=f"{wattage}W")

    # ---------- Refresh ----------
    def _refresh_all(self) -> None:
        self._refresh_header()
        self._refresh_left_sidebar()
        self._refresh_metrics()
        self._refresh_dashboard_rankings()
        self._refresh_sidebar_visibility()
        self._refresh_panel()
        self._refresh_map_view()
        self._refresh_map_highlight()

    def _toggle_left_sidebar(self) -> None:
        self._sidebar_collapsed = not self._sidebar_collapsed
        self._refresh_left_sidebar()

    def _refresh_left_sidebar(self) -> None:
        if self._left_sidebar is None:
            return

        self._left_sidebar.configure(
            width=SIDEBAR_COLLAPSED_WIDTH if self._sidebar_collapsed else SIDEBAR_EXPANDED_WIDTH
        )
        self._left_sidebar.update_idletasks()

        if self._sidebar_toggle_button is not None:
            self._sidebar_toggle_button.configure(text="\u203A" if self._sidebar_collapsed else "\u2039")

        if self._user_value_label is not None:
            if self._sidebar_collapsed:
                self._user_value_label.grid_remove()
            else:
                self._user_value_label.grid()

        button_specs = (
            (self._sidebar_save_button, "Save"),
            (self._sidebar_budget_button, "Budget"),
            (self._sidebar_logout_button, "Logout"),
        )
        for button, label in button_specs:
            if button is None:
                continue
            button.configure(
                text="" if self._sidebar_collapsed else label,
                width=42 if self._sidebar_collapsed else 104,
                anchor="center" if self._sidebar_collapsed else "w",
            )

    def _refresh_sidebar_visibility(self) -> None:
        if self._body_frame is None or self._left_content_frame is None or self._right_sidebar is None:
            return

        should_show = self._selected_room is not None
        if should_show == self._right_sidebar_visible:
            return

        if should_show:
            self._body_frame.grid_columnconfigure(1, weight=0, minsize=420)
            self._left_content_frame.grid_configure(padx=(16, 8))
            self._right_sidebar.grid(row=0, column=1, sticky="nsew", padx=(8, 16), pady=(16, 16))
        else:
            self._right_sidebar.grid_remove()
            self._body_frame.grid_columnconfigure(1, weight=0, minsize=0)
            self._left_content_frame.grid_configure(padx=(16, 16))

        self._right_sidebar_visible = should_show
        self.after(0, self._sync_overview_heights)

    def _refresh_header(self) -> None:
        if self._user_value_label is not None:
            username = self._app.current_username or "-"
            self._user_value_label.configure(text=f"User: {username}")

    def _refresh_metrics(self) -> None:
        total = self._app.total_cost()
        budget_status = self._app.budget_status()
        budget_value = self._app.budget

        if self._cost_value_label is not None:
            self._cost_value_label.configure(text=f"P{total:,.2f}")
        if self._cost_budget_suffix_label is not None:
            if budget_value is None:
                self._cost_budget_suffix_label.configure(text=" / No budget", text_color=TEXT_SECONDARY)
            else:
                self._cost_budget_suffix_label.configure(text=f" / P{budget_value:,.2f}", text_color=TEXT_SECONDARY)

        if self._budget_value_label is not None:
            status_color = STATUS_NOTSET
            if budget_status == "UNDER BUDGET":
                status_color = STATUS_UNDER
            elif budget_status == "OVER BUDGET":
                status_color = STATUS_OVER
            self._budget_value_label.configure(text=budget_status, text_color=status_color)

    def _refresh_dashboard_rankings(self) -> None:
        self._clear_container(self._ranking_container)
        if self._ranking_container is None:
            return

        mode = self._ranking_mode_var.get() if self._ranking_mode_var is not None else "Appliance"
        if mode == "Room":
            ranked_rooms = self._app.ranked_rooms()[:5]
            if not ranked_rooms:
                ctk.CTkLabel(
                    self._ranking_container,
                    text="Add appliances to see room rankings.",
                    font=FONT_BODY,
                    text_color=TEXT_SECONDARY,
                ).pack(anchor="w", padx=6, pady=6)
                return
            total = len(ranked_rooms)
            for idx, (room, cost) in enumerate(ranked_rooms, start=1):
                ctk.CTkLabel(
                    self._ranking_container,
                    text=f"{idx}. {room} - P{cost:,.2f}",
                    font=FONT_BODY,
                    text_color=TEXT_PRIMARY,
                ).pack(anchor="w", padx=6, pady=2)
                if idx < total:
                    self._pack_subtle_divider(self._ranking_container)
            return

        ranked_appliances = self._app.ranked_appliances()[:5]
        if not ranked_appliances:
            ctk.CTkLabel(
                self._ranking_container,
                text="Add appliances to see appliance rankings.",
                font=FONT_BODY,
                text_color=TEXT_SECONDARY,
            ).pack(anchor="w", padx=6, pady=6)
            return
        total = len(ranked_appliances)
        for idx, record in enumerate(ranked_appliances, start=1):
            ctk.CTkLabel(
                self._ranking_container,
                text=f"{idx}. {record.appliance} ({record.room}, {record.wattage}W) - P{record.monthly_cost:,.2f}",
                font=FONT_BODY,
                text_color=TEXT_PRIMARY,
            ).pack(anchor="w", padx=6, pady=2)
            if idx < total:
                self._pack_subtle_divider(self._ranking_container)

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
        self._refresh_selected_appliance_wattage()

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

        total = len(indexed_records)
        for position, (idx, record) in enumerate(indexed_records, start=1):
            row = ctk.CTkFrame(
                self._room_records_container,
                fg_color="transparent",
                corner_radius=0,
                border_width=0,
            )
            row.pack(fill="x", padx=2, pady=1)
            row.grid_columnconfigure(0, weight=1)
            row.grid_columnconfigure(1, weight=0)
            row.grid_columnconfigure(2, weight=0)

            ctk.CTkLabel(
                row,
                text=f"{self._usage_icon(record.usage_level)} {record.appliance} - P{record.monthly_cost:,.2f}",
                font=FONT_BODY,
                text_color=TEXT_PRIMARY,
            ).grid(row=0, column=0, padx=(2, 8), pady=2, sticky="w")

            ctk.CTkButton(
                row,
                text="\u270E",
                command=lambda i=idx: self._show_edit_modal(i),
                fg_color="transparent",
                hover_color=BG_SURFACE,
                text_color=TEXT_SECONDARY,
                width=28,
                height=28,
                corner_radius=8,
                border_width=0,
                font=FONT_CARD_HEADING,
            ).grid(row=0, column=1, padx=(0, 2), pady=1)
            ctk.CTkButton(
                row,
                text="\U0001F5D1",
                command=lambda i=idx: self._delete_record(i),
                fg_color="transparent",
                hover_color=BG_SURFACE,
                text_color=STATUS_OVER,
                corner_radius=8,
                height=28,
                width=28,
                border_width=0,
                font=FONT_CARD_SUBHEADING,
            ).grid(row=0, column=2, padx=(0, 2), pady=1)
            if position < total:
                self._pack_subtle_divider(self._room_records_container, padx=(4, 4), pady=(3, 3))

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
                    text=f"{idx}. {record.appliance} ({record.room}, {record.wattage}W) - P{record.monthly_cost:,.2f}",
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
        room_counts = self._room_record_counts()
        for room, button in self._map_buttons.items():
            accent = self._room_colors.get(room, ACCENT_PRIMARY)
            button.configure(text=self._room_button_text(room, room_counts.get(room, 0)))
            if room == self._selected_room:
                button.configure(fg_color=accent, hover_color=accent, text_color="#FFFFFF")
            else:
                button.configure(fg_color=BG_SURFACE, hover_color=ACCENT_MUTED, text_color=TEXT_PRIMARY)

    # ---------- Actions ----------
    def _on_room_click(self, room_name: str) -> None:
        self._selected_room = room_name
        self._map_zoomed_room = room_name
        self._refresh_all()

    def _on_map_background_click(self, _: object | None = None) -> None:
        self._selected_room = None
        self._map_zoomed_room = None
        self._refresh_all()

    def _add_entry(self) -> None:
        if self._selected_room is None or self._appliance_menu_var is None or self._usage_menu_var is None:
            return
        appliance = self._appliance_menu_var.get().strip()
        usage_selection = self._usage_menu_var.get().strip()
        usage = self._usage_to_raw(usage_selection)
        custom_hours: float | None = None

        if usage_selection == self._custom_usage_display:
            if self._custom_usage_entry is None:
                self._show_info_modal("Invalid Selection", "Custom usage field is unavailable.")
                return
            raw_hours = self._custom_usage_entry.get().strip()
            try:
                custom_hours = float(raw_hours)
            except ValueError:
                self._show_info_modal("Invalid Selection", "Enter whole-number custom usage hours (1-24).")
                return
            usage = "Custom"
        if not appliance:
            self._show_info_modal("Invalid Selection", "Please select an appliance.")
            return
        try:
            self._app.add_appliance_usage(self._selected_room, appliance, usage, custom_hours_per_day=custom_hours)
        except (ValueError, KeyError, RuntimeError) as exc:
            self._show_info_modal("Error", str(exc))
            return
        if self._custom_usage_entry is not None:
            self._custom_usage_entry.delete(0, "end")
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
        self._selected_room = None
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
        # Recenter after idle because some Windows/Tk setups finalize geometry slightly later.
        modal.after(10, lambda: self._safe_center_modal(modal))
        return modal

    def _safe_center_modal(self, modal: ctk.CTkToplevel) -> None:
        if not modal.winfo_exists():
            return
        self._center_modal(modal)

    def _center_modal(self, modal: ctk.CTkToplevel) -> None:
        self.update_idletasks()
        modal.update_idletasks()

        modal_w = max(1, modal.winfo_width())
        modal_h = max(1, modal.winfo_height())
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()

        parent_mapped = self.winfo_ismapped()
        parent_w = self.winfo_width()
        parent_h = self.winfo_height()

        if parent_mapped and parent_w > 1 and parent_h > 1:
            x = self.winfo_x() + (parent_w - modal_w) // 2
            y = self.winfo_y() + (parent_h - modal_h) // 2
        else:
            x = (screen_w - modal_w) // 2
            y = (screen_h - modal_h) // 2

        max_x = max(0, screen_w - modal_w)
        max_y = max(0, screen_h - modal_h)
        x = max(0, min(x, max_x))
        y = max(0, min(y, max_y))
        modal.geometry(f"+{x}+{y}")

    def _center_main_window(self) -> None:
        self.update_idletasks()
        geometry = self.geometry().split("+")[0]
        width = 1500
        height = 920
        if "x" in geometry:
            parts = geometry.split("x", 1)
            if len(parts) == 2:
                try:
                    width = int(parts[0])
                    height = int(parts[1])
                except ValueError:
                    width = max(self.winfo_width(), 1500)
                    height = max(self.winfo_height(), 920)
        else:
            width = max(self.winfo_width(), 1500)
            height = max(self.winfo_height(), 920)

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        width = min(width, screen_w)
        height = min(height, screen_h)
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _schedule_startup_centering(self) -> None:
        self._startup_center_attempts = 0
        self.after(0, self._center_main_window_once_mapped)

    def _center_main_window_once_mapped(self) -> None:
        # On some Windows setups, CTk/Tk applies the real top-level position a bit later.
        # Retry centering briefly after map to prevent ending up at a screen corner.
        self._center_main_window()
        self._startup_center_attempts += 1
        if self._startup_center_attempts < 6:
            self.after(120, self._center_main_window_once_mapped)

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

        initial_usage = self._usage_to_display(record.usage_level)
        if record.usage_level.startswith("Custom ("):
            initial_usage = self._custom_usage_display
        usage_var = ctk.StringVar(value=initial_usage)
        usage_menu = ctk.CTkComboBox(
            modal,
            values=self._usage_display_values(),
            variable=usage_var,
            state="readonly",
            fg_color=FIELD_BG,
            border_color=BORDER_DEFAULT,
            button_color=ACCENT_MUTED,
            button_hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            width=320,
        )
        usage_menu.pack(padx=20, pady=(0, 14), anchor="w")
        self._bind_field_focus_border(usage_menu)

        custom_usage_entry = ctk.CTkEntry(
            modal,
            placeholder_text="Custom hours/day (1-24)",
            fg_color=FIELD_BG,
            border_color=BORDER_DEFAULT,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            width=320,
        )
        custom_usage_entry.pack(padx=20, pady=(0, 14), anchor="w")
        self._bind_field_focus_border(custom_usage_entry)

        if record.usage_level.startswith("Custom ("):
            custom_usage_entry.insert(0, str(record.hours_per_day))
            custom_usage_entry.configure(state="normal")
        else:
            custom_usage_entry.configure(state="disabled")
            custom_usage_entry.pack_forget()

        def on_usage_change(selected: str) -> None:
            if selected == self._custom_usage_display:
                custom_usage_entry.pack(padx=20, pady=(0, 14), anchor="w")
                custom_usage_entry.configure(state="normal")
            else:
                custom_usage_entry.delete(0, "end")
                custom_usage_entry.configure(state="disabled")
                custom_usage_entry.pack_forget()

        usage_menu.configure(command=on_usage_change)

        actions = ctk.CTkFrame(modal, fg_color="transparent")
        actions.pack(fill="x", padx=20, pady=(0, 16))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, weight=1)

        self._make_secondary_button(actions, "Cancel", modal.destroy).grid(row=0, column=0, padx=(0, 6), sticky="ew")

        def save_edit() -> None:
            selected_usage = usage_var.get().strip()
            usage = self._usage_to_raw(selected_usage)
            custom_hours: float | None = None
            if selected_usage == self._custom_usage_display:
                raw_hours = custom_usage_entry.get().strip()
                try:
                    custom_hours = float(raw_hours)
                except ValueError:
                    self._show_info_modal("Error", "Enter whole-number custom usage hours (1-24).")
                    return
                usage = "Custom"
            try:
                self._app.update_record_usage_at(index, usage, custom_hours_per_day=custom_hours)
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
            fg_color=FIELD_BG,
            border_color=BORDER_DEFAULT,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            height=36,
            width=320,
        )
        entry.pack(anchor="w", padx=20, pady=(0, 4))
        self._bind_field_focus_border(entry)

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

        ctk.CTkLabel(modal, text="WattzUp", font=FONT_MODAL_BRAND, text_color=TEXT_PRIMARY).pack(
            pady=(20, 4)
        )
        ctk.CTkLabel(
            modal,
            text="Continue an existing session or create a new one.",
            font=FONT_BODY,
            text_color=TEXT_SECONDARY,
        ).pack(pady=(0, 14))

        user_var = ctk.StringVar(value=users[0] if users else "")
        user_menu = ctk.CTkComboBox(
            modal,
            values=users if users else [""],
            variable=user_var,
            state="readonly",
            fg_color=FIELD_BG,
            border_color=BORDER_DEFAULT,
            button_color=ACCENT_MUTED,
            button_hover_color=ACCENT_HOVER,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            width=340,
        )
        user_menu.pack(pady=(0, 10))
        self._bind_field_focus_border(user_menu)
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
            fg_color=FIELD_BG,
            border_color=BORDER_DEFAULT,
            text_color=TEXT_PRIMARY,
            corner_radius=8,
            width=340,
            height=36,
        )
        entry.pack(anchor="w", padx=20, pady=(0, 4))
        self._bind_field_focus_border(entry)

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

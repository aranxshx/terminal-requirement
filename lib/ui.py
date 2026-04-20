from __future__ import annotations

import os

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFont
from tkinter import messagebox

from lib.app import WattzUpApplicationService, create_default_application_service
from util.config import USAGE_LEVELS

ctk.set_appearance_mode("Dark")


class WattzUpVisual(ctk.CTk):
    """CustomTkinter desktop application for WattzUp."""

    def __init__(self, application_service: WattzUpApplicationService | None = None) -> None:
        super().__init__()
        self._app = application_service or create_default_application_service()

        self.title("WattzUp | Home Energy Dashboard")
        self.geometry("1500x900")
        self.configure(fg_color="#111214")
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        self._current_room_color = "#50C878"
        self._current_room_name = "Kitchen"
        self._map_buttons: dict[str, ctk.CTkButton] = {}
        self._room_hotspots: dict[str, tuple[float, float, str]] = {}
        # MDI private-use glyphs rendered as button images from local font file.
        self._room_icons = {
            "Kitchen": "\U000F04B9",       # mdi-stove
            "Living Room": "\U000F04B8",   # mdi-sofa
            "Bedroom": "\U000F02E3",       # mdi-bed
            "Bathroom": "\U000F09A0",      # mdi-shower
            "Dining Area": "\U000F0A70",   # mdi-silverware-fork-knife
        }
        self._room_icon_images: dict[str, ctk.CTkImage] = {}
        self._map_focus_room: str | None = None
        self._map_image_label: ctk.CTkLabel | None = None
        self._back_button: ctk.CTkButton | None = None
        self._current_crop_box: tuple[float, float, float, float] | None = None
        self._zoom_after_id: str | None = None
        self._is_zoom_animating = False
        self._enable_zoom_animation = False
        self._map_display_size = (900, 700)
        self._base_map_image: Image.Image | None = None
        self._resample_filter = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
        self._fast_resample_filter = Image.Resampling.BILINEAR if hasattr(Image, "Resampling") else Image.BILINEAR
        self._font_family = "Segoe UI"
        self._load_room_icon_images()

        self._configure_grid()
        self._build_sidebar()
        self._build_main_containers()
        self._load_background_image()

        self._login_user()
        self._show_map()

    def _configure_grid(self) -> None:
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=1)

    def _build_sidebar(self) -> None:
        self.sidebar = ctk.CTkFrame(self, width=110, corner_radius=0, fg_color="#1a1c1e", border_width=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        logo_label = ctk.CTkLabel(
            self.sidebar,
            text="⚡",
            font=(self._font_family, 26, "bold"),
            text_color="#50C878",
        )
        logo_label.pack(pady=(30, 40))

        self._create_sidebar_item("🏠", "Dashboard", self._collapse_card, pady=10, active=True)
        self._create_sidebar_item("💾", "Save Data", self._save_data, pady=10)
        self._create_sidebar_item("💰", "Budget", self._set_budget_ui, pady=10)
        self._create_sidebar_item("📥", "Log Out", self._logout, pady=30, side="bottom")

    def _build_main_containers(self) -> None:
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew")

        self.card_panel = ctk.CTkFrame(
            self,
            fg_color="#1a1c1e",
            width=470,
            corner_radius=0,
            border_width=1,
            border_color="#2d2f31",
        )

    def _load_background_image(self) -> None:
        try:
            self._blueprint_source = Image.open("Blueprint.png").convert("RGBA")
            self._base_map_image = self._blueprint_source.resize(self._map_display_size, self._resample_filter)
            self.bg_image = self._build_map_image()
        except Exception as exc:  # pragma: no cover - GUI environment specific
            self._blueprint_source = None
            self._base_map_image = None
            self.bg_image = None
            messagebox.showerror("File Error", f"Could not load Blueprint.png: {exc}")

    def _build_map_image(self, focus_room: str | None = None) -> ctk.CTkImage | None:
        if self._blueprint_source is None:
            return None

        map_width, map_height = 900, 700
        image = self._blueprint_source.copy()
        hotspot = self._room_hotspots.get(focus_room or "")
        if hotspot is not None:
            rel_x, rel_y, _ = hotspot
            source_width, source_height = image.size
            zoom = 1.9

            crop_width = max(1, int(source_width / zoom))
            crop_height = max(1, int(source_height / zoom))
            center_x = int(rel_x * source_width)
            center_y = int(rel_y * source_height)

            # Keep the selected room under the same hotspot position so map buttons stay fixed.
            left = int(center_x - (rel_x * crop_width))
            top = int(center_y - (rel_y * crop_height))
            left = max(0, min(source_width - crop_width, left))
            top = max(0, min(source_height - crop_height, top))
            right = left + crop_width
            bottom = top + crop_height

            image = image.crop((left, top, right, bottom))
            resample_filter = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
            image = image.resize((source_width, source_height), resample_filter)

        return ctk.CTkImage(light_image=image, dark_image=image, size=(map_width, map_height))

    def _create_sidebar_item(
        self,
        icon: str,
        label: str,
        command,
        pady: int,
        side: str = "top",
        active: bool = False,
    ) -> None:
        container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        container.pack(pady=pady, side=side, fill="x")

        bg_color = "#2d2f31" if active else "transparent"
        text_color = "#50C878" if active else "#8a8d91"

        button = ctk.CTkButton(
            container,
            text=icon,
            width=60,
            height=45,
            font=(self._font_family, 24),
            fg_color=bg_color,
            hover_color="#2d2f31",
            command=command,
            text_color=text_color,
        )
        button.pack()

        label_widget = ctk.CTkLabel(
            container,
            text=label,
            font=(self._font_family, 11, "bold"),
            text_color=text_color,
        )
        label_widget.pack(pady=(2, 5))

    def _load_room_icon_images(self) -> None:
        font_path = os.path.join("assets", "materialdesignicons-webfont.ttf")
        if not os.path.exists(font_path):
            return

        try:
            icon_font = ImageFont.truetype(font_path, 20)
        except OSError:
            return

        for room_name, glyph in self._room_icons.items():
            icon_canvas = Image.new("RGBA", (24, 24), (0, 0, 0, 0))
            draw = ImageDraw.Draw(icon_canvas)
            text_box = draw.textbbox((0, 0), glyph, font=icon_font)
            glyph_width = text_box[2] - text_box[0]
            glyph_height = text_box[3] - text_box[1]
            draw.text(
                ((24 - glyph_width) / 2 - text_box[0], (24 - glyph_height) / 2 - text_box[1]),
                glyph,
                font=icon_font,
                fill=(235, 241, 247, 255),
            )
            self._room_icon_images[room_name] = ctk.CTkImage(
                light_image=icon_canvas,
                dark_image=icon_canvas,
                size=(18, 18),
            )

    def _show_map(self) -> None:
        for widget in self.main_view.winfo_children():
            widget.destroy()
        self._map_image_label = None
        self._back_button = None

        total_cost = self._app.total_cost()
        if not self._app.records:
            status_text = "NO RECORDS YET"
            status_color = "gray"
        else:
            status_text = self._app.budget_status()
            status_color = "#50C878" if status_text == "UNDER BUDGET" else "#8B0000"

        pill_container = ctk.CTkFrame(
            self.main_view,
            fg_color="#1e2023",
            corner_radius=35,
            border_width=2,
            border_color="#2d2f31",
        )
        pill_container.pack(pady=(30, 10), padx=20)

        ctk.CTkLabel(
            pill_container,
            text=f"Estimated Monthly Cost: P{total_cost:,.2f}",
            font=(self._font_family, 27, "bold"),
        ).pack(pady=(15, 0), padx=40)
        ctk.CTkLabel(
            pill_container,
            text=f"Budget Status: {status_text}",
            font=(self._font_family, 19, "bold"),
            text_color=status_color,
        ).pack(pady=(0, 15))

        self._build_default_rankings(self.main_view)

        if self._blueprint_source is not None:
            initial_box = self._target_crop_box(self._map_focus_room)
            self._current_crop_box = initial_box
            self.bg_image = self._build_map_image_from_crop(initial_box)
            if self.bg_image is not None:
                image_label = ctk.CTkLabel(self.main_view, image=self.bg_image, text="")
                image_label.pack(expand=True, pady=20)
                self._map_image_label = image_label
                self._add_hotspots(image_label)
                self._sync_back_button()

    def _add_hotspots(self, parent: ctk.CTkLabel) -> None:
        self._map_buttons.clear()
        hotspots = [
            ("Kitchen", 0.40, 0.48, "#FF7F50"),
            ("Living Room", 0.75, 0.65, "#50C878"),
            ("Bedroom", 0.48, 0.25, "#4A90E2"),
            ("Bathroom", 0.65, 0.35, "#87CEEB"),
            ("Dining Area", 0.32, 0.68, "#FFD700"),
        ]
        self._room_hotspots = {room_name: (rel_x, rel_y, color) for room_name, rel_x, rel_y, color in hotspots}

        for room_name, rel_x, rel_y, color in hotspots:
            button = ctk.CTkButton(
                parent,
                text=room_name,
                image=self._room_icon_images.get(room_name),
                compound="left",
                width=140,
                height=45,
                font=(self._font_family, 14, "bold"),
                fg_color="#1e2023",
                border_width=2,
                border_color=color,
                hover_color=color,
                border_spacing=0,
                corner_radius=6,
                command=lambda room=room_name, value=color: self._on_room_click(room, value),
            )
            projected = self._project_hotspot_to_view(rel_x, rel_y, self._current_crop_box)
            if projected is not None:
                view_x, view_y = projected
                button.place(relx=view_x, rely=view_y, anchor="center")
            else:
                button.place_forget()
            self._map_buttons[room_name] = button

        self._set_hotspot_presentation(self._is_zoom_animating)
        self._refresh_room_highlight()

    def _project_hotspot_to_view(
        self,
        rel_x: float,
        rel_y: float,
        crop_box: tuple[float, float, float, float] | None,
    ) -> tuple[float, float] | None:
        """Map hotspot coordinates from blueprint space into current cropped view."""
        if self._blueprint_source is None:
            return None

        source_width, source_height = self._blueprint_source.size
        pixel_x = rel_x * source_width
        pixel_y = rel_y * source_height

        left, top, right, bottom = crop_box or self._full_crop_box()
        crop_width = max(1.0, right - left)
        crop_height = max(1.0, bottom - top)

        view_x = (pixel_x - left) / crop_width
        view_y = (pixel_y - top) / crop_height
        if 0.0 <= view_x <= 1.0 and 0.0 <= view_y <= 1.0:
            return (view_x, view_y)
        return None

    def _reposition_hotspots(self) -> None:
        for room_name, button in self._map_buttons.items():
            hotspot = self._room_hotspots.get(room_name)
            if hotspot is None:
                continue
            rel_x, rel_y, _ = hotspot
            projected = self._project_hotspot_to_view(rel_x, rel_y, self._current_crop_box)
            if projected is None:
                button.place_forget()
                continue
            view_x, view_y = projected
            button.place(relx=view_x, rely=view_y, anchor="center")

    def _on_room_click(self, room_name: str, color: str) -> None:
        self._start_zoom_transition(room_name)
        self._open_card(room_name, color)

    def _reset_map_focus(self) -> None:
        self._start_zoom_transition(None)
        self._collapse_card()
        self._refresh_room_highlight()

    def _sync_back_button(self) -> None:
        if self._map_image_label is None:
            return

        if self._map_focus_room is not None:
            if self._back_button is None:
                self._back_button = ctk.CTkButton(
                    self._map_image_label,
                    text="← Back to Full Map",
                    width=170,
                    fg_color="#2d2f31",
                    hover_color="#404347",
                    font=(self._font_family, 12, "bold"),
                    command=self._reset_map_focus,
                )
                self._back_button.place(relx=0.03, rely=0.05, anchor="nw")
        elif self._back_button is not None:
            self._back_button.destroy()
            self._back_button = None

    def _full_crop_box(self) -> tuple[float, float, float, float]:
        if self._blueprint_source is None:
            return (0.0, 0.0, 1.0, 1.0)
        width, height = self._blueprint_source.size
        return (0.0, 0.0, float(width), float(height))

    def _target_crop_box(self, focus_room: str | None) -> tuple[float, float, float, float]:
        full = self._full_crop_box()
        if focus_room is None or focus_room not in self._room_hotspots or self._blueprint_source is None:
            return full

        rel_x, rel_y, _ = self._room_hotspots[focus_room]
        source_width, source_height = self._blueprint_source.size
        zoom = 1.9

        crop_width = max(1.0, source_width / zoom)
        crop_height = max(1.0, source_height / zoom)
        center_x = rel_x * source_width
        center_y = rel_y * source_height

        left = center_x - (rel_x * crop_width)
        top = center_y - (rel_y * crop_height)
        left = max(0.0, min(source_width - crop_width, left))
        top = max(0.0, min(source_height - crop_height, top))
        return (left, top, left + crop_width, top + crop_height)

    def _build_map_image_from_crop(
        self,
        crop_box: tuple[float, float, float, float],
        high_quality: bool = True,
    ) -> ctk.CTkImage | None:
        if self._blueprint_source is None:
            return None

        map_width, map_height = self._map_display_size
        full_box = self._full_crop_box()
        is_full = self._boxes_close(crop_box, full_box)

        if is_full and self._base_map_image is not None:
            image = self._base_map_image
        else:
            image = self._blueprint_source
            left, top, right, bottom = crop_box
            crop = (
                int(round(left)),
                int(round(top)),
                int(round(right)),
                int(round(bottom)),
            )
            image = image.crop(crop)
            resize_filter = self._resample_filter if high_quality else self._fast_resample_filter
            image = image.resize((map_width, map_height), resize_filter)

        return ctk.CTkImage(light_image=image, dark_image=image, size=(map_width, map_height))

    @staticmethod
    def _lerp(start: float, end: float, t: float) -> float:
        return start + ((end - start) * t)

    @classmethod
    def _lerp_box(
        cls,
        start_box: tuple[float, float, float, float],
        end_box: tuple[float, float, float, float],
        t: float,
    ) -> tuple[float, float, float, float]:
        return (
            cls._lerp(start_box[0], end_box[0], t),
            cls._lerp(start_box[1], end_box[1], t),
            cls._lerp(start_box[2], end_box[2], t),
            cls._lerp(start_box[3], end_box[3], t),
        )

    @staticmethod
    def _boxes_close(
        a: tuple[float, float, float, float],
        b: tuple[float, float, float, float],
        tolerance: float = 0.5,
    ) -> bool:
        return all(abs(x - y) <= tolerance for x, y in zip(a, b))

    def _render_crop_box(self, crop_box: tuple[float, float, float, float], high_quality: bool = True) -> None:
        if self._map_image_label is None:
            return
        image = self._build_map_image_from_crop(crop_box, high_quality=high_quality)
        if image is None:
            return
        self.bg_image = image
        self._map_image_label.configure(image=self.bg_image)
        self._current_crop_box = crop_box
        self._reposition_hotspots()

    def _start_zoom_transition(self, target_focus_room: str | None) -> None:
        if self._blueprint_source is None:
            self._map_focus_room = target_focus_room
            self._sync_back_button()
            return

        start_box = self._current_crop_box or self._target_crop_box(self._map_focus_room)
        end_box = self._target_crop_box(target_focus_room)

        if not self._enable_zoom_animation:
            self._map_focus_room = target_focus_room
            self._set_hotspot_presentation(False)
            self._render_crop_box(end_box, high_quality=True)
            self._sync_back_button()
            return

        if self._boxes_close(start_box, end_box):
            self._map_focus_room = target_focus_room
            self._render_crop_box(end_box)
            self._sync_back_button()
            return

        if self._zoom_after_id is not None:
            self.after_cancel(self._zoom_after_id)
            self._zoom_after_id = None

        duration_ms = 220
        frame_ms = 12
        steps = max(10, duration_ms // frame_ms)
        self._map_focus_room = target_focus_room
        self._sync_back_button()
        self._set_hotspot_presentation(True)

        def animate(step: int) -> None:
            t = step / steps
            box = self._lerp_box(start_box, end_box, t)
            self._render_crop_box(box, high_quality=False)
            if step < steps:
                self._zoom_after_id = self.after(frame_ms, lambda: animate(step + 1))
            else:
                self._zoom_after_id = None
                self._render_crop_box(end_box, high_quality=True)
                self._set_hotspot_presentation(False)
                self._sync_back_button()

        animate(0)

    def _set_hotspot_presentation(self, animated: bool) -> None:
        """Hide hotspots during animation; restore labeled buttons after animation."""
        self._is_zoom_animating = animated
        for room_name, button in self._map_buttons.items():
            _, _, color = self._room_hotspots.get(room_name, (0.0, 0.0, "#50C878"))
            if animated:
                button.place_forget()
            else:
                button.configure(
                    text=room_name,
                    image=self._room_icon_images.get(room_name),
                    compound="left",
                    width=140,
                    height=45,
                    corner_radius=6,
                    border_width=2,
                    border_color=color,
                    fg_color="#1e2023",
                    hover_color=color,
                )
        if not animated:
            self._reposition_hotspots()
            self._refresh_room_highlight()

    def _refresh_room_highlight(self) -> None:
        for room_name, button in self._map_buttons.items():
            if self._is_zoom_animating:
                continue
            if room_name == self._current_room_name:
                button.configure(fg_color="#50C878", text_color="#FFFFFF", hover_color="#50C878")
            else:
                button.configure(fg_color="#1e2023", text_color="#f5f5f5")

    def _build_default_rankings(self, parent: ctk.CTkFrame) -> None:
        ranking_wrap = ctk.CTkFrame(parent, fg_color="#1a1c1e", corner_radius=16, border_color="#2d2f31", border_width=1)
        ranking_wrap.pack(fill="x", padx=30, pady=(5, 10))

        left = ctk.CTkFrame(ranking_wrap, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=(16, 8), pady=12)
        right = ctk.CTkFrame(ranking_wrap, fg_color="transparent")
        right.pack(side="left", fill="both", expand=True, padx=(8, 16), pady=12)

        ctk.CTkLabel(left, text="Appliance Ranking", font=(self._font_family, 18, "bold")).pack(anchor="w", pady=(0, 8))
        ranked_appliances = self._app.ranked_appliances()[:5]
        if ranked_appliances:
            for index, record in enumerate(ranked_appliances, start=1):
                ctk.CTkLabel(
                    left,
                    text=f"{index}. {record.appliance} ({record.room}) - P{record.monthly_cost:,.2f}",
                    font=(self._font_family, 14),
                    anchor="w",
                ).pack(anchor="w", pady=2)
        else:
            ctk.CTkLabel(left, text="No appliance rankings yet.", font=(self._font_family, 13), text_color="#8a8d91").pack(anchor="w")

        ctk.CTkLabel(right, text="Room Ranking", font=(self._font_family, 18, "bold")).pack(anchor="w", pady=(0, 8))
        ranked_rooms = self._app.ranked_rooms()[:5]
        if ranked_rooms:
            for index, (room, cost) in enumerate(ranked_rooms, start=1):
                ctk.CTkLabel(
                    right,
                    text=f"{index}. {room} - P{cost:,.2f}",
                    font=(self._font_family, 14),
                    anchor="w",
                ).pack(anchor="w", pady=2)
        else:
            ctk.CTkLabel(right, text="No room rankings yet.", font=(self._font_family, 13), text_color="#8a8d91").pack(anchor="w")

    def _open_card(self, room_name: str, color: str) -> None:
        self._current_room_name = room_name
        self._current_room_color = color
        self._refresh_room_highlight()
        self._fill_card_content(room_name, color)
        self.card_panel.grid(row=0, column=2, sticky="nsew")
        self.update_idletasks()

    def _collapse_card(self) -> None:
        self.card_panel.grid_forget()
        for widget in self.card_panel.winfo_children():
            widget.destroy()
        self.update_idletasks()

    def _fill_card_content(self, room_name: str, color: str) -> None:
        for widget in self.card_panel.winfo_children():
            widget.destroy()

        ctk.CTkButton(
            self.card_panel,
            text="✕",
            width=30,
            height=30,
            fg_color="transparent",
            font=(self._font_family, 18),
            hover_color="#e74c3c",
            command=self._collapse_card,
        ).pack(anchor="ne", padx=10, pady=10)

        ctk.CTkLabel(
            self.card_panel,
            text=f" {room_name}",
            font=(self._font_family, 32, "bold"),
            text_color=color,
        ).pack(pady=(0, 10))

        tabview = ctk.CTkTabview(self.card_panel, segmented_button_selected_color=color, fg_color="#1e2023")
        tabview.pack(fill="both", expand=True, padx=20, pady=15)

        manage_tab = tabview.add("Manage Household")
        appliance_tab = tabview.add("Appliance Ranking")
        room_tab = tabview.add("Room Ranking")

        self._build_manage_tab(manage_tab, room_name, color)
        self._build_appliance_ranking_tab(appliance_tab, room_name)
        self._build_room_ranking_tab(room_tab)

    def _build_manage_tab(self, tab: ctk.CTkFrame, room_name: str, color: str) -> None:
        ctk.CTkLabel(tab, text="+ Add New Appliance:", font=(self._font_family, 16, "bold")).pack(pady=10)

        appliances = self._app.catalog.appliances_for_room(room_name)
        app_var = ctk.StringVar(value=appliances[0] if appliances else "")
        usage_var = ctk.StringVar(value="Moderate")

        ctk.CTkOptionMenu(tab, values=appliances or [""], variable=app_var, width=250).pack(pady=10)
        ctk.CTkOptionMenu(tab, values=list(USAGE_LEVELS.keys()), variable=usage_var, width=250).pack(pady=10)

        ctk.CTkButton(
            tab,
            text="Confirm Addition",
            width=250,
            height=45,
            fg_color=color,
            text_color="#111214",
            font=(self._font_family, 14, "bold"),
            border_spacing=0,
            corner_radius=6,
            command=lambda: self._add_entry(room_name, app_var.get(), usage_var.get(), color),
        ).pack(pady=20)

        ctk.CTkLabel(tab, text="Existing Records", font=(self._font_family, 16, "bold")).pack(pady=(8, 6))
        self._build_room_records_list(tab, room_name, color)

    def _build_appliance_ranking_tab(self, tab: ctk.CTkFrame, room_name: str) -> None:
        room_records = [record for record in self._app.ranked_appliances() if record.room == room_name]
        if room_records:
            for index, record in enumerate(room_records, start=1):
                ctk.CTkLabel(
                    tab,
                    text=f"{index}. {record.appliance}: P{record.monthly_cost:.2f}",
                    font=(self._font_family, 15),
                ).pack(pady=4, anchor="w", padx=15)
        else:
            self._add_empty_state_diagram(tab, text="Analyze your usage ranking.")

    def _build_room_ranking_tab(self, tab: ctk.CTkFrame) -> None:
        ranking = self._app.ranked_rooms()
        if ranking:
            for index, (room, cost) in enumerate(ranking, start=1):
                ctk.CTkLabel(
                    tab,
                    text=f"{index}. {room}: P{cost:,.2f}",
                    font=(self._font_family, 15),
                ).pack(pady=4, anchor="w", padx=15)
        else:
            self._add_empty_state_diagram(tab, text="Add appliance entries to generate room rankings.")

    def _add_empty_state_diagram(self, parent: ctk.CTkFrame, text: str = "Add your first appliance to populate this room.") -> None:
        diagram_frame = ctk.CTkFrame(parent, fg_color="transparent")
        diagram_frame.pack(pady=40)

        ctk.CTkLabel(
            diagram_frame,
            text="[□] [□] [|]",
            font=(self._font_family, 28, "bold"),
            text_color="#2d2f31",
        ).pack()
        ctk.CTkLabel(
            diagram_frame,
            text="[O] [□] [|]",
            font=(self._font_family, 28, "bold"),
            text_color="#2d2f31",
        ).pack()
        ctk.CTkLabel(
            parent,
            text=text,
            font=(self._font_family, 14),
            text_color="#8a8d91",
            wraplength=350,
        ).pack(pady=10)

    def _build_room_records_list(self, parent: ctk.CTkFrame, room_name: str, color: str) -> None:
        list_frame = ctk.CTkScrollableFrame(parent, height=200, fg_color="#17191b")
        list_frame.pack(fill="x", padx=10, pady=(0, 10))

        indexed_room_records = [
            (index, record)
            for index, record in enumerate(self._app.records)
            if record.room == room_name
        ]

        if not indexed_room_records:
            ctk.CTkLabel(
                list_frame,
                text="No appliances recorded for this room.",
                font=(self._font_family, 13),
                text_color="#8a8d91",
            ).pack(anchor="w", pady=8)
            return

        for index, record in indexed_room_records:
            row = ctk.CTkFrame(list_frame, fg_color="#1f2226")
            row.pack(fill="x", padx=4, pady=4)

            summary_button = ctk.CTkButton(
                row,
                text=f"{record.appliance} | {record.usage_level} | P{record.monthly_cost:,.2f}",
                fg_color="#2a2d32",
                hover_color="#343941",
                font=(self._font_family, 13),
                anchor="w",
                command=lambda: None,
            )
            summary_button.pack(side="left", fill="x", expand=True, padx=(8, 6), pady=8)

            ctk.CTkButton(
                row,
                text="Edit",
                width=56,
                fg_color=color,
                text_color="#111214",
                font=(self._font_family, 12, "bold"),
                command=lambda i=index: self._edit_record(i),
            ).pack(side="left", padx=(0, 4), pady=8)

            ctk.CTkButton(
                row,
                text="Delete",
                width=64,
                fg_color="#8B0000",
                hover_color="#6e0000",
                font=(self._font_family, 12, "bold"),
                command=lambda i=index, room=room_name, room_color=color: self._delete_record(i, room, room_color),
            ).pack(side="left", padx=(0, 8), pady=8)

    def _edit_record(self, index: int) -> None:
        record = self._app.records[index]
        dialog = ctk.CTkInputDialog(
            text=(
                f"Editing: {record.appliance}\n"
                f"Current usage: {record.usage_level}\n\n"
                "Enter new usage level (Heavy, Moderate, Eco):"
            ),
            title="Edit Appliance",
        )
        raw_input = dialog.get_input()
        if raw_input is None:
            return

        normalized = raw_input.strip().title()
        try:
            self._app.update_record_usage_at(index, normalized)
        except (ValueError, IndexError) as exc:
            messagebox.showerror("Error", str(exc))
            return

        self._show_map()
        self._fill_card_content(self._current_room_name, self._current_room_color)

    def _delete_record(self, index: int, room_name: str, color: str) -> None:
        should_delete = messagebox.askyesno("Delete Appliance", "Delete this appliance record?")
        if not should_delete:
            return

        try:
            self._app.delete_record_at(index)
        except (RuntimeError, IndexError) as exc:
            messagebox.showerror("Error", str(exc))
            return

        self._show_map()
        self._fill_card_content(room_name, color)

    def _login_user(self) -> None:
        existing = self._app.list_existing_users()
        continue_existing = bool(existing) and messagebox.askyesno(
            "Startup",
            "Continue an existing record?\nChoose No to create a new user.",
        )

        if continue_existing:
            self._continue_existing_user(existing)
            return

        self._create_new_user(existing)

    def _continue_existing_user(self, existing: list[str]) -> None:
        selection = self._select_existing_user_dialog(existing)
        if selection is None:
            self.destroy()
            return

        try:
            self._app.continue_user_session(selection)
        except ValueError:
            messagebox.showerror("Invalid User", "Please select a valid existing username.")
            self._continue_existing_user(existing)

    def _select_existing_user_dialog(self, existing: list[str]) -> str | None:
        modal = ctk.CTkToplevel(self)
        modal.title("Continue User")
        modal.geometry("380x200")
        modal.resizable(False, False)
        modal.transient(self)
        modal.grab_set()

        ctk.CTkLabel(
            modal,
            text="Select an existing user record:",
            font=(self._font_family, 15, "bold"),
        ).pack(pady=(20, 10), padx=20, anchor="w")

        selected_user = ctk.StringVar(value=existing[0] if existing else "")
        dropdown = ctk.CTkOptionMenu(
            modal,
            values=existing if existing else [""],
            variable=selected_user,
            width=320,
            dynamic_resizing=False,
        )
        dropdown.pack(pady=(0, 20))

        choice: dict[str, str | None] = {"value": None}

        def _confirm() -> None:
            value = selected_user.get().strip()
            choice["value"] = value or None
            modal.destroy()

        def _cancel() -> None:
            choice["value"] = None
            modal.destroy()

        actions = ctk.CTkFrame(modal, fg_color="transparent")
        actions.pack(pady=(0, 16))

        ctk.CTkButton(
            actions,
            text="Cancel",
            width=110,
            fg_color="#2d2f31",
            hover_color="#3b3f44",
            command=_cancel,
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            actions,
            text="Continue",
            width=110,
            fg_color="#50C878",
            text_color="#111214",
            hover_color="#45b36b",
            command=_confirm,
        ).pack(side="left", padx=6)

        modal.protocol("WM_DELETE_WINDOW", _cancel)
        self.wait_window(modal)
        return choice["value"]

    def _create_new_user(self, existing: list[str]) -> None:
        del existing
        while True:
            dialog = ctk.CTkInputDialog(text="Enter new username:", title="Create User")
            username = dialog.get_input()
            if username is None:
                self.destroy()
                return

            try:
                self._app.create_new_user_session(username)
                return
            except ValueError as exc:
                messagebox.showerror("Invalid Username", str(exc))

    def _set_budget_ui(self) -> None:
        dialog = ctk.CTkInputDialog(text="Set Monthly Limit (P):", title="Budget Settings")
        value = dialog.get_input()
        if value is None:
            return

        try:
            self._app.set_budget(float(value.replace(",", "")))
        except ValueError:
            messagebox.showerror("Error", "Invalid number")
            return

        self._show_map()

    def _add_entry(self, room: str, appliance: str, usage_level: str, color: str) -> None:
        if not appliance:
            messagebox.showerror("Invalid Selection", "Please select an appliance.")
            return

        try:
            self._app.add_appliance_usage(room, appliance, usage_level)
        except (ValueError, KeyError, RuntimeError) as exc:
            messagebox.showerror("Error", str(exc))
            return

        self._show_map()
        self._fill_card_content(room, color)

    def _save_data(self) -> None:
        try:
            self._app.save_current_session()
        except RuntimeError as exc:
            messagebox.showerror("Error", str(exc))
            return

        messagebox.showinfo("Saved", "Progress saved successfully")

    def _logout(self) -> None:
        should_save = messagebox.askyesno("Save", "Save records before logging out?")
        if should_save:
            self._save_data()
        self.destroy()

    def _on_window_close(self) -> None:
        if self._app.records:
            should_save = messagebox.askyesno("Save", "Save records before exiting?")
            if should_save:
                self._save_data()
        self.destroy()


if __name__ == "__main__":
    app = WattzUpVisual()
    app.mainloop()

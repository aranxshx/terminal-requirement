from __future__ import annotations

import customtkinter as ctk
from PIL import Image
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

        logo_label = ctk.CTkLabel(self.sidebar, text="⚡", font=("Arial", 25, "bold"), text_color="#50C878")
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
            image = Image.open("Blueprint.png")
            self.bg_image = ctk.CTkImage(light_image=image, dark_image=image, size=(900, 700))
        except Exception as exc:  # pragma: no cover - GUI environment specific
            self.bg_image = None
            messagebox.showerror("File Error", f"Could not load Blueprint.png: {exc}")

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
            font=("Arial", 24),
            fg_color=bg_color,
            hover_color="#2d2f31",
            command=command,
            text_color=text_color,
        )
        button.pack()

        label_widget = ctk.CTkLabel(container, text=label, font=("Arial", 10), text_color=text_color)
        label_widget.pack(pady=(2, 5))

    def _show_map(self) -> None:
        for widget in self.main_view.winfo_children():
            widget.destroy()

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
            font=("Arial", 26, "bold"),
        ).pack(pady=(15, 0), padx=40)
        ctk.CTkLabel(
            pill_container,
            text=f"Budget Status: {status_text}",
            font=("Arial", 18),
            text_color=status_color,
        ).pack(pady=(0, 15))

        if self.bg_image is not None:
            image_label = ctk.CTkLabel(self.main_view, image=self.bg_image, text="")
            image_label.pack(expand=True, pady=20)
            self._add_hotspots(image_label)

    def _add_hotspots(self, parent: ctk.CTkLabel) -> None:
        hotspots = [
            ("Kitchen", 0.40, 0.48, "#FF7F50"),
            ("Living Room", 0.75, 0.65, "#50C878"),
            ("Bedroom", 0.48, 0.25, "#4A90E2"),
            ("Bathroom", 0.65, 0.35, "#87CEEB"),
            ("Dining Area", 0.32, 0.68, "#FFD700"),
        ]

        for room_name, rel_x, rel_y, color in hotspots:
            button = ctk.CTkButton(
                parent,
                text=room_name,
                width=140,
                height=45,
                font=("Arial", 14, "bold"),
                fg_color="#1e2023",
                border_width=2,
                border_color=color,
                hover_color=color,
                border_spacing=0,
                corner_radius=6,
                command=lambda room=room_name, value=color: self._open_card(room, value),
            )
            button.place(relx=rel_x, rely=rel_y, anchor="center")

    def _open_card(self, room_name: str, color: str) -> None:
        self._current_room_name = room_name
        self._current_room_color = color
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
            font=("Arial", 18),
            hover_color="#e74c3c",
            command=self._collapse_card,
        ).pack(anchor="ne", padx=10, pady=10)

        ctk.CTkLabel(
            self.card_panel,
            text=f" {room_name}",
            font=("Arial", 32, "bold"),
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
        ctk.CTkLabel(tab, text="+ Add New Appliance:", font=("Arial", 16)).pack(pady=10)

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
            font=("Arial", 14, "bold"),
            border_spacing=0,
            corner_radius=6,
            command=lambda: self._add_entry(room_name, app_var.get(), usage_var.get(), color),
        ).pack(pady=20)

        self._add_empty_state_diagram(tab)

    def _build_appliance_ranking_tab(self, tab: ctk.CTkFrame, room_name: str) -> None:
        room_records = [record for record in self._app.ranked_appliances() if record.room == room_name]
        if room_records:
            for index, record in enumerate(room_records, start=1):
                ctk.CTkLabel(
                    tab,
                    text=f"{index}. {record.appliance}: P{record.monthly_cost:.2f}",
                    font=("Arial", 15),
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
                    font=("Arial", 15),
                ).pack(pady=4, anchor="w", padx=15)
        else:
            self._add_empty_state_diagram(tab, text="Add appliance entries to generate room rankings.")

    def _add_empty_state_diagram(self, parent: ctk.CTkFrame, text: str = "Add your first appliance to populate this room.") -> None:
        diagram_frame = ctk.CTkFrame(parent, fg_color="transparent")
        diagram_frame.pack(pady=40)

        ctk.CTkLabel(diagram_frame, text="[□] [□] [|]", font=("Arial", 28, "bold"), text_color="#2d2f31").pack()
        ctk.CTkLabel(diagram_frame, text="[O] [□] [|]", font=("Arial", 28, "bold"), text_color="#2d2f31").pack()
        ctk.CTkLabel(parent, text=text, font=("Arial", 14), text_color="#8a8d91", wraplength=350).pack(pady=10)

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
        existing_text = "\n".join(f"- {name}" for name in existing)
        while True:
            dialog = ctk.CTkInputDialog(
                text=f"Available users:\n{existing_text}\n\nEnter username to continue:",
                title="Continue User",
            )
            selection = dialog.get_input()
            if selection is None:
                self.destroy()
                return

            try:
                self._app.continue_user_session(selection)
                return
            except ValueError:
                messagebox.showerror("Invalid User", "Please enter a valid existing username.")

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

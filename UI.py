import customtkinter as ctk
from PIL import Image
import wattzup as logic
from tkinter import messagebox

ctk.set_appearance_mode("Dark")

class WattzUpVisual(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("WattzUp | Home Energy Dashboard")
        self.geometry("1500x900")
        self.configure(fg_color="#111214")

        self.records = []
        self.username = "User"
        self.monthly_budget = 0.0
        
        try:
            self.bg_image = ctk.CTkImage(
                light_image=Image.open("blueprint.png"),
                dark_image=Image.open("blueprint.png"),
                size=(900, 700) 
            )
        except Exception as e:
            messagebox.showerror("File Error", f"Error: {e}")

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1) 
        self.grid_columnconfigure(2, weight=0) 
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=110, corner_radius=0, fg_color="#1a1c1e", border_width=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        logo_label = ctk.CTkLabel(self.sidebar, text="⚡", font=("Arial", 25, "bold"), text_color="#50C878")
        logo_label.pack(pady=(30, 40))

        # Sidebar Navigation
        self.create_sidebar_item("🏠", "Dashboard", self.collapse_card, pady=10, active=True)
        self.create_sidebar_item("💾", "Save Data", self.save_data, pady=10)
        self.create_sidebar_item("💰", "Budget", self.set_budget_ui, pady=10) 
        self.create_sidebar_item("📥", "Log Out", self.quit, pady=30, side="bottom")

        # Main View Container
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew")

        # Slide-out Panel (Card)
        self.card_panel = ctk.CTkFrame(self, fg_color="#1a1c1e", width=450, corner_radius=0, border_width=1, border_color="#2d2f31")

        self.login_user()
        self.show_map()

    def create_sidebar_item(self, icon, label, command, pady, side="top", active=False):
        container = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        container.pack(pady=pady, side=side, fill="x")
        bg_color = "#2d2f31" if active else "transparent"
        text_color = "#50C878" if active else "#8a8d91"
        btn = ctk.CTkButton(container, text=icon, width=60, height=45, font=("Arial", 24), 
                            fg_color=bg_color, hover_color="#2d2f31", command=command, text_color=text_color)
        btn.pack()
        lbl = ctk.CTkLabel(container, text=label, font=("Arial", 10), text_color=text_color)
        lbl.pack(pady=(2, 5))

    def show_map(self):
        for widget in self.main_view.winfo_children(): widget.destroy()
        total_cost = sum(r.get('monthly_cost', 0) for r in self.records)
        status_text = "NO RECORDS YET" if not self.records else ("WITHIN BUDGET" if total_cost <= self.monthly_budget or self.monthly_budget == 0 else "OVER BUDGET")
        status_color = "#50C878" if "WITHIN" in status_text else ("#8B0000" if "OVER" in status_text else "gray")

        # Monthly Stats Header
        pill_container = ctk.CTkFrame(self.main_view, fg_color="#1e2023", corner_radius=35, border_width=2, border_color="#2d2f31")
        pill_container.pack(pady=(30, 10), padx=20)
        ctk.CTkLabel(pill_container, text=f"Estimated Monthly Cost: ₱{total_cost:,.2f}", font=("Arial", 26, "bold")).pack(pady=(15, 0), padx=40)
        ctk.CTkLabel(pill_container, text=f"Budget Status: {status_text}", font=("Arial", 18), text_color=status_color).pack(pady=(0, 15))

        # House Blueprint
        img_label = ctk.CTkLabel(self.main_view, image=self.bg_image, text="")
        img_label.pack(expand=True, pady=20)

        self.add_hotspot(img_label, "Kitchen", 0.40, 0.48, "#FF7F50")
        self.add_hotspot(img_label, "Living Room", 0.75, 0.65, "#50C878")
        self.add_hotspot(img_label, "Bedroom", 0.48, 0.25, "#4A90E2")
        self.add_hotspot(img_label, "Bathroom", 0.65, 0.35, "#87CEEB")
        self.add_hotspot(img_label, "Dining Area", 0.32, 0.68, "#FFD700")

    def add_hotspot(self, parent, room_name, x, y, color):
        btn = ctk.CTkButton(parent, text=room_name, width=140, height=45, font=("Arial", 14, "bold"),
                             fg_color="#1e2023", border_width=2, border_color=color, hover_color=color,
                             border_spacing=0, corner_radius=6,
                             command=lambda n=room_name, c=color: self.open_card(n, c))
        btn.place(relx=x, rely=y, anchor="center")

    def open_card(self, room_name, color):
        self.fill_card_content(room_name, color)
        self.card_panel.grid(row=0, column=2, sticky="nsew")
        self.update_idletasks()

    def collapse_card(self):
        self.card_panel.grid_forget()
        for widget in self.card_panel.winfo_children(): widget.destroy()
        self.update_idletasks()

    def fill_card_content(self, room_name, color):
        for widget in self.card_panel.winfo_children(): widget.destroy()
        
        # Exit Button
        ctk.CTkButton(self.card_panel, text="✕", width=30, height=30, fg_color="transparent", font=("Arial", 18),
                      hover_color="#e74c3c", command=self.collapse_card).pack(anchor="ne", padx=10, pady=10)

        ctk.CTkLabel(self.card_panel, text=f" {room_name}", font=("Arial", 32, "bold"), text_color=color).pack(pady=(0, 10))

        tabview = ctk.CTkTabview(self.card_panel, segmented_button_selected_color=color, fg_color="#1e2023")
        tabview.pack(fill="both", expand=True, padx=20, pady=15)
        
        t_manage = tabview.add("Manage Household")
        t_app_rank = tabview.add("Appliance Ranking")
        t_room_rank = tabview.add("Room Ranking")

        ctk.CTkLabel(t_manage, text="+ Add New Appliance:", font=("Arial", 16)).pack(pady=10)
        app_var = ctk.StringVar(value="Select")
        ctk.CTkOptionMenu(t_manage, values=logic.get_appliances(room_name), variable=app_var, width=250).pack(pady=10)
        ctk.CTkButton(t_manage, text="Confirm Addition", width=250, height=45, fg_color=color, text_color="#111214", 
                      font=("Arial", 14, "bold"), border_spacing=0, corner_radius=6,
                      command=lambda: self.add_entry(room_name, app_var.get(), color)).pack(pady=20)
        
        self.add_empty_state_diagram(t_manage)
        room_recs = sorted([r for r in self.records if r.get("room") == room_name], key=lambda x: x['monthly_cost'], reverse=True)
        if room_recs:
            for i, r in enumerate(room_recs, 1):
                ctk.CTkLabel(t_app_rank, text=f"{i}. {r['appliance']}: ₱{r['monthly_cost']:.2f}", font=("Arial", 15)).pack(pady=4, anchor="w", padx=15)
        else:
            self.add_empty_state_diagram(t_app_rank, text="Analyze your usage ranking.")

    def add_empty_state_diagram(self, parent, text="Add your first appliance to populate this room."):
        diagram_frame = ctk.CTkFrame(parent, fg_color="transparent")
        diagram_frame.pack(pady=40)
        ctk.CTkLabel(diagram_frame, text="[□] [□] [|]", font=("Arial", 28, "bold"), text_color="#2d2f31").pack()
        ctk.CTkLabel(diagram_frame, text="[O] [□] [|]", font=("Arial", 28, "bold"), text_color="#2d2f31").pack()
        ctk.CTkLabel(parent, text=text, font=("Arial", 14), text_color="#8a8d91", wraplength=350).pack(pady=10)

    def login_user(self):
        dialog = ctk.CTkInputDialog(text="Enter Username:", title="Login")
        name = dialog.get_input()
        if name:
            self.username = name
            self.records = logic.load_records(logic._user_records_path(name))
            self.show_map()

    def set_budget_ui(self):
        dialog = ctk.CTkInputDialog(text="Set Monthly Limit (₱):", title="Budget Settings")
        val = dialog.get_input()
        if val:
            try:
                self.monthly_budget = float(val)
                self.show_map()
            except ValueError:
                messagebox.showerror("Error", "Invalid Number")

    def add_entry(self, room, app, color):
        if app == "Select" or not app: return
        wattage = logic.get_wattage(room, app)
        new_rec = logic.build_record(room, app, wattage, "Moderate", 4)
        self.records.append(new_rec)
        self.show_map()
        self.fill_card_content(room, color)

    def save_data(self):
        logic.save_records(self.records, logic._user_records_path(self.username))
        messagebox.showinfo("Saved", "Progress Saved Successfully")

if __name__ == "__main__":
    app = WattzUpVisual()
    app.mainloop()
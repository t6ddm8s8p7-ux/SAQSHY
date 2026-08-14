import customtkinter as ctk


def make_card(parent, label, value, color=None, command=None):
    card = ctk.CTkFrame(parent, corner_radius=14)

    if command:
        ctk.CTkButton(
            card,
            text=label,
            font=("Arial", 12, "bold"),
            width=120,
            height=28,
            fg_color=color if color else "#1f6aa5",
            command=command
        ).pack(pady=(10, 5))
    else:
        ctk.CTkLabel(
            card,
            text=label,
            font=("Arial", 12, "bold"),
            text_color=color if color else "white"
        ).pack(pady=(10, 5))

    ctk.CTkLabel(
        card,
        text=str(value),
        font=("Arial", 24, "bold")
    ).pack(pady=(0, 10))

    return card


def build_stats_cards(parent, stats):
    for i, (label, value, color, command) in enumerate(stats):
        card = make_card(parent, label, value, color=color, command=command)
        card.grid(row=0, column=i, padx=5, pady=10, sticky="nsew")
        parent.grid_columnconfigure(i, weight=1)
import json
import os
import customtkinter as ctk

from modules import esen
from modules.translations import tr

CONFIG_FILE = "config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8-sig") as f:
            return json.load(f)

    return {
        "esen_login": "",
        "esen_password": "",
        "esen_url": "https://e-sen.kz"
    }


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=4)


def settings_window():
    config = load_config()

    window = ctk.CTkToplevel()
    window.title(tr("esen_settings"))
    window.geometry("550x520")
    window.lift()
    window.focus_force()

    ctk.CTkLabel(
        window,
        text=f"⚙️ {tr('esen_settings')}",
        font=("Arial", 28, "bold")
    ).pack(pady=20)

    ctk.CTkLabel(window, text=tr("esen_login")).pack(anchor="w", padx=60)

    login_entry = ctk.CTkEntry(window, width=400)
    login_entry.insert(0, config.get("esen_login", ""))
    login_entry.pack(pady=5)

    ctk.CTkLabel(window, text=tr("esen_password")).pack(anchor="w", padx=60)

    password_entry = ctk.CTkEntry(window, width=400, show="*")
    password_entry.insert(0, config.get("esen_password", ""))
    password_entry.pack(pady=5)

    ctk.CTkLabel(window, text=tr("esen_url")).pack(anchor="w", padx=60)

    url_entry = ctk.CTkEntry(window, width=400)
    url_entry.insert(0, config.get("esen_url", "https://e-sen.kz"))
    url_entry.pack(pady=5)

    status = ctk.CTkLabel(window, text="")
    status.pack(pady=10)

    def save_settings():
        save_config({
            "esen_login": login_entry.get(),
            "esen_password": password_entry.get(),
            "esen_url": url_entry.get()
        })

        status.configure(text=f"✅ {tr('settings_saved')}")

    ctk.CTkButton(
        window,
        text=f"💾 {tr('save')}",
        width=250,
        command=save_settings
    ).pack(pady=10)

    def open_esen():
        esen.open_esen_login()

        status.configure(
            text=f"🌐 {tr('esen_opened')}"
        )

    ctk.CTkButton(
        window,
        text=f"🔗 {tr('check_connection')}",
        width=250,
        command=open_esen
    ).pack()
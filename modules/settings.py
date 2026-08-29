# -*- coding: utf-8 -*-
"""Страница настроек приложения."""
import customtkinter as ctk
import json
import hashlib
from pathlib import Path
from tkinter import messagebox

from modules.translations import LANGUAGES, get_language, set_language, tr
from modules.crypto import encrypt_text, decrypt_text, is_encrypted


def _save_setting(key, value):
    config_file = Path("config.json")
    config = {}
    if config_file.exists():
        try:
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
        except:
            config = {}
    if "settings" not in config:
        config["settings"] = {}
    config["settings"][key] = value
    with open(config_file, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def _load_setting(key, default=None):
    config_file = Path("config.json")
    if not config_file.exists():
        return default
    try:
        with open(config_file, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("settings", {}).get(key, default)
    except:
        return default


def build_settings_page(parent, main_window):
    lang = get_language()
    
    print("=== НАЧАЛО build_settings_page ===")
    print(f"Текущий язык: {lang}")
    
    ctk.CTkLabel(
        parent,
        text="⚙️ " + tr('settings'),
        font=("Arial", 34, "bold")
    ).pack(pady=(20, 10))
    
    # ========== РАЗДЕЛ 1: НАСТРОЙКИ E-SEN ==========
    esen_frame = ctk.CTkFrame(parent, corner_radius=14)
    esen_frame.pack(fill="x", padx=20, pady=10)
    
    ctk.CTkLabel(
        esen_frame,
        text="🔐 e-SEN баптаулары / Настройки e-SEN",
        font=("Arial", 18, "bold"),
        text_color="#fec50c"
    ).pack(anchor="w", padx=20, pady=(15, 10))
    
    # БИН (логин)
    bin_frame = ctk.CTkFrame(esen_frame, fg_color="transparent")
    bin_frame.pack(fill="x", padx=20, pady=8)
    
    ctk.CTkLabel(
        bin_frame,
        text=" БИН / Логин e-SEN:",
        font=("Arial", 14),
        anchor="w"
    ).pack(fill="x", padx=10, pady=5)
    
    # ✅ ЗАГРУЗКА И ДЕШИФРОВКА логина
    encrypted_login = _load_setting("esen_login", "")
    login_value = decrypt_text(encrypted_login) if encrypted_login else ""
    
    bin_entry = ctk.CTkEntry(
        bin_frame,
        placeholder_text="Введите БИН объекта",
        width=400,
        height=38
    )
    bin_entry.insert(0, login_value)
    bin_entry.pack(fill="x", padx=10, pady=5)
    
    # Пароль
    pass_frame = ctk.CTkFrame(esen_frame, fg_color="transparent")
    pass_frame.pack(fill="x", padx=20, pady=8)
    
    ctk.CTkLabel(
        pass_frame,
        text="🔒 Пароль e-SEN:",
        font=("Arial", 14),
        anchor="w"
    ).pack(fill="x", padx=10, pady=5)
    
    # ✅ ЗАГРУЗКА И ДЕШИФРОВКА пароля
    encrypted_password = _load_setting("esen_password", "")
    password_value = decrypt_text(encrypted_password) if encrypted_password else ""
    
    pass_entry = ctk.CTkEntry(
        pass_frame,
        placeholder_text="Введите пароль",
        show="*",
        width=400,
        height=38
    )
    pass_entry.insert(0, password_value)
    pass_entry.pack(fill="x", padx=10, pady=5)
    
    # Ссылка
    url_frame = ctk.CTkFrame(esen_frame, fg_color="transparent")
    url_frame.pack(fill="x", padx=20, pady=8)
    
    ctk.CTkLabel(
        url_frame,
        text="🌐 Ссылка e-SEN:",
        font=("Arial", 14),
        anchor="w"
    ).pack(fill="x", padx=10, pady=5)
    
    url_entry = ctk.CTkEntry(
        url_frame,
        placeholder_text="https://e-sen.kz",
        width=400,
        height=38
    )
    url_entry.insert(0, _load_setting("esen_url", "https://e-sen.kz"))
    url_entry.pack(fill="x", padx=10, pady=5)
    
    def save_esen_settings():
        login = bin_entry.get()
        password = pass_entry.get()
        url = url_entry.get()
        
        # ✅ ШИФРОВАНИЕ перед сохранением
        _save_setting("esen_login", encrypt_text(login))
        _save_setting("esen_password", encrypt_text(password))
        _save_setting("esen_url", url)
        
        messagebox.showinfo("SanEpi AI", "✅ Настройки e-SEN сохранены (зашифрованы)!")
    
    ctk.CTkButton(
        esen_frame,
        text="💾 Сақтау / Сохранить",
        width=300,
        height=42,
        fg_color="#16a34a",
        hover_color="#15803d",
        font=("Arial", 14, "bold"),
        command=save_esen_settings
    ).pack(pady=10)
    
    print("✅ Раздел e-SEN создан")
    
    # ========== РАЗДЕЛ 2: ИНТЕРФЕЙС ==========
    interface_frame = ctk.CTkFrame(parent, corner_radius=14)
    interface_frame.pack(fill="x", padx=20, pady=10)
    
    ctk.CTkLabel(
        interface_frame,
        text="🎨 Интерфейс баптаулары",
        font=("Arial", 18, "bold"),
        text_color="#fec50c"
    ).pack(anchor="w", padx=20, pady=(15, 10))
    
    lang_frame = ctk.CTkFrame(interface_frame, fg_color="transparent")
    lang_frame.pack(fill="x", padx=20, pady=10)
    
    ctk.CTkLabel(
        lang_frame,
        text="🌐 Тіл / Language:",
        font=("Arial", 14),
        anchor="w"
    ).pack(fill="x", padx=10, pady=5)
    
    current_lang_code = get_language()
    current_lang_name = LANGUAGES.get(current_lang_code, "RU Русский")
    
    lang_menu = ctk.CTkOptionMenu(
        lang_frame,
        values=list(LANGUAGES.values()),
        width=400,
        height=38
    )
    lang_menu.set(current_lang_name)
    lang_menu.pack(fill="x", padx=10, pady=5)
    
    def save_language():
        selected = lang_menu.get()
        for code, name in LANGUAGES.items():
            if name == selected:
                set_language(code)
                main_window.sidebar.destroy()
                main_window.resize_grip.destroy()
                main_window.content.destroy()
                main_window.nav_buttons = {}
                main_window.is_resizing = False
                main_window._build_ui()
                main_window._set_active("settings")
                main_window.open_settings()
                messagebox.showinfo("SanEpi AI", f"Язык изменён: {name}")
                break
    
    ctk.CTkButton(
        lang_frame,
        text="💾 Қолдану / Применить",
        width=300,
        height=42,
        fg_color="#16a34a",
        hover_color="#15803d",
        font=("Arial", 14, "bold"),
        command=save_language
    ).pack(pady=10)
    
    print("=== КОНЕЦ build_settings_page ===")
# -*- coding: utf-8 -*-
"""Страница настроек приложения."""
import customtkinter as ctk
import json
import hashlib
from pathlib import Path
from tkinter import messagebox

from modules.translations import LANGUAGES, get_language, set_language, tr


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


# ВАЖНО: добавлен аргумент main_window
def build_settings_page(parent, main_window):
    lang = get_language()
    
    print("=== НАЧАЛО build_settings_page ===")
    print(f"Текущий язык: {lang}")
    
    # Заголовок
    ctk.CTkLabel(
        parent,
        text="⚙️ " + tr('settings'),
        font=("Arial", 34, "bold")
    ).pack(pady=(20, 10))
    
    # ========== РАЗДЕЛ 1: ИНТЕРФЕЙС ==========
    interface_frame = ctk.CTkFrame(parent, corner_radius=14)
    interface_frame.pack(fill="x", padx=20, pady=10)
    
    ctk.CTkLabel(
        interface_frame,
        text="🎨 Интерфейс баптаулары",
        font=("Arial", 18, "bold"),
        text_color="#fec50c"
    ).pack(anchor="w", padx=20, pady=(15, 10))
    
    # --- ЯЗЫК ---
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
        print(f"Выбран язык: {selected}")
        for code, name in LANGUAGES.items():
            if name == selected:
                set_language(code)
                
                # ТЕПЕРЬ ЭТО РАБОТАЕТ НА 100%, так как main_window передан напрямую
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
    
    print("✅ Кнопка языка создана")
    
    # --- РАЗМЕР ШРИФТА ---
    font_frame = ctk.CTkFrame(interface_frame, fg_color="transparent")
    font_frame.pack(fill="x", padx=20, pady=10)
    
    ctk.CTkLabel(
        font_frame,
        text="🔤 Қаріп өлшемі / Размер шрифта:",
        font=("Arial", 14),
        anchor="w"
    ).pack(fill="x", padx=10, pady=5)
    
    saved_font_size = _load_setting("font_size", 14)
    font_size_var = ctk.StringVar(value=str(saved_font_size))
    
    font_slider = ctk.CTkSlider(
        font_frame,
        from_=12,
        to=20,
        number_of_steps=8,
        command=lambda v: font_size_var.set(str(int(v)))
    )
    font_slider.set(int(saved_font_size))
    font_slider.pack(fill="x", padx=10, pady=5)
    
    ctk.CTkLabel(
        font_frame,
        textvariable=font_size_var,
        font=("Arial", 16, "bold"),
    ).pack(pady=5)
    
    def save_font_size():
        size = int(font_size_var.get())
        _save_setting("font_size", size)
        messagebox.showinfo("SanEpi AI", f"Размер шрифта: {size}")
    
    ctk.CTkButton(
        font_frame,
        text="💾 Сақтау / Сохранить",
        width=300,
        height=40,
        fg_color="#16a34a",
        hover_color="#15803d",
        command=save_font_size
    ).pack(pady=10)
    
    print("✅ Кнопка шрифта создана")
    
    # --- ТЕМА ---
    theme_frame = ctk.CTkFrame(interface_frame, fg_color="transparent")
    theme_frame.pack(fill="x", padx=20, pady=10)
    
    ctk.CTkLabel(
        theme_frame,
        text="🎨 Тақырып / Тема:",
        font=("Arial", 14),
        anchor="w"
    ).pack(fill="x", padx=10, pady=5)
    
    saved_theme = _load_setting("theme", "Dark")
    theme_names = {"Dark": "Қараңғы / Тёмная", "Light": "Жарық / Светлая", "System": "Жүйе / Системная"}
    
    theme_menu = ctk.CTkOptionMenu(
        theme_frame,
        values=["Қараңғы / Тёмная", "Жарық / Светлая", "Жүйе / Системная"],
        width=300,
        height=38
    )
    theme_menu.set(theme_names.get(saved_theme, "Қараңғы / Тёмная"))
    theme_menu.pack(fill="x", padx=10, pady=5)
    
    def save_theme():
        theme = theme_menu.get()
        theme_map = {
            "Қараңғы / Тёмная": "Dark",
            "Жарық / Светлая": "Light",
            "Жүйе / Системная": "System"
        }
        _save_setting("theme", theme_map.get(theme, "Dark"))
        ctk.set_appearance_mode(theme_map.get(theme, "Dark").lower())
        messagebox.showinfo("SanEpi AI", f"Тема: {theme}")
    
    ctk.CTkButton(
        theme_frame,
        text="💾 Сақтау / Сохранить",
        width=300,
        height=40,
        fg_color="#16a34a",
        hover_color="#15803d",
        command=save_theme
    ).pack(pady=10)
    
    print("✅ Кнопка темы создана")
    
    # ========== РАЗДЕЛ 2: БЕЗОПАСНОСТЬ ==========
    security_frame = ctk.CTkFrame(parent, corner_radius=14)
    security_frame.pack(fill="x", padx=20, pady=10)
    
    ctk.CTkLabel(
        security_frame,
        text="🔐 Қауіпсіздік / Безопасность",
        font=("Arial", 18, "bold"),
        text_color="#fec50c"
    ).pack(anchor="w", padx=20, pady=(15, 10))
    
    ctk.CTkButton(
        security_frame,
        text="🔑 Құпия сөзді өзгерту / Изменить пароль",
        width=350,
        height=42,
        fg_color="#7c3aed",
        hover_color="#6d28d9",
        command=lambda: messagebox.showinfo("SanEpi AI", "Функция в разработке")
    ).pack(pady=10)
    
    lock_frame = ctk.CTkFrame(security_frame, fg_color="transparent")
    lock_frame.pack(fill="x", padx=20, pady=10)
    
    ctk.CTkLabel(
        lock_frame,
        text="⏱️ Автоблоктау (мин):",
        font=("Arial", 14),
        anchor="w"
    ).pack(fill="x", padx=10, pady=5)
    
    lock_var = ctk.StringVar(value=str(_load_setting("auto_lock", "0")))
    lock_menu = ctk.CTkOptionMenu(
        lock_frame,
        variable=lock_var,
        values=["0", "5", "10", "15", "30", "60"],
        width=200,
        height=36
    )
    lock_menu.pack(fill="x", padx=10, pady=5)
    
    def save_lock():
        _save_setting("auto_lock", lock_var.get())
        messagebox.showinfo("SanEpi AI", f"Автоблокировка: {lock_var.get()} мин")
    
    ctk.CTkButton(
        lock_frame,
        text="💾 Сақтау / Сохранить",
        width=300,
        height=40,
        fg_color="#16a34a",
        hover_color="#15803d",
        command=save_lock
    ).pack(pady=10)
    
    log_frame = ctk.CTkFrame(security_frame, fg_color="transparent")
    log_frame.pack(fill="x", padx=20, pady=10)
    
    ctk.CTkLabel(
        log_frame,
        text="📋 Логтау / Логирование:",
        font=("Arial", 14),
        anchor="w"
    ).pack(fill="x", padx=10, pady=5)
    
    log_var = ctk.BooleanVar(value=_load_setting("enable_logging", True))
    ctk.CTkSwitch(
        log_frame,
        text="Қосулы / Включено",
        variable=log_var
    ).pack(pady=5)
    
    def save_log():
        _save_setting("enable_logging", log_var.get())
        messagebox.showinfo("SanEpi AI", f"Логирование: {'вкл' if log_var.get() else 'выкл'}")
    
    ctk.CTkButton(
        log_frame,
        text="💾 Сақтау / Сохранить",
        width=300,
        height=40,
        fg_color="#16a34a",
        hover_color="#15803d",
        command=save_log
    ).pack(pady=10)
    
    print("=== КОНЕЦ build_settings_page ===")
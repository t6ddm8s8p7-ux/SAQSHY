"""
SAQSHY SanEpi — фирменный интерфейс.
Логотип: щит стража с шаңыраком внутри.
"""
import math
import warnings
import tkinter as tk
import customtkinter as ctk
from datetime import datetime

# Подавляем warning про PhotoImage (это не критично)
warnings.filterwarnings("ignore", category=UserWarning, module="customtkinter")

from modules import dashboard, hr_page, settings, site_sync, pool_page, hygiene_page
from modules import violations_page, lab_page, complaints_page
from modules.ai_assistant_page import build_ai_assistant_page
from modules.esen_page import build_esen_page
from modules.haccp import build_haccp_page
from modules.inspection import build_inspection_page
from modules.laws_page import build_laws_page
from modules.medical import build_medical_page
from modules.suppliers import build_suppliers_page
from modules.reports import build_reports_page
from modules.ses_objects import build_ses_page
from modules.letters import build_letters_page
from modules.dd_page import DDPage

# ИМПОРТ ПЕРЕВОДОВ
from modules.translations import LANGUAGES, get_language, set_language, tr
from modules.ui_translations import get_ui_translation

# ================= БРЕНД =================
APP_NAME = "SAQSHY SanEpi"
APP_TAG = "Санитарный страж • Sanitary Guardian"

# ================= ПАЛИТРА =================
GOLD = "#fec50c"
GOLD_HOVER = "#e0ad00"
BG_SIDE = "#062a33"
BG_TOP = "#083341"
BG_PAGE = "#07222b"
BG_HOVER = "#0d3d4b"
TEXT_MAIN = "#e8f6fb"
TEXT_MUTED = "#7fb6c9"
FONT = "Segoe UI"

def _lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

def _hx(c):
    return "#%02x%02x%02x" % c

def make_logo(size=72, bg=BG_SIDE):
    """🛡️ Щит стража с шаңыраком внутри."""
    img = tk.PhotoImage(width=size, height=size)
    top, bottom = (0, 147, 176), (0, 84, 112)
    gold = (254, 197, 12)
    bgc = tuple(int(BG_SIDE[i:i + 2], 16) for i in (1, 3, 5))

    def in_shield(u, v, m):
        top_v = 0.06 + m
        bot_v = 0.94 - m * 1.6
        hw = 0.40 - m
        if v < top_v or v > bot_v: return False
        if v <= 0.45: h = hw
        else:
            t = (v - 0.45) / (0.94 - 0.45)
            h = hw * max(0.0, 1 - t * t) ** 0.5
        return abs(u - 0.5) <= h

    cx, cy, R = 0.5, 0.46, 0.20
    for y in range(size):
        v = y / size
        g = _lerp(top, bottom, v)
        row = []
        for x in range(size):
            u = x / size
            col = bgc
            if in_shield(u, v, 0.0):
                if not in_shield(u, v, 0.06): col = gold
                else:
                    col = g
                    d = ((u - cx) ** 2 + (v - cy) ** 2) ** 0.5
                    if abs(d - R) <= 0.025: col = gold
                    else:
                        for ang in (0.0, 60.0, 120.0):
                            a = math.radians(ang)
                            du, dv = u - cx, v - cy
                            along = du * math.cos(a) + dv * math.sin(a)
                            perp = -du * math.sin(a) + dv * math.cos(a)
                            if abs(perp) <= 0.02 and abs(along) <= R:
                                col = gold
                                break
            row.append(_hx(col))
        img.put(" ".join(row), to=(0, y))
    return img

def build_dd_page(master):
    DDPage(master).pack(fill="both", expand=True)

class MainWindow:
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.app = ctk.CTk()
        self.app.title(f"{APP_NAME} — {APP_TAG}")
        self.app.geometry("1440x900")
        self.app.minsize(1200, 760)

        self.logo_img = make_logo(72)
        self.logo_small = make_logo(44)
        try:
            self.app.iconphoto(True, self.logo_img)
        except Exception:
            pass

        self.nav_buttons = {}
        self.is_resizing = False
        self.start_x = 0
        self.start_width = 0
        
        self._build_ui()
        self._set_active("dashboard")
        self.open_dashboard()
        self._tick()

    def _build_ui(self):
        # 1. Сайдбар: ширина 400px
        self.sidebar = ctk.CTkFrame(self.app, width=400, corner_radius=0, fg_color=BG_SIDE)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # 2. Полоса для изменения размера
        self.resize_grip = ctk.CTkFrame(self.app, width=8, corner_radius=0, fg_color=BG_SIDE)
        self.resize_grip.pack(side="left", fill="y")
        self.resize_grip.pack_propagate(False)
        
        # 3. Привязка событий: меняем размер ТОЛЬКО при отпускании кнопки мыши
        self.resize_grip.bind("<ButtonPress-1>", self.start_resize)
        self.resize_grip.bind("<ButtonRelease-1>", self.finish_resize)
        self.resize_grip.bind("<Enter>", lambda e: self.resize_grip.configure(fg_color=GOLD, cursor="sb_h_double_arrow"))
        self.resize_grip.bind("<Leave>", lambda e: self.resize_grip.configure(fg_color=BG_SIDE, cursor=""))

        # 4. Основной контент
        self.content = ctk.CTkFrame(self.app, corner_radius=0, fg_color=BG_PAGE)
        self.content.pack(side="right", fill="both", expand=True)
        
        self._build_sidebar()
        self._build_topbar()
        self.page_frame = ctk.CTkFrame(self.content, corner_radius=0, fg_color="transparent")
        self.page_frame.pack(fill="both", expand=True)

    def start_resize(self, event):
        """Начало изменения ширины сайдбара."""
        self.is_resizing = True
        self.start_x = event.x_root
        self.start_width = self.sidebar.winfo_width()

    def finish_resize(self, event):
        """Применяем новую ширину только ПОСЛЕ отпускания кнопки мыши (без лагов)."""
        if not self.is_resizing:
            return
        self.is_resizing = False
        
        delta = event.x_root - self.start_x
        new_width = self.start_width + delta
        
        # Ограничиваем ширину от 320 до 550px
        if 320 <= new_width <= 550:
            self.sidebar.configure(width=new_width)

    def _build_sidebar(self):
        lang = get_language()
        
        head = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        head.pack(fill="x", padx=14, pady=(16, 6))
        head.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(head, text="", image=self.logo_small, width=44, height=44).grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="n")
        ctk.CTkLabel(head, text=APP_NAME, font=(FONT, 19, "bold"), text_color=GOLD).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(head, text=APP_TAG, font=(FONT, 10), text_color=TEXT_MUTED).grid(row=1, column=1, sticky="w")

        ctk.CTkFrame(self.sidebar, height=2, corner_radius=0, fg_color=GOLD).pack(fill="x", padx=16, pady=(8, 4))

        menu_scroll = ctk.CTkScrollableFrame(
            self.sidebar, fg_color="transparent", corner_radius=0,
            scrollbar_button_color="#0d3d4b", scrollbar_button_hover_color="#155e75",
        )
        menu_scroll.pack(fill="both", expand=True, padx=10, pady=(4, 8))

        self.nav_buttons = {}
        groups = [
            (get_ui_translation("персонал", lang), [
                ("dashboard", "🏠", f" {tr('dashboard')}", self.open_dashboard),
                ("hr", "👥", f" {tr('hr')}", self.open_hr),
                ("esen", "🏥", f" {tr('esen')}", self.open_esen),
                ("medical", "🩺", f" {tr('medical')}", self.open_medical),
                ("hygiene", "🎓", f" {get_ui_translation('гигиеническое_обучение', lang)}", self.open_hygiene),
            ]),
            (get_ui_translation("контроль", lang), [
                ("haccp", "🌡️", f" {tr('haccp')}", self.open_haccp),
                ("pool", "🏊", f" {get_ui_translation('бассейны', lang)}", self.open_pool),
                ("violations", "📷", f" {get_ui_translation('нарушения', lang)}", self.open_violations),
                ("lab", "🧪", f" {get_ui_translation('лаборатория', lang)}", self.open_lab),
                ("complaints", "📢", f" {get_ui_translation('жалобы', lang)}", self.open_complaints),
                ("inspections", "📄", f" {tr('inspections')}", self.open_inspections),
                ("ses", "🏛️", f" {get_ui_translation('сэс', lang)}", self.open_ses),
                ("dd", "🛡️", f" {get_ui_translation('дд', lang)}", self.open_dd),
                ("suppliers", "📦", f" {tr('suppliers')}", self.open_suppliers),
            ]),
            (get_ui_translation("документы", lang), [
                ("laws", "📑", f" {tr('laws')}", self.open_laws),
                ("letters", "✉️", f" {tr('letters')}", self.open_letters),
                ("reports", "📊", f" {tr('reports')}", self.open_reports),
            ]),
            (get_ui_translation("интеллект", lang), [
                ("ai", "🤖", f" {tr('ai_assistant')}", self.open_ai_assistant),
            ]),
            (get_ui_translation("система", lang), [
                ("settings", "⚙️", f" {tr('settings')}", self.open_settings),
                ("sitesync", "🔄", f" {get_ui_translation('сайт_haccp', lang)}", lambda: site_sync.open_sync_window()),
            ]),
        ]

        for title, items in groups:
            ctk.CTkLabel(menu_scroll, text=title, font=(FONT, 10, "bold"), text_color=GOLD).pack(anchor="w", padx=10, pady=(12, 3))
            for btn_id, icon, text, method in items:
                btn = ctk.CTkButton(
                    menu_scroll, 
                    text=icon + text, 
                    font=(FONT, 12),
                    height=40,
                    corner_radius=10, 
                    anchor="w",
                    fg_color="transparent", 
                    hover_color=BG_HOVER, 
                    text_color=TEXT_MAIN,
                )
                btn.pack(fill="x", pady=2)
                btn.configure(command=lambda b=btn_id, m=method: (self._set_active(b), m()))
                self.nav_buttons[btn_id] = btn

        # Показываем текущий язык (без возможности выбора здесь)
        bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom.pack(fill="x", padx=14, pady=(0, 14))
        current_lang_name = LANGUAGES.get(get_language(), "🇷🇺 Русский")
        ctk.CTkLabel(
            bottom, 
            text=f"🌐 Язык: {current_lang_name}", 
            font=(FONT, 11), 
            text_color=TEXT_MUTED
        ).pack(anchor="w")

    def _build_topbar(self):
        top = ctk.CTkFrame(self.content, height=62, corner_radius=0, fg_color=BG_TOP)
        top.pack(fill="x")
        top.pack_propagate(False)

        ctk.CTkFrame(top, width=5, corner_radius=0, fg_color=GOLD).pack(side="left", padx=(18, 10), pady=14)
        self.title_label = ctk.CTkLabel(top, text="", font=(FONT, 18, "bold"), text_color=TEXT_MAIN)
        self.title_label.pack(side="left")

        right = ctk.CTkFrame(top, fg_color="transparent")
        right.pack(side="right", padx=18)
        self.clock_label = ctk.CTkLabel(right, text="", font=("Consolas", 20, "bold"), text_color=GOLD)
        self.clock_label.pack(side="left", padx=(0, 14))
        self.date_label = ctk.CTkLabel(right, text="", font=(FONT, 12), text_color=TEXT_MUTED)
        self.date_label.pack(side="left", padx=(0, 14))
        
        user_info = get_ui_translation("дәурен_оспан__гл_санврач", get_language())
        chip = ctk.CTkFrame(right, corner_radius=20, fg_color="#0d3d4b", border_width=1, border_color=GOLD)
        chip.pack(side="left")
        ctk.CTkLabel(chip, text=f"👤 {user_info}", font=(FONT, 12, "bold"), text_color=TEXT_MAIN).pack(padx=14, pady=7)

        ctk.CTkFrame(self.content, height=2, corner_radius=0, fg_color=GOLD).pack(fill="x")

    def _tick(self):
        now = datetime.now()
        lang = get_language()
        
        days = {
            "ru": ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"],
            "kk": ["Дүйсенбі", "Сейсенбі", "Сәрсенбі", "Бейсенбі", "Жұма", "Сенбі", "Жексенбі"],
            "en": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
            "tr": ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
        }
        day_name = days.get(lang, days["ru"])[now.weekday()]
        
        try:
            self.clock_label.configure(text=now.strftime("%H:%M:%S"))
            self.date_label.configure(text=f"{now.day:02d}.{now.month:02d}.{now.year} • {day_name}")
        except Exception:
            pass
        self.app.after(1000, self._tick)

    def _set_active(self, btn_id):
        for b_id, btn in self.nav_buttons.items():
            if b_id == btn_id:
                btn.configure(fg_color=GOLD, hover_color=GOLD_HOVER, text_color="#062733", font=(FONT, 12, "bold"))
            else:
                btn.configure(fg_color="transparent", hover_color=BG_HOVER, text_color=TEXT_MAIN, font=(FONT, 12))

    def change_language(self, selected_name):
        lang_code = "ru"
        for code, name in LANGUAGES.items():
            if name == selected_name:
                lang_code = code
                break
        set_language(lang_code)
        self.sidebar.destroy()
        self.resize_grip.destroy()
        self.content.destroy()
        self.nav_buttons = {}
        self.is_resizing = False
        self._build_ui()
        self._set_active("dashboard")
        self.open_dashboard()

    def clear_content(self):
        for widget in self.page_frame.winfo_children():
            widget.destroy()

    def _show(self, title_key, builder):
        title = get_ui_translation(title_key, get_language())
        self.title_label.configure(text=title)
        self.clear_content()
        builder(self.page_frame)

    # --- МЕТОДЫ ОТКРЫТИЯ СТРАНИЦ ---
    def open_dashboard(self): self._show("dashboard", dashboard.build_dashboard_page)
    def open_hr(self): self._show("hr", hr_page.build_hr_page)
    def open_esen(self): self._show("esen", build_esen_page)
    def open_medical(self): self._show("medical", build_medical_page)
    def open_hygiene(self): self._show("гигиеническое_обучение_заголовок", hygiene_page.build_hygiene_page)
    def open_laws(self): self._show("laws", build_laws_page)
    def open_haccp(self): self._show("haccp", build_haccp_page)
    def open_pool(self): self._show("бассейны_заголовок", pool_page.build_pool_page)
    def open_violations(self): self._show("нарушения_заголовок", violations_page.build_violations_page)
    def open_lab(self): self._show("лабораторные_исследования_заголовок", lab_page.build_lab_page)
    def open_complaints(self): self._show("журнал_жалоб_заголовок", complaints_page.build_complaints_page)
    def open_suppliers(self): self._show("suppliers", build_suppliers_page)
    def open_inspections(self): self._show("inspections", build_inspection_page)
    def open_ses(self): self._show("сэс_заголовок", build_ses_page)
    def open_dd(self): self._show("дд_заголовок", build_dd_page)
    def open_ai_assistant(self): self._show("ai_assistant", build_ai_assistant_page)
    def open_letters(self): self._show("letters", build_letters_page)
    def open_reports(self): self._show("reports", build_reports_page)
    
    # ИСПРАВЛЕНО: Передаем self (экземпляр MainWindow) вторым аргументом
    def open_settings(self): 
        self._show("settings", lambda parent: settings.build_settings_page(parent, self))

    def run(self):
        self.app.mainloop()

def start_main_window():
    app = MainWindow()
    app.run()
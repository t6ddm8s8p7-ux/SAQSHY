"""
SAQSHY SanEpi — фирменный интерфейс.
Логотип: щит стража с шаңыраком внутри.
"""
import math
import tkinter as tk
import customtkinter as ctk
from datetime import datetime

from modules import dashboard
from modules import hr_page
from modules import settings
from modules import site_sync
from modules import pool_page
from modules import hygiene_page
from modules import violations_page
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
from modules.translations import LANGUAGES, get_language, set_language, tr

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
        if v < top_v or v > bot_v:
            return False
        if v <= 0.45:
            h = hw
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
                if not in_shield(u, v, 0.06):
                    col = gold
                else:
                    col = g
                    d = ((u - cx) ** 2 + (v - cy) ** 2) ** 0.5
                    if abs(d - R) <= 0.025:
                        col = gold
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
        self._build_ui()
        self._set_active("dashboard")
        self.open_dashboard()
        self._tick()

    def _build_ui(self):
        self.sidebar = ctk.CTkFrame(self.app, width=252, corner_radius=0, fg_color=BG_SIDE)
        self.sidebar.pack(side="left", fill="y")
        self.content = ctk.CTkFrame(self.app, corner_radius=0, fg_color=BG_PAGE)
        self.content.pack(side="right", fill="both", expand=True)
        self._build_sidebar()
        self._build_topbar()
        self.page_frame = ctk.CTkFrame(self.content, corner_radius=0, fg_color="transparent")
        self.page_frame.pack(fill="both", expand=True)

    def _build_sidebar(self):
        head = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        head.pack(fill="x", padx=14, pady=(16, 6))
        head.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(head, text="", image=self.logo_small,
                     width=44, height=44).grid(row=0, column=0, rowspan=2, padx=(0, 10), sticky="n")
        ctk.CTkLabel(head, text=APP_NAME, font=(FONT, 19, "bold"),
                     text_color=GOLD).grid(row=0, column=1, sticky="w")
        ctk.CTkLabel(head, text=APP_TAG, font=(FONT, 10),
                     text_color=TEXT_MUTED).grid(row=1, column=1, sticky="w")

        ctk.CTkFrame(self.sidebar, height=2, corner_radius=0, fg_color=GOLD).pack(fill="x", padx=16, pady=(8, 4))

        menu_scroll = ctk.CTkScrollableFrame(
            self.sidebar, fg_color="transparent", corner_radius=0,
            scrollbar_button_color="#0d3d4b", scrollbar_button_hover_color="#155e75",
        )
        menu_scroll.pack(fill="both", expand=True, padx=10, pady=(4, 8))

        self.nav_buttons = {}
        groups = [
            ("ПЕРСОНАЛ", [
                ("dashboard", "🏠", f" {tr('dashboard')}", self.open_dashboard),
                ("hr", "👥", f" {tr('hr')}", self.open_hr),
                ("esen", "🏥", f" {tr('esen')}", self.open_esen),
                ("medical", "🩺", f" {tr('medical')}", self.open_medical),
                ("hygiene", "🎓", " Гиг. обучение", self.open_hygiene),
            ]),
            ("КОНТРОЛЬ", [
                ("haccp", "🌡️", f" {tr('haccp')}", self.open_haccp),
                ("pool", "🏊", " Бассейны", self.open_pool),
                ("violations", "📷", " Нарушения", self.open_violations),
                ("inspections", "📄", f" {tr('inspections')}", self.open_inspections),
                ("ses", "🏛️", " СЭС", self.open_ses),
                ("dd", "🛡️", " ДД", self.open_dd),
                ("suppliers", "📦", f" {tr('suppliers')}", self.open_suppliers),
            ]),
            ("ДОКУМЕНТЫ", [
                ("laws", "📑", f" {tr('laws')}", self.open_laws),
                ("letters", "✉️", f" {tr('letters')}", self.open_letters),
                ("reports", "📊", f" {tr('reports')}", self.open_reports),
            ]),
            ("ИНТЕЛЛЕКТ", [
                ("ai", "🤖", f" {tr('ai_assistant')}", self.open_ai_assistant),
            ]),
            ("СИСТЕМА", [
                ("settings", "⚙️", f" {tr('settings')}", lambda: settings.settings_window()),
                ("sitesync", "🔄", " Сайт HACCP", lambda: site_sync.open_sync_window()),
            ]),
        ]

        for title, items in groups:
            ctk.CTkLabel(menu_scroll, text=title, font=(FONT, 10, "bold"),
                         text_color=GOLD).pack(anchor="w", padx=10, pady=(12, 3))
            for btn_id, icon, text, method in items:
                btn = ctk.CTkButton(
                    menu_scroll, text=icon + text, font=(FONT, 14),
                    height=38, corner_radius=10, anchor="w",
                    fg_color="transparent", hover_color=BG_HOVER, text_color=TEXT_MAIN,
                )
                btn.pack(fill="x", pady=2)
                btn.configure(command=lambda b=btn_id, m=method: (self._set_active(b), m()))
                self.nav_buttons[btn_id] = btn

        bottom = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        bottom.pack(fill="x", padx=14, pady=(0, 14))
        ctk.CTkLabel(bottom, text="🌐 " + tr("language"), font=(FONT, 11, "bold"),
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 3))
        current_name = LANGUAGES.get(get_language(), "🇷 Русский")
        self.language = ctk.StringVar(value=current_name)
        ctk.CTkOptionMenu(
            bottom, values=list(LANGUAGES.values()), variable=self.language,
            height=32, font=(FONT, 12), corner_radius=10,
            fg_color="#0d3d4b", button_color="#0d3d4b", button_hover_color=BG_HOVER,
            command=self.change_language,
        ).pack(fill="x")

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
        chip = ctk.CTkFrame(right, corner_radius=20, fg_color="#0d3d4b", border_width=1, border_color=GOLD)
        chip.pack(side="left")
        ctk.CTkLabel(chip, text="👤 Дәурен Оспан • Гл. санврач",
                     font=(FONT, 12, "bold"), text_color=TEXT_MAIN).pack(padx=14, pady=7)

        ctk.CTkFrame(self.content, height=2, corner_radius=0, fg_color=GOLD).pack(fill="x")

    def _tick(self):
        now = datetime.now()
        try:
            self.clock_label.configure(text=now.strftime("%H:%M:%S"))
            self.date_label.configure(text=now.strftime("%d.%m.%Y • %A"))
        except Exception:
            pass
        self.app.after(1000, self._tick)

    def _set_active(self, btn_id):
        for b_id, btn in self.nav_buttons.items():
            if b_id == btn_id:
                btn.configure(fg_color=GOLD, hover_color=GOLD_HOVER,
                              text_color="#062733", font=(FONT, 14, "bold"))
            else:
                btn.configure(fg_color="transparent", hover_color=BG_HOVER,
                              text_color=TEXT_MAIN, font=(FONT, 14))

    def change_language(self, selected_name):
        lang_code = "ru"
        for code, name in LANGUAGES.items():
            if name == selected_name:
                lang_code = code
                break
        set_language(lang_code)
        self.sidebar.destroy()
        self.content.destroy()
        self.nav_buttons = {}
        self._build_ui()
        self._set_active("dashboard")
        self.open_dashboard()

    def clear_content(self):
        for widget in self.page_frame.winfo_children():
            widget.destroy()

    def _show(self, title, builder):
        self.title_label.configure(text=title)
        self.clear_content()
        builder(self.page_frame)

    def open_dashboard(self):
        self._show(f"🏠 {tr('dashboard')}", dashboard.build_dashboard_page)

    def open_hr(self):
        self._show(f"👥 {tr('hr')}", hr_page.build_hr_page)

    def open_esen(self):
        self._show(f"🏥 {tr('esen')}", build_esen_page)

    def open_medical(self):
        self._show(f"🩺 {tr('medical')}", build_medical_page)

    def open_hygiene(self):
        self._show("🎓 Гигиеническое обучение", hygiene_page.build_hygiene_page)

    def open_laws(self):
        self._show(f"📑 {tr('laws')}", build_laws_page)

    def open_haccp(self):
        self._show(f"🌡️ {tr('haccp')}", build_haccp_page)

    def open_pool(self):
        self._show("🏊 Бассейны", pool_page.build_pool_page)

    def open_violations(self):
        self._show("📷 Нарушения", violations_page.build_violations_page)

    def open_suppliers(self):
        self._show(f"📦 {tr('suppliers')}", build_suppliers_page)

    def open_inspections(self):
        self._show(f"📄 {tr('inspections')}", build_inspection_page)

    def open_ses(self):
        self._show("🏛️ СЭС", build_ses_page)

    def open_dd(self):
        self._show("🛡️ ДД", build_dd_page)

    def open_ai_assistant(self):
        self._show(f"🤖 {tr('ai_assistant')}", build_ai_assistant_page)

    def open_letters(self):
        self._show(f"✉️ {tr('letters')}", build_letters_page)

    def open_reports(self):
        self._show(f"📊 {tr('reports')}", build_reports_page)

    def run(self):
        self.app.mainloop()


def start_main_window():
    app = MainWindow()
    app.run()
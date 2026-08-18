# -*- coding: utf-8 -*-
"""Журнал воды бассейнов по ҚР ДСМ-67 от 26.07.2022 (приложения 1–2) — 4 языка."""
import sqlite3
from datetime import date, datetime
from pathlib import Path

import customtkinter as ctk
from tkinter import messagebox

from modules.translations import get_language

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "database" / "sanepi.db"

YEARS = [2025, 2026, 2027, 2028, 2029, 2030]
MONTH_ORDER = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]

# Нормы по ҚР ДСМ-67: приложение 1 (температура) и приложение 2 (хлор, pH)
NORMS = {
    "adult":    {"t": (24.0, 26.0), "cl": (0.3, 0.6), "ph": (6.0, 9.0)},
    "children": {"t": (30.0, 32.0), "cl": (0.1, 0.3), "ph": (6.0, 9.0)},
    "open":     {"t": (27.0, 29.0), "cl": (0.3, 0.6), "ph": (6.0, 9.0)},
}

T = {
    "title": {"ru": "🏊 Качество воды бассейнов", "kk": "🏊 Бассейн суының сапасы", "en": "🏊 Pool water quality", "tr": "🏊 Havuz suyu kalitesi"},
    "law": {"ru": "ҚР ДСМ-67 от 26.07.2022 (прил. 1–2)", "kk": "26.07.2022 ж. ҚР ДСМ-67 (1–2 қосымшалар)", "en": "QR DSM-67 (app. 1–2)", "tr": "QR DSM-67 (ek 1–2)"},
    "add": {"ru": "➕ Добавить замер", "kk": "➕ Өлшем қосу", "en": "➕ Add measurement", "tr": "➕ Ölçüm ekle"},
    "pools_title": {"ru": "🏊 Мои бассейны:", "kk": "🏊 Менің бассейндерім:", "en": "🏊 My pools:", "tr": "🏊 Havuzlarım:"},
    "add_pool": {"ru": "➕ Добавить бассейн", "kk": "➕ Бассейн қосу", "en": "➕ Add pool", "tr": "➕ Havuz ekle"},
    "no_pools": {"ru": "Бассейнов нет — нажмите «➕ Добавить бассейн».", "kk": "Бассейндер жоқ — «➕ Бассейн қосу» басыңыз.", "en": "No pools — click “➕ Add pool”.", "tr": "Havuz yok — “➕ Havuz ekle”."},
    "dlg_pool": {"ru": "Бассейн", "kk": "Бассейн", "en": "Pool", "tr": "Havuz"},
    "pool_name": {"ru": "Название бассейна:", "kk": "Бассейн атауы:", "en": "Pool name:", "tr": "Havuz adı:"},
    "pool_type": {"ru": "Тип бассейна:", "kk": "Бассейн түрі:", "en": "Pool type:", "tr": "Havuz türü:"},
    "type_adult": {"ru": "🏊 Взрослый (24–26°)", "kk": "🏊 Ересектер (24–26°)", "en": "🏊 Adult (24–26°)", "tr": "🏊 Yetişkin (24–26°)"},
    "type_children": {"ru": "🧒 Детский (30–32°)", "kk": "🧒 Балалар (30–32°)", "en": "🧒 Children (30–32°)", "tr": "🧒 Çocuk (30–32°)"},
    "type_open": {"ru": "🌊 Открытый (27–29°)", "kk": "🌊 Ашық (27–29°)", "en": "🌊 Open (27–29°)", "tr": "🌊 Açık (27–29°)"},
    "del_pool": {"ru": "Удалить бассейн и все его замеры?", "kk": "Бассейн мен оның барлық өлшемдерін жою керек пе?", "en": "Delete the pool and all its measurements?", "tr": "Havuz ve tüm ölçümleri silinsin mi?"},
    "period": {"ru": "📅 Период:", "kk": "📅 Кезең:", "en": "📅 Period:", "tr": "📅 Dönem:"},
    "all_months": {"ru": "Все месяцы", "kk": "Барлық айлар", "en": "All months", "tr": "Tüm aylar"},
    "journal": {"ru": "📜 Журнал замеров", "kk": "📜 Өлшемдер журналы", "en": "📜 Measurement journal", "tr": "📜 Ölçüm günlüğü"},
    "no_rec": {"ru": "Замеров нет — нажмите «➕ Добавить замер».", "kk": "Өлшемдер жоқ — «➕ Өлшем қосу» басыңыз.", "en": "No measurements — click “➕ Add measurement”.", "tr": "Ölçüm yok — “➕ Ölçüm ekle”."},
    "pool": {"ru": "Бассейн:", "kk": "Бассейн:", "en": "Pool:", "tr": "Havuz:"},
    "date_lbl": {"ru": "Дата (ГГГГ-ММ-ДД):", "kk": "Күні (ЖЖЖЖ-АА-КК):", "en": "Date (YYYY-MM-DD):", "tr": "Tarih (YYYY-AA-GG):"},
    "time_lbl": {"ru": "Время (ЧЧ:ММ):", "kk": "Уақыты (СС:ММ):", "en": "Time (HH:MM):", "tr": "Saat (SS:DD):"},
    "cl_lbl": {"ru": "Свободный хлор, мг/л:", "kk": "Еркін хлор, мг/л:", "en": "Free chlorine, mg/L:", "tr": "Serbest klor, mg/L:"},
    "ph_lbl": {"ru": "pH:", "kk": "pH:", "en": "pH:", "tr": "pH:"},
    "t_lbl": {"ru": "Температура, °C:", "kk": "Температура, °C:", "en": "Temperature, °C:", "tr": "Sıcaklık, °C:"},
    "resp": {"ru": "Ответственный:", "kk": "Жауапты:", "en": "Responsible:", "tr": "Sorumlu:"},
    "corr": {"ru": "Корректирующее действие (при отклонении):", "kk": "Түзету іс-әрекеті (ауытқу кезінде):", "en": "Corrective action (on deviation):", "tr": "Düzeltici işlem (sapmada):"},
    "save": {"ru": "💾 Сохранить", "kk": "💾 Сақтау", "en": "💾 Save", "tr": "💾 Kaydet"},
    "warning": {"ru": "⚠️ Внимание", "kk": "⚠️ Назар аударыңыз", "en": "⚠️ Warning", "tr": "⚠️ Uyarı"},
    "need_corr": {"ru": "При отклонении укажите корректирующее действие!", "kk": "Ауытқу кезінде түзету іс-әрекетін көрсетіңіз!", "en": "Specify corrective action on deviation!", "tr": "Sapmada düzeltici işlemi belirtin!"},
    "need_vals": {"ru": "Заполните бассейн, дату и показатели.", "kk": "Бассейн, күні және көрсеткіштерді толтырыңыз.", "en": "Fill pool, date and values.", "tr": "Havuz, tarih ve değerleri doldurun."},
    "need_pool": {"ru": "Сначала добавьте бассейн!", "kk": "Алдымен бассейн қосыңыз!", "en": "Add a pool first!", "tr": "Önce havuz ekleyin!"},
    "del_rec": {"ru": "Удалить этот замер?", "kk": "Осы өлшемді жою керек пе?", "en": "Delete this measurement?", "tr": "Bu ölçüm silinsin mi?"},
    "norms_line": {"ru": "Нормы:", "kk": "Нормативтер:", "en": "Norms:", "tr": "Normlar:"},
}

MONTHS = {
    1: {"ru": "Январь", "kk": "Қаңтар", "en": "January", "tr": "Ocak"},
    2: {"ru": "Февраль", "kk": "Ақпан", "en": "February", "tr": "Şubat"},
    3: {"ru": "Март", "kk": "Наурыз", "en": "March", "tr": "Mart"},
    4: {"ru": "Апрель", "kk": "Сәуір", "en": "April", "tr": "Nisan"},
    5: {"ru": "Май", "kk": "Мамыр", "en": "May", "tr": "Mayıs"},
    6: {"ru": "Июнь", "kk": "Маусым", "en": "June", "tr": "Haziran"},
    7: {"ru": "Июль", "kk": "Шілде", "en": "July", "tr": "Temmuz"},
    8: {"ru": "Август", "kk": "Тамыз", "en": "August", "tr": "Ağustos"},
    9: {"ru": "Сентябрь", "kk": "Қыркүйек", "en": "September", "tr": "Eylül"},
    10: {"ru": "Октябрь", "kk": "Қазан", "en": "October", "tr": "Ekim"},
    11: {"ru": "Ноябрь", "kk": "Қараша", "en": "November", "tr": "Kasım"},
    12: {"ru": "Декабрь", "kk": "Желтоқсан", "en": "December", "tr": "Aralık"},
}


def tt(key):
    d = T.get(key)
    if not d:
        return key
    return d.get(get_language(), d.get("ru", key))


def month_name(m):
    d = MONTHS.get(m, {})
    return d.get(get_language(), d.get("ru", str(m)))


def type_label(t):
    return tt({"adult": "type_adult", "children": "type_children", "open": "type_open"}.get(t, "type_adult"))


def norms_text(t):
    n = NORMS.get(t, NORMS["adult"])
    return f"t: {n['t'][0]}–{n['t'][1]}°C • хлор: {n['cl'][0]}–{n['cl'][1]} • pH: {n['ph'][0]}–{n['ph'][1]}"


def db():
    return sqlite3.connect(DB_PATH)


def ensure_pool_tables():
    """Создаёт таблицы бассейнов, если их ещё нет."""
    c = db()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS pools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        pool_type TEXT DEFAULT 'adult',
        notes TEXT
    );
    CREATE TABLE IF NOT EXISTS pool_water_records (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pool_id INTEGER,
        date TEXT,
        time TEXT,
        free_chlorine TEXT,
        ph TEXT,
        temperature TEXT,
        status TEXT DEFAULT 'Норма',
        responsible TEXT,
        corrective_action TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    );
    """)
    c.commit()
    c.close()


def today_str():
    return date.today().isoformat()


def build_pool_page(master):
    PoolPage(master).pack(fill="both", expand=True)


class PoolPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        t = date.today()
        self.sel_year = t.year if t.year in YEARS else 2026
        self.sel_mnum = t.month
        ensure_pool_tables()
        self.rebuild()

    def rebuild(self):
        for w in self.winfo_children():
            w.destroy()
        head = ctk.CTkFrame(self)
        head.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(head, text=tt("title"), font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=10, pady=8)
        ctk.CTkButton(head, text=tt("add"), width=180, fg_color="#0891b2", hover_color="#0e7490",
                      command=self.record_dialog).pack(side="right", padx=10)
        ctk.CTkLabel(head, text=tt("law"), text_color="gray").pack(side="left", pady=8)
        self.pools_card()
        self.filter_row()
        self.journal_card()

    # ---------- Реестр бассейнов ----------
    def pools_card(self):
        card = ctk.CTkFrame(self)
        card.pack(fill="x", padx=10, pady=5)
        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=10, pady=(8, 0))
        ctk.CTkLabel(head, text=tt("pools_title"), font=ctk.CTkFont(size=15, weight="bold")).pack(side="left")
        ctk.CTkButton(head, text=tt("add_pool"), width=170, fg_color="#0891b2", hover_color="#0e7490",
                      command=lambda: self.pool_dialog()).pack(side="right")
        box = ctk.CTkFrame(card, fg_color="transparent")
        box.pack(fill="x", padx=10, pady=(4, 8))
        pools = db().execute("SELECT id, name, pool_type FROM pools ORDER BY name").fetchall()
        if not pools:
            ctk.CTkLabel(box, text=tt("no_pools"), text_color="gray").pack(pady=6)
        for pid, name, ptype in pools:
            row = ctk.CTkFrame(box, fg_color="gray15")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=f"{name} • {type_label(ptype)}",
                         font=ctk.CTkFont(size=13, weight="bold"), anchor="w").pack(side="left", padx=8, pady=6)
            ctk.CTkLabel(row, text=f"{tt('norms_line')} {norms_text(ptype)}",
                         text_color="gray", anchor="w").pack(side="left", padx=8)
            right = ctk.CTkFrame(row, fg_color="transparent")
            right.pack(side="right", padx=6)
            ctk.CTkButton(right, text="🗑️", width=36, fg_color="#7f1d1d", hover_color="#991b1b",
                          command=lambda p=pid: self.delete_pool(p)).pack(side="right", padx=(3, 0))
            ctk.CTkButton(right, text="✏️", width=36, fg_color="gray25",
                          command=lambda p=pid, n=name, t=ptype: self.pool_dialog((p, n, t))).pack(side="right")

    def pool_dialog(self, pool=None):
        win = ctk.CTkToplevel(self)
        win.title(tt("dlg_pool"))
        win.geometry("400x220")
        win.grab_set()
        ctk.CTkLabel(win, text=tt("pool_name")).pack(anchor="w", padx=20, pady=(12, 0))
        e_name = ctk.CTkEntry(win)
        e_name.insert(0, pool[1] if pool else "")
        e_name.pack(fill="x", padx=20)
        ctk.CTkLabel(win, text=tt("pool_type")).pack(anchor="w", padx=20, pady=(8, 0))
        om = ctk.CTkOptionMenu(win, values=[tt("type_adult"), tt("type_children"), tt("type_open")])
        om.set(type_label(pool[2]) if pool else tt("type_adult"))
        om.pack(fill="x", padx=20)

        def save():
            name = e_name.get().strip()
            if not name:
                messagebox.showwarning(tt("warning"), tt("pool_name"))
                return
            ptype = {"type_adult": "adult", "type_children": "children", "type_open": "open"}.get(
                next((k for k in ("type_adult", "type_children", "type_open") if tt(k) == om.get()), "type_adult"), "adult")
            c = db()
            if pool:
                c.execute("UPDATE pools SET name=?, pool_type=? WHERE id=?", (name, ptype, pool[0]))
            else:
                c.execute("INSERT INTO pools (name, pool_type) VALUES (?,?)", (name, ptype))
            c.commit(); c.close()
            win.destroy(); self.rebuild()
        ctk.CTkButton(win, text=tt("save"), command=save).pack(pady=12)

    def delete_pool(self, pid):
        if messagebox.askyesno(tt("warning"), tt("del_pool")):
            c = db()
            c.execute("DELETE FROM pool_water_records WHERE pool_id=?", (pid,))
            c.execute("DELETE FROM pools WHERE id=?", (pid,))
            c.commit(); c.close()
            self.rebuild()

    # ---------- Фильтр ----------
    def filter_row(self):
        filt = ctk.CTkFrame(self, fg_color="transparent")
        filt.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(filt, text=tt("period"), font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        yom = ctk.CTkOptionMenu(filt, values=[str(y) for y in YEARS], width=100, command=self._on_year)
        yom.set(str(self.sel_year))
        yom.pack(side="right", padx=(4, 0))
        mvals = [tt("all_months")] + [month_name(m) for m in MONTH_ORDER]
        mom = ctk.CTkOptionMenu(filt, values=mvals, width=150, command=self._on_month)
        mom.set(tt("all_months") if self.sel_mnum == 0 else month_name(self.sel_mnum))
        mom.pack(side="right", padx=(4, 0))

    def _on_year(self, v):
        self.sel_year = int(v)
        self.rebuild()

    def _on_month(self, v):
        self.sel_mnum = 0 if v == tt("all_months") else next((m for m in MONTH_ORDER if month_name(m) == v), 0)
        self.rebuild()

    # ---------- Журнал ----------
    def journal_card(self):
        card = ctk.CTkFrame(self)
        card.pack(fill="both", expand=True, padx=10, pady=5)
        ctk.CTkLabel(card, text=tt("journal"), font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=10, pady=(8, 0))
        self._box = ctk.CTkScrollableFrame(card, height=280)
        self._box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._render()

    def _render(self):
        box = self._box
        for w in box.winfo_children():
            w.destroy()
        q = """SELECT r.id, p.name, r.date, r.time, r.free_chlorine, r.ph, r.temperature, r.status, r.responsible, r.corrective_action, p.pool_type
               FROM pool_water_records r LEFT JOIN pools p ON p.id = r.pool_id
               WHERE substr(r.date,1,4)=?"""
        params = [str(self.sel_year)]
        if self.sel_mnum:
            q += " AND substr(r.date,6,2)=?"
            params.append(f"{self.sel_mnum:02d}")
        q += " ORDER BY r.date DESC, r.time DESC LIMIT 300"
        rows = db().execute(q, params).fetchall()
        if not rows:
            ctk.CTkLabel(box, text=tt("no_rec"), text_color="gray").pack(pady=10)
            return
        for rid, pname, d, tm, cl, ph, t, status, resp, corr, ptype in rows:
            row = ctk.CTkFrame(box, fg_color="gray15")
            row.pack(fill="x", pady=2)
            icon = "✅" if status == "Норма" else "❌"
            txt = f"{icon} {d} {tm} • {pname or '—'} • хлор: {cl} • pH: {ph} • t: {t}° • {resp or ''}"
            if status != "Норма" and corr:
                txt += f" ⚙️ {corr}"
            ctk.CTkLabel(row, text=txt, anchor="w", justify="left", wraplength=880).pack(side="left", padx=8, pady=6)
            right = ctk.CTkFrame(row, fg_color="transparent")
            right.pack(side="right", padx=6)
            ctk.CTkButton(right, text="🗑️", width=36, fg_color="#7f1d1d", hover_color="#991b1b",
                          command=lambda r=rid: self.delete_rec(r)).pack(side="right", padx=(3, 0))
            rec = (rid, pname, d, tm, cl, ph, t, resp, corr)
            ctk.CTkButton(right, text="✏️", width=36, fg_color="gray25",
                          command=lambda r=rec: self.record_dialog(record=r)).pack(side="right")

    def delete_rec(self, rid):
        if messagebox.askyesno(tt("warning"), tt("del_rec")):
            c = db()
            c.execute("DELETE FROM pool_water_records WHERE id=?", (rid,))
            c.commit(); c.close()
            self.rebuild()

    # ---------- Замер ----------
    def record_dialog(self, record=None):
        pools = db().execute("SELECT id, name, pool_type FROM pools ORDER BY name").fetchall()
        if not pools:
            messagebox.showwarning(tt("warning"), tt("need_pool"))
            return
        win = ctk.CTkToplevel(self)
        win.title(tt("title"))
        win.geometry("460x560")
        win.grab_set()
        ctk.CTkLabel(win, text=tt("pool")).pack(anchor="w", padx=20, pady=(10, 0))
        om = ctk.CTkOptionMenu(win, values=[p[1] for p in pools])
        if record and record[1]:
            om.set(record[1])
        om.pack(fill="x", padx=20)
        info = ctk.CTkLabel(win, text="", text_color="gray")
        info.pack(anchor="w", padx=20)

        def show_norms(*_):
            p = next((x for x in pools if x[1] == om.get()), None)
            if p:
                info.configure(text=f"{tt('norms_line')} {norms_text(p[2])}")
        om.configure(command=show_norms)
        show_norms()

        ctk.CTkLabel(win, text=tt("date_lbl")).pack(anchor="w", padx=20, pady=(8, 0))
        e_date = ctk.CTkEntry(win)
        e_date.insert(0, record[2] if record else today_str())
        e_date.pack(fill="x", padx=20)
        ctk.CTkLabel(win, text=tt("time_lbl")).pack(anchor="w", padx=20, pady=(8, 0))
        e_time = ctk.CTkEntry(win)
        e_time.insert(0, record[3] if record else datetime.now().strftime("%H:%M"))
        e_time.pack(fill="x", padx=20)
        ctk.CTkLabel(win, text=tt("cl_lbl")).pack(anchor="w", padx=20, pady=(8, 0))
        e_cl = ctk.CTkEntry(win)
        e_cl.insert(0, record[4] if record else "")
        e_cl.pack(fill="x", padx=20)
        ctk.CTkLabel(win, text=tt("ph_lbl")).pack(anchor="w", padx=20, pady=(8, 0))
        e_ph = ctk.CTkEntry(win)
        e_ph.insert(0, record[5] if record else "")
        e_ph.pack(fill="x", padx=20)
        ctk.CTkLabel(win, text=tt("t_lbl")).pack(anchor="w", padx=20, pady=(8, 0))
        e_t = ctk.CTkEntry(win)
        e_t.insert(0, record[6] if record else "")
        e_t.pack(fill="x", padx=20)
        ctk.CTkLabel(win, text=tt("resp")).pack(anchor="w", padx=20, pady=(8, 0))
        e_resp = ctk.CTkEntry(win)
        e_resp.insert(0, record[7] if record else "Дәурен Оспан")
        e_resp.pack(fill="x", padx=20)
        ctk.CTkLabel(win, text=tt("corr")).pack(anchor="w", padx=20, pady=(8, 0))
        e_corr = ctk.CTkEntry(win)
        e_corr.insert(0, record[8] if record else "")
        e_corr.pack(fill="x", padx=20)

        def save():
            p = next((x for x in pools if x[1] == om.get()), None)
            if not p:
                messagebox.showwarning(tt("warning"), tt("need_pool"))
                return
            cl_s, ph_s, t_s = e_cl.get().strip(), e_ph.get().strip(), e_t.get().strip()
            if not e_date.get() or not (cl_s or ph_s or t_s):
                messagebox.showwarning(tt("warning"), tt("need_vals"))
                return
            n = NORMS.get(p[2], NORMS["adult"])
            ok = True
            for val, (lo, hi) in ((cl_s, n["cl"]), (ph_s, n["ph"]), (t_s, n["t"])):
                if val:
                    try:
                        v = float(val.replace(",", "."))
                        if v < lo or v > hi:
                            ok = False
                    except ValueError:
                        ok = False
            status = "Норма" if ok else "Отклонение"
            if not ok and not e_corr.get().strip():
                messagebox.showwarning(tt("warning"), tt("need_corr"))
                return
            c = db()
            if record:
                c.execute("""UPDATE pool_water_records SET pool_id=?, date=?, time=?, free_chlorine=?, ph=?, temperature=?, status=?, responsible=?, corrective_action=? WHERE id=?""",
                          (p[0], e_date.get(), e_time.get(), cl_s, ph_s, t_s, status, e_resp.get(), e_corr.get(), record[0]))
            else:
                c.execute("""INSERT INTO pool_water_records (pool_id, date, time, free_chlorine, ph, temperature, status, responsible, corrective_action) VALUES (?,?,?,?,?,?,?,?,?)""",
                          (p[0], e_date.get(), e_time.get(), cl_s, ph_s, t_s, status, e_resp.get(), e_corr.get()))
            c.commit(); c.close()
            win.destroy(); self.rebuild()
        ctk.CTkButton(win, text=tt("save"), command=save).pack(pady=12)
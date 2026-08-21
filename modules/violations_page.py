# -*- coding: utf-8 -*-
"""Журнал нарушений с фотофиксацией — 4 языка."""
import json
import os
import shutil
import sqlite3
from datetime import date, datetime
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox

from modules.translations import get_language

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "database" / "sanepi.db"
PHOTO_DIR = PROJECT_ROOT / "database" / "violation_photos"

T = {
    "title": {"ru": "📷 Нарушения (фотофиксация)", "kk": "📷 Бұзушылықтар (фотофиксация)", "en": "📷 Violations (photo)", "tr": "📷 İhlaller (foto)"},
    "add": {"ru": "➕ Добавить нарушение", "kk": "➕ Бұзушылық қосу", "en": "➕ Add violation", "tr": "➕ İhlal ekle"},
    "date": {"ru": "Дата выявления (ГГГГ-ММ-ДД):", "kk": "Анықталған күні (ЖЖЖЖ-АА-КК):", "en": "Detection date (YYYY-MM-DD):", "tr": "Tespit tarihi (YYYY-AA-GG):"},
    "location": {"ru": "Место / подразделение (объекты СЭС):", "kk": "Орын / бөлімше (СЭС нысандары):", "en": "Location (SES objects):", "tr": "Yer / birim (SES nesneleri):"},
    "description": {"ru": "Описание нарушения:", "kk": "Бұзушылық сипаттамасы:", "en": "Violation description:", "tr": "İhlal açıklaması:"},
    "responsible": {"ru": "Ответственный за устранение:", "kk": "Жоюға жауапты:", "en": "Responsible for fix:", "tr": "Düzeltmeden sorumlu:"},
    "deadline": {"ru": "Срок устранения (ГГГГ-ММ-ДД):", "kk": "Жою мерзімі (ЖЖЖЖ-АА-КК):", "en": "Fix deadline (YYYY-MM-DD):", "tr": "Düzeltme tarihi (YYYY-AA-GG):"},
    "photo": {"ru": "📷 Фото: не выбрано", "kk": "📷 Фото: таңдалмаған", "en": "📷 Photo: not selected", "tr": "📷 Foto: seçilmedi"},
    "attach": {"ru": "📎 Прикрепить фото", "kk": "📎 Фото тіркеу", "en": "📎 Attach photo", "tr": "📎 Foto ekle"},
    "open": {"ru": "🔴 Открыто", "kk": "🔴 Ашық", "en": "🔴 Open", "tr": "🔴 Açık"},
    "fixed": {"ru": "✅ Устранено", "kk": "✅ Жойылды", "en": "✅ Fixed", "tr": "✅ Düzeltildi"},
    "overdue": {"ru": "⚠️ Просрочено", "kk": "⚠️ Мерзімі өткен", "en": "🔴 Overdue", "tr": "⚠️ Gecikmiş"},
    "all": {"ru": "Все", "kk": "Барлығы", "en": "All", "tr": "Tümü"},
    "filter": {"ru": "🔎 Фильтр:", "kk": "🔎 Сүзгі:", "en": "🔎 Filter:", "tr": "🔎 Filtre:"},
    "save": {"ru": "💾 Сохранить", "kk": "💾 Сақтау", "en": "💾 Save", "tr": "💾 Kaydet"},
    "warning": {"ru": "⚠️ Внимание", "kk": "⚠️ Назар аударыңыз", "en": "⚠️ Warning", "tr": "⚠️ Uyarı"},
    "need_desc": {"ru": "Опишите нарушение!", "kk": "Бұзушылықты сипаттаңыз!", "en": "Describe the violation!", "tr": "İhlali açıklayın!"},
    "del_rec": {"ru": "Удалить запись?", "kk": "Жазбаны жою керек пе?", "en": "Delete record?", "tr": "Kayıt silinsin mi?"},
    "no_rec": {"ru": "Нарушений нет — отличная работа! 🎉", "kk": "Бұзушылықтар жоқ — керемет! 🎉", "en": "No violations — great job! 🎉", "tr": "İhlal yok — harika! 🎉"},
}


def tt(key):
    d = T.get(key)
    if not d:
        return key
    return d.get(get_language(), d.get("ru", key))


def db():
    return sqlite3.connect(DB_PATH)


def today_str():
    return date.today().isoformat()


def ensure_table():
    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    c = db()
    c.execute("""CREATE TABLE IF NOT EXISTS violations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        location TEXT,
        description TEXT,
        photo_path TEXT,
        responsible TEXT,
        deadline TEXT,
        status TEXT DEFAULT 'open',
        fix_note TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    )""")
    c.commit()
    c.close()


def get_locations():
    """Объекты только из раздела СЭС — из того же файла ses_objects.json (один источник)."""
    locs = set()
    p = PROJECT_ROOT / "database" / "ses_objects.json"
    try:
        with open(p, "r", encoding="utf-8-sig") as f:
            items = json.load(f)
    except Exception:
        items = []
    for m in items if isinstance(items, list) else []:
        name = (m.get("name") or "").strip()
        if name:
            locs.add(name)
        for ch in m.get("children", []) or []:
            cname = (ch.get("name") or "").strip()
            if cname:
                locs.add(cname)
    if not locs:
        # запасной вариант: старая таблица ses_objects
        c = db()
        try:
            cols = [r[1] for r in c.execute("PRAGMA table_info(ses_objects)").fetchall()]
            col = next((x for x in ("name", "object_name", "title", "object") if x in cols), None)
            if col:
                for (n,) in c.execute(f"SELECT {col} FROM ses_objects").fetchall():
                    if n and str(n).strip():
                        locs.add(str(n).strip())
        except sqlite3.Error:
            pass
        c.close()
    return sorted(locs)


def build_violations_page(master):
    ViolationsPage(master).pack(fill="both", expand=True)


class ViolationsPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        self.flt = "all"
        ensure_table()
        self.rebuild()

    def rebuild(self):
        for w in self.winfo_children():
            w.destroy()
        head = ctk.CTkFrame(self)
        head.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(head, text=tt("title"), font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=10, pady=8)
        ctk.CTkButton(head, text=tt("add"), width=210, fg_color="#DC2626", hover_color="#b91c1c",
                      command=self.dialog).pack(side="right", padx=10)
        ctk.CTkLabel(head, text=tt("filter"), font=ctk.CTkFont(size=13, weight="bold")).pack(side="right", padx=(10, 0))
        om = ctk.CTkOptionMenu(head, values=[tt("all"), tt("open"), tt("fixed")], width=140, command=self._on_flt)
        om.set({ "all": tt("all"), "open": tt("open"), "fixed": tt("fixed") }[self.flt])
        om.pack(side="right", padx=(4, 0))

        card = ctk.CTkFrame(self)
        card.pack(fill="both", expand=True, padx=10, pady=5)
        box = ctk.CTkScrollableFrame(card, height=320)
        box.pack(fill="both", expand=True, padx=10, pady=10)
        q = "SELECT id, date, location, description, photo_path, responsible, deadline, status FROM violations"
        params = []
        if self.flt == "fixed":
            q += " WHERE status='fixed'"
        elif self.flt == "open":
            q += " WHERE status='open'"
        q += " ORDER BY date DESC LIMIT 200"
        rows = db().execute(q, params).fetchall()
        if not rows:
            ctk.CTkLabel(box, text=tt("no_rec"), text_color="gray").pack(pady=10)
            return
        for rid, d, loc, desc, photo, resp, dl, status in rows:
            row = ctk.CTkFrame(box, fg_color="gray15")
            row.pack(fill="x", pady=3)
            if status == "fixed":
                s_txt, s_col = tt("fixed"), "#16A34A"
            elif dl and dl < today_str():
                s_txt, s_col = tt("overdue"), "#F59E0B"
            else:
                s_txt, s_col = tt("open"), "#DC2626"
            ctk.CTkLabel(row, text=f"{d or '—'} • {loc or ''}", font=ctk.CTkFont(size=13, weight="bold"),
                         anchor="w").pack(anchor="w", padx=8, pady=(6, 0))
            ctk.CTkLabel(row, text=desc or "", text_color="gray", anchor="w", justify="left",
                         wraplength=880).pack(anchor="w", padx=8)
            ctk.CTkLabel(row, text=f"{s_txt} • срок: {dl or '—'} • {resp or ''}",
                         text_color=s_col, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=8, pady=(0, 6))
            right = ctk.CTkFrame(row, fg_color="transparent")
            right.pack(side="right", padx=6, pady=6)
            ctk.CTkButton(right, text="🗑️", width=36, fg_color="#7f1d1d", hover_color="#991b1b",
                          command=lambda r=rid: self.delete(r)).pack(side="right", padx=(3, 0))
            if status != "fixed":
                ctk.CTkButton(right, text="✅", width=36, fg_color="#16A34A", hover_color="#15803D",
                              command=lambda r=rid: self.mark_fixed(r)).pack(side="right", padx=(3, 0))
            rec = (rid, d, loc, desc, photo, resp, dl)
            ctk.CTkButton(right, text="✏️", width=36, fg_color="gray25",
                          command=lambda r=rec: self.dialog(r)).pack(side="right", padx=(3, 0))
            if photo and os.path.exists(photo):
                ctk.CTkButton(right, text="📷", width=36, fg_color="gray25",
                              command=lambda p=photo: os.startfile(p)).pack(side="right")

    def _on_flt(self, v):
        self.flt = {"all": "all", "open": "open", "fixed": "fixed"}.get(
            next((k for k in ("all", "open", "fixed") if tt(k) == v), "all"), "all")
        self.rebuild()

    def delete(self, rid):
        if messagebox.askyesno(tt("warning"), tt("del_rec")):
            c = db()
            c.execute("DELETE FROM violations WHERE id=?", (rid,))
            c.commit(); c.close()
            self.rebuild()

    def mark_fixed(self, rid):
        c = db()
        c.execute("UPDATE violations SET status='fixed' WHERE id=?", (rid,))
        c.commit(); c.close()
        self.rebuild()

    def dialog(self, rec=None):
        win = ctk.CTkToplevel(self)
        win.title(tt("title"))
        win.geometry("460x560")
        win.grab_set()
        ctk.CTkLabel(win, text=tt("date")).pack(anchor="w", padx=20, pady=(10, 0))
        e_date = ctk.CTkEntry(win)
        e_date.insert(0, rec[1] if rec else today_str())
        e_date.pack(fill="x", padx=20)
        ctk.CTkLabel(win, text=tt("location")).pack(anchor="w", padx=20, pady=(8, 0))
        locs = get_locations()
        e_loc = ctk.CTkComboBox(win, values=locs if locs else [""])
        e_loc.set(rec[2] if rec else "")
        e_loc.pack(fill="x", padx=20)
        ctk.CTkLabel(win, text=tt("description")).pack(anchor="w", padx=20, pady=(8, 0))
        e_desc = ctk.CTkEntry(win)
        e_desc.insert(0, rec[3] if rec else "")
        e_desc.pack(fill="x", padx=20)
        ctk.CTkLabel(win, text=tt("responsible")).pack(anchor="w", padx=20, pady=(8, 0))
        e_resp = ctk.CTkEntry(win)
        e_resp.insert(0, rec[5] if rec else "")
        e_resp.pack(fill="x", padx=20)
        ctk.CTkLabel(win, text=tt("deadline")).pack(anchor="w", padx=20, pady=(8, 0))
        e_dl = ctk.CTkEntry(win)
        e_dl.insert(0, rec[6] if rec else "")
        e_dl.pack(fill="x", padx=20)
        photo_holder = {"path": rec[4] if rec else ""}
        lbl_photo = ctk.CTkLabel(win, text=f"📷 {os.path.basename(photo_holder['path'])}" if photo_holder["path"] else tt("photo"),
                                 text_color="gray")
        lbl_photo.pack(anchor="w", padx=20, pady=(8, 0))

        def pick():
            p = filedialog.askopenfilename(filetypes=[("Фото", "*.jpg *.jpeg *.png *.heic")])
            if p:
                PHOTO_DIR.mkdir(parents=True, exist_ok=True)
                dst = PHOTO_DIR / f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.path.basename(p)}"
                shutil.copy2(p, dst)
                photo_holder["path"] = str(dst)
                lbl_photo.configure(text=f"📷 {dst.name}")
        ctk.CTkButton(win, text=tt("attach"), fg_color="gray25", command=pick).pack(pady=(4, 0))

        def save():
            if not e_desc.get().strip():
                messagebox.showwarning(tt("warning"), tt("need_desc"))
                return
            c = db()
            if rec:
                c.execute("UPDATE violations SET date=?, location=?, description=?, responsible=?, deadline=?, photo_path=? WHERE id=?",
                          (e_date.get(), e_loc.get(), e_desc.get(), e_resp.get(), e_dl.get(), photo_holder["path"], rec[0]))
            else:
                c.execute("INSERT INTO violations (date, location, description, responsible, deadline, photo_path) VALUES (?,?,?,?,?,?)",
                          (e_date.get(), e_loc.get(), e_desc.get(), e_resp.get(), e_dl.get(), photo_holder["path"]))
            c.commit(); c.close()
            win.destroy(); self.rebuild()
        ctk.CTkButton(win, text=tt("save"), command=save).pack(pady=12)
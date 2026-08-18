# -*- coding: utf-8 -*-
"""Страница «Дезинсекция и дератизация (ДД)» — с переводом на 4 языка."""
import os
import sqlite3
import shutil
from datetime import date
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox

from modules.translations import get_language

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "database" / "sanepi.db"
DD_ACTS_DIR = PROJECT_ROOT / "database" / "dd_acts"

ICONS = {"dis_crawling": "🪳", "dis_flying": "🦟", "deratization": "🐀", "disinfection": "🧴"}

YEARS = [2025, 2026, 2027, 2028, 2029, 2030]
MONTH_ORDER = [4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2, 3]  # с апреля вперёд

T = {
    "title": {"ru": "🛡️ Дезинсекция и дератизация (ДД)", "kk": "🛡️ Дезинсекция және дератизация (ДД)", "en": "🛡️ Disinsection & Deratization (DD)", "tr": "🛡️ Dezenfeksiyon ve Deratizasyon (DD)"},
    "refresh": {"ru": "🔄 Обновить", "kk": "🔄 Жаңарту", "en": "🔄 Refresh", "tr": "🔄 Yenile"},
    "on_demand": {"ru": "➕ Разовая по заявке", "kk": "➕ Бір реттік өтінім", "en": "➕ One-off request", "tr": "➕ Tek seferlik talep"},
    "edit": {"ru": "✏️ Изменить", "kk": "✏️ Өзгерту", "en": "✏️ Edit", "tr": "✏️ Düzenle"},
    "add_contract": {"ru": "➕ Добавить договор", "kk": "➕ Шарт қосу", "en": "➕ Add contract", "tr": "➕ Sözleşme ekle"},
    "no_contract": {"ru": "Договор не добавлен", "kk": "Шарт қосылмаған", "en": "No contract added", "tr": "Sözleşme eklenmedi"},
    "date": {"ru": "дата:", "kk": "күні:", "en": "date:", "tr": "tarih:"},
    "valid": {"ru": "срок до:", "kk": "мерзімі:", "en": "valid until:", "tr": "geçerlilik:"},
    "mark": {"ru": "➕ Отметить обработку", "kk": "➕ Өңдеуді белгілеу", "en": "➕ Mark treatment", "tr": "➕ İşlemeyi işaretle"},
    "done": {"ru": "— выполнено", "kk": "— орындалды", "en": "— done", "tr": "— tamam"},
    "short": {"ru": "— НЕДОБОР", "kk": "— ОРЫНДАЛМАҒАН", "en": "— SHORTFALL", "tr": "— EKSİK"},
    "left": {"ru": "— осталось", "kk": "— қалды", "en": "— left", "tr": "— kaldı"},
    "month": {"ru": "— в течение месяца", "kk": "— ай ішінде", "en": "— within the month", "tr": "— ay içinde"},
    "future": {"ru": "— запланировано", "kk": "— жоспарланды", "en": "— planned", "tr": "— planlandı"},
    "by_month": {"ru": "📅 Период:", "kk": "📅 Кезең:", "en": "📅 Period:", "tr": "📅 Dönem:"},
    "history": {"ru": "📜 История обработок", "kk": "📜 Өңдеулер тарихы", "en": "📜 Treatment history", "tr": "📜 İşlem geçmişi"},
    "all_months": {"ru": "Все месяцы", "kk": "Барлық айлар", "en": "All months", "tr": "Tüm aylar"},
    "no_treat": {"ru": "Пока нет обработок — нажмите «➕ Отметить обработку».", "kk": "Әзірге өңдеулер жоқ — «➕ Өңдеуді белгілеу» басыңыз.", "en": "No treatments yet — click “➕ Mark treatment”.", "tr": "Henüz işlem yok — “➕ İşlemeyi işaretle” düğmesine tıklayın."},
    "service": {"ru": "Услуга:", "kk": "Қызмет:", "en": "Service:", "tr": "Hizmet:"},
    "date_lbl": {"ru": "Дата (ГГГГ-ММ-ДД):", "kk": "Күні (ЖЖЖЖ-АА-КК):", "en": "Date (YYYY-MM-DD):", "tr": "Tarih (YYYY-AA-GG):"},
    "reason": {"ru": "Причина заявки:", "kk": "Өтінім себебі:", "en": "Request reason:", "tr": "Talep nedeni:"},
    "comment": {"ru": "Комментарий:", "kk": "Ескертпе:", "en": "Comment:", "tr": "Yorum:"},
    "pdf_none": {"ru": "📄 PDF акт: не выбран", "kk": "📄 PDF акт: таңдалмаған", "en": "📄 PDF act: not selected", "tr": "📄 PDF tutanak: seçilmedi"},
    "pdf_attach": {"ru": "📎 Прикрепить PDF-акт", "kk": "📎 PDF акт тіркеу", "en": "📎 Attach PDF act", "tr": "📎 PDF tutanak ekle"},
    "save": {"ru": "💾 Сохранить", "kk": "💾 Сақтау", "en": "💾 Save", "tr": "💾 Kaydet"},
    "onetime": {"ru": "разовая", "kk": "бір реттік", "en": "one-off", "tr": "tek seferlik"},
    "planned": {"ru": "плановая", "kk": "жоспарлы", "en": "planned", "tr": "planlı"},
    "dlg_contract": {"ru": "Договор ДД", "kk": "ДД шарты", "en": "DD contract", "tr": "DD sözleşmesi"},
    "contractor": {"ru": "Подрядчик", "kk": "Мердігер", "en": "Contractor", "tr": "Yüklenici"},
    "contract_no": {"ru": "Номер договора", "kk": "Шарт нөмірі", "en": "Contract number", "tr": "Sözleşme no"},
    "contract_date": {"ru": "Дата договора (ГГГГ-ММ-ДД)", "kk": "Шарт күні (ЖЖЖЖ-АА-КК)", "en": "Contract date (YYYY-MM-DD)", "tr": "Sözleşme tarihi (YYYY-AA-GG)"},
    "contract_valid": {"ru": "Срок действия (ГГГГ-ММ-ДД)", "kk": "Қолданылу мерзімі (ЖЖЖЖ-АА-КК)", "en": "Valid until (YYYY-MM-DD)", "tr": "Geçerlilik (YYYY-AA-GG)"},
    "dlg_treat": {"ru": "Обработка", "kk": "Өңдеу", "en": "Treatment", "tr": "İşleme"},
    "warning": {"ru": "⚠️ Внимание", "kk": "⚠️ Назар аударыңыз", "en": "⚠️ Warning", "tr": "⚠️ Uyarı"},
    "del_treat": {"ru": "Удалить эту запись об обработке?", "kk": "Осы өңдеу жазбасын жою керек пе?", "en": "Delete this treatment record?", "tr": "Bu işlem kaydı silinsin mi?"},
}

SERVICE_TR = {
    "Дезинсекция — ползающие насекомые": {"kk": "Дезинсекция — жорғалайтын жәндіктер", "en": "Disinsection — crawling insects", "tr": "Dezenfeksiyon — sürünen böcekler"},
    "Дезинсекция — летающие (внутри зданий)": {"kk": "Дезинсекция — ұшатын жәндіктер (ғимарат ішінде)", "en": "Disinsection — flying (indoors)", "tr": "Dezenfeksiyon — uçan (iç mekân)"},
    "Дезинсекция — летающие (снаружи зданий)": {"kk": "Дезинсекция — ұшатын жәндіктер (ғимарат сыртында)", "en": "Disinsection — flying (outdoors)", "tr": "Dezenfeksiyon — uçan (dış mekân)"},
    "Дератизация": {"kk": "Дератизация", "en": "Deratization", "tr": "Deratizasyon"},
    "Дезинфекция (разовая по заявке)": {"kk": "Дезинфекция (бір реттік өтінім бойынша)", "en": "Disinfection (one-off on request)", "tr": "Dezenfeksiyon (tek seferlik talep)"},
}

DATA_TR = {
    "внутри": {"kk": "ішінде", "en": "indoors", "tr": "iç mekân"},
    "снаружи": {"kk": "сыртында", "en": "outdoors", "tr": "dış mekân"},
    "Подрядчик по договору ДД (Rixos Water World Aktau)": {"kk": "ДД шарты бойынша мердігер (Rixos Water World Aktau)", "en": "DD contractor (Rixos Water World Aktau)", "tr": "DD yüklenicisi (Rixos Water World Aktau)"},
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

DEFAULT_SERVICES = [
    ("Дезинсекция — ползающие насекомые", "dis_crawling", "внутри", 2, ""),
    ("Дезинсекция — летающие (внутри зданий)", "dis_flying", "внутри", 3, ""),
    ("Дезинсекция — летающие (снаружи зданий)", "dis_flying", "снаружи", 2, "22:00–04:00"),
    ("Дератизация", "deratization", "", 2, ""),
    ("Дезинфекция (разовая по заявке)", "disinfection", "", 0, ""),
]


def tt(key):
    d = T.get(key)
    if not d:
        return key
    return d.get(get_language(), d.get("ru", key))


def month_name(m):
    d = MONTHS.get(m, {})
    return d.get(get_language(), d.get("ru", str(m)))


def tr_title(title):
    d = SERVICE_TR.get(title)
    if not d:
        return title
    return d.get(get_language(), title)


def tr_data(s):
    d = DATA_TR.get(s)
    return d.get(get_language(), s) if d else s


def db():
    return sqlite3.connect(DB_PATH)


def today_str():
    return date.today().isoformat()


def ensure_default_services():
    """Если какая-то услуга по договору отсутствует — возвращает её."""
    c = db()
    cid = c.execute("SELECT id FROM dd_contracts ORDER BY id LIMIT 1").fetchone()
    cid = cid[0] if cid else None
    for title, stype, loc, pm, tw in DEFAULT_SERVICES:
        if not c.execute("SELECT 1 FROM dd_services WHERE title=?", (title,)).fetchone():
            c.execute(
                "INSERT INTO dd_services (contract_id,title,service_type,location,per_month,time_window,notes) VALUES (?,?,?,?,?,?,?)",
                (cid, title, stype, loc, pm, tw, ""))
    c.commit()
    c.close()


class DDPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.configure(fg_color="transparent")
        t = date.today()
        self.card_year = t.year if t.year in YEARS else 2026
        self.card_mnum = t.month
        self.hist_year = t.year if t.year in YEARS else 2026
        self.hist_mnum = t.month  # 0 = все месяцы года
        ensure_default_services()
        self.rebuild()

    def rebuild(self):
        for w in self.winfo_children():
            w.destroy()
        head = ctk.CTkFrame(self)
        head.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(head, text=tt("title"), font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=10, pady=8)
        ctk.CTkButton(head, text=tt("on_demand"), width=170, fg_color="#8B5CF6",
                      command=lambda: self.treatment_dialog(on_demand=True)).pack(side="right", padx=10)
        ctk.CTkButton(head, text=tt("refresh"), width=100, fg_color="gray25",
                      command=self.rebuild).pack(side="right", padx=5)
        self.contract_card()
        self.services_cards()
        self.history_block()

    def _period_menus(self, parent, year, mnum, on_change, with_all=False):
        ctk.CTkLabel(parent, text=tt("by_month"), font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        yom = ctk.CTkOptionMenu(parent, values=[str(y) for y in YEARS], width=100,
                                command=lambda v: on_change("y", v))
        yom.set(str(year))
        yom.pack(side="right", padx=(4, 0))
        mvals = ([tt("all_months")] if with_all else []) + [month_name(m) for m in MONTH_ORDER]
        mom = ctk.CTkOptionMenu(parent, values=mvals, width=150,
                                command=lambda v: on_change("m", v))
        cur = tt("all_months") if mnum == 0 else month_name(mnum)
        mom.set(cur)
        mom.pack(side="right", padx=(4, 0))

    def _card_period(self, kind, value):
        if kind == "y":
            self.card_year = int(value)
        else:
            self.card_mnum = next((m for m in MONTH_ORDER if month_name(m) == value), self.card_mnum)
        self.rebuild()

    def _hist_period(self, kind, value):
        if kind == "y":
            self.hist_year = int(value)
        else:
            if value == tt("all_months"):
                self.hist_mnum = 0
            else:
                self.hist_mnum = next((m for m in MONTH_ORDER if month_name(m) == value), 0)
        self.rebuild()

    def contract_card(self):
        row = db().execute("SELECT * FROM dd_contracts ORDER BY id LIMIT 1").fetchone()
        card = ctk.CTkFrame(self)
        card.pack(fill="x", padx=10, pady=5)
        if not row:
            ctk.CTkButton(card, text=tt("add_contract"), command=self.contract_dialog).pack(pady=10)
            return
        _, contractor, number, cdate, valid_until, notes, _ = row
        ctk.CTkLabel(card, text=f"📄 {tr_data(contractor)}", font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=10, pady=(8, 0))
        ctk.CTkLabel(card, text=f"№ {number or '—'} | {tt('date')} {cdate or '—'} | {tt('valid')} {valid_until or '—'}",
                     text_color="gray").pack(anchor="w", padx=10)
        ctk.CTkButton(card, text=tt("edit"), width=110, fg_color="gray25",
                      command=self.contract_dialog).pack(anchor="e", padx=10, pady=(0, 8))

    def contract_dialog(self):
        old = db().execute("SELECT * FROM dd_contracts ORDER BY id LIMIT 1").fetchone()
        win = ctk.CTkToplevel(self)
        win.title(tt("dlg_contract"))
        win.geometry("420x320")
        win.grab_set()
        labels = [("contractor", tt("contractor")), ("contract_number", tt("contract_no")),
                  ("contract_date", tt("contract_date")), ("contract_valid", tt("contract_valid"))]
        vals = {"contractor": old[1] if old else "", "contract_number": old[2] if old else "",
                "contract_date": old[3] if old else "", "contract_valid": old[4] if old else ""}
        fields = {}
        for key, lab in labels:
            ctk.CTkLabel(win, text=lab).pack(anchor="w", padx=20, pady=(8, 0))
            e = ctk.CTkEntry(win)
            e.insert(0, vals[key] or "")
            e.pack(fill="x", padx=20)
            fields[key] = e
        def save():
            c = db()
            if old:
                c.execute("UPDATE dd_contracts SET contractor=?, contract_number=?, contract_date=?, valid_until=? WHERE id=?",
                          (fields["contractor"].get(), fields["contract_number"].get(),
                           fields["contract_date"].get(), fields["contract_valid"].get(), old[0]))
            else:
                c.execute("INSERT INTO dd_contracts (contractor, contract_number, contract_date, valid_until) VALUES (?,?,?,?)",
                          (fields["contractor"].get(), fields["contract_number"].get(),
                           fields["contract_date"].get(), fields["contract_valid"].get()))
            c.commit(); c.close()
            win.destroy(); self.rebuild()
        ctk.CTkButton(win, text=tt("save"), command=save).pack(pady=12)

    # ---------- Карточки услуг (без удаления!) ----------
    def services_cards(self):
        cur = db()
        services = cur.execute("SELECT id,title,service_type,location,per_month,time_window FROM dd_services").fetchall()
        cur_month = today_str()[:7]
        cur_day = date.today().day
        sel_month = f"{self.card_year:04d}-{self.card_mnum:02d}"
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.pack(fill="x", padx=10, pady=5)

        head = ctk.CTkFrame(wrap, fg_color="transparent")
        head.pack(fill="x", pady=(0, 4))
        self._period_menus(head, self.card_year, self.card_mnum, self._card_period)

        for sid, title, stype, loc, per_month, tw in services:
            if not per_month:
                continue
            done = cur.execute(
                "SELECT COUNT(*) FROM dd_treatments WHERE service_id=? AND status='done' AND substr(actual_date,1,7)=?",
                (sid, sel_month)).fetchone()[0]
            card = ctk.CTkFrame(wrap)
            card.pack(fill="x", pady=4)
            extra = (f" • {tr_data(loc)}" if loc else "") + (f" • {tw}" if tw else "")
            ctk.CTkLabel(card, text=f"{ICONS.get(stype, '🛡️')} {tr_title(title)}{extra}",
                         font=ctk.CTkFont(size=14, weight="bold")).pack(anchor="w", padx=10, pady=(8, 0))
            if sel_month > cur_month:
                status, color = f"🟢 {done}/{per_month} {tt('future')}", "#16A34A"
            elif sel_month < cur_month:
                if done >= per_month:
                    status, color = f"✅ {done}/{per_month} {tt('done')}", "#16A34A"
                else:
                    status, color = f"🔴 {done}/{per_month} {tt('short')}", "#DC2626"
            else:
                if done >= per_month:
                    status, color = f"✅ {done}/{per_month} {tt('done')}", "#16A34A"
                elif cur_day >= 25:
                    status, color = f"🔴 {done}/{per_month} {tt('short')}", "#DC2626"
                elif cur_day >= 15:
                    status, color = f"⚠️ {done}/{per_month} {tt('left')} {per_month - done}", "#F59E0B"
                else:
                    status, color = f"🟢 {done}/{per_month} {tt('month')}", "#16A34A"
            ctk.CTkLabel(card, text=status, text_color=color).pack(anchor="w", padx=10)
            ctk.CTkButton(card, text=tt("mark"), width=190,
                          command=lambda s=sid: self.treatment_dialog(service_id=s)).pack(anchor="e", padx=10, pady=(0, 8))
        cur.close()

    # ---------- Диалог обработки (новая / редактирование записи) ----------
    def treatment_dialog(self, on_demand=False, service_id=None, record=None):
        win = ctk.CTkToplevel(self)
        win.title(tt("on_demand") if on_demand else tt("dlg_treat"))
        win.geometry("460x450")
        win.grab_set()
        services = db().execute("SELECT id,title FROM dd_services").fetchall()
        ctk.CTkLabel(win, text=tt("service")).pack(anchor="w", padx=20, pady=(10, 0))
        om = ctk.CTkOptionMenu(win, values=[tr_title(t) for _, t in services])
        if record:
            om.set(tr_title(dict(services).get(record[2], "")))
        elif service_id:
            om.set(tr_title(dict(services)[service_id]))
        om.pack(fill="x", padx=20)
        ctk.CTkLabel(win, text=tt("date_lbl")).pack(anchor="w", padx=20, pady=(8, 0))
        e_date = ctk.CTkEntry(win)
        e_date.insert(0, record[4] if record else today_str())
        e_date.pack(fill="x", padx=20)
        e_reason = None
        if on_demand or (record and record[3] == "on_demand"):
            ctk.CTkLabel(win, text=tt("reason")).pack(anchor="w", padx=20, pady=(8, 0))
            e_reason = ctk.CTkEntry(win)
            e_reason.insert(0, record[7] if record else "")
            e_reason.pack(fill="x", padx=20)
        ctk.CTkLabel(win, text=tt("comment")).pack(anchor="w", padx=20, pady=(8, 0))
        e_notes = ctk.CTkEntry(win)
        e_notes.insert(0, record[8] if record else "")
        e_notes.pack(fill="x", padx=20)
        pdf_holder = {"path": record[6] if record else ""}
        lbl_pdf = ctk.CTkLabel(win, text=f"📄 {os.path.basename(pdf_holder['path'])}" if pdf_holder["path"] else tt("pdf_none"),
                               text_color="gray")
        lbl_pdf.pack(anchor="w", padx=20, pady=(8, 0))
        def pick():
            p = filedialog.askopenfilename(filetypes=[("PDF", "*.pdf")])
            if p:
                pdf_holder["path"] = p
                lbl_pdf.configure(text=f"📄 {os.path.basename(p)}")
        ctk.CTkButton(win, text=tt("pdf_attach"), fg_color="gray25", command=pick).pack(pady=(4, 0))

        def save():
            titles = {tr_title(t): i for i, t in services}
            sid = titles.get(om.get(), services[0][0])
            act = pdf_holder["path"] or ""
            if act and not os.path.exists(act):
                act = ""
            if act and pdf_holder["path"] != (record[6] if record else ""):
                DD_ACTS_DIR.mkdir(parents=True, exist_ok=True)
                dst = DD_ACTS_DIR / f"{e_date.get()}_{os.path.basename(pdf_holder['path'])}"
                shutil.copy2(pdf_holder["path"], dst)
                act = str(dst)
            c = db()
            if record:
                c.execute("""UPDATE dd_treatments SET service_id=?, actual_date=?, request_reason=?, notes=?, act_pdf_path=? WHERE id=?""",
                          (sid, e_date.get(), e_reason.get() if e_reason else (record[7] or ""),
                           e_notes.get(), act, record[0]))
            else:
                c.execute("""INSERT INTO dd_treatments
                    (contract_id, service_id, treatment_type, actual_date, status, act_pdf_path, request_reason, notes, performed_by)
                    VALUES ((SELECT id FROM dd_contracts LIMIT 1), ?, ?, ?, 'done', ?, ?, ?, ?)""",
                          (sid, "on_demand" if on_demand else "planned", e_date.get(), act,
                           e_reason.get() if e_reason else "", e_notes.get(), "Дәурен Оспан"))
            c.commit(); c.close()
            win.destroy(); self.rebuild()
        ctk.CTkButton(win, text=tt("save"), command=save).pack(pady=12)

    def delete_treatment(self, rec_id):
        if messagebox.askyesno(tt("warning"), tt("del_treat")):
            c = db()
            c.execute("DELETE FROM dd_treatments WHERE id=?", (rec_id,))
            c.commit(); c.close()
            self.rebuild()

    # ---------- История с фильтром и редактированием записей ----------
    def history_block(self):
        card = ctk.CTkFrame(self)
        card.pack(fill="both", expand=True, padx=10, pady=5)
        head = ctk.CTkFrame(card, fg_color="transparent")
        head.pack(fill="x", padx=10, pady=(8, 0))
        ctk.CTkLabel(head, text=tt("history"), font=ctk.CTkFont(size=15, weight="bold")).pack(side="left")
        self._period_menus(head, self.hist_year, self.hist_mnum, self._hist_period, with_all=True)
        self._hist_box = ctk.CTkScrollableFrame(card, height=260)
        self._hist_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._render_history()

    def _render_history(self):
        box = self._hist_box
        for w in box.winfo_children():
            w.destroy()
        q = """SELECT t.id, t.actual_date, s.title, t.treatment_type, t.status, t.act_pdf_path, t.request_reason, t.notes, s.id
               FROM dd_treatments t LEFT JOIN dd_services s ON s.id = t.service_id
               WHERE substr(t.actual_date,1,4) = ?"""
        params = [str(self.hist_year)]
        if self.hist_mnum:
            q += " AND substr(t.actual_date,6,2) = ?"
            params.append(f"{self.hist_mnum:02d}")
        q += " ORDER BY t.actual_date DESC LIMIT 200"
        rows = db().execute(q, params).fetchall()
        if not rows:
            ctk.CTkLabel(box, text=tt("no_treat"), text_color="gray").pack(pady=10)
        for rid, d, title, ttype, status, act, reason, notes, sid in rows:
            row = ctk.CTkFrame(box, fg_color="gray15")
            row.pack(fill="x", pady=2)
            txt = f"{d} • {tr_title(title or '')} • {tt('onetime') if ttype == 'on_demand' else tt('planned')}"
            if reason:
                txt += f" ({reason})"
            ctk.CTkLabel(row, text=txt, anchor="w").pack(side="left", padx=8, pady=6)
            right = ctk.CTkFrame(row, fg_color="transparent")
            right.pack(side="right", padx=6)
            ctk.CTkButton(right, text="🗑️", width=36, fg_color="#7f1d1d", hover_color="#991b1b",
                          command=lambda r=rid: self.delete_treatment(r)).pack(side="right", padx=(3, 0))
            rec = (rid, d, sid, ttype, d, "", act, reason, notes)
            ctk.CTkButton(right, text="✏️", width=36, fg_color="gray25",
                          command=lambda r=rec: self.treatment_dialog(record=r)).pack(side="right", padx=(3, 0))
            if act:
                ctk.CTkButton(right, text="📄", width=36, fg_color="gray25",
                              command=lambda p=act: os.startfile(p)).pack(side="right")
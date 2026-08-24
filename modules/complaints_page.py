# -*- coding: utf-8 -*-
"""Журнал жалоб и обращений (гости, онлайн, СЭС, внутренние)."""
import sqlite3
from datetime import date, timedelta
from pathlib import Path

import customtkinter as ctk
from tkinter import filedialog, messagebox

from modules.translations import get_language

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "database" / "sanepi.db"

SOURCES = ["Гость (устно)", "Гость (книга жалоб)", "Комментарии гостей (карточки отеля)",
           "Онлайн-отзыв (2GIS/Google)", "Booking/Expedia",
           "СЭС / ДСЭК", "Прокуратура / Акимат", "Внутренний аудит", "Соцсети (Instagram)"]
CATEGORIES = ["Питание /Restaurant", "Чистота / Номера", "Обслуживание", "Бассейн / Аквапарк",
              "СПА / Массаж", "Шум / Кондиционер", "Безопасность", "Детский клуб", "Прачечная",
              "Трансфер / Парковка", "Wi-Fi / Техника", "Другое"]
STATUSES = ["🆕 Новая", "⚙️ В работе", "✅ Решена", "❌ Отклонена", "🔁 Повторная"]
PRIORITIES = ["🔴 Высокая", "🟡 Средняя", "🟢 Низкая"]

COMPLAINT_TYPES = [
    "Пищевое отравление / подозрение на отравление",
    "Некачественная еда / холодное блюдо",
    "Медленное обслуживание в ресторане",
    "Грязный номер / плохая уборка",
    "Неприятный запах в номере / помещении",
    "Насекомые / грызуны в помещении",
    "Бассейн: температура / чистота воды",
    "Шум от соседей / мероприятий",
    "Не работает кондиционер",
    "Проблема с Wi-Fi / техникой",
    "Грубость персонала",
    "Долгое заселение / очередь на ресепшн",
    "СПА: замечания по записи / обслуживанию",
    "Детский клуб: замечания",
    "Трансфер / парковка: замечания",
    "Безопасность: замечание",
]

T = {
    "title": {"ru": "📢 Журнал жалоб и обращений", "kk": "📢 Шағымдар журналы", "en": "📢 Complaints log"},
    "add": {"ru": "➕ Новая жалоба", "kk": "➕ Жаңа шағым", "en": "➕ New"},
    "export": {"ru": "📥 Excel", "kk": "📥 Excel", "en": "📥 Excel"},
    "no_rec": {"ru": "Жалоб за период нет.", "kk": "Кезеңде шағымдар жоқ.", "en": "No complaints."},
    "warning": {"ru": "⚠️ Внимание", "kk": "⚠️ Назар аударыңыз", "en": "⚠️ Warning"},
    "del": {"ru": "Удалить жалобу?", "kk": "Шағымды жою?", "en": "Delete complaint?"},
    "need_text": {"ru": "Опишите суть жалобы!", "kk": "Шағымның мәнін жазыңыз!", "en": "Describe the complaint!"},
    "from": {"ru": "с", "kk": "бастап", "en": "from"},
    "to": {"ru": "по", "kk": "дейін", "en": "to"},
    "save": {"ru": "💾 Сохранить", "kk": "💾 Сақтау", "en": "💾 Save"},
    "date": {"ru": "Дата поступления:", "kk": "Келіп түскен күні:", "en": "Received:"},
    "source": {"ru": "Источник:", "kk": "Көзі:", "en": "Source:"},
    "source_note": {"ru": "💬 Комментарий к источнику (ссылка, № комнаты, кто сообщил):",
                    "kk": "💬 Дереккөзге түсініктеме (сілтеме, № бөлме, кім хабарлады):",
                    "en": "💬 Source comment (link, room №, who reported):"},
    "category": {"ru": "Категория:", "kk": "Санат:", "en": "Category:"},
    "priority": {"ru": "Приоритет:", "kk": "Басымдық:", "en": "Priority:"},
    "status": {"ru": "Статус:", "kk": "Мәртебе:", "en": "Status:"},
    "guest": {"ru": "Гость / ФИО / № комнаты:", "kk": "Қонақ / АТЖ / № бөлме:", "en": "Guest / Room:"},
    "department": {"ru": "Ответственный отдел:", "kk": "Жауапты бөлім:", "en": "Department:"},
    "assignee": {"ru": "Исполнитель:", "kk": "Орындаушы:", "en": "Assignee:"},
    "deadline": {"ru": "Срок решения:", "kk": "Шешу мерзімі:", "en": "Deadline:"},
    "description": {"ru": "Суть жалобы (выберите или впишите):", "kk": "Шағымның мәні (таңдаңыз немесе жазыңыз):", "en": "Complaint (choose or type):"},
    "measures": {"ru": "Принятые меры:", "kk": "Қабылданған шаралар:", "en": "Measures:"},
    "result": {"ru": "Итог / ответ гостю:", "kk": "Нәтиже / қонаққа жауап:", "en": "Result:"},
}


def tt(key):
    d = T.get(key)
    return d.get(get_language(), d.get("ru", key)) if d else key


def db():
    return sqlite3.connect(DB_PATH)


def ensure_table():
    c = db()
    c.execute("""CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        source TEXT,
        source_note TEXT DEFAULT '',
        category TEXT,
        priority TEXT,
        status TEXT,
        guest TEXT,
        department TEXT,
        assignee TEXT,
        deadline TEXT,
        description TEXT,
        measures TEXT,
        result TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    )""")
    try:  # миграция старой базы
        c.execute("ALTER TABLE complaints ADD COLUMN source_note TEXT DEFAULT ''")
    except sqlite3.OperationalError:
        pass
    c.commit()
    c.close()


def month_bounds():
    t = date.today()
    f = t.replace(day=1).isoformat()
    if t.month == 12:
        to = t.replace(year=t.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        to = t.replace(month=t.month + 1, day=1) - timedelta(days=1)
    return f, to.isoformat()


def build_complaints_page(master):
    ComplaintsPage(master).pack(fill="both", expand=True)


class ComplaintsPage(ctk.CTkFrame):
    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.configure(fg_color="transparent")
        ensure_table()
        f, t = month_bounds()
        self.from_var = ctk.StringVar(value=f)
        self.to_var = ctk.StringVar(value=t)
        self.filter_cat = ctk.StringVar(value="Все")
        self.filter_st = ctk.StringVar(value="Все")
        self.rebuild()

    def rebuild(self):
        for w in self.winfo_children():
            w.destroy()

        head = ctk.CTkFrame(self)
        head.pack(fill="x", padx=10, pady=(10, 5))
        ctk.CTkLabel(head, text=tt("title"), font=ctk.CTkFont(size=20, weight="bold")).pack(side="left", padx=10, pady=8)
        ctk.CTkButton(head, text=tt("export"), width=110, fg_color="#1d4ed8", hover_color="#1e40af",
                      command=self.export_excel).pack(side="right", padx=10)
        ctk.CTkButton(head, text=tt("add"), width=180, fg_color="#0891b2", hover_color="#0e7490",
                      command=self.dialog).pack(side="right", padx=10)

        stats = self._stats()
        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.pack(fill="x", padx=10, pady=5)
        for color, label, val in [
            ("#1e40af", "Всего", stats["total"]),
            ("#dc2626", "🆕 Новых", stats["new"]),
            ("#ca8a04", "⚙️ В работе", stats["work"]),
            ("#16a34a", "✅ Решено", stats["done"]),
            ("#7c3aed", "🔴 Высокий приоритет", stats["high"]),
        ]:
            card = ctk.CTkFrame(sf, fg_color=color, corner_radius=10)
            card.pack(side="left", fill="x", expand=True, padx=3)
            ctk.CTkLabel(card, text=str(val), font=ctk.CTkFont(size=22, weight="bold")).pack(padx=10, pady=(6, 0))
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=11)).pack(padx=10, pady=(0, 6))

        pf = ctk.CTkFrame(self)
        pf.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(pf, text=tt("from")).pack(side="left", padx=(10, 4))
        ctk.CTkEntry(pf, textvariable=self.from_var, width=110).pack(side="left")
        ctk.CTkLabel(pf, text=tt("to")).pack(side="left", padx=(10, 4))
        ctk.CTkEntry(pf, textvariable=self.to_var, width=110).pack(side="left")
        ctk.CTkOptionMenu(pf, values=["Все"] + CATEGORIES, variable=self.filter_cat, width=180).pack(side="left", padx=10)
        ctk.CTkOptionMenu(pf, values=["Все"] + STATUSES, variable=self.filter_st, width=140).pack(side="left")
        ctk.CTkButton(pf, text="🔎", width=40, fg_color="gray25", command=self.rebuild).pack(side="left", padx=10)

        card = ctk.CTkFrame(self)
        card.pack(fill="both", expand=True, padx=10, pady=5)
        box = ctk.CTkScrollableFrame(card, height=360)
        box.pack(fill="both", expand=True, padx=10, pady=10)

        rows = self._fetch()
        if not rows:
            ctk.CTkLabel(box, text=tt("no_rec"), text_color="gray").pack(pady=10)
            return

        for r in rows:
            rid, d, src, srcnote, cat, prio, st, guest, dep, asn, dl, desc, meas, res = r
            row = ctk.CTkFrame(box, fg_color="gray15")
            row.pack(fill="x", pady=3)

            prio_col = {"🔴 Высокая": "#dc2626", "🟡 Средняя": "#ca8a04"}.get(prio, "#16a34a")
            st_col = {"🆕 Новая": "#dc2626", "⚙️ В работе": "#ca8a04", "✅ Решена": "#16a34a"}.get(st, "#6b7280")

            top = ctk.CTkFrame(row, fg_color="transparent")
            top.pack(fill="x", padx=8, pady=(6, 0))
            ctk.CTkLabel(top, text=f"{d} • {cat}", font=ctk.CTkFont(size=13, weight="bold"),
                         anchor="w").pack(side="left")
            ctk.CTkLabel(top, text=prio, text_color=prio_col,
                         font=ctk.CTkFont(size=12, weight="bold")).pack(side="right", padx=(4, 0))
            ctk.CTkLabel(top, text=st, text_color=st_col,
                         font=ctk.CTkFont(size=12, weight="bold")).pack(side="right")

            src_txt = f"📥 {src}" + (f" • 💬 {srcnote}" if srcnote else "") + (f" • 👤 {guest}" if guest else "")
            ctk.CTkLabel(row, text=src_txt, text_color="gray", anchor="w",
                         justify="left", wraplength=880).pack(anchor="w", padx=8)
            ctk.CTkLabel(row, text=f"🏢 {dep}" + (f" • 🔧 {asn}" if asn else "") + (f" • ⏰ до {dl}" if dl else ""),
                         text_color="#7fb6c9", anchor="w").pack(anchor="w", padx=8)
            ctk.CTkLabel(row, text=desc, anchor="w", justify="left", wraplength=880).pack(anchor="w", padx=8)
            if meas:
                ctk.CTkLabel(row, text=f"🛠 {meas}", text_color="#86efac", anchor="w",
                             justify="left", wraplength=880).pack(anchor="w", padx=8)
            if res:
                ctk.CTkLabel(row, text=f"✅ {res}", text_color="#93c5fd", anchor="w",
                             justify="left", wraplength=880).pack(anchor="w", padx=8, pady=(0, 6))

            ctk.CTkButton(row, text="🗑️", width=36, fg_color="#7f1d1d", hover_color="#991b1b",
                          command=lambda i=rid: self.delete(i)).pack(side="right", padx=6, pady=6)
            ctk.CTkButton(row, text="✏️", width=36, fg_color="gray25",
                          command=lambda rec=r: self.dialog(rec)).pack(side="right", pady=6)

    def _where(self):
        conds = ["date BETWEEN ? AND ?"]
        args = [self.from_var.get(), self.to_var.get()]
        if self.filter_cat.get() != "Все":
            conds.append("category = ?")
            args.append(self.filter_cat.get())
        if self.filter_st.get() != "Все":
            conds.append("status = ?")
            args.append(self.filter_st.get())
        return " AND ".join(conds), args

    def _fetch(self):
        w, a = self._where()
        return db().execute(
            f"SELECT id, date, source, source_note, category, priority, status, guest, department, "
            f"assignee, deadline, description, measures, result "
            f"FROM complaints WHERE {w} ORDER BY date DESC, id DESC", a).fetchall()

    def _stats(self):
        rows = self._fetch()
        return {
            "total": len(rows),
            "new": sum(1 for r in rows if r[6] == "🆕 Новая"),
            "work": sum(1 for r in rows if r[6] == "⚙️ В работе"),
            "done": sum(1 for r in rows if r[6] == "✅ Решена"),
            "high": sum(1 for r in rows if r[5] == "🔴 Высокая"),
        }

    def delete(self, rid):
        if messagebox.askyesno(tt("warning"), tt("del")):
            c = db(); c.execute("DELETE FROM complaints WHERE id=?", (rid,)); c.commit(); c.close()
            self.rebuild()

    def dialog(self, rec=None):
        win = ctk.CTkToplevel(self)
        win.title(tt("title"))
        win.geometry("560x780")
        win.grab_set()
        g = rec or ("", date.today().isoformat(), SOURCES[0], "", CATEGORIES[0], PRIORITIES[1], STATUSES[0],
                    "", "", "", "", "", "", "")

        scroll = ctk.CTkScrollableFrame(win, corner_radius=10)
        scroll.pack(fill="both", expand=True, padx=12, pady=(12, 6))

        ctk.CTkLabel(scroll, text=tt("date")).pack(anchor="w", pady=(4, 0))
        e_date = ctk.CTkEntry(scroll); e_date.insert(0, g[1]); e_date.pack(fill="x")

        ctk.CTkLabel(scroll, text=tt("source")).pack(anchor="w", pady=(8, 0))
        m_src = ctk.CTkOptionMenu(scroll, values=SOURCES); m_src.set(g[2]); m_src.pack(fill="x")

        ctk.CTkLabel(scroll, text=tt("source_note")).pack(anchor="w", pady=(8, 0))
        e_srcnote = ctk.CTkEntry(scroll, placeholder_text="напр.: ссылка на отзыв, № комнаты, ФИО сообщившего")
        e_srcnote.insert(0, g[3]); e_srcnote.pack(fill="x")

        ctk.CTkLabel(scroll, text=tt("category")).pack(anchor="w", pady=(8, 0))
        m_cat = ctk.CTkOptionMenu(scroll, values=CATEGORIES); m_cat.set(g[4]); m_cat.pack(fill="x")

        r3 = ctk.CTkFrame(scroll, fg_color="transparent"); r3.pack(fill="x", pady=(8, 0))
        ctk.CTkLabel(r3, text=tt("priority")).pack(side="left", padx=(0, 6))
        m_prio = ctk.CTkOptionMenu(r3, values=PRIORITIES, width=140); m_prio.set(g[5]); m_prio.pack(side="left")
        ctk.CTkLabel(r3, text=tt("status")).pack(side="left", padx=(16, 6))
        m_st = ctk.CTkOptionMenu(r3, values=STATUSES, width=140); m_st.set(g[6]); m_st.pack(side="left")

        ctk.CTkLabel(scroll, text=tt("guest")).pack(anchor="w", pady=(8, 0))
        e_guest = ctk.CTkEntry(scroll); e_guest.insert(0, g[7]); e_guest.pack(fill="x")

        ctk.CTkLabel(scroll, text=tt("department")).pack(anchor="w", pady=(8, 0))
        e_dep = ctk.CTkEntry(scroll); e_dep.insert(0, g[8]); e_dep.pack(fill="x")

        ctk.CTkLabel(scroll, text=tt("assignee")).pack(anchor="w", pady=(8, 0))
        e_asn = ctk.CTkEntry(scroll); e_asn.insert(0, g[9]); e_asn.pack(fill="x")

        ctk.CTkLabel(scroll, text=tt("deadline")).pack(anchor="w", pady=(8, 0))
        e_dl = ctk.CTkEntry(scroll); e_dl.insert(0, g[10]); e_dl.pack(fill="x")

        ctk.CTkLabel(scroll, text=tt("description")).pack(anchor="w", pady=(8, 0))
        c_desc = ctk.CTkComboBox(scroll, values=COMPLAINT_TYPES)
        c_desc.set(g[11] if g[11] else "")
        c_desc.pack(fill="x")

        ctk.CTkLabel(scroll, text=tt("measures")).pack(anchor="w", pady=(8, 0))
        t_meas = ctk.CTkTextbox(scroll, height=60); t_meas.pack(fill="x")
        t_meas.insert("1.0", g[12])

        ctk.CTkLabel(scroll, text=tt("result")).pack(anchor="w", pady=(8, 0))
        t_res = ctk.CTkTextbox(scroll, height=60); t_res.pack(fill="x")
        t_res.insert("1.0", g[13])

        def save():
            desc = c_desc.get().strip()
            if not desc:
                messagebox.showwarning(tt("warning"), tt("need_text")); return
            vals = (e_date.get(), m_src.get(), e_srcnote.get().strip(), m_cat.get(), m_prio.get(), m_st.get(),
                    e_guest.get(), e_dep.get(), e_asn.get(), e_dl.get(), desc,
                    t_meas.get("1.0", "end").strip(), t_res.get("1.0", "end").strip())
            c = db()
            if rec:
                c.execute("UPDATE complaints SET date=?, source=?, source_note=?, category=?, priority=?, status=?, "
                          "guest=?, department=?, assignee=?, deadline=?, description=?, measures=?, result=? WHERE id=?",
                          vals + (rec[0],))
            else:
                c.execute("INSERT INTO complaints (date, source, source_note, category, priority, status, guest, "
                          "department, assignee, deadline, description, measures, result) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
                          vals)
            c.commit(); c.close()
            win.destroy(); self.rebuild()

        ctk.CTkButton(win, text=tt("save"), command=save, height=40,
                      fg_color="#0891b2", hover_color="#0e7490").pack(fill="x", padx=12, pady=(0, 12))

    def export_excel(self):
        rows = self._fetch()
        if not rows:
            messagebox.showwarning(tt("warning"), tt("no_rec")); return
        path = filedialog.asksaveasfilename(
            defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")],
            initialfile=f"complaints_{self.from_var.get()}_{self.to_var.get()}.xlsx")
        if not path:
            return
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Alignment, Border, Font, Side, PatternFill
        except ImportError:
            messagebox.showerror("Ошибка", "pip install openpyxl"); return

        wb = Workbook(); ws = wb.active; ws.title = "Жалобы"
        wrap = Alignment(wrap_text=True, vertical="top")
        thin = Border(*[Side(style="thin")] * 4)
        bold = Font(bold=True)
        yellow = PatternFill("solid", fgColor="FEC50C")

        ws.merge_cells("A1:M1")
        ws["A1"] = "ЖУРНАЛ ЖАЛОБ И ОБРАЩЕНИЙ"
        ws["A1"].font = Font(bold=True, size=14)
        ws["A1"].fill = yellow
        ws["A2"] = f"Период: {self.from_var.get()} — {self.to_var.get()}"

        headers = ["Дата", "Источник", "💬 Комментарий источника", "Категория", "Приоритет", "Статус",
                   "Гость/№ комнаты", "Отдел", "Исполнитель", "Срок", "Описание", "Меры", "Итог"]
        for j, h in enumerate(headers, start=1):
            cell = ws.cell(row=4, column=j, value=h); cell.font = bold; cell.border = thin

        prio_fill = {"🔴 Высокая": "FCA5A5", "🟡 Средняя": "FDE68A", "🟢 Низкая": "BBF7D0"}
        st_fill = {"🆕 Новая": "FCA5A5", "⚙️ В работе": "FDE68A", "✅ Решена": "BBF7D0", "❌ Отклонена": "D1D5DB"}

        for i, r in enumerate(rows, start=5):
            vals = r[1:14]
            for j, v in enumerate(vals, start=1):
                cell = ws.cell(row=i, column=j, value=v); cell.alignment = wrap; cell.border = thin
            p = vals[4]
            if p in prio_fill:
                ws.cell(row=i, column=5).fill = PatternFill("solid", fgColor=prio_fill[p])
            s = vals[5]
            if s in st_fill:
                ws.cell(row=i, column=6).fill = PatternFill("solid", fgColor=st_fill[s])

        for j, w in enumerate([12, 24, 32, 22, 14, 14, 22, 20, 20, 12, 40, 30, 30], start=1):
            ws.column_dimensions[chr(64 + j)].width = w
        wb.save(path)
        messagebox.showinfo("✅", f"Сохранено:\n{path}")
# -*- coding: utf-8 -*-
"""Гигиеническое обучение — тренинги по отделам (планирование и учёт), 4 языка."""
import sqlite3
from datetime import date
from pathlib import Path

import customtkinter as ctk
from tkinter import messagebox

from modules.translations import get_language

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "database" / "sanepi.db"

T = {
    "title": {"ru": "🎓 Гигиеническое обучение — тренинги", "kk": "🎓 Гигиеналық оқыту — тренингтер", "en": "🎓 Hygiene training sessions", "tr": "🎓 Hijyen eğitimi oturumları"},
    "sub": {"ru": "Проведение тренингов по отделам", "kk": "Бөлімдер бойынша тренингтер өткізу", "en": "Department trainings", "tr": "Birim eğitimleri"},
    "add": {"ru": "➕ Запланировать тренинг", "kk": "➕ Тренинг жоспарлау", "en": "➕ Plan training", "tr": "➕ Eğitim planla"},
    "date": {"ru": "Дата проведения (ГГГГ-ММ-ДД):", "kk": "Өткізу күні (ЖЖЖЖ-АА-КК):", "en": "Date (YYYY-MM-DD):", "tr": "Tarih (YYYY-AA-GG):"},
    "department": {"ru": "Отдел:", "kk": "Бөлім:", "en": "Department:", "tr": "Birim:"},
    "dept_ph": {"ru": "Например: Кухня, F&B, Хаускипинг, Инженерный…", "kk": "Мысалы: Ас үйі, F&B, Хаускипинг…", "en": "e.g. Kitchen, F&B, Housekeeping…", "tr": "örn. Mutfak, F&B, Kat hizmetleri…"},
    "topic": {"ru": "Тема тренинга:", "kk": "Тренинг тақырыбы:", "en": "Training topic:", "tr": "Eğitim konusu:"},
    "topic_ph": {"ru": "Например: Личная гигиена персонала", "kk": "Мысалы: Персоналдың жеке гигиенасы", "en": "e.g. Staff personal hygiene", "tr": "örn. Personel hijyeni"},
    "trainer": {"ru": "Тренер (кто проводит):", "kk": "Тренер (кім өткізеді):", "en": "Trainer:", "tr": "Eğitmen:"},
    "attendees": {"ru": "Присутствовали (ФИО с новой строки):", "kk": "Қатысушылар (әр жолда жаңа ФИО):", "en": "Attendees (one per line):", "tr": "Katılımcılar (her satırda bir):"},
    "notes": {"ru": "Заметка:", "kk": "Ескертпе:", "en": "Note:", "tr": "Not:"},
    "save": {"ru": "💾 Сохранить", "kk": "💾 Сақтау", "en": "💾 Save", "tr": "💾 Kaydet"},
    "warning": {"ru": "⚠️ Внимание", "kk": "⚠️ Назар аударыңыз", "en": "⚠️ Warning", "tr": "⚠️ Uyarı"},
    "need_dept": {"ru": "Укажите отдел!", "kk": "Бөлімді көрсетіңіз!", "en": "Enter department!", "tr": "Birimi girin!"},
    "need_topic": {"ru": "Укажите тему тренинга!", "kk": "Тренинг тақырыбын көрсетіңіз!", "en": "Enter topic!", "tr": "Konuyu girin!"},
    "del_rec": {"ru": "Удалить тренинг?", "kk": "Тренингті жою керек пе?", "en": "Delete training?", "tr": "Eğitim silinsin mi?"},
    "no_rec": {"ru": "Тренингов нет — запланируйте первый!", "kk": "Тренингтер жоқ — алғашқысын жоспарлаңыз!", "en": "No trainings — plan the first one!", "tr": "Eğitim yok — ilkini planlayın!"},
    "planned": {"ru": "🟢 Запланирован", "kk": "🟢 Жоспарланды", "en": "🟢 Planned", "tr": "🟢 Planlandı"},
    "done": {"ru": "✅ Проведён", "kk": "✅ Өткізілді", "en": "✅ Done", "tr": "✅ Yapıldı"},
    "mark_done": {"ru": "✅", "kk": "✅", "en": "✅", "tr": "✅"},
    "all": {"ru": "Все", "kk": "Барлығы", "en": "All", "tr": "Tümü"},
    "flt_plan": {"ru": "Запланированные", "kk": "Жоспарланған", "en": "Planned", "tr": "Planlanan"},
    "flt_done": {"ru": "Проведённые", "kk": "Өткізілген", "en": "Done", "tr": "Yapılan"},
    "filter": {"ru": "🔎 Фильтр:", "kk": "🔎 Сүзгі:", "en": "🔎 Filter:", "tr": "🔎 Filtre:"},
    "sum_done": {"ru": "✅ Проведено:", "kk": "✅ Өткізілген:", "en": "✅ Done:", "tr": "✅ Yapılan:"},
    "sum_plan": {"ru": "🟢 В плане:", "kk": "🟢 Жоспарда:", "en": "🟢 Planned:", "tr": "🟢 Planda:"},
    "sum_dept": {"ru": "🏢 Отделов охвачено:", "kk": "🏢 Қамтылған бөлімдер:", "en": "🏢 Departments covered:", "tr": "🏢 Kapsanan birim:"},
    "persons": {"ru": "👥 человек", "kk": "👥 адам", "en": "👥 persons", "tr": "👥 kişi"},
}

TOPIC_IDEAS = [
    "Личная гигиена персонала",
    "Мытьё рук и использование перчаток",
    "Температурный режим хранения продуктов",
    "Маркировка и сроки годности",
    "Профилактика пищевых отравлений",
    "Уборка и дезинфекция помещений",
    "Требования к спецодежде",
    "Действия при отклонениях HACCP",
]


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
    c = db()
    c.execute("""CREATE TABLE IF NOT EXISTS hygiene_trainings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        department TEXT,
        topic TEXT,
        trainer TEXT,
        attendees TEXT,
        notes TEXT,
        status TEXT DEFAULT 'planned',
        created_at TEXT DEFAULT (datetime('now','localtime'))
    )""")
    c.commit()
    c.close()


def build_hygiene_page(master):
    HygienePage(master).pack(fill="both", expand=True)


class HygienePage(ctk.CTkFrame):
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
        ctk.CTkButton(head, text=tt("add"), width=220, fg_color="#0891b2", hover_color="#0e7490",
                      command=self.dialog).pack(side="right", padx=10)
        ctk.CTkLabel(head, text=tt("sub"), text_color="gray").pack(side="left", pady=8)

        year = str(date.today().year)
        rows = db().execute("SELECT status, department FROM hygiene_trainings WHERE substr(date,1,4)=?", (year,)).fetchall()
        done = sum(1 for s, _ in rows if s == "done")
        plan = sum(1 for s, _ in rows if s == "planned")
        depts = len({(d or "").strip().lower() for st, d in rows if st == "done"})
        summ = ctk.CTkFrame(self)
        summ.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(summ, text=f"{tt('sum_done')} {done}", text_color="#16A34A",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=12, pady=8)
        ctk.CTkLabel(summ, text=f"{tt('sum_plan')} {plan}", text_color="#F59E0B",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=12)
        ctk.CTkLabel(summ, text=f"{tt('sum_dept')} {depts}", text_color="#60a5fa",
                     font=ctk.CTkFont(size=14, weight="bold")).pack(side="left", padx=12)

        filt = ctk.CTkFrame(self, fg_color="transparent")
        filt.pack(fill="x", padx=10, pady=5)
        ctk.CTkLabel(filt, text=tt("filter"), font=ctk.CTkFont(size=13, weight="bold")).pack(side="left")
        om = ctk.CTkOptionMenu(filt, values=[tt("all"), tt("flt_plan"), tt("flt_done")], width=180, command=self._on_flt)
        om.set({"all": tt("all"), "planned": tt("flt_plan"), "done": tt("flt_done")}[self.flt])
        om.pack(side="right", padx=(4, 0))

        card = ctk.CTkFrame(self)
        card.pack(fill="both", expand=True, padx=10, pady=5)
        box = ctk.CTkScrollableFrame(card, height=320)
        box.pack(fill="both", expand=True, padx=10, pady=10)
        q = "SELECT id, date, department, topic, trainer, attendees, status FROM hygiene_trainings"
        if self.flt != "all":
            q += f" WHERE status='{self.flt}'"
        q += " ORDER BY date DESC LIMIT 200"
        rows = db().execute(q).fetchall()
        if not rows:
            ctk.CTkLabel(box, text=tt("no_rec"), text_color="gray").pack(pady=10)
            return
        for rid, d, dept, topic, trainer, att, status in rows:
            n_att = len([x for x in (att or "").replace(",", "\n").split("\n") if x.strip()])
            row = ctk.CTkFrame(box, fg_color="gray15")
            row.pack(fill="x", pady=3)
            s_txt, s_col = (tt("done"), "#16A34A") if status == "done" else (tt("planned"), "#F59E0B")
            ctk.CTkLabel(row, text=f"🎓 {d or '—'} • {dept or ''}", font=ctk.CTkFont(size=13, weight="bold"),
                         anchor="w").pack(anchor="w", padx=8, pady=(6, 0))
            ctk.CTkLabel(row, text=f"📖 {topic or ''}", anchor="w", justify="left", wraplength=880).pack(anchor="w", padx=8)
            ctk.CTkLabel(row, text=f"{s_txt} • 🧑‍🏫 {trainer or '—'} • {n_att} {tt('persons')}",
                         text_color=s_col, font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=8, pady=(0, 6))
            right = ctk.CTkFrame(row, fg_color="transparent")
            right.pack(side="right", padx=6, pady=6)
            ctk.CTkButton(right, text="🗑️", width=36, fg_color="#7f1d1d", hover_color="#991b1b",
                          command=lambda r=rid: self.delete(r)).pack(side="right", padx=(3, 0))
            rec = (rid, d, dept, topic, trainer, att, status)
            ctk.CTkButton(right, text="✏️", width=36, fg_color="gray25",
                          command=lambda r=rec: self.dialog(r)).pack(side="right", padx=(3, 0))
            if status != "done":
                ctk.CTkButton(right, text=tt("mark_done"), width=36, fg_color="#16A34A", hover_color="#15803D",
                              command=lambda r=rid: self.mark_done(r)).pack(side="right")

    def _on_flt(self, v):
        self.flt = next((k for k in ("all", "planned", "done") if tt(k if k != "all" else "all") == v
                         or (k == "all" and v == tt("all")) or (k == "planned" and v == tt("flt_plan"))
                         or (k == "done" and v == tt("flt_done"))), "all")
        self.rebuild()

    def mark_done(self, rid):
        c = db()
        c.execute("UPDATE hygiene_trainings SET status='done' WHERE id=?", (rid,))
        c.commit(); c.close()
        self.rebuild()

    def delete(self, rid):
        if messagebox.askyesno(tt("warning"), tt("del_rec")):
            c = db()
            c.execute("DELETE FROM hygiene_trainings WHERE id=?", (rid,))
            c.commit(); c.close()
            self.rebuild()

    def dialog(self, rec=None):
        win = ctk.CTkToplevel(self)
        win.title(tt("title"))
        win.geometry("480x620")
        win.grab_set()
        ctk.CTkLabel(win, text=tt("date")).pack(anchor="w", padx=20, pady=(10, 0))
        e_date = ctk.CTkEntry(win)
        e_date.insert(0, rec[1] if rec else today_str())
        e_date.pack(fill="x", padx=20)
        ctk.CTkLabel(win, text=tt("department")).pack(anchor="w", padx=20, pady=(8, 0))
        e_dept = ctk.CTkEntry(win, placeholder_text=tt("dept_ph"))
        e_dept.insert(0, rec[2] if rec else "")
        e_dept.pack(fill="x", padx=20)
        ctk.CTkLabel(win, text=tt("topic")).pack(anchor="w", padx=20, pady=(8, 0))
        e_topic = ctk.CTkEntry(win, placeholder_text=tt("topic_ph"))
        e_topic.insert(0, rec[3] if rec else "")
        e_topic.pack(fill="x", padx=20)
        ideas = ctk.CTkFrame(win, fg_color="transparent")
        ideas.pack(fill="x", padx=20, pady=(4, 0))
        for i, idea in enumerate(TOPIC_IDEAS[:4]):
            ctk.CTkButton(ideas, text=idea, width=210, height=24, font=("Segoe UI", 10),
                          fg_color="#4b5563", hover_color="#374151",
                          command=lambda t=idea: (e_topic.delete(0, "end"), e_topic.insert(0, t))).grid(row=i // 2, column=i % 2, padx=2, pady=2)
        ctk.CTkLabel(win, text=tt("trainer")).pack(anchor="w", padx=20, pady=(8, 0))
        e_tr = ctk.CTkEntry(win)
        e_tr.insert(0, rec[4] if rec else "Дәурен Оспан")
        e_tr.pack(fill="x", padx=20)
        ctk.CTkLabel(win, text=tt("attendees")).pack(anchor="w", padx=20, pady=(8, 0))
        t_att = ctk.CTkTextbox(win, height=110)
        t_att.pack(fill="x", padx=20)
        if rec and rec[5]:
            t_att.insert("1.0", rec[5])
        ctk.CTkLabel(win, text=tt("notes")).pack(anchor="w", padx=20, pady=(8, 0))
        e_notes = ctk.CTkEntry(win)
        e_notes.insert(0, rec[6] if rec else "")
        e_notes.pack(fill="x", padx=20)

        def save():
            if not e_dept.get().strip():
                messagebox.showwarning(tt("warning"), tt("need_dept"))
                return
            if not e_topic.get().strip():
                messagebox.showwarning(tt("warning"), tt("need_topic"))
                return
            c = db()
            if rec:
                c.execute("UPDATE hygiene_trainings SET date=?, department=?, topic=?, trainer=?, attendees=?, notes=? WHERE id=?",
                          (e_date.get(), e_dept.get(), e_topic.get(), e_tr.get(), t_att.get("1.0", "end").strip(), e_notes.get(), rec[0]))
            else:
                c.execute("INSERT INTO hygiene_trainings (date, department, topic, trainer, attendees, notes) VALUES (?,?,?,?,?,?)",
                          (e_date.get(), e_dept.get(), e_topic.get(), e_tr.get(), t_att.get("1.0", "end").strip(), e_notes.get()))
            c.commit(); c.close()
            win.destroy(); self.rebuild()
        ctk.CTkButton(win, text=tt("save"), command=save).pack(pady=12)
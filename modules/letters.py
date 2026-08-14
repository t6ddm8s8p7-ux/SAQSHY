"""
Страница «✉️ Письма» — реестр входящей и исходящей
корреспонденции санитарного врача с контролем сроков ответа.
"""
import json
import os
import uuid
from datetime import date, datetime
from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk
import pandas as pd

from modules.translations import tr

DATABASE_DIR = Path("database")
LETTERS_FILE = DATABASE_DIR / "letters.json"
EXPORTS_DIR = Path("exports") / "letters"


def _load_letters():
    if not LETTERS_FILE.exists():
        return []
    try:
        with open(LETTERS_FILE, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_letters(letters):
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    with open(LETTERS_FILE, "w", encoding="utf-8") as f:
        json.dump(letters, f, ensure_ascii=False, indent=2)


def _parse_date(value):
    text = str(value or "").strip()
    for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except Exception:
            continue
    return None


def _deadline_status(deadline_str):
    """Возвращает ('status_key', 'days_left', 'color')."""
    if not deadline_str:
        return "no_deadline", "-", "#9ca3af"
    d = _parse_date(deadline_str)
    if not d:
        return "no_deadline", "-", "#9ca3af"
    days = (d - date.today()).days
    if days < 0:
        return "overdue", days, "#ef4444"
    if days <= 7:
        return "urgent", days, "#f59e0b"
    return "ok", days, "#22c55e"


def make_card(parent, title, value, color):
    card = ctk.CTkFrame(parent, corner_radius=14)
    ctk.CTkLabel(
        card, text=title, font=("Arial", 13, "bold"), text_color=color
    ).pack(pady=(10, 4))
    ctk.CTkLabel(card, text=str(value), font=("Arial", 22, "bold")).pack(pady=(0, 10))
    return card


def add_letter_dialog(parent, on_refresh):
    dialog = ctk.CTkToplevel(parent)
    dialog.title("Новое письмо")
    dialog.geometry("560x680")
    dialog.lift()
    dialog.focus_force()
    dialog.grab_set()

    ctk.CTkLabel(
        dialog, text="✉️ Новое письмо", font=("Arial", 22, "bold")
    ).pack(pady=(20, 10))

    type_var = ctk.StringVar(value="incoming")
    type_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    type_frame.pack(fill="x", padx=30, pady=(0, 10))
    ctk.CTkRadioButton(
        type_frame, text="📥 Входящее",
        variable=type_var, value="incoming",
    ).pack(side="left", padx=10)
    ctk.CTkRadioButton(
        type_frame, text="📤 Исходящее",
        variable=type_var, value="outgoing",
    ).pack(side="left", padx=10)

    ctk.CTkLabel(dialog, text="Номер письма:").pack(anchor="w", padx=30, pady=(6, 2))
    number_entry = ctk.CTkEntry(dialog, width=460, placeholder_text="например: 123/45-вх")
    number_entry.pack(padx=30)

    ctk.CTkLabel(dialog, text="Дата:").pack(anchor="w", padx=30, pady=(6, 2))
    date_entry = ctk.CTkEntry(dialog, width=460, placeholder_text=date.today().strftime("%d.%m.%Y"))
    date_entry.insert(0, date.today().strftime("%d.%m.%Y"))
    date_entry.pack(padx=30)

    ctk.CTkLabel(dialog, text="От кого / Кому:").pack(anchor="w", padx=30, pady=(6, 2))
    counterparty_entry = ctk.CTkEntry(dialog, width=460, placeholder_text="Организация или ФИО")
    counterparty_entry.pack(padx=30)

    ctk.CTkLabel(dialog, text="Тема / Краткое содержание:").pack(anchor="w", padx=30, pady=(6, 2))
    subject_box = ctk.CTkTextbox(dialog, width=460, height=80, font=("Arial", 13))
    subject_box.pack(padx=30)

    ctk.CTkLabel(dialog, text="Срок ответа (только для входящих):").pack(anchor="w", padx=30, pady=(6, 2))
    deadline_entry = ctk.CTkEntry(dialog, width=460, placeholder_text="дд.мм.гггг")
    deadline_entry.pack(padx=30)

    attachment_path = {"path": ""}
    attach_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    attach_frame.pack(fill="x", padx=30, pady=(10, 4))
    attach_label = ctk.CTkLabel(attach_frame, text="📎 Файл: не выбран", font=("Arial", 12))
    attach_label.pack(side="left")

    def pick_file():
        p = filedialog.askopenfilename(
            title="Выберите файл письма",
            filetypes=[("Все файлы", "*.*"), ("PDF", "*.pdf"), ("Изображения", "*.jpg;*.png")],
        )
        if p:
            attachment_path["path"] = p
            attach_label.configure(text=f"📎 {Path(p).name}")

    ctk.CTkButton(
        attach_frame, text="Выбрать", width=110, height=32, command=pick_file
    ).pack(side="right")

    def save():
        number = number_entry.get().strip()
        if not number:
            messagebox.showwarning("SanEpi AI", "Введите номер письма.")
            return
        counterparty = counterparty_entry.get().strip()
        if not counterparty:
            messagebox.showwarning("SanEpi AI", "Укажите от кого / кому.")
            return
        subject = subject_box.get("1.0", "end").strip()
        if not subject:
            messagebox.showwarning("SanEpi AI", "Введите тему письма.")
            return

        date_text = date_entry.get().strip() or date.today().strftime("%d.%m.%Y")
        parsed_date = _parse_date(date_text)
        if not parsed_date:
            messagebox.showwarning("SanEpi AI", "Неверный формат даты.")
            return

        deadline_text = deadline_entry.get().strip()
        if deadline_text:
            parsed_deadline = _parse_date(deadline_text)
            if not parsed_deadline:
                messagebox.showwarning("SanEpi AI", "Неверный формат срока ответа.")
                return
            deadline_iso = parsed_deadline.isoformat()
        else:
            deadline_iso = ""

        letter = {
            "id": str(uuid.uuid4()),
            "type": type_var.get(),
            "number": number,
            "date": parsed_date.isoformat(),
            "counterparty": counterparty,
            "subject": subject,
            "deadline": deadline_iso,
            "status": "open" if type_var.get() == "incoming" and deadline_iso else "answered",
            "attachment": attachment_path["path"],
            "created_at": datetime.now().isoformat(timespec="seconds"),
        }

        letters = _load_letters()
        letters.append(letter)
        _save_letters(letters)
        dialog.destroy()
        on_refresh()
        messagebox.showinfo("SanEpi AI", f"Письмо №{number} сохранено.")

    ctk.CTkButton(
        dialog, text="💾 Сохранить письмо",
        width=300, height=42, fg_color="#059669",
        hover_color="#047857", command=save,
    ).pack(pady=20)


def export_letters_excel():
    letters = _load_letters()
    if not letters:
        messagebox.showinfo("SanEpi AI", "Писем пока нет.")
        return
    rows = []
    for lt in letters:
        status_key, days, _ = _deadline_status(lt.get("deadline"))
        status_map = {
            "overdue": "Просрочено",
            "urgent": "Истекает",
            "ok": "В срок",
            "no_deadline": "-",
        }
        rows.append({
            "Тип": "Входящее" if lt["type"] == "incoming" else "Исходящее",
            "Номер": lt.get("number", "-"),
            "Дата": lt.get("date", "-"),
            "Контрагент": lt.get("counterparty", "-"),
            "Тема": lt.get("subject", "-"),
            "Срок ответа": lt.get("deadline", "-"),
            "Осталось дней": days,
            "Статус": status_map.get(status_key, "-"),
            "Файл": Path(lt["attachment"]).name if lt.get("attachment") else "-",
        })
    df = pd.DataFrame(rows)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = EXPORTS_DIR / f"letters_{date.today()}.xlsx"
    df.to_excel(path, index=False)
    messagebox.showinfo("SanEpi AI", f"✅ Экспорт сохранён:\n{path}")
    try:
        os.startfile(str(EXPORTS_DIR))
    except Exception:
        pass


def build_letters_page(parent):
    ctk.CTkLabel(
        parent, text=f"✉️ {tr('letters')}", font=("Arial", 34, "bold")
    ).pack(pady=(20, 5))
    ctk.CTkLabel(
        parent,
        text="Входящая и исходящая корреспонденция. "
             "Сроки ответа по входящим письмам подсвечиваются автоматически.",
        font=("Arial", 13),
        text_color="#9ca3af",
    ).pack(pady=(0, 10))

    state = {"filter": "all", "search": ""}

    def refresh():
        letters = _load_letters()

        total = len(letters)
        incoming = [l for l in letters if l["type"] == "incoming"]
        outgoing = [l for l in letters if l["type"] == "outgoing"]
        overdue = sum(
            1 for l in incoming if _deadline_status(l.get("deadline"))[0] == "overdue"
        )
        urgent = sum(
            1 for l in incoming if _deadline_status(l.get("deadline"))[0] == "urgent"
        )

        for w in cards_frame.winfo_children():
            w.destroy()
        cards_data = [
            ("📨 Всего писем", total, "#60a5fa"),
            ("📥 Входящих", len(incoming), "#38bdf8"),
            ("📤 Исходящих", len(outgoing), "#a78bfa"),
            ("🟡 Истекают 7 дн", urgent, "#f59e0b"),
            ("🔴 Просрочено", overdue, "#ef4444"),
        ]
        for i, (t, v, c) in enumerate(cards_data):
            card = make_card(cards_frame, t, v, c)
            card.grid(row=0, column=i, padx=6, pady=6, sticky="nsew")
            cards_frame.grid_columnconfigure(i, weight=1)

        render_table()

    # Кнопки
    top_btns = ctk.CTkFrame(parent, fg_color="transparent")
    top_btns.pack(fill="x", padx=20, pady=(0, 8))
    ctk.CTkButton(
        top_btns, text="➕ Новое письмо",
        width=200, height=38,
        fg_color="#059669", hover_color="#047857",
        command=lambda: add_letter_dialog(parent, refresh),
    ).pack(side="left", padx=4)
    ctk.CTkButton(
        top_btns, text="🔄 Обновить",
        width=130, height=38, fg_color="#6b7280",
        command=refresh,
    ).pack(side="left", padx=4)
    ctk.CTkButton(
        top_btns, text="📥 Экспорт в Excel",
        width=200, height=38, fg_color="#1d4ed8",
        hover_color="#1e40af", command=export_letters_excel,
    ).pack(side="right", padx=4)

    # Поиск
    search_entry = ctk.CTkEntry(
        parent, width=400, height=38,
        placeholder_text="🔍 Поиск по номеру, контрагенту, теме...",
    )
    search_entry.pack(padx=20, pady=(0, 6), anchor="w")

    def on_search(*_):
        state["search"] = search_entry.get().lower().strip()
        render_table()
    search_entry.bind("<KeyRelease>", on_search)

    # Фильтры
    filter_frame = ctk.CTkFrame(parent, corner_radius=14)
    filter_frame.pack(fill="x", padx=20, pady=(0, 10))

    def set_filter(v):
        state["filter"] = v
        render_table()

    filter_buttons = [
        ("📨 Все", "all"),
        ("📥 Входящие", "incoming"),
        ("📤 Исходящие", "outgoing"),
        ("🔴 Просрочено", "overdue"),
        ("🟡 Истекают", "urgent"),
    ]
    for text, value in filter_buttons:
        ctk.CTkButton(
            filter_frame, text=text, width=150, height=34,
            fg_color="#4b5563", hover_color="#374151",
            command=lambda v=value: set_filter(v),
        ).pack(side="left", padx=4, pady=6)

    # Карточки
    cards_frame = ctk.CTkFrame(parent, corner_radius=14)
    cards_frame.pack(fill="x", padx=20, pady=(0, 10))

    # Таблица
    table = ctk.CTkScrollableFrame(parent, corner_radius=14)
    table.pack(fill="both", expand=True, padx=20, pady=(0, 15))

    headers = ["Тип", "Номер", "Дата", "Контрагент", "Тема", "Срок", "Осталось", "Статус", ""]

    def render_table():
        for w in table.winfo_children():
            w.destroy()
        for col, h in enumerate(headers):
            ctk.CTkLabel(
                table, text=h, font=("Arial", 13, "bold")
            ).grid(row=0, column=col, padx=8, pady=6, sticky="w")

        letters = _load_letters()
        letters.sort(key=lambda l: l.get("date", ""), reverse=True)

        row = 1
        for lt in letters:
            lt_type = lt.get("type", "")
            status_key, days, color = _deadline_status(lt.get("deadline"))

            if state["filter"] == "incoming" and lt_type != "incoming":
                continue
            if state["filter"] == "outgoing" and lt_type != "outgoing":
                continue
            if state["filter"] == "overdue" and status_key != "overdue":
                continue
            if state["filter"] == "urgent" and status_key != "urgent":
                continue

            search = state["search"]
            if search:
                text = (
                    f"{lt.get('number', '')} "
                    f"{lt.get('counterparty', '')} "
                    f"{lt.get('subject', '')}"
                ).lower()
                if search not in text:
                    continue

            type_emoji = "📥" if lt_type == "incoming" else "📤"
            status_text = {
                "overdue": "🔴 Просрочено",
                "urgent": "🟡 Истекает",
                "ok": "🟢 В срок",
                "no_deadline": "-",
            }.get(status_key, "-")

            values = [
                type_emoji,
                lt.get("number", "-"),
                lt.get("date", "-"),
                lt.get("counterparty", "-"),
                lt.get("subject", "-"),
                lt.get("deadline", "-"),
                days if status_key != "no_deadline" else "-",
                status_text,
            ]

            for col, v in enumerate(values):
                text_color = color if col == 7 else None
                label = ctk.CTkLabel(
                    table, text=str(v),
                    font=("Arial", 13),
                    text_color=text_color,
                    anchor="w",
                )
                label.grid(row=row, column=col, padx=8, pady=5, sticky="w")

            # Кнопки: открыть файл / удалить
            btns = ctk.CTkFrame(table, fg_color="transparent")
            btns.grid(row=row, column=8, padx=6, pady=5, sticky="w")

            if lt.get("attachment") and Path(lt["attachment"]).exists():
                def open_file(p=lt["attachment"]):
                    try:
                        os.startfile(p)
                    except Exception as e:
                        messagebox.showerror("SanEpi AI", f"Не удалось открыть:\n{e}")
                ctk.CTkButton(
                    btns, text="📎", width=40, height=28,
                    fg_color="#4b5563", command=open_file,
                ).pack(side="left", padx=2)

            def delete(lid=lt["id"]):
                if not messagebox.askyesno("Удалить письмо", "Удалить это письмо из реестра?"):
                    return
                lst = [x for x in _load_letters() if x["id"] != lid]
                _save_letters(lst)
                refresh()

            ctk.CTkButton(
                btns, text="🗑️", width=40, height=28,
                fg_color="#b91c1c", hover_color="#991b1b",
                command=delete,
            ).pack(side="left", padx=2)

            row += 1

        if row == 1:
            ctk.CTkLabel(
                table, text="Нет писем по выбранному фильтру.",
                font=("Arial", 14),
            ).grid(row=1, column=0, columnspan=9, pady=30)

    refresh()
import os
import webbrowser
from datetime import datetime, date
from pathlib import Path
from urllib.parse import quote

import customtkinter as ctk
import pandas as pd
from tkinter import messagebox

from modules.dashboard_data import load_dashboard_data
from modules.translations import tr
from modules.esen_name_fix import open_name_fix_window
from modules.dashboard_quality import show_quality_details
from modules.email_sender import send_email_notification
from modules.letter_generator import generate_medical_expiring_letter


def parse_valid_until(value):
    text = str(value).strip()
    if " - " in text:
        text = text.split(" - ")[-1].strip()
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except Exception:
        return None


def get_medical_status(emp):
    expiry = parse_valid_until(emp.get("valid_until", ""))
    if not expiry:
        return "unknown", "-", "#9ca3af"
    days_left = (expiry - date.today()).days
    if days_left < 0:
        return "expired", days_left, "#ef4444"
    if days_left <= 30:
        return "expiring", days_left, "#f59e0b"
    return "valid", days_left, "#22c55e"


def get_hr_matched_esen(data):
    """Только сотрудники из списка HR (совпавшие с e-SEN при сверке)."""
    compare = data.get("compare", {}) or {}
    result = []
    for m in (compare.get("matched", []) or []):
        if isinstance(m, dict) and isinstance(m.get("esen"), dict):
            result.append(m["esen"])
    return result


def make_stat_card(parent, title, value, color):
    card = ctk.CTkFrame(parent, corner_radius=14)
    ctk.CTkLabel(
        card,
        text=title,
        font=("Arial", 14, "bold"),
        text_color=color,
    ).pack(pady=(10, 5))
    ctk.CTkLabel(
        card,
        text=str(value),
        font=("Arial", 24, "bold"),
    ).pack(pady=(0, 10))
    return card


def clean_phone_number(phone):
    number = "".join(char for char in str(phone) if char.isdigit())
    if number.startswith("8") and len(number) == 11:
        number = "7" + number[1:]
    if len(number) == 10:
        number = "7" + number
    return number


def get_whatsapp_message(emp, status_key, days_left):
    fio = str(emp.get("fio", "")).strip()
    valid_until = str(emp.get("valid_until", "")).strip()
    if status_key == "expired":
        expired_days = abs(days_left) if isinstance(days_left, int) else "-"
        return (
            f"Здравствуйте, {fio}!\n\n"
            f"Срок действия Вашего медицинского допуска истёк "
            f"{valid_until}.\n"
            f"Просрочка: {expired_days} дн.\n\n"
            f"Просим пройти периодический медицинский осмотр "
            f"и предоставить действующий медицинский допуск.\n\n"
            f"SanEpi AI"
        )
    return (
        f"Здравствуйте, {fio}!\n\n"
        f"Срок действия Вашего медицинского допуска истекает "
        f"{valid_until}.\n"
        f"Осталось дней: {days_left}.\n\n"
        f"Просим своевременно пройти периодический медицинский осмотр, "
        f"не допуская перерыва в сроке действия допуска.\n\n"
        f"SanEpi AI"
    )


def open_whatsapp_window(emp):
    status_key, days_left, status_color = get_medical_status(emp)

    window = ctk.CTkToplevel()
    window.title("WhatsApp")
    window.geometry("620x570")
    window.minsize(560, 520)
    window.lift()
    window.focus_force()
    window.grab_set()

    ctk.CTkLabel(
        window,
        text="📲 WhatsApp",
        font=("Arial", 26, "bold"),
    ).pack(pady=(20, 8))

    ctk.CTkLabel(
        window,
        text=str(emp.get("fio", "-")),
        font=("Arial", 17, "bold"),
        wraplength=560,
    ).pack(padx=20, pady=(0, 5))

    ctk.CTkLabel(
        window,
        text=f"{tr('period')}: {emp.get('valid_until', '-')}",
        font=("Arial", 14),
    ).pack(pady=3)

    ctk.CTkLabel(
        window,
        text=tr(status_key),
        font=("Arial", 15, "bold"),
        text_color=status_color,
    ).pack(pady=(3, 12))

    phone_entry = ctk.CTkEntry(
        window,
        placeholder_text="Номер телефона: 77011234567",
        width=540,
        height=40,
        font=("Arial", 15),
    )
    phone_entry.pack(padx=25, pady=(5, 12))
    phone_entry.focus()

    ctk.CTkLabel(
        window,
        text="Сообщение:",
        font=("Arial", 14, "bold"),
    ).pack(anchor="w", padx=40, pady=(5, 5))

    message_box = ctk.CTkTextbox(
        window,
        width=540,
        height=250,
        font=("Arial", 14),
        wrap="word",
    )
    message_box.pack(fill="both", expand=True, padx=25, pady=(0, 12))
    message_box.insert("1.0", get_whatsapp_message(emp, status_key, days_left))

    error_label = ctk.CTkLabel(
        window,
        text="",
        font=("Arial", 13),
        text_color="#ef4444",
        wraplength=540,
    )
    error_label.pack(padx=25, pady=(0, 5))

    def open_whatsapp():
        phone_number = clean_phone_number(phone_entry.get())
        if not phone_number:
            error_label.configure(text="Введите номер телефона.")
            return
        if len(phone_number) < 10:
            error_label.configure(
                text="Проверьте номер телефона. Номер слишком короткий."
            )
            return
        message = message_box.get("1.0", "end").strip()
        if not message:
            error_label.configure(text="Сообщение не должно быть пустым.")
            return
        error_label.configure(text="")
        whatsapp_url = f"https://wa.me/{phone_number}?text={quote(message)}"
        webbrowser.open(whatsapp_url)

    buttons_frame = ctk.CTkFrame(window, fg_color="transparent")
    buttons_frame.pack(fill="x", padx=25, pady=(5, 20))

    ctk.CTkButton(
        buttons_frame,
        text="📲 Открыть WhatsApp",
        height=42,
        command=open_whatsapp,
    ).pack(side="left", fill="x", expand=True, padx=(0, 6))

    ctk.CTkButton(
        buttons_frame,
        text="Закрыть",
        height=42,
        fg_color="#6b7280",
        hover_color="#4b5563",
        command=window.destroy,
    ).pack(side="left", fill="x", expand=True, padx=(6, 0))


def export_only_esen_excel():
    """🆕 Отдельный Excel по «лишним»: есть в e-SEN, но нет в HR."""
    data = load_dashboard_data()
    only_esen = (data.get("compare", {}) or {}).get("only_esen", []) or []
    if not only_esen:
        messagebox.showinfo("SanEpi AI", "Лишних нет: все сотрудники e-SEN есть в HR.")
        return

    rows = []
    for emp in only_esen:
        if not isinstance(emp, dict):
            continue
        rows.append({
            "ФИО": emp.get("fio", "-"),
            "Отдел": str(emp.get("department", "") or "-"),
            "Должность": emp.get("position", "-"),
            "Медкнижка": emp.get("medical_book", "-"),
            "Период действия": emp.get("valid_until", "-"),
            "Статус e-SEN": emp.get("status", "-"),
        })

    if not rows:
        messagebox.showinfo("SanEpi AI", "Лишних нет: все сотрудники e-SEN есть в HR.")
        return

    df = pd.DataFrame(rows)
    out_dir = Path("exports") / "reports"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"lishnie_est_v_esen_net_v_hr_{date.today()}.xlsx"
    df.to_excel(path, index=False)
    messagebox.showinfo(
        "SanEpi AI",
        f"✅ Сохранено сотрудников: {len(rows)}\n\n{path}",
    )
    try:
        os.startfile(str(out_dir))
    except Exception:
        pass


def send_expiring_letter():
    """Отправляет письмо руководству об истекающих медосмотрах (только по HR)."""
    data = load_dashboard_data()
    esen = get_hr_matched_esen(data)

    expiring = []
    for emp in esen:
        status_key, days_left, _ = get_medical_status(emp)
        if status_key in ("expiring", "expired"):
            expiring.append({
                "fio": emp.get("fio", "-"),
                "department": emp.get("department", "-"),
                "medical_book": emp.get("medical_book", "-"),
                "valid_until": emp.get("valid_until", "-"),
                "days_left": days_left if isinstance(days_left, int) else 0,
            })

    if not expiring:
        messagebox.showinfo("SanEpi AI", "Нет истекающих медосмотров для отправки.")
        return

    subject, body = generate_medical_expiring_letter(expiring, 30)
    if subject:
        send_email_notification(subject, body)
        messagebox.showinfo(
            "SanEpi AI",
            f"✅ Письмо сформировано!\n"
            f"Тема: {subject}\n"
            f"Получатель: Dauren.OSPAN@rixos.com\n\n"
            f"Проверьте текст и нажмите 'Отправить' в почтовом клиенте."
        )


def build_medical_page(parent):
    data = load_dashboard_data()
    esen = get_hr_matched_esen(data)  # только по списку HR

    valid_count = 0
    expiring_count = 0
    expired_count = 0
    unknown_count = 0

    for emp in esen:
        status, _, _ = get_medical_status(emp)
        if status == "valid":
            valid_count += 1
        elif status == "expiring":
            expiring_count += 1
        elif status == "expired":
            expired_count += 1
        else:
            unknown_count += 1

    ctk.CTkLabel(
        parent,
        text=f"🩺 {tr('medical')}",
        font=("Arial", 34, "bold"),
    ).pack(pady=(20, 10))

    ctk.CTkLabel(
        parent,
        text="Показаны только сотрудники из списка HR (совпавшие с e-SEN)",
        font=("Arial", 13),
        text_color="#9ca3af",
    ).pack(pady=(0, 8))

    stats_frame = ctk.CTkFrame(parent, corner_radius=14)
    stats_frame.pack(fill="x", padx=20, pady=10)

    cards = [
        ("👥 Всего по HR", len(esen), "#60a5fa"),
        (f"🟢 {tr('valid')}", valid_count, "#22c55e"),
        (f"🟡 {tr('expiring')}", expiring_count, "#f59e0b"),
        (f"🔴 {tr('expired')}", expired_count, "#ef4444"),
        (f"⚪ {tr('unknown')}", unknown_count, "#9ca3af"),
    ]

    for i, (title, value, color) in enumerate(cards):
        card = make_stat_card(stats_frame, title, value, color)
        card.grid(row=0, column=i, padx=8, pady=8, sticky="nsew")
        stats_frame.grid_columnconfigure(i, weight=1)

    # ============================================================
    # КНОПКИ ДЕЙСТВИЙ
    # ============================================================
    tools_frame = ctk.CTkFrame(parent, fg_color="transparent")
    tools_frame.pack(fill="x", padx=20, pady=(5, 5))

    ctk.CTkButton(
        tools_frame,
        text="✏️ Назначить ФИО по номеру медкнижки",
        width=380,
        height=38,
        fg_color="#7c3aed",
        hover_color="#6d28d9",
        command=open_name_fix_window,
    ).pack(side="left", padx=(0, 8))

    ctk.CTkButton(
        tools_frame,
        text="⚠️ Без ФИО и дубликаты e-SEN",
        width=380,
        height=38,
        fg_color="#d97706",
        hover_color="#b45309",
        command=lambda: show_quality_details(data["quality"]),
    ).pack(side="left")

    ctk.CTkButton(
        tools_frame,
        text="📧 Отправить письмо руководству",
        width=380,
        height=38,
        fg_color="#1d4ed8",
        hover_color="#1e40af",
        command=send_expiring_letter,
    ).pack(side="right")

    # 🆕 ВТОРАЯ СТРОКА: экспорт «лишних» (есть в e-SEN, нет в HR)
    tools_frame2 = ctk.CTkFrame(parent, fg_color="transparent")
    tools_frame2.pack(fill="x", padx=20, pady=(0, 5))

    ctk.CTkButton(
        tools_frame2,
        text="🟡 Лишние (есть в e-SEN, нет в HR) → Excel",
        width=380,
        height=38,
        fg_color="#ca8a04",
        hover_color="#a16207",
        command=export_only_esen_excel,
    ).pack(side="left")

    # ============================================================

    search_var = ctk.StringVar(value="")
    filter_var = ctk.StringVar(value="all")
    department_var = ctk.StringVar(value=tr("all_departments"))

    departments = sorted(
        set(
            str(emp.get("department", "")).strip()
            for emp in esen
            if str(emp.get("department", "")).strip()
        )
    )

    search_entry = ctk.CTkEntry(
        parent,
        textvariable=search_var,
        placeholder_text=f"🔍 {tr('search')}",
        height=38,
    )
    search_entry.pack(fill="x", padx=20, pady=(10, 5))

    department_menu = ctk.CTkOptionMenu(
        parent,
        variable=department_var,
        values=[tr("all_departments")] + departments,
        width=300,
        height=38,
        command=lambda value: render_table(),
    )
    department_menu.pack(fill="x", padx=20, pady=(5, 10))

    filter_frame = ctk.CTkFrame(parent, corner_radius=14)
    filter_frame.pack(fill="x", padx=20, pady=(5, 10))

    filters = [
        ("👥 " + tr("all"), "all"),
        ("🟢 " + tr("valid"), "valid"),
        ("🟡 " + tr("expiring"), "expiring"),
        ("🔴 " + tr("expired"), "expired"),
        ("⚪ " + tr("unknown"), "unknown"),
    ]

    def set_filter(value):
        filter_var.set(value)
        render_table()

    for text, value in filters:
        ctk.CTkButton(
            filter_frame,
            text=text,
            width=160,
            height=36,
            command=lambda v=value: set_filter(v),
        ).pack(side="left", padx=6, pady=8)

    # ДОБАВЛЕНА ГОРИЗОНТАЛЬНАЯ ПРОКРУТКА ДЛЯ ТАБЛИЦЫ
    table_scroll = ctk.CTkScrollableFrame(
        parent, 
        corner_radius=14, 
        orientation="horizontal",  # Горизонтальная прокрутка
        scrollbar_button_color="#0d3d4b",
        scrollbar_button_hover_color="#155e75",
    )
    table_scroll.pack(fill="both", expand=True, padx=20, pady=15)

    # Внутренний контейнер для таблицы (фиксированная минимальная ширина)
    table = ctk.CTkFrame(table_scroll, fg_color="transparent")
    table.pack(fill="both", expand=True)
    table.configure(width=1400)  # Минимальная ширина таблицы

    headers = [
        tr("fio"),
        tr("department"),
        tr("position"),
        tr("medical_book"),
        tr("period"),
        tr("days_left"),
        tr("status"),
    ]
    
    # Фиксированные ширины колонок, чтобы текст не обрезался
    col_widths = [300, 220, 250, 150, 120, 100, 150]

    def clear_table():
        for widget in table.winfo_children():
            widget.destroy()

    def render_table():
        clear_table()

        for col, (header, width) in enumerate(zip(headers, col_widths)):
            ctk.CTkLabel(
                table,
                text=header,
                font=("Arial", 15, "bold"),
                width=width,
                anchor="w"
            ).grid(row=0, column=col, padx=12, pady=8, sticky="w")

        search = search_var.get().lower().strip()
        selected_filter = filter_var.get()
        selected_department = department_var.get()

        row = 1

        for emp in esen:
            status_key, days_left, color = get_medical_status(emp)
            emp_department = str(emp.get("department", "")).strip()

            if (
                selected_department != tr("all_departments")
                and emp_department != selected_department
            ):
                continue

            search_text = (
                str(emp.get("fio", ""))
                + " "
                + emp_department
                + " "
                + str(emp.get("position", ""))
                + " "
                + str(emp.get("medical_book", ""))
                + " "
                + str(emp.get("status", ""))
            ).lower()

            if search and search not in search_text:
                continue

            if selected_filter != "all" and status_key != selected_filter:
                continue

            status_text = tr(status_key)

            values = [
                emp.get("fio", "-"),
                emp_department if emp_department else tr("unknown"),
                emp.get("position", "-"),
                emp.get("medical_book", "-"),
                emp.get("valid_until", "-"),
                days_left,
                status_text,
            ]

            for col, (value, width) in enumerate(zip(values, col_widths)):
                if col == 0:
                    fio_frame = ctk.CTkFrame(table, fg_color="transparent")
                    fio_frame.grid(
                        row=row,
                        column=col,
                        padx=10,
                        pady=5,
                        sticky="w",
                    )
                    ctk.CTkButton(
                        fio_frame,
                        text=str(value),
                        width=250,  # Фиксированная ширина для кнопки с ФИО
                        anchor="w",
                    ).pack(side="left")

                    if status_key in ("expiring", "expired"):
                        ctk.CTkButton(
                            fio_frame,
                            text="📲",
                            width=42,
                            height=32,
                            fg_color="#16a34a",
                            hover_color="#15803d",
                            command=lambda e=emp: open_whatsapp_window(e),
                        ).pack(side="left", padx=(6, 0))
                else:
                    ctk.CTkLabel(
                        table,
                        text=str(value),
                        font=("Arial", 14),
                        width=width,
                        anchor="w",
                        text_color=color if col == 6 else None,
                    ).grid(
                        row=row,
                        column=col,
                        padx=10,
                        pady=5,
                        sticky="w",
                    )

            row += 1

        if row == 1:
            ctk.CTkLabel(
                table,
                text=tr("nothing_found"),
                font=("Arial", 16),
            ).grid(row=1, column=0, padx=12, pady=20, sticky="w")

    search_var.trace_add("write", lambda *args: render_table())
    filter_var.trace_add("write", lambda *args: render_table())
    department_var.trace_add("write", lambda *args: render_table())
    
    render_table()
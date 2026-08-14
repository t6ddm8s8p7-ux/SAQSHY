import json
import os
from datetime import date, datetime
from pathlib import Path

import customtkinter as ctk
import pandas as pd
from tkinter import messagebox

from modules.export_reports import export_missing_to_excel
from modules.email_sender import send_email_notification
from modules.letter_generator import (
    generate_medical_expiring_letter,
    generate_esen_missing_letter,
    generate_weekly_report_letter,
)
# 🆕 ИМПОРТ БЫСТРОЙ ОТПРАВКИ
from modules.mail_tools import (
    open_daily_email,
    send_medical_departments_email,
    send_haccp_email,
    send_inspections_email,
)

DATABASE_DIR = Path("database")
EXPORTS_DIR = Path("exports") / "reports"


def _load_json(path, default):
    try:
        if Path(path).exists():
            with open(path, "r", encoding="utf-8-sig") as f:
                return json.load(f)
    except Exception:
        pass
    return default


def _parse_expiry(valid_until):
    text = str(valid_until or "").strip()
    if " - " in text:
        text = text.split(" - ")[-1].strip()
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except Exception:
        return None


def load_sync_history():
    data = _load_json(DATABASE_DIR / "sync_history.json", [])
    return data if isinstance(data, list) else []


def load_esen():
    return _load_json(DATABASE_DIR / "esen_employees.json", [])


def load_hr():
    return _load_json(DATABASE_DIR / "hr_employees.json", [])


def load_compare():
    return _load_json(DATABASE_DIR / "compare_result.json", {})


def load_haccp_records():
    return _load_json(DATABASE_DIR / "haccp_temperature_records.json", [])


def get_expiring(esen, days=60):
    today = date.today()
    result = []
    for emp in esen:
        expiry = _parse_expiry(emp.get("valid_until", ""))
        if not expiry:
            continue
        delta = (expiry - today).days
        if delta < 0:
            status = "Просрочено"
        elif delta <= days:
            status = "Истекает"
        else:
            continue
        result.append({
            "fio": emp.get("fio", "-"),
            "department": emp.get("department", "") or "-",
            "medical_book": emp.get("medical_book", "-"),
            "valid_until": emp.get("valid_until", "-"),
            "days_left": delta,
            "status": status,
        })
    result.sort(key=lambda r: r["days_left"])
    return result


def _open_folder():
    try:
        os.startfile(str(EXPORTS_DIR))
    except Exception:
        messagebox.showinfo("SanEpi AI", f"Файлы лежат в папке:\n{EXPORTS_DIR}")


# ============================================================
# ЭКСПОРТЫ
# ============================================================
def export_expiring_excel():
    rows = get_expiring(load_esen(), days=60)
    if not rows:
        messagebox.showinfo("SanEpi AI", "Нет истекающих или просроченных медосмотров.")
        return
    df = pd.DataFrame(rows)
    df = df[["fio", "department", "medical_book", "valid_until", "days_left", "status"]]
    df.columns = ["ФИО", "Отдел", "Медкнижка", "Период действия", "Осталось дней", "Статус"]
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = EXPORTS_DIR / f"medosmotry_istekayushchie_{date.today()}.xlsx"
    df.to_excel(path, index=False)
    messagebox.showinfo("SanEpi AI", f"✅ Отчёт сохранён:\n{path}")
    _open_folder()


def export_haccp_excel():
    records = load_haccp_records()
    if not records:
        messagebox.showinfo("SanEpi AI", "Журнал HACCP пока пуст.")
        return
    df = pd.DataFrame(records)
    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = EXPORTS_DIR / f"haccp_journal_{date.today()}.xlsx"
    df.to_excel(path, index=False)
    messagebox.showinfo("SanEpi AI", f"✅ Журнал HACCP сохранён:\n{path}")
    _open_folder()


def export_summary_report():
    hr = load_hr()
    esen = load_esen()
    compare = load_compare()
    history = load_sync_history()
    expiring = get_expiring(esen, 30)
    overdue = [r for r in expiring if r["days_left"] < 0]

    matched = len(compare.get("matched", []))
    only_hr = len(compare.get("only_hr", []))
    only_esen = len(compare.get("only_esen", []))

    lines = [
        "=" * 70,
        "СВОДНЫЙ ОТЧЁТ SANEPI AI",
        f"Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
        "=" * 70,
        "",
        "1. СВЕРКА HR ↔ e-SEN",
        f"   Всего HR:            {len(hr)}",
        f"   Всего e-SEN:         {len(esen)}",
        f"   Совпали:             {matched}",
        f"   Нет в e-SEN:         {only_hr}",
        f"   Нет в HR:            {only_esen}",
        "",
        "2. МЕДИЦИНСКИЕ ОСМОТРЫ",
        f"   Истекают в 30 дней:  {len([r for r in expiring if r['days_left'] >= 0])}",
        f"   Просрочено:          {len(overdue)}",
        "",
    ]
    if expiring:
        lines.append("   Список истекающих/просроченных:")
        for r in expiring[:30]:
            lines.append(
                f"   • {r['fio']} — {r['department']} — "
                f"до {r['valid_until']} ({r['days_left']} дн.) [{r['status']}]"
            )
        lines.append("")

    lines += ["3. ДИНАМИКА СВЕРОК (последние 10)", ""]
    for h in history[-10:]:
        lines.append(
            f"   {h.get('synced_at', '-')[:16]} | HR: {h.get('total_hr', '-')} | "
            f"e-SEN: {h.get('total_esen', '-')} | совпали: {h.get('matched', '-')} | "
            f"нет в e-SEN: {h.get('only_hr', '-')}"
        )

    lines += [
        "",
        "=" * 70,
        "Отчёт сформирован автоматически: SanEpi AI",
        "=" * 70,
    ]

    EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = EXPORTS_DIR / f"svodny_otchet_{date.today()}.txt"
    path.write_text("\n".join(lines), encoding="utf-8")
    messagebox.showinfo("SanEpi AI", f"✅ Сводный отчёт сохранён:\n{path}")
    try:
        os.startfile(str(path))
    except Exception:
        _open_folder()


def send_weekly_report_email():
    """Отправляет сводный отчёт руководству по email."""
    hr = load_hr()
    esen = load_esen()
    compare = load_compare()
    haccp_records = load_haccp_records()

    expiring = get_expiring(esen, 30)
    expired = [r for r in expiring if r["days_left"] < 0]

    matched = len(compare.get("matched", []))
    only_hr = len(compare.get("only_hr", []))
    total_hr = len(hr)
    match_percent = round(matched / total_hr * 100, 1) if total_hr else 0

    report_data = {
        "total_hr": total_hr,
        "matched": matched,
        "only_hr": only_hr,
        "match_percent": match_percent,
        "expiring_30": len([r for r in expiring if r["days_left"] >= 0]),
        "expired": len(expired),
        "haccp_records": len(haccp_records),
        "missed_checks": 0,
    }

    subject, body = generate_weekly_report_letter(report_data)
    if subject:
        send_email_notification(subject, body)
        messagebox.showinfo(
            "SanEpi AI",
            f"✅ Еженедельный отчёт сформирован!\n"
            f"Тема: {subject}\n"
            f"Получатель: Dauren.OSPAN@rixos.com\n\n"
            f"Проверьте текст и нажмите 'Отправить' в почтовом клиенте."
        )


def send_esen_missing_email():
    """Отправляет письмо о сотрудниках без регистрации в e-SEN."""
    compare = load_compare()
    only_hr = compare.get("only_hr", [])

    if not only_hr:
        messagebox.showinfo("SanEpi AI", "Все сотрудники HR зарегистрированы в e-SEN.")
        return

    subject, body = generate_esen_missing_letter(only_hr)
    if subject:
        send_email_notification(subject, body)
        messagebox.showinfo(
            "SanEpi AI",
            f"✅ Письмо сформировано!\n"
            f"Тема: {subject}\n"
            f"Сотрудников без регистрации: {len(only_hr)}",
        )


# ============================================================
# СТРАНИЦА (теперь с прокруткой!)
# ============================================================
def make_card(parent, title, value, color):
    card = ctk.CTkFrame(parent, corner_radius=14)
    ctk.CTkLabel(
        card, text=title, font=("Arial", 13, "bold"), text_color=color
    ).pack(pady=(10, 4))
    ctk.CTkLabel(card, text=str(value), font=("Arial", 22, "bold")).pack(pady=(0, 10))
    return card


def build_reports_page(parent):
    # 🆕 Вся страница внутри прокручиваемого контейнера
    scroll = ctk.CTkScrollableFrame(parent, corner_radius=0, fg_color="transparent")
    scroll.pack(fill="both", expand=True)

    ctk.CTkLabel(
        scroll, text="📊 Отчёты", font=("Arial", 34, "bold")
    ).pack(pady=(20, 10))

    hr = load_hr()
    esen = load_esen()
    compare = load_compare()
    history = load_sync_history()
    expiring = get_expiring(esen, 30)

    last_sync = history[-1].get("synced_at", "-")[:16] if history else "—"

    cards_frame = ctk.CTkFrame(scroll, corner_radius=14)
    cards_frame.pack(fill="x", padx=20, pady=10)
    cards = [
        ("👥 Всего HR", len(hr), "#60a5fa"),
        ("🏥 Всего e-SEN", len(esen), "#38bdf8"),
        ("🟢 Совпали", len(compare.get("matched", [])), "#22c55e"),
        ("🔴 Нет в e-SEN", len(compare.get("only_hr", [])), "#ef4444"),
        ("⏰ Истекают 30 дн", len(expiring), "#f59e0b"),
    ]
    for i, (title, value, color) in enumerate(cards):
        card = make_card(cards_frame, title, value, color)
        card.grid(row=0, column=i, padx=8, pady=8, sticky="nsew")
        cards_frame.grid_columnconfigure(i, weight=1)

    ctk.CTkLabel(
        scroll,
        text=f"🕒 Последняя сверка: {last_sync}",
        font=("Arial", 13),
        text_color="#9ca3af",
    ).pack(pady=(0, 8))

    # ---------- Динамика сверок ----------
    ctk.CTkLabel(
        scroll, text="📈 Динамика сверок HR ↔ e-SEN", font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=24, pady=(8, 4))

    history_frame = ctk.CTkFrame(scroll, corner_radius=14)
    history_frame.pack(fill="x", padx=20, pady=(0, 10))

    headers = ["Дата сверки", "HR", "e-SEN", "Совпали", "Нет в e-SEN", "% совпадения"]
    for col, h in enumerate(headers):
        ctk.CTkLabel(
            history_frame, text=h, font=("Arial", 13, "bold")
        ).grid(row=0, column=col, padx=10, pady=6, sticky="w")

    if not history:
        ctk.CTkLabel(
            history_frame,
            text="Сверок пока не было. Выполните «⚖️ Сравнить с e-SEN» на странице HR.",
            font=("Arial", 13),
        ).grid(row=1, column=0, columnspan=6, pady=15)
    else:
        for row, h in enumerate(history[-10:], start=1):
            total_hr = h.get("total_hr", 0) or 0
            matched = h.get("matched", 0) or 0
            percent = round(matched / total_hr * 100, 1) if total_hr else 0
            values = [
                str(h.get("synced_at", "-"))[:16],
                total_hr,
                h.get("total_esen", "-"),
                matched,
                h.get("only_hr", "-"),
                f"{percent}%",
            ]
            for col, v in enumerate(values):
                ctk.CTkLabel(
                    history_frame,
                    text=str(v),
                    font=("Arial", 13),
                    text_color="#22c55e" if col == 5 and percent >= 80 else None,
                ).grid(row=row, column=col, padx=10, pady=4, sticky="w")

    # ---------- Истекающие медосмотры ----------
    ctk.CTkLabel(
        scroll, text="⏰ Истекающие медосмотры (30 дней)", font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=24, pady=(8, 4))

    exp_frame = ctk.CTkFrame(scroll, corner_radius=14)
    exp_frame.pack(fill="x", padx=20, pady=(0, 10))

    if not expiring:
        ctk.CTkLabel(
            exp_frame, text="✅ В ближайшие 30 дней истечений нет.", font=("Arial", 13)
        ).pack(pady=15)
    else:
        for r in expiring:
            color = "#ef4444" if r["days_left"] < 0 else "#f59e0b"
            ctk.CTkLabel(
                exp_frame,
                text=(
                    f"{r['fio']}  |  {r['department']}  |  "
                    f"до {r['valid_until']}  |  {r['days_left']} дн.  |  {r['status']}"
                ),
                font=("Arial", 13),
                text_color=color,
            ).pack(anchor="w", padx=12, pady=3)

    # ---------- Кнопки экспорта ----------
    ctk.CTkLabel(
        scroll, text="📥 Экспорт в файлы", font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=24, pady=(8, 4))

    export_frame = ctk.CTkFrame(scroll, fg_color="transparent")
    export_frame.pack(fill="x", padx=20, pady=(0, 10))

    ctk.CTkButton(
        export_frame,
        text="📄 Истекающие медосмотры (Excel)",
        height=40,
        fg_color="#f59e0b",
        hover_color="#d97706",
        command=export_expiring_excel,
    ).pack(side="left", fill="x", expand=True, padx=4)

    ctk.CTkButton(
        export_frame,
        text="📄 Нет в e-SEN (Excel)",
        height=40,
        fg_color="#ef4444",
        hover_color="#dc2626",
        command=export_missing_to_excel,
    ).pack(side="left", fill="x", expand=True, padx=4)

    ctk.CTkButton(
        export_frame,
        text="📄 Журнал HACCP (Excel)",
        height=40,
        fg_color="#38bdf8",
        hover_color="#0284c7",
        command=export_haccp_excel,
    ).pack(side="left", fill="x", expand=True, padx=4)

    ctk.CTkButton(
        export_frame,
        text="📝 Сводный отчёт (TXT)",
        height=40,
        fg_color="#7c3aed",
        hover_color="#6d28d9",
        command=export_summary_report,
    ).pack(side="left", fill="x", expand=True, padx=4)

    # ---------- Кнопки отправки писем руководству ----------
    ctk.CTkLabel(
        scroll, text="📧 Отправка писем руководству", font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=24, pady=(14, 4))

    email_frame = ctk.CTkFrame(scroll, fg_color="transparent")
    email_frame.pack(fill="x", padx=20, pady=(0, 20))

    ctk.CTkButton(
        email_frame,
        text="📧 Отправить сводку руководству",
        height=42,
        fg_color="#059669",
        hover_color="#047857",
        command=send_weekly_report_email,
    ).pack(side="left", fill="x", expand=True, padx=4)

    ctk.CTkButton(
        email_frame,
        text="📧 Письмо о сотрудниках без e-SEN",
        height=42,
        fg_color="#dc2626",
        hover_color="#b91c1c",
        command=send_esen_missing_email,
    ).pack(side="left", fill="x", expand=True, padx=4)

    # ---------- 🆕 БЫСТРАЯ ОТПРАВКА ПИСЕМ (GMAIL WEB) ----------
    ctk.CTkLabel(
        scroll, text="🚀 Быстрая отправка (Gmail)", font=("Arial", 20, "bold")
    ).pack(anchor="w", padx=24, pady=(14, 4))

    quick_email_frame = ctk.CTkFrame(scroll, fg_color="transparent")
    quick_email_frame.pack(fill="x", padx=20, pady=(0, 20))

    ctk.CTkButton(
        quick_email_frame,
        text="📝 Ежедневное",
        height=42,
        fg_color="#6b7280",
        hover_color="#4b5563",
        command=open_daily_email,
    ).pack(side="left", fill="x", expand=True, padx=4)

    ctk.CTkButton(
        quick_email_frame,
        text="🏥 Медосмотры (отделы)",
        height=42,
        fg_color="#db2777",
        hover_color="#be185d",
        command=send_medical_departments_email,
    ).pack(side="left", fill="x", expand=True, padx=4)

    ctk.CTkButton(
        quick_email_frame,
        text="🌡️ HACCP",
        height=42,
        fg_color="#0d9488",
        hover_color="#0f766e",
        command=send_haccp_email,
    ).pack(side="left", fill="x", expand=True, padx=4)

    ctk.CTkButton(
        quick_email_frame,
        text="🔍 Проверки (30 дн)",
        height=42,
        fg_color="#2563eb",
        hover_color="#1d4ed8",
        command=send_inspections_email,
    ).pack(side="left", fill="x", expand=True, padx=4)
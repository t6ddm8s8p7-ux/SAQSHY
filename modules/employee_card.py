import customtkinter as ctk
from datetime import datetime, date

from modules.dashboard_data import load_dashboard_data
from modules.translations import tr
from modules.localization import translate_department
from modules.ai_expert import show_ai_expert


def normalize_name(name):
    text = str(name).strip().upper()
    text = text.replace("Ё", "Е")
    text = text.replace("Ә", "А").replace("І", "И").replace("Ң", "Н")
    text = text.replace("Ғ", "Г").replace("Ү", "У").replace("Ұ", "У")
    text = text.replace("Қ", "К").replace("Ө", "О").replace("Һ", "Х")
    return " ".join(text.split())


def parse_valid_until(valid_until):
    text = str(valid_until).strip()

    if " - " in text:
        text = text.split(" - ")[-1].strip()

    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except Exception:
        return None


def find_esen_employee(hr_emp):
    data = load_dashboard_data()
    esen = data["esen"]

    hr_name = normalize_name(hr_emp.get("Сотрудник", hr_emp.get("fio", "")))

    for emp in esen:
        esen_name = normalize_name(emp.get("fio", ""))

        if hr_name and hr_name == esen_name:
            return emp

    return None


def build_ai_text(hr_emp, esen_emp):
    lines = []

    if not hr_emp:
        lines.append(f"🔴 {tr('not_in_hr')}.")
        lines.append("⚠️ Возможно, сотрудник уволен или отсутствует в новой HR таблице.")
        lines.append("Рекомендация: проверить с HR и при необходимости удалить из e-SEN.")
        return "\n".join(lines)

    lines.append(f"🟢 HR: {tr('exists_in_hr')}.")

    if not esen_emp:
        lines.append(f"🔴 e-SEN: {tr('not_in_esen')}.")
        lines.append("Рекомендация: добавить сотрудника в e-SEN.")
        return "\n".join(lines)

    lines.append(f"🟢 e-SEN: {tr('exists_in_esen')}.")

    status = str(esen_emp.get("status", "")).lower()
    valid_until = esen_emp.get("valid_until", "")
    expiry = parse_valid_until(valid_until)

    if "қабылданды" in status or "принят" in status or "допущ" in status:
        lines.append(f"🟢 {tr('status')}: {tr('admitted')}.")
    else:
        lines.append(f"🔴 {tr('status')}: {tr('not_admitted')}.")

    if expiry:
        days_left = (expiry - date.today()).days

        if days_left < 0:
            lines.append(f"🔴 {tr('expired')}: {abs(days_left)} күн.")
            lines.append("Рекомендация: сотрудника нельзя допускать до обновления медкнижки.")
        elif days_left <= 30:
            lines.append(f"🟡 {tr('expiring')}. {tr('days_left')}: {days_left}.")
            lines.append("Рекомендация: заранее организовать продление.")
        else:
            lines.append(f"🟢 {tr('days_left')}: {days_left}.")
            lines.append(f"☑️ {tr('no_action_required')}.")
    else:
        lines.append("⚠️ Срок действия медкнижки не определён.")

    return "\n".join(lines)


def show_employee_card(emp):
    esen_emp = find_esen_employee(emp)

    window = ctk.CTkToplevel()
    window.title(tr("employee_card"))
    window.geometry("950x700")
    window.lift()
    window.focus_force()

    ctk.CTkLabel(
        window,
        text=f"👤 {tr('employee_card')}",
        font=("Arial", 30, "bold")
    ).pack(pady=20)

    main = ctk.CTkFrame(window)
    main.pack(fill="both", expand=True, padx=20, pady=10)

    left = ctk.CTkFrame(main)
    left.pack(side="left", fill="both", expand=True, padx=(0, 10))

    right = ctk.CTkFrame(main, width=260)
    right.pack(side="right", fill="y")

    if esen_emp:
        medical_book = esen_emp.get("medical_book", "-")
        status = esen_emp.get("status", "-")
        valid_until = esen_emp.get("valid_until", "-")
        position = esen_emp.get("position", emp.get("Должность", "-"))
        esen_status = f"🟢 {tr('exists_in_esen')}"
    else:
        medical_book = "-"
        status = tr("not_in_esen")
        valid_until = "-"
        position = emp.get("Должность", "-")
        esen_status = f"🔴 {tr('not_in_esen')}"

    department = emp.get("Отдел", "-")

    fields = [
        (tr("fio"), emp.get("Сотрудник", emp.get("fio", "-"))),
        (tr("department"), translate_department(department)),
        (tr("position"), position),
        ("HR", f"🟢 {tr('exists_in_hr')}"),
        ("e-SEN", esen_status),
        (tr("medical_book"), medical_book),
        (tr("status"), status),
        (tr("period"), valid_until),
    ]

    for title, value in fields:
        row = ctk.CTkFrame(left, corner_radius=10)
        row.pack(fill="x", pady=5)

        ctk.CTkLabel(
            row,
            text=title,
            width=180,
            anchor="w",
            font=("Arial", 15, "bold")
        ).pack(side="left", padx=12, pady=10)

        ctk.CTkLabel(
            row,
            text=str(value),
            anchor="w",
            font=("Arial", 15)
        ).pack(side="left", padx=8)

    ctk.CTkLabel(
        right,
        text=tr("condition"),
        font=("Arial", 20, "bold")
    ).pack(pady=(25, 15))

    expiry = parse_valid_until(valid_until)

    if not esen_emp:
        color = "#dc2626"
        condition_text = f"🔴 {tr('not_in_esen')}"
    elif expiry and (expiry - date.today()).days < 0:
        color = "#dc2626"
        condition_text = f"🔴 {tr('expired')}"
    elif expiry and (expiry - date.today()).days <= 30:
        color = "#f59e0b"
        condition_text = f"🟡 {tr('expiring')}"
    else:
        color = "#22c55e"
        condition_text = f"🟢 {tr('admitted')}"

    ctk.CTkButton(
        right,
        text=condition_text,
        fg_color=color,
        width=210,
        height=45
    ).pack(pady=10)

    analysis_box = ctk.CTkTextbox(
        right,
        width=230,
        height=350,
        font=("Arial", 13)
    )
    analysis_box.pack(pady=20)

    analysis_box.insert("end", build_ai_text(emp, esen_emp))
    analysis_box.configure(state="disabled")

    ctk.CTkButton(
        right,
        text=f"🤖 {tr('ai_analysis')}",
        width=210,
        command=lambda: show_ai_expert(
            emp,
            esen_emp,
            build_ai_text(emp, esen_emp),
            tr
        )
    ).pack(pady=10)
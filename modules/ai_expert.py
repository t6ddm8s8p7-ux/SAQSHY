import customtkinter as ctk
from datetime import datetime, date

from modules.translations import tr
from modules.localization import translate_department


def parse_valid_until(valid_until):
    text = str(valid_until).strip()

    if " - " in text:
        text = text.split(" - ")[-1].strip()

    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except Exception:
        return None


def build_expert_report(emp, esen_emp):
    name = emp.get("Сотрудник", emp.get("fio", "-"))
    department = translate_department(emp.get("Отдел", "-"))
    position = emp.get("Должность", "-")

    if esen_emp:
        status = str(esen_emp.get("status", "-"))
        valid_until = esen_emp.get("valid_until", "-")
        medical_book = esen_emp.get("medical_book", "-")
        expiry = parse_valid_until(valid_until)
    else:
        status = tr("not_in_esen")
        valid_until = "-"
        medical_book = "-"
        expiry = None

    if not esen_emp:
        risk_icon = "🔴"
        risk_level = tr("high")
        conclusion = (
            f"{tr('not_in_esen')}\n"
            f"{tr('register_in_esen')}"
        )
        med_status = tr("not_in_esen")
        days_text = "-"
    elif expiry:
        days_left = (expiry - date.today()).days

        if days_left < 0:
            risk_icon = "🔴"
            risk_level = tr("high")
            med_status = tr("expired")
            days_text = f"{abs(days_left)}"
            conclusion = (
                f"{tr('medical_book_expired')}\n"
                f"{tr('employee_not_allowed')}"
            )
        elif days_left <= 30:
            risk_icon = "🟡"
            risk_level = tr("medium")
            med_status = tr("expiring")
            days_text = str(days_left)
            
            conclusion = (
                f"{tr('medical_book_expiring')}\n"
                f"{tr('organize_med_exam_before_expiry')}\n"
                f"{tr('avoid_gap_between_medbooks')}"
            )
        else:
            risk_icon = "🟢"
            risk_level = tr("low")
            med_status = tr("admitted")
            days_text = str(days_left)
            conclusion = (
                f"{tr('no_violations_found')}\n"
                f"{tr('employee_can_work')}"
            )
    else:
        risk_icon = "🟡"
        risk_level = tr("medium")
        med_status = tr("unknown")
        days_text = "-"
        conclusion = (
            f"{tr('medical_book_unknown')}\n"
            f"{tr('check_employee_data')}"
        )

    report = f"""
══════════════════════════════════════

👤 {tr('employee_card')}

{tr('fio')}: {name}
{tr('department')}: {department}
{tr('position')}: {position}

══════════════════════════════════════

✅ {tr("check").upper()}

🟢 HR: {tr('exists_in_hr')}
{"🟢" if esen_emp else "🔴"} e-SEN: {tr('exists_in_esen') if esen_emp else tr('not_in_esen')}

{tr('medical_book')}: {medical_book}
{tr('status')}: {status}
{tr('period')}: {valid_until}

📅 {tr('days_left')}: {days_text}

══════════════════════════════════════

⚠️ {tr('risk_level')}

{risk_icon} {risk_level}

══════════════════════════════════════

🤖 SanEpi AI Expert

{conclusion}

══════════════════════════════════════
"""
    return report


def show_ai_expert(emp, esen_emp, analysis_text, tr_func):
    window = ctk.CTkToplevel()
    window.title("SanEpi AI Expert")
    window.geometry("850x700")

    window.lift()
    window.focus_force()

    ctk.CTkLabel(
        window,
        text="🤖 SanEpi AI Expert",
        font=("Arial", 30, "bold")
    ).pack(pady=20)

    textbox = ctk.CTkTextbox(
        window,
        width=780,
        height=540,
        font=("Arial", 15)
    )
    textbox.pack(padx=20, pady=10, fill="both", expand=True)

    textbox.insert("end", build_expert_report(emp, esen_emp))
    textbox.configure(state="disabled")

    ctk.CTkButton(
        window,
        text="OK",
        width=180,
        command=window.destroy
    ).pack(pady=15)
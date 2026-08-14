import json
import os
import ctypes
import subprocess
import webbrowser
import urllib.parse
from datetime import datetime, timedelta
from tkinter import messagebox

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_DIR = os.path.join(BASE_DIR, "database")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports", "reports")

DEFAULT_TO = "Dauren.OSPAN@rixos.com"
SIGNATURE = "С уважением,\nДәурен Оспан"


def _load(path, default):
    try:
        with open(os.path.join(DB_DIR, path), "r", encoding="utf-8-sig") as f:
            return json.load(f)
    except Exception:
        return default


def _copy_text_to_clipboard(text):
    try:
        CF_UNICODETEXT = 13
        GMEM_MOVEABLE = 0x0002
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        user32.OpenClipboard(0)
        user32.EmptyClipboard()
        data = text.encode("utf-16-le") + b"\x00\x00"
        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        pointer = kernel32.GlobalLock(handle)
        ctypes.memmove(pointer, data, len(data))
        kernel32.GlobalUnlock(handle)
        user32.SetClipboardData(CF_UNICODETEXT, handle)
        user32.CloseClipboard()
        return True
    except Exception:
        return False


def _copy_file_to_clipboard(path):
    """Копирует ФАЙЛ в буфер обмена Windows: Ctrl+V в Gmail прикрепит его."""
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", f'Set-Clipboard -Path "{path}"'],
            check=True, timeout=15,
        )
        return True
    except Exception:
        return False


def _open_gmail(subject, body, to=DEFAULT_TO):
    full_body = f"{body}\n\n{SIGNATURE}"
    head = (
        "https://mail.google.com/mail/?view=cm&fs=1"
        f"&to={urllib.parse.quote(to)}&su={urllib.parse.quote(subject)}"
    )
    url = f"{head}&body={urllib.parse.quote(full_body)}"
    note = ""
    if len(url) > 1800:
        if _copy_text_to_clipboard(full_body):
            short = ("Полный текст отчёта скопирован в буфер обмена.\n"
                     "Нажмите Ctrl+V, чтобы вставить его в это поле.")
            url = f"{head}&body={urllib.parse.quote(short)}"
            note = "📋 Текст скопирован в буфер обмена — в Gmail нажмите Ctrl+V."
        else:
            url = f"{head}&body={urllib.parse.quote(full_body[:1700] + chr(10) + '… (полный список — в SanEpi AI)')}"
    try:
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe"),
        ]
        chrome = next((p for p in paths if os.path.exists(p)), None)
        if chrome:
            webbrowser.register("chrome", None, webbrowser.BackgroundBrowser(chrome))
            webbrowser.get("chrome").open(url)
        else:
            webbrowser.open(url)
    except Exception:
        webbrowser.open(url)
    if note:
        messagebox.showinfo("SanEpi AI", note)


def open_daily_email():
    """1. Пустое письмо с подписью."""
    _open_gmail("", "")


def send_medical_departments_email():
    """2. Медосмотры по отделам ТОЛЬКО по списку HR:
    сроки — из matched (отдел берётся из HR), «нет в e-SEN» — из only_hr.
    В письме — количества, в Excel — имена."""
    compare_res = _load("compare_result.json", {})
    if not isinstance(compare_res, dict):
        compare_res = {}

    departments = {}
    today = datetime.now().date()

    def add_emp(dept, status, row):
        departments.setdefault(dept, {"expired": [], "expires_30": [], "missing": []})[status].append(row)

    # --- HR + e-SEN (matched): отдел из HR, срок из e-SEN ---
    for m in (compare_res.get("matched", []) or []):
        if not isinstance(m, dict):
            continue
        hr_emp = m.get("hr") or {}
        esen_emp = m.get("esen") or {}
        dept = str(hr_emp.get("Отдел") or m.get("department") or "").strip() or "Без отдела"
        name = hr_emp.get("Сотрудник") or m.get("hr_name") or "Неизвестно"
        raw = str(esen_emp.get("valid_until") or "").strip()
        if " - " in raw:
            raw = raw.split(" - ")[-1].strip()
        try:
            exam = datetime.strptime(raw, "%Y-%m-%d").date()
        except Exception:
            continue
        delta = (exam - today).days
        if delta < 0:
            add_emp(dept, "expired", {"fio": name, "medical_book": esen_emp.get("medical_book", "-"),
                                      "valid_until": esen_emp.get("valid_until", "-"), "days": delta})
        elif delta <= 30:
            add_emp(dept, "expires_30", {"fio": name, "medical_book": esen_emp.get("medical_book", "-"),
                                         "valid_until": esen_emp.get("valid_until", "-"), "days": delta})

    # --- Только HR: нет в e-SEN ---
    for emp in (compare_res.get("only_hr", []) or []):
        if isinstance(emp, dict):
            dept = str(emp.get("Отдел") or "").strip() or "Без отдела"
            name = emp.get("Сотрудник") or "Неизвестно"
        else:
            dept, name = "Без отдела", str(emp)
        add_emp(dept, "missing", {"fio": name, "medical_book": "-", "valid_until": "-", "days": "-"})

    if not departments:
        _open_gmail("Медосмотры: сводка по отделам (SanEpi AI)",
                    "✅ Просроченных, истекающих и отсутствующих в e-SEN нет.")
        return

    # ---- EXCEL-ПРИЛОЖЕНИЕ С ИМЕНАМИ ----
    xlsx_path, excel_ok = "", False
    try:
        import pandas as pd
        os.makedirs(EXPORTS_DIR, exist_ok=True)
        xlsx_path = os.path.join(EXPORTS_DIR, f"medosmotry_po_otdelam_{today}.xlsx")
        summary_rows, name_rows = [], []
        for dept in sorted(departments):
            d = departments[dept]
            summary_rows.append({
                "Отдел": dept,
                "Просрочено": len(d["expired"]),
                "Истекает (30 дн)": len(d["expires_30"]),
                "Нет в e-SEN": len(d["missing"]),
                "Всего": len(d["expired"]) + len(d["expires_30"]) + len(d["missing"]),
            })
            for key, label in (("expired", "Просрочено"),
                               ("expires_30", "Истекает (30 дн)"),
                               ("missing", "Нет в e-SEN")):
                for r in d[key]:
                    name_rows.append({
                        "Отдел": dept, "ФИО": r["fio"], "Статус": label,
                        "Медкнижка": r["medical_book"], "Период действия": r["valid_until"],
                        "Осталось дней": r["days"],
                    })
        with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
            pd.DataFrame(summary_rows).to_excel(writer, sheet_name="Сводка", index=False)
            pd.DataFrame(name_rows).to_excel(writer, sheet_name="Сотрудники", index=False)
        excel_ok = True
    except Exception as e:
        messagebox.showwarning("SanEpi AI", f"Не удалось создать Excel-приложение:\n{e}")

    attached = _copy_file_to_clipboard(xlsx_path) if excel_ok else False

    # ---- ТЕЛО ПИСЬМА: ТОЛЬКО КОЛИЧЕСТВА ----
    t_exp = sum(len(d["expired"]) for d in departments.values())
    t_30 = sum(len(d["expires_30"]) for d in departments.values())
    t_miss = sum(len(d["missing"]) for d in departments.values())

    body = "Сводка по медицинским осмотрам сотрудников (по отделам, список HR).\n\n"
    body += (f"ВСЕГО: 🔴 просрочено — {t_exp}, 🟡 истекает (30 дн) — {t_30}, "
             f"⚪ нет в e-SEN — {t_miss}\n\n")
    for dept in sorted(departments):
        d = departments[dept]
        body += (f"📍 {dept}\n"
                 f"   🔴 Просрочено: {len(d['expired'])}\n"
                 f"   🟡 Истекает (30 дн): {len(d['expires_30'])}\n"
                 f"   ⚪ Нет в e-SEN: {len(d['missing'])}\n\n")
    body += "Приложение: Excel-файл с поимённым списком сотрудников.\n"
    if attached:
        body += "Файл скопирован — нажмите Ctrl+V в письме, чтобы прикрепить его."
    elif excel_ok:
        body += "Прикрепите файл вручную (перетащите в окно письма)."

    _open_gmail("Медосмотры: сводка по отделам (SanEpi AI)", body)

    if excel_ok:
        note = f"✅ Письмо с количествами открыто в Gmail.\n\n📎 Excel с именами:\n{xlsx_path}"
        if attached:
            note += "\n\nФайл в буфере обмена — в Gmail нажмите Ctrl+V, и он прикрепится."
        else:
            note += "\nПеретащите файл в окно Gmail вручную."
            try:
                os.startfile(EXPORTS_DIR)
            except Exception:
                pass
        messagebox.showinfo("SanEpi AI", note)


def send_haccp_email():
    """3. Температурные замеры HACCP."""
    records = _load("haccp_temperature_records.json", [])
    violations, total = [], 0
    for rec in (records if isinstance(records, list) else []):
        if not isinstance(rec, dict):
            continue
        total += 1
        if rec.get("status") == "Отклонение":
            loc = f"{rec.get('object_name', '')} / {rec.get('department_name', '')} / {rec.get('equipment_name', '')}"
            violations.append(
                f"- {rec.get('date', '-')} {rec.get('time', '')} | {loc}: "
                f"{rec.get('temperature')}°C (норма {rec.get('temperature_min')}…{rec.get('temperature_max')}°C)"
            )
    body = f"Всего замеров в журнале: {total}\n\n"
    if violations:
        body += "🚨 ОТКЛОНЕНИЯ ТЕМПЕРАТУРНОГО РЕЖИМА:\n" + "\n".join(violations) + "\n"
    else:
        body += "✅ Все замеры в пределах нормы.\n"
    _open_gmail("HACCP: температурный режим (SanEpi AI)", body)


def send_inspections_email():
    """4. Проверки объекта за последние 30 дней."""
    inspections = _load("inspections.json", [])
    start = (datetime.now() - timedelta(days=30)).date()
    recent = []
    for insp in (inspections if isinstance(inspections, list) else []):
        if not isinstance(insp, dict):
            continue
        try:
            d = datetime.strptime(str(insp.get("date", ""))[:10], "%Y-%m-%d").date()
        except Exception:
            continue
        if d >= start:
            line = (f"- {d} | {insp.get('object_name', '')} / {insp.get('department_name', '')} | "
                    f"{insp.get('result', '')}")
            if str(insp.get("violation", "")).strip():
                line += f"\n   Нарушение: {insp['violation']}"
            if str(insp.get("corrective_action", "")).strip():
                line += f"\n   Меры: {insp['corrective_action']} (срок: {insp.get('deadline', '-') or '-'})"
            recent.append(line)
    body = "Проверки объекта за последние 30 дней.\n\n"
    body += "\n".join(recent) + "\n" if recent else "Проверок за последние 30 дней не было.\n"
    _open_gmail("Проверки объекта за 30 дней (SanEpi AI)", body)
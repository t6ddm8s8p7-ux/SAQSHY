import json
from pathlib import Path
from datetime import datetime, date

ESEN_FILE = Path("database/esen_employees.json")


def load_esen():
    if not ESEN_FILE.exists():
        return []

    with open(ESEN_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    return data if isinstance(data, list) else []


def parse_valid_until(valid_until):
    """
    e-SEN формат может быть:
    2026-06-21 - 2026-09-30
    или просто 2026-09-30
    """

    if not valid_until:
        return None

    text = str(valid_until).strip()

    if " - " in text:
        text = text.split(" - ")[-1].strip()

    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except Exception:
        return None


def get_expiring_medbooks(days=30):
    today = date.today()
    employees = load_esen()

    result = []

    for emp in employees:
        expiry_date = parse_valid_until(emp.get("valid_until", ""))

        if not expiry_date:
            continue

        days_left = (expiry_date - today).days

        if days_left <= days:
            result.append({
                "fio": emp.get("fio", ""),
                "workplace": emp.get("workplace", ""),
                "position": emp.get("position", ""),
                "medical_book": emp.get("medical_book", ""),
                "group": emp.get("group", ""),
                "valid_until": emp.get("valid_until", ""),
                "expiry_date": str(expiry_date),
                "days_left": days_left,
                "status": "Просрочено" if days_left < 0 else "Истекает"
            })

    result.sort(key=lambda x: x["days_left"])
    return result
import json
import re
from datetime import datetime
from pathlib import Path

DATABASE_DIR = Path("database")
ESEN_FILE = DATABASE_DIR / "esen_employees.json"
QUALITY_FILE = DATABASE_DIR / "esen_quality_report.json"
FIXES_FILE = DATABASE_DIR / "esen_name_fixes.json"

PLACEHOLDER_NAMES = {
    "", "-", "МӘЛІМЕТ ЖОҚ", "МАЛИМЕТ ЖОК",
    "НЕТ ДАННЫХ", "НЕТ ИНФОРМАЦИИ", "NO NAME", "БЕЗ ФИО",
}

FIO_REPLACEMENTS = {
    "Ё": "Е", "Ә": "А", "І": "И", "Ң": "Н", "Ғ": "Г",
    "Ү": "У", "Ұ": "У", "Қ": "К", "Ө": "О", "Һ": "Х",
}

MEDBOOK_CYR_TO_LAT = {
    "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M",
    "Н": "H", "О": "O", "Р": "P", "С": "C", "Т": "T", "Х": "X",
}


def normalize_medbook(value):
    text = str(value or "").strip().upper()
    for cyr, lat in MEDBOOK_CYR_TO_LAT.items():
        text = text.replace(cyr, lat)
    return re.sub(r"[^A-Z0-9]", "", text)


def normalize_fio(value):
    text = str(value or "").strip().upper()
    for old, new in FIO_REPLACEMENTS.items():
        text = text.replace(old, new)
    return " ".join(text.split())


def is_placeholder_fio(fio):
    normalized = normalize_fio(fio)
    return not normalized or normalized in PLACEHOLDER_NAMES


def parse_expiry(valid_until):
    text = str(valid_until or "").strip()
    if " - " in text:
        text = text.split(" - ")[-1].strip()
    try:
        return datetime.strptime(text, "%Y-%m-%d")
    except Exception:
        return datetime.min


def load_raw():
    if not ESEN_FILE.exists():
        return []
    with open(ESEN_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def load_fixes():
    if not FIXES_FILE.exists():
        return {}
    try:
        with open(FIXES_FILE, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as e:
        print("Ошибка чтения esen_name_fixes.json:", e)
        return {}


def apply_name_fixes(raw, fixes):
    fixed_count = 0
    for emp in raw:
        med = normalize_medbook(emp.get("medical_book"))
        fix = fixes.get(med)
        if not fix:
            continue
        emp["fio"] = fix.get("fio", emp.get("fio", ""))
        if fix.get("department") and not str(emp.get("department", "")).strip():
            emp["department"] = fix["department"]
        emp["name_fixed"] = True
        fixed_count += 1
    return fixed_count


def run_esen_engine():
    raw = load_raw()
    fixes = load_fixes()
    fixed_count = apply_name_fixes(raw, fixes)

    groups = {}
    for emp in raw:
        fio = normalize_fio(emp.get("fio", ""))
        med = normalize_medbook(emp.get("medical_book"))
        if is_placeholder_fio(emp.get("fio", "")):
            # БЕЗ ФИО — НЕ склеиваем между собой!
            # Каждая такая запись — отдельный сотрудник.
            key = ("MED", med or f"ROW{emp.get('page_number')}-{emp.get('row_number')}")
        else:
            key = ("FIO", fio)
        groups.setdefault(key, []).append(emp)

    clean = []
    duplicates_list = []
    for key, records in groups.items():
        records.sort(
            key=lambda e: parse_expiry(e.get("valid_until")),
            reverse=True,
        )
        best = records[0]
        clean.append(best)
        if len(records) > 1:
            duplicates_list.append({
                "fio": best.get("fio", ""),
                "used_medbook": best.get("medical_book", ""),
                "used_valid_until": best.get("valid_until", ""),
                "old_records": records[1:],
            })

    bad_records_list = []
    for emp in clean:
        if is_placeholder_fio(emp.get("fio", "")):
            bad_records_list.append({
                "fio": emp.get("fio", ""),
                "medical_book": emp.get("medical_book", ""),
                "position": emp.get("position", ""),
                "valid_until": emp.get("valid_until", ""),
                "data_problem": (
                    "ФИО отсутствует в e-SEN. "
                    "Добавьте сотрудника в database/esen_name_fixes.json"
                ),
            })

    with open(ESEN_FILE, "w", encoding="utf-8") as f:
        json.dump(clean, f, ensure_ascii=False, indent=4)

    quality = {
        "total_raw": len(raw),
        "total_clean": len(clean),
        "bad_records": len(bad_records_list),
        "duplicates": len(duplicates_list),
        "bad_records_list": bad_records_list,
        "duplicates_list": duplicates_list,
    }
    with open(QUALITY_FILE, "w", encoding="utf-8") as f:
        json.dump(quality, f, ensure_ascii=False, indent=4)

    print("✅ ESEN Engine завершён")
    print(f"Исправлено имён по рем-файлу: {fixed_count}")
    print(f"Сырых строк: {len(raw)}")
    print(f"Чистых сотрудников: {len(clean)}")
    print(f"Технических дублей: {len(duplicates_list)}")
    print(f"Сотрудников без ФИО: {len(bad_records_list)}")
    return clean


if __name__ == "__main__":
    run_esen_engine()
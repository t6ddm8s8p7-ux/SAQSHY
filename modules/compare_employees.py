import json
import os
from datetime import datetime
from difflib import SequenceMatcher
from modules.export_reports import export_missing_separate_files_by_departments

HR_FILE = "database/hr_employees.json"
ESEN_FILE = "database/esen_employees.json"
RESULT_FILE = "database/compare_result.json"
HISTORY_FILE = "database/sync_history.json"


def load_json(path):
    if not os.path.exists(path):
        print(f"Файл не найден: {path}")
        return []

    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def append_sync_history(result):
    """Сохраняет историю сверок для отчётов и динамики."""
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8-sig") as f:
                history = json.load(f)
        except Exception:
            history = []
    if not isinstance(history, list):
        history = []

    history.append({
        "synced_at": result.get("synced_at", ""),
        "total_hr": result.get("total_hr", 0),
        "total_esen": result.get("total_esen", 0),
        "matched": len(result.get("matched", [])),
        "only_hr": len(result.get("only_hr", [])),
        "only_esen": len(result.get("only_esen", [])),
    })

    history = history[-100:]  # храним последние 100 сверок
    save_json(HISTORY_FILE, history)


def normalize_text(text):
    text = str(text).strip().upper()

    replacements = {
        "Ё": "Е", "Ә": "А", "І": "И", "Ң": "Н", "Ғ": "Г",
        "Ү": "У", "Ұ": "У", "Қ": "К", "Ө": "О", "Һ": "Х",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return " ".join(text.split())


def similarity(a, b):
    return SequenceMatcher(None, normalize_text(a), normalize_text(b)).ratio()


def split_name(full_name):
    parts = normalize_text(full_name).split()
    return (
        parts[0] if len(parts) > 0 else "",
        parts[1] if len(parts) > 1 else "",
        parts[2] if len(parts) > 2 else "",
    )


def get_hr_name(emp):
    return normalize_text(emp.get("Сотрудник", ""))


def get_esen_name(emp):
    return normalize_text(emp.get("fio", ""))


def is_good_match(hr_name, esen_name):
    hr_surname, hr_name_part, hr_patronymic = split_name(hr_name)
    es_surname, es_name_part, es_patronymic = split_name(esen_name)

    if not hr_surname or not es_surname:
        return False, 0

    surname_score = similarity(hr_surname, es_surname)
    name_score = similarity(hr_name_part, es_name_part)

    if surname_score < 0.95:
        return False, 0

    if name_score < 0.90:
        return False, 0

    if hr_patronymic and es_patronymic:
        patronymic_score = similarity(hr_patronymic, es_patronymic)
        total_score = (
            surname_score * 0.45
            + name_score * 0.35
            + patronymic_score * 0.20
        )
    else:
        total_score = surname_score * 0.60 + name_score * 0.40

    return total_score >= 0.95, total_score


def find_best_match(hr_name, esen_list, used_esen):
    best_emp = None
    best_score = 0

    for i, esen_emp in enumerate(esen_list):
        if i in used_esen:
            continue

        esen_name = get_esen_name(esen_emp)
        ok, score = is_good_match(hr_name, esen_name)

        if ok and score > best_score:
            best_score = score
            best_emp = (i, esen_emp)

    return best_emp, best_score


def enrich_esen_with_hr(esen_emp, hr_emp):
    esen_emp["department"] = hr_emp.get("Отдел", "")
    esen_emp["hr_position"] = hr_emp.get("Должность", "")
    esen_emp["hr_status"] = hr_emp.get("Состояние", "")
    esen_emp["hr_hire_date"] = hr_emp.get("Дата приема", "")
    esen_emp["hr_birth_date"] = hr_emp.get("Дата рождения", "")
    esen_emp["matched_with_hr"] = True
    return esen_emp


def compare_employees():
    hr = load_json(HR_FILE)
    esen = load_json(ESEN_FILE)

    matched = []
    only_hr = []
    used_esen = set()

    for hr_emp in hr:
        hr_name = get_hr_name(hr_emp)

        if not hr_name:
            continue

        best, score = find_best_match(hr_name, esen, used_esen)

        if best:
            index, esen_emp = best
            used_esen.add(index)

            esen[index] = enrich_esen_with_hr(esen_emp, hr_emp)

            matched.append({
                "hr_name": hr_name,
                "esen_name": get_esen_name(esen_emp),
                "similarity": round(score * 100, 1),
                "department": hr_emp.get("Отдел", ""),
                "hr_position": hr_emp.get("Должность", ""),
                "hr": hr_emp,
                "esen": esen[index],
            })
        else:
            only_hr.append(hr_emp)

    only_esen = []

    for i, esen_emp in enumerate(esen):
        if i not in used_esen:
            esen_emp["matched_with_hr"] = False
            only_esen.append(esen_emp)

    result = {
        "total_hr": len(hr),
        "total_esen": len(esen),
        "matched": matched,
        "possible_matches": [],
        "only_hr": only_hr,
        "only_esen": only_esen,
    }

    result["synced_at"] = datetime.now().isoformat(timespec="seconds")
    append_sync_history(result)

    save_json(ESEN_FILE, esen)
    save_json(RESULT_FILE, result)

    print("✅ Сверка завершена")
    print(f"HR Excel: {len(hr)}")
    print(f"e-SEN: {len(esen)}")
    print(f"Совпали: {len(matched)}")
    print("Проверить вручную: 0")
    print(f"Есть в HR, но нет в e-SEN: {len(only_hr)}")
    print(f"Есть в e-SEN, но нет в HR: {len(only_esen)}")

    export_missing_separate_files_by_departments()

    return result


def run_compare():
    return compare_employees()


def run():
    return compare_employees()
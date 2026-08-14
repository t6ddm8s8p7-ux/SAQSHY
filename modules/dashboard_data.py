import json
from pathlib import Path
from collections import Counter

from modules.medical_expiry import get_expiring_medbooks


HR_FILE = Path("database/hr_employees.json")
ESEN_FILE = Path("database/esen_employees.json")
COMPARE_FILE = Path("database/compare_result.json")
QUALITY_FILE = Path("database/esen_quality_report.json")

_CACHE = None


def clear_dashboard_cache():
    global _CACHE
    _CACHE = None


def load_json(file):
    if file.exists():
        with open(file, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return []


def get_department(emp):
    dep = emp.get("Отдел", "")
    if dep:
        return str(dep).strip().lower()
    return "не указан"


def department_stats(compare):
    stats = {}

    for item in compare.get("matched", []):
        dep = get_department(item.get("hr", {}))
        stats.setdefault(dep, {"matched": 0, "only_hr": 0})
        stats[dep]["matched"] += 1

    for emp in compare.get("only_hr", []):
        dep = get_department(emp)
        stats.setdefault(dep, {"matched": 0, "only_hr": 0})
        stats[dep]["only_hr"] += 1

    return stats


def load_dashboard_data(force_reload=False):
    global _CACHE

    if _CACHE is not None and not force_reload:
        return _CACHE

    hr = load_json(HR_FILE)
    esen = load_json(ESEN_FILE)
    compare = load_json(COMPARE_FILE)
    quality = load_json(QUALITY_FILE)

    if not isinstance(hr, list):
        hr = []
    if not isinstance(esen, list):
        esen = []
    if not isinstance(compare, dict):
        compare = {}
    if not isinstance(quality, dict):
        quality = {}

    matched = len(compare.get("matched", []))
    total_hr = len(hr)

    _CACHE = {
        "hr": hr,
        "esen": esen,
        "compare": compare,
        "quality": quality,
        "total_hr": total_hr,
        "total_esen": len(esen),
        "matched": matched,
        "only_hr": len(compare.get("only_hr", [])),
        "only_esen": len(compare.get("only_esen", [])),
        "duplicate_count": quality.get("duplicates", 0),
        "bad_count": quality.get("bad_records", 0),
        "expiring_count": len(get_expiring_medbooks(30)),
        "match_percent": round((matched / total_hr) * 100, 1) if total_hr else 0,
        "departments": Counter(get_department(emp) for emp in hr),
        "dep_compare": department_stats(compare),
    }

    return _CACHE
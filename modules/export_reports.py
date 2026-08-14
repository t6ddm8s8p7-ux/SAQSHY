import json
from pathlib import Path
import pandas as pd

COMPARE_FILE = Path("database/compare_result.json")
EXPORT_DIR = Path("exports")


def load_compare():
    if not COMPARE_FILE.exists():
        print("❌ compare_result.json не найден")
        return {}

    with open(COMPARE_FILE, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def export_missing_to_excel():
    compare = load_compare()
    missing = compare.get("only_hr", [])

    if not missing:
        print("✅ Отсутствующих в e-SEN нет")
        return None
def export_missing_separate_files_by_departments():
    compare = load_compare()
    missing = compare.get("only_hr", [])

    if not missing:
        print("✅ Отсутствующих в e-SEN нет")
        return []

    output_dir = EXPORT_DIR / "missing_by_departments"
    output_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    for emp in missing:
        rows.append({
            "Отдел": emp.get("Отдел", ""),
            "ФИО": emp.get("Сотрудник", ""),
            "Должность": emp.get("Должность", ""),
            "Дата приема": emp.get("Дата приема", ""),
            "Дата рождения": emp.get("Дата рождения", ""),
            "Состояние": emp.get("Состояние", ""),
            "Статус": "Нет в e-SEN"
        })

    df = pd.DataFrame(rows)

    files = []

    for department, dep_df in df.groupby("Отдел"):
        safe_name = str(department).strip()

        if not safe_name:
            safe_name = "Без отдела"

        for ch in ["\\", "/", "*", "?", ":", "[", "]"]:
            safe_name = safe_name.replace(ch, "-")

        output = output_dir / f"{safe_name}.xlsx"

        dep_df = dep_df.copy()
        dep_df.insert(0, "№", range(1, len(dep_df) + 1))

        dep_df.to_excel(output, index=False)

        files.append(output)

    print(f"✅ Создано Excel-файлов по отделам: {len(files)}")
    return files

    EXPORT_DIR.mkdir(exist_ok=True)

    rows = []
    for emp in missing:
        rows.append({
            "Отдел": emp.get("Отдел", ""),
            "ФИО": emp.get("Сотрудник", ""),
            "Должность": emp.get("Должность", ""),
            "Дата приема": emp.get("Дата приема", ""),
            "Дата рождения": emp.get("Дата рождения", ""),
            "Состояние": emp.get("Состояние", ""),
            "Статус": "Нет в e-SEN"
        })

    df = pd.DataFrame(rows)

    output = EXPORT_DIR / "missing_in_esen.xlsx"

    with pd.ExcelWriter(output, engine="openpyxl") as writer:

        # Общая сводка
        summary = (
            df.groupby("Отдел")
            .size()
            .reset_index(name="Количество")
            .sort_values("Количество", ascending=False)
        )

        summary.to_excel(writer, sheet_name="Сводка", index=False)

        # Каждый отдел — отдельный лист
        for department, dep_df in df.groupby("Отдел"):

            dep_df = dep_df.copy()
            dep_df.insert(0, "№", range(1, len(dep_df) + 1))

            sheet = str(department)[:31] if department else "Без отдела"

            dep_df.to_excel(
                writer,
                sheet_name=sheet,
                index=False
            )

    print(f"✅ Excel отчет создан: {output}")
    return output
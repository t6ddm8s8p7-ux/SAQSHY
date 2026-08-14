import json
import re
from pathlib import Path
import customtkinter as ctk
from tkinter import messagebox

DATABASE_DIR = Path("database")
ESEN_FILE = DATABASE_DIR / "esen_employees.json"
FIXES_FILE = DATABASE_DIR / "esen_name_fixes.json"

PLACEHOLDER_NAMES = {
    "", "-", "МӘЛІМЕТ ЖОҚ", "МАЛИМЕТ ЖОК",
    "НЕТ ДАННЫХ", "НЕТ ИНФОРМАЦИИ", "NO NAME", "БЕЗ ФИО",
}


def normalize_medbook(value):
    text = str(value or "").strip().upper()
    for cyr, lat in {
        "А": "A", "В": "B", "Е": "E", "К": "K", "М": "M",
        "Н": "H", "О": "O", "Р": "P", "С": "C", "Т": "T", "Х": "X",
    }.items():
        text = text.replace(cyr, lat)
    return re.sub(r"[^A-Z0-9]", "", text)


def is_placeholder_fio(fio):
    normalized = str(fio or "").strip().upper()
    return not normalized or normalized in PLACEHOLDER_NAMES


def load_esen():
    if not ESEN_FILE.exists():
        return []
    with open(ESEN_FILE, "r", encoding="utf-8-sig") as f:
        data = json.load(f)
    return data if isinstance(data, list) else []


def save_esen(data):
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    with open(ESEN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_fixes():
    if not FIXES_FILE.exists():
        return {}
    try:
        with open(FIXES_FILE, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_fixes(fixes):
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    with open(FIXES_FILE, "w", encoding="utf-8") as f:
        json.dump(fixes, f, ensure_ascii=False, indent=4)


def apply_name_fixes_to_esen_file():
    """Применяет сохранённые исправления к esen_employees.json."""
    fixes = load_fixes()
    if not fixes:
        return 0
    esen = load_esen()
    changed = 0
    for emp in esen:
        med = normalize_medbook(emp.get("medical_book"))
        fix = fixes.get(med)
        if not fix:
            continue
        new_fio = str(fix.get("fio", "")).strip()
        if not new_fio:
            continue
        if str(emp.get("fio", "")).strip() != new_fio:
            emp["fio"] = new_fio
            emp["name_fixed"] = True
            changed += 1
        department = str(fix.get("department", "")).strip()
        if department and not str(emp.get("department", "")).strip():
            emp["department"] = department
    if changed:
        save_esen(esen)
    return changed


def open_name_fix_window():
    window = ctk.CTkToplevel()
    window.title("✏️ ФИО по медкнижке")
    window.geometry("780x660")
    window.lift()
    window.focus_force()

    ctk.CTkLabel(
        window,
        text="✏️ Назначить ФИО по номеру медкнижки",
        font=("Arial", 22, "bold"),
    ).pack(pady=(16, 4))
    ctk.CTkLabel(
        window,
        text=(
            "Для сотрудников, у которых в e-SEN нет имени.\n"
            "Имя сохраняется в SanEpi AI и восстанавливается после каждого импорта."
        ),
        font=("Arial", 13),
        text_color="#9ca3af",
        wraplength=700,
    ).pack(pady=(0, 10))

    body = ctk.CTkScrollableFrame(window, width=740, height=500)
    body.pack(padx=16, pady=(0, 10), fill="both", expand=True)

    def render():
        for widget in body.winfo_children():
            widget.destroy()
        esen = load_esen()
        unknown = [e for e in esen if is_placeholder_fio(e.get("fio"))]

        ctk.CTkLabel(
            body,
            text=f"Без ФИО в e-SEN: {len(unknown)}",
            font=("Arial", 16, "bold"),
        ).pack(anchor="w", padx=8, pady=(6, 8))

        if not unknown:
            ctk.CTkLabel(
                body,
                text="✅ Все записи e-SEN с ФИО.",
                font=("Arial", 14),
            ).pack(anchor="w", padx=8, pady=8)

        for emp in unknown:
            row = ctk.CTkFrame(body, corner_radius=10)
            row.pack(fill="x", padx=6, pady=6)

            ctk.CTkLabel(
                row,
                text=(
                    f"Медкнижка: {emp.get('medical_book', '-')}\n"
                    f"Должность: {emp.get('position', '-')}\n"
                    f"Место: {emp.get('workplace', '-')}\n"
                    f"Срок: {emp.get('valid_until', '-')}"
                ),
                font=("Arial", 12),
                anchor="w",
                justify="left",
            ).pack(side="left", padx=10, pady=8)

            fio_entry = ctk.CTkEntry(
                row, width=230,
                placeholder_text="ФИО полностью",
            )
            fio_entry.pack(side="left", padx=4)

            dep_entry = ctk.CTkEntry(
                row, width=140,
                placeholder_text="Отдел (необяз.)",
            )
            dep_entry.pack(side="left", padx=4)

            def save(emp=emp, fio_entry=fio_entry, dep_entry=dep_entry):
                new_fio = fio_entry.get().strip()
                if len(new_fio) < 5:
                    messagebox.showwarning(
                        "SanEpi AI", "Введите ФИО полностью."
                    )
                    return
                med = normalize_medbook(emp.get("medical_book"))
                department = dep_entry.get().strip()

                esen = load_esen()
                for item in esen:
                    if normalize_medbook(item.get("medical_book")) == med:
                        item["fio"] = new_fio
                        item["name_fixed"] = True
                        if department:
                            item["department"] = department
                save_esen(esen)

                fixes = load_fixes()
                fixes[med] = {
                    "fio": new_fio,
                    "department": department,
                }
                save_fixes(fixes)
                messagebox.showinfo(
                    "SanEpi AI",
                    f"Сохранено: {new_fio}\nМедкнижка: {emp.get('medical_book')}",
                )
                render()

            ctk.CTkButton(
                row,
                text="💾",
                width=52,
                height=36,
                fg_color="#059669",
                hover_color="#047857",
                command=save,
            ).pack(side="left", padx=6)

        ctk.CTkLabel(
            body,
            text="Поиск сотрудника по номеру медкнижки:",
            font=("Arial", 15, "bold"),
        ).pack(anchor="w", padx=8, pady=(14, 4))
        search_frame = ctk.CTkFrame(body, fg_color="transparent")
        search_frame.pack(fill="x", padx=6, pady=4)
        search_entry = ctk.CTkEntry(
            search_frame, width=260,
            placeholder_text="Например: AC707522",
        )
        search_entry.pack(side="left", padx=4)

        def show():
            med = normalize_medbook(search_entry.get())
            found = [
                e for e in load_esen()
                if normalize_medbook(e.get("medical_book")) == med
            ]
            if not found:
                messagebox.showwarning(
                    "SanEpi AI",
                    "Сотрудник с такой медкнижкой не найден.",
                )
                return
            emp = found[0]
            messagebox.showinfo(
                "SanEpi AI",
                f"ФИО: {emp.get('fio', '-')}\n"
                f"Должность: {emp.get('position', '-')}\n"
                f"Отдел: {emp.get('department', '-')}\n"
                f"Срок: {emp.get('valid_until', '-')}",
            )

        ctk.CTkButton(
            search_frame, text="🔍 Найти",
            width=110, command=show,
        ).pack(side="left", padx=4)

    render()

    bottom = ctk.CTkFrame(window, fg_color="transparent")
    bottom.pack(fill="x", padx=16, pady=(0, 14))

    def apply_and_compare():
        changed = apply_name_fixes_to_esen_file()
        try:
            from modules.compare_employees import compare_employees
            result = compare_employees()
            messagebox.showinfo(
                "SanEpi AI",
                f"Применено исправлений: {changed}\n"
                f"Совпали: {len(result['matched'])}\n"
                f"Нет в e-SEN: {len(result['only_hr'])}\n"
                f"Нет в HR: {len(result['only_esen'])}",
            )
        except Exception:
            messagebox.showinfo(
                "SanEpi AI", f"Применено исправлений: {changed}"
            )

    ctk.CTkButton(
        bottom,
        text="🔄 Применить исправления и сравнить с HR",
        height=42,
        fg_color="#7c3aed",
        hover_color="#6d28d9",
        command=apply_and_compare,
    ).pack(fill="x")
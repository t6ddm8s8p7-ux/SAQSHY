import json
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_ROOT / "database"

OBJECTS_FILE = DATABASE_DIR / "haccp_objects.json"
RECORDS_FILE = DATABASE_DIR / "haccp_temperature_records.json"


def load_json(file_path, default):
    if not file_path.exists():
        return default

    try:
        with file_path.open(
            "r",
            encoding="utf-8-sig"
        ) as file:
            data = json.load(file)

        return data

    except Exception as error:
        print(f"Ошибка чтения {file_path.name}:")
        print(error)
        return default


def load_objects():
    data = load_json(
        OBJECTS_FILE,
        []
    )

    return data if isinstance(data, list) else []


def load_records():
    data = load_json(
        RECORDS_FILE,
        []
    )

    return data if isinstance(data, list) else []


def normalize_time(value):
    value = str(value or "").strip()

    try:
        return datetime.strptime(
            value,
            "%H:%M"
        ).strftime("%H:%M")

    except ValueError:
        return value


def record_exists(
    records,
    equipment_id,
    selected_date,
    control_time
):
    control_time = normalize_time(
        control_time
    )

    for record in records:
        if (
            str(record.get("equipment_id", ""))
            == str(equipment_id)
            and str(record.get("date", ""))
            == selected_date
            and normalize_time(
                record.get("time", "")
            )
            == control_time
        ):
            return record

    return None


def get_time_status(
    selected_date,
    control_time,
    record
):
    if record:
        return "Выполнено"

    try:
        selected_datetime = datetime.strptime(
            f"{selected_date} {control_time}",
            "%Y-%m-%d %H:%M"
        )

    except ValueError:
        return "Ошибка времени"

    if selected_datetime <= datetime.now():
        return "Пропущено"

    return "Ожидается"


def collect_control_items(
    objects,
    records,
    selected_date
):
    items = []

    for haccp_object in objects:
        object_name = str(
            haccp_object.get(
                "name",
                "Объект"
            )
        )

        departments = haccp_object.get(
            "departments",
            []
        )

        if not isinstance(
            departments,
            list
        ):
            continue

        for department in departments:
            department_name = str(
                department.get(
                    "name",
                    "Подразделение"
                )
            )

            equipment_list = department.get(
                "equipment",
                []
            )

            if not isinstance(
                equipment_list,
                list
            ):
                continue

            for equipment in equipment_list:
                if not equipment.get(
                    "active",
                    True
                ):
                    continue

                equipment_id = str(
                    equipment.get(
                        "id",
                        ""
                    )
                )

                if not equipment_id:
                    continue

                equipment_name = str(
                    equipment.get(
                        "name",
                        "Оборудование"
                    )
                )

                responsible = str(
                    equipment.get(
                        "responsible",
                        ""
                    )
                )

                control_times = equipment.get(
                    "control_times",
                    []
                )

                if isinstance(
                    control_times,
                    str
                ):
                    control_times = [
                        item.strip()
                        for item
                        in control_times.split(",")
                        if item.strip()
                    ]

                if not isinstance(
                    control_times,
                    list
                ):
                    continue

                for control_time in control_times:
                    control_time = normalize_time(
                        control_time
                    )

                    record = record_exists(
                        records=records,
                        equipment_id=equipment_id,
                        selected_date=selected_date,
                        control_time=control_time
                    )

                    status = get_time_status(
                        selected_date=selected_date,
                        control_time=control_time,
                        record=record
                    )

                    items.append(
                        {
                            "object_name": object_name,
                            "department_name": department_name,
                            "equipment_name": equipment_name,
                            "equipment_id": equipment_id,
                            "responsible": responsible,
                            "control_time": control_time,
                            "status": status,
                            "record": record,
                        }
                    )

    items.sort(
        key=lambda item: (
            item["object_name"],
            item["department_name"],
            item["equipment_name"],
            item["control_time"],
        )
    )

    return items


def open_missing_measurements_window(
    parent
):
    window = ctk.CTkToplevel(parent)
    window.title(
        "Контроль замеров HACCP"
    )
    window.geometry(
        "1100x720"
    )
    window.minsize(
        900,
        600
    )
    window.lift()
    window.focus_force()

    ctk.CTkLabel(
        window,
        text="⏰ Контроль замеров температуры",
        font=("Arial", 28, "bold")
    ).pack(
        pady=(20, 6)
    )

    ctk.CTkLabel(
        window,
        text=(
            "Выполненные, ожидаемые "
            "и пропущенные замеры"
        ),
        font=("Arial", 14),
        text_color="#9ca3af"
    ).pack(
        pady=(0, 15)
    )

    filter_frame = ctk.CTkFrame(
        window,
        corner_radius=12
    )
    filter_frame.pack(
        fill="x",
        padx=20,
        pady=(0, 10)
    )

    selected_date = ctk.StringVar(
        value=datetime.now().strftime(
            "%Y-%m-%d"
        )
    )

    selected_status = ctk.StringVar(
        value="Все статусы"
    )

    ctk.CTkLabel(
        filter_frame,
        text="Дата",
        font=("Arial", 13, "bold")
    ).grid(
        row=0,
        column=0,
        padx=10,
        pady=(10, 4),
        sticky="w"
    )

    date_entry = ctk.CTkEntry(
        filter_frame,
        textvariable=selected_date,
        width=200,
        height=36
    )
    date_entry.grid(
        row=1,
        column=0,
        padx=10,
        pady=(0, 10),
        sticky="ew"
    )

    ctk.CTkLabel(
        filter_frame,
        text="Статус",
        font=("Arial", 13, "bold")
    ).grid(
        row=0,
        column=1,
        padx=10,
        pady=(10, 4),
        sticky="w"
    )

    status_menu = ctk.CTkOptionMenu(
        filter_frame,
        variable=selected_status,
        values=[
            "Все статусы",
            "Выполнено",
            "Пропущено",
            "Ожидается",
        ],
        width=220,
        height=36
    )
    status_menu.grid(
        row=1,
        column=1,
        padx=10,
        pady=(0, 10),
        sticky="ew"
    )

    apply_button = ctk.CTkButton(
        filter_frame,
        text="🔄 Обновить",
        width=180,
        height=36
    )
    apply_button.grid(
        row=1,
        column=2,
        padx=10,
        pady=(0, 10),
        sticky="ew"
    )

    filter_frame.grid_columnconfigure(
        0,
        weight=1
    )
    filter_frame.grid_columnconfigure(
        1,
        weight=1
    )
    filter_frame.grid_columnconfigure(
        2,
        weight=0
    )

    summary_label = ctk.CTkLabel(
        window,
        text="",
        font=("Arial", 15, "bold")
    )
    summary_label.pack(
        anchor="w",
        padx=25,
        pady=(5, 8)
    )

    results_frame = ctk.CTkScrollableFrame(
        window,
        corner_radius=12
    )
    results_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 20)
    )

    def render_items():
        for widget in (
            results_frame.winfo_children()
        ):
            widget.destroy()

        date_value = (
            selected_date.get().strip()
        )

        try:
            datetime.strptime(
                date_value,
                "%Y-%m-%d"
            )

        except ValueError:
            messagebox.showwarning(
                "SanEpi AI",
                "Введите дату в формате ГГГГ-ММ-ДД."
            )
            return

        objects = load_objects()
        records = load_records()

        all_items = collect_control_items(
            objects=objects,
            records=records,
            selected_date=date_value
        )

        completed = sum(
            1
            for item in all_items
            if item["status"] == "Выполнено"
        )

        missed = sum(
            1
            for item in all_items
            if item["status"] == "Пропущено"
        )

        waiting = sum(
            1
            for item in all_items
            if item["status"] == "Ожидается"
        )

        summary_label.configure(
            text=(
                f"Всего по графику: {len(all_items)}   "
                f"✅ Выполнено: {completed}   "
                f"❌ Пропущено: {missed}   "
                f"⏳ Ожидается: {waiting}"
            )
        )

        status_filter = (
            selected_status.get()
        )

        if (
            status_filter
            != "Все статусы"
        ):
            items = [
                item
                for item in all_items
                if item["status"]
                == status_filter
            ]
        else:
            items = all_items

        if not items:
            ctk.CTkLabel(
                results_frame,
                text=(
                    "По выбранным условиям "
                    "записей нет."
                ),
                font=("Arial", 16),
                text_color="#9ca3af"
            ).pack(
                pady=50
            )
            return

        status_colors = {
            "Выполнено": "#166534",
            "Пропущено": "#991b1b",
            "Ожидается": "#92400e",
            "Ошибка времени": "#4b5563",
        }

        for item in items:
            status = item["status"]

            card = ctk.CTkFrame(
                results_frame,
                corner_radius=10,
                border_width=1,
                border_color=status_colors.get(
                    status,
                    "#4b5563"
                )
            )
            card.pack(
                fill="x",
                padx=8,
                pady=6
            )

            if status == "Выполнено":
                status_icon = "✅"
            elif status == "Пропущено":
                status_icon = "❌"
            else:
                status_icon = "⏳"

            title = (
                f"{status_icon} {item['control_time']} — "
                f"{item['equipment_name']}"
            )

            ctk.CTkLabel(
                card,
                text=title,
                font=("Arial", 17, "bold"),
                text_color=(
                    "#22c55e"
                    if status == "Выполнено"
                    else (
                        "#ef4444"
                        if status == "Пропущено"
                        else "#f59e0b"
                    )
                )
            ).pack(
                anchor="w",
                padx=15,
                pady=(12, 5)
            )

            details = (
                f"Объект: {item['object_name']}\n"
                f"Подразделение: "
                f"{item['department_name']}\n"
                f"Ответственный: "
                f"{item['responsible'] or '-'}\n"
                f"Статус: {status}"
            )

            record = item.get("record")

            if record:
                details += (
                    f"\nТемпература: "
                    f"{record.get('temperature', '-')} °C"
                )

            ctk.CTkLabel(
                card,
                text=details,
                font=("Arial", 14),
                justify="left"
            ).pack(
                anchor="w",
                padx=15,
                pady=(0, 12)
            )

    apply_button.configure(
        command=render_items
    )

    status_menu.configure(
        command=lambda _value: render_items()
    )

    window.bind(
        "<Return>",
        lambda _event: render_items()
    )

    render_items()
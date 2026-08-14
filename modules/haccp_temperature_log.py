import json
import uuid
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_ROOT / "database"
RECORDS_FILE = (
    DATABASE_DIR
    / "haccp_temperature_records.json"
)


def create_id():
    return uuid.uuid4().hex


def ensure_database():
    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if not RECORDS_FILE.exists():
        save_records([])


def load_records():
    ensure_database()

    try:
        with RECORDS_FILE.open(
            "r",
            encoding="utf-8-sig"
        ) as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except Exception as error:
        print("Ошибка чтения журнала температур:")
        print(error)
        return []


def save_records(records):
    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    temporary_file = RECORDS_FILE.with_suffix(
        ".tmp"
    )

    try:
        with temporary_file.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                records,
                file,
                ensure_ascii=False,
                indent=2
            )

        temporary_file.replace(
            RECORDS_FILE
        )

        return True

    except Exception as error:
        messagebox.showerror(
            "SanEpi AI",
            (
                "Не удалось сохранить "
                f"журнал температур:\n{error}"
            )
        )

        return False


def normalize_temperature(value):
    value = str(value or "").strip()
    value = value.replace(",", ".")

    if not value:
        raise ValueError(
            "Введите фактическую температуру."
        )

    try:
        return float(value)

    except ValueError as error:
        raise ValueError(
            "Температура должна быть числом."
        ) from error


def format_temperature(value):
    if value is None or value == "":
        return "Не установлена"

    try:
        number = float(value)

        if number.is_integer():
            return f"{int(number)} °C"

        return f"{number:g} °C"

    except (TypeError, ValueError):
        return f"{value} °C"


def determine_status(
    temperature,
    minimum,
    maximum
):
    if minimum is not None:
        if temperature < float(minimum):
            return "Отклонение"

    if maximum is not None:
        if temperature > float(maximum):
            return "Отклонение"

    return "Норма"


def open_temperature_log(
    parent,
    object_name,
    department_name,
    equipment
):
    records = load_records()

    equipment_id = equipment.get("id")

    if not equipment_id:
        messagebox.showerror(
            "SanEpi AI",
            "У оборудования отсутствует ID."
        )
        return

    window = ctk.CTkToplevel(parent)
    window.title("Журнал температуры")
    window.geometry("1100x750")
    window.minsize(900, 650)
    window.lift()
    window.focus_force()
    window.grab_set()

    ctk.CTkLabel(
        window,
        text="🌡️ Журнал температуры",
        font=("Arial", 28, "bold")
    ).pack(
        pady=(20, 5)
    )

    ctk.CTkLabel(
        window,
        text=(
            f"{object_name}\n"
            f"{department_name} → "
            f"{equipment.get('name', 'Оборудование')}"
        ),
        font=("Arial", 15),
        text_color="#9ca3af",
        justify="center"
    ).pack(
        pady=(0, 12)
    )

    minimum = equipment.get(
        "temperature_min"
    )
    maximum = equipment.get(
        "temperature_max"
    )

    ctk.CTkLabel(
        window,
        text=(
            "Допустимый диапазон: "
            f"{format_temperature(minimum)} — "
            f"{format_temperature(maximum)}"
        ),
        font=("Arial", 15, "bold"),
        text_color="#22c55e"
    ).pack(
        pady=(0, 15)
    )

    header = ctk.CTkFrame(
        window,
        corner_radius=12
    )
    header.pack(
        fill="x",
        padx=20,
        pady=(0, 10)
    )

    count_label = ctk.CTkLabel(
        header,
        text="",
        font=("Arial", 16, "bold")
    )
    count_label.pack(
        side="left",
        padx=15,
        pady=12
    )

    add_record_button = ctk.CTkButton(
        header,
        text="➕ Добавить замер",
        width=200,
        height=38
    )
    add_record_button.pack(
        side="right",
        padx=15,
        pady=10
    )

    records_frame = ctk.CTkScrollableFrame(
        window,
        corner_radius=12
    )
    records_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 20)
    )

    def get_equipment_records():
        equipment_records = [
            record
            for record in records
            if record.get("equipment_id")
            == equipment_id
        ]

        equipment_records.sort(
            key=lambda record: (
                record.get("date", ""),
                record.get("time", ""),
                record.get("created_at", ""),
            ),
            reverse=True
        )

        return equipment_records

    def render_records():
        for widget in (
            records_frame.winfo_children()
        ):
            widget.destroy()

        equipment_records = (
            get_equipment_records()
        )

        count_label.configure(
            text=(
                "Записей: "
                f"{len(equipment_records)}"
            )
        )

        if not equipment_records:
            ctk.CTkLabel(
                records_frame,
                text=(
                    "Замеры температуры "
                    "ещё не добавлены.\n\n"
                    "Нажмите «Добавить замер»."
                ),
                font=("Arial", 16),
                text_color="#9ca3af",
                justify="center"
            ).pack(
                pady=80
            )
            return

        for record in equipment_records:
            status = record.get(
                "status",
                "Норма"
            )

            is_deviation = (
                status == "Отклонение"
            )

            card = ctk.CTkFrame(
                records_frame,
                corner_radius=12,
                border_width=2,
                border_color=(
                    "#ef4444"
                    if is_deviation
                    else "#22c55e"
                )
            )
            card.pack(
                fill="x",
                padx=8,
                pady=7
            )

            card.grid_columnconfigure(
                0,
                weight=1
            )

            date_value = record.get(
                "date",
                "-"
            )

            time_value = record.get(
                "time",
                "-"
            )

            temperature = (
                format_temperature(
                    record.get("temperature")
                )
            )

            ctk.CTkLabel(
                card,
                text=(
                    f"📅 {date_value}   "
                    f"🕒 {time_value}   "
                    f"🌡️ {temperature}"
                ),
                font=("Arial", 18, "bold"),
                anchor="w"
            ).grid(
                row=0,
                column=0,
                sticky="ew",
                padx=16,
                pady=(14, 5)
            )

            ctk.CTkLabel(
                card,
                text=status,
                font=("Arial", 15, "bold"),
                text_color=(
                    "#ef4444"
                    if is_deviation
                    else "#22c55e"
                )
            ).grid(
                row=0,
                column=1,
                padx=12,
                pady=(14, 5)
            )

            details = (
                f"Ответственный: "
                f"{record.get('responsible', 'Не указан')}"
            )

            corrective_action = str(
                record.get(
                    "corrective_action",
                    ""
                )
            ).strip()

            if corrective_action:
                details += (
                    "\nКорректирующее действие: "
                    f"{corrective_action}"
                )

            ctk.CTkLabel(
                card,
                text=details,
                font=("Arial", 14),
                justify="left",
                anchor="w",
                wraplength=720
            ).grid(
                row=1,
                column=0,
                sticky="ew",
                padx=16,
                pady=(5, 14)
            )

            ctk.CTkButton(
                card,
                text="Удалить",
                width=100,
                height=34,
                fg_color="#dc2626",
                hover_color="#b91c1c",
                command=(
                    lambda item=record:
                    delete_record(item)
                )
            ).grid(
                row=1,
                column=1,
                padx=12,
                pady=(5, 14)
            )

    def delete_record(record):
        confirmed = messagebox.askyesno(
            "Удаление замера",
            (
                "Удалить запись?\n\n"
                f"{record.get('date', '')} "
                f"{record.get('time', '')}\n"
                f"{format_temperature(record.get('temperature'))}"
            ),
            parent=window
        )

        if not confirmed:
            return

        records.remove(record)

        if save_records(records):
            render_records()

    def open_record_form():
        form = ctk.CTkToplevel(window)
        form.title("Новый замер температуры")
        form.geometry("650x690")
        form.minsize(600, 620)
        form.lift()
        form.focus_force()
        form.grab_set()

        ctk.CTkLabel(
            form,
            text="➕ Новый замер",
            font=("Arial", 25, "bold")
        ).pack(
            pady=(20, 12)
        )

        fields = ctk.CTkScrollableFrame(
            form,
            corner_radius=12
        )
        fields.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 12)
        )

        def add_label(text):
            ctk.CTkLabel(
                fields,
                text=text,
                font=("Arial", 14, "bold")
            ).pack(
                anchor="w",
                padx=15,
                pady=(12, 4)
            )

        add_label("Дата")

        date_entry = ctk.CTkEntry(
            fields,
            height=40,
            placeholder_text="ГГГГ-ММ-ДД"
        )
        date_entry.pack(
            fill="x",
            padx=15
        )
        date_entry.insert(
            0,
            datetime.now().strftime(
                "%Y-%m-%d"
            )
        )

        add_label("Время контроля")

        control_times = equipment.get(
            "control_times",
            []
        )

        if not control_times:
            control_times = [
                "09:00",
                "16:00",
                "21:00",
                "03:00",
            ]

        selected_time = ctk.StringVar(
            value=control_times[0]
        )

        time_menu = ctk.CTkOptionMenu(
            fields,
            values=control_times,
            variable=selected_time,
            height=40
        )
        time_menu.pack(
            fill="x",
            padx=15
        )

        add_label("Фактическая температура, °C")

        temperature_entry = ctk.CTkEntry(
            fields,
            height=40,
            placeholder_text="Например: 4"
        )
        temperature_entry.pack(
            fill="x",
            padx=15
        )

        add_label("Ответственный")

        responsible_entry = ctk.CTkEntry(
            fields,
            height=40,
            placeholder_text="ФИО или должность"
        )
        responsible_entry.pack(
            fill="x",
            padx=15
        )
        responsible_entry.insert(
            0,
            equipment.get(
                "responsible",
                ""
            )
        )

        add_label(
            "Корректирующее действие "
            "(обязательно при отклонении)"
        )

        corrective_entry = ctk.CTkTextbox(
            fields,
            height=100,
            font=("Arial", 14),
            wrap="word"
        )
        corrective_entry.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        error_label = ctk.CTkLabel(
            form,
            text="",
            font=("Arial", 13),
            text_color="#ef4444"
        )
        error_label.pack(
            pady=(0, 5)
        )

        def save_record():
            date_value = date_entry.get().strip()

            try:
                datetime.strptime(
                    date_value,
                    "%Y-%m-%d"
                )

            except ValueError:
                error_label.configure(
                    text=(
                        "Дата должна быть "
                        "в формате ГГГГ-ММ-ДД."
                    )
                )
                return

            try:
                temperature = (
                    normalize_temperature(
                        temperature_entry.get()
                    )
                )

            except ValueError as error:
                error_label.configure(
                    text=str(error)
                )
                return

            responsible = (
                responsible_entry.get().strip()
            )

            if not responsible:
                error_label.configure(
                    text=(
                        "Укажите ответственного."
                    )
                )
                return

            status = determine_status(
                temperature=temperature,
                minimum=minimum,
                maximum=maximum
            )

            corrective_action = (
                corrective_entry
                .get("1.0", "end")
                .strip()
            )

            if (
                status == "Отклонение"
                and not corrective_action
            ):
                error_label.configure(
                    text=(
                        "При отклонении укажите "
                        "корректирующее действие."
                    )
                )
                return

            record = {
                "id": create_id(),
                "object_name": object_name,
                "department_name": (
                    department_name
                ),
                "equipment_id": equipment_id,
                "equipment_name": equipment.get(
                    "name",
                    "Оборудование"
                ),
                "date": date_value,
                "time": selected_time.get(),
                "temperature": temperature,
                "temperature_min": minimum,
                "temperature_max": maximum,
                "status": status,
                "responsible": responsible,
                "corrective_action": (
                    corrective_action
                ),
                "created_at": (
                    datetime.now().isoformat(
                        timespec="seconds"
                    )
                ),
            }

            records.append(record)

            if save_records(records):
                form.destroy()
                render_records()

        buttons = ctk.CTkFrame(
            form,
            fg_color="transparent"
        )
        buttons.pack(
            fill="x",
            padx=20,
            pady=(5, 20)
        )

        ctk.CTkButton(
            buttons,
            text="💾 Сохранить",
            height=42,
            command=save_record
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 6)
        )

        ctk.CTkButton(
            buttons,
            text="Отмена",
            height=42,
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=form.destroy
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(6, 0)
        )

    add_record_button.configure(
        command=open_record_form
    )

    render_records()
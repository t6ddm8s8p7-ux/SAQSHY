import uuid
from tkinter import messagebox

import customtkinter as ctk
from modules.haccp_temperature_log import open_temperature_log

EQUIPMENT_TYPES = [
    "Холодильник",
    "Морозильник",
    "Холодильная камера",
    "Морозильная камера",
    "Холодильная витрина",
    "Мармит",
    "Термометр",
    "Фритюр",
    "Другое",
]

DEFAULT_CONTROL_TIMES = (
    "09:00, 16:00, 21:00, 03:00"
)


def create_id():
    return uuid.uuid4().hex


def normalize_temperature(value):
    value = str(value or "").strip()

    if not value:
        return None

    value = value.replace(",", ".")

    try:
        return float(value)

    except ValueError as error:
        raise ValueError(
            f"Неверная температура: {value}"
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


def open_equipment_window(
    parent,
    object_name,
    department,
    save_callback
):
    """
    Открывает окно управления оборудованием
    выбранного подразделения.

    save_callback вызывается после изменений
    для сохранения haccp_objects.json.
    """
    equipment_list = department.setdefault(
        "equipment",
        []
    )

    window = ctk.CTkToplevel(parent)
    window.title("Оборудование HACCP")
    window.geometry("1000x720")
    window.minsize(850, 620)
    window.lift()
    window.focus_force()
    window.grab_set()

    ctk.CTkLabel(
        window,
        text="🌡️ Оборудование HACCP",
        font=("Arial", 28, "bold")
    ).pack(
        pady=(20, 5)
    )

    ctk.CTkLabel(
        window,
        text=(
            f"{object_name}\n"
            f"{department.get('name', 'Подразделение')}"
        ),
        font=("Arial", 15),
        text_color="#9ca3af",
        justify="center"
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

    add_button = ctk.CTkButton(
        header,
        text="➕ Добавить оборудование",
        width=230,
        height=38
    )
    add_button.pack(
        side="right",
        padx=15,
        pady=10
    )

    equipment_frame = ctk.CTkScrollableFrame(
        window,
        corner_radius=12
    )
    equipment_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 20)
    )

    def save_changes():
        result = save_callback()

        return result is not False

    def render_equipment():
        for widget in (
            equipment_frame.winfo_children()
        ):
            widget.destroy()

        count_label.configure(
            text=(
                "Оборудование: "
                f"{len(equipment_list)}"
            )
        )

        if not equipment_list:
            ctk.CTkLabel(
                equipment_frame,
                text=(
                    "Оборудование ещё не добавлено.\n\n"
                    "Нажмите «Добавить оборудование»."
                ),
                font=("Arial", 16),
                text_color="#9ca3af",
                justify="center"
            ).pack(
                pady=80
            )
            return

        for equipment in equipment_list:
            card = ctk.CTkFrame(
                equipment_frame,
                corner_radius=12
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

            equipment_name = equipment.get(
                "name",
                "Оборудование"
            )

            equipment_type = equipment.get(
                "type",
                "Другое"
            )

            location = equipment.get(
                "location",
                ""
            )

            responsible = equipment.get(
                "responsible",
                ""
            )

            minimum = format_temperature(
                equipment.get(
                    "temperature_min"
                )
            )

            maximum = format_temperature(
                equipment.get(
                    "temperature_max"
                )
            )

            control_times = ", ".join(
                equipment.get(
                    "control_times",
                    []
                )
            )

            active = equipment.get(
                "active",
                True
            )

            status_text = (
                "Активно"
                if active
                else "Отключено"
            )

            status_color = (
                "#22c55e"
                if active
                else "#9ca3af"
            )

            ctk.CTkLabel(
                card,
                text=f"🌡️ {equipment_name}",
                font=("Arial", 19, "bold"),
                anchor="w"
            ).grid(
                row=0,
                column=0,
                sticky="ew",
                padx=16,
                pady=(14, 4)
            )

            ctk.CTkLabel(
                card,
                text=status_text,
                font=("Arial", 13, "bold"),
                text_color=status_color
            ).grid(
                row=0,
                column=1,
                padx=10,
                pady=(14, 4)
            )

            details = (
                f"Тип: {equipment_type}\n"
                f"Местонахождение: "
                f"{location or 'Не указано'}\n"
                f"Допустимый диапазон: "
                f"{minimum} — {maximum}\n"
                f"Ответственный: "
                f"{responsible or 'Не указан'}\n"
                f"Время контроля: "
                f"{control_times or 'Не установлено'}"
            )

            ctk.CTkLabel(
                card,
                text=details,
                font=("Arial", 14),
                justify="left",
                anchor="w"
            ).grid(
                row=1,
                column=0,
                sticky="ew",
                padx=16,
                pady=(4, 14)
            )

            actions = ctk.CTkFrame(
                card,
                fg_color="transparent"
            )
            actions.grid(
                row=1,
                column=1,
                padx=12,
                pady=(4, 14)
            )
            ctk.CTkButton(
                actions,
                text="Журнал",
                width=105,
                height=34,
                fg_color="#059669",
                hover_color="#047857",
                command=(
                    lambda item=equipment:
                    open_temperature_log(
                        parent=window,
                        object_name=object_name,
                        department_name=department.get(
                            "name",
                            "Подразделение"
                        ),
                        equipment=item
                    )
                )
            ).pack(
                pady=(0, 5)
            )
            
            ctk.CTkButton(
                actions,
                text="Изменить",
                width=105,
                height=34,
                fg_color="#7c3aed",
                hover_color="#6d28d9",
                command=(
                    lambda item=equipment:
                    open_equipment_form(item)
                )
            ).pack(
                pady=(0, 5)
            )

            ctk.CTkButton(
                actions,
                text=(
                    "Отключить"
                    if active
                    else "Включить"
                ),
                width=105,
                height=34,
                fg_color="#6b7280",
                hover_color="#4b5563",
                command=(
                    lambda item=equipment:
                    toggle_equipment(item)
                )
            ).pack(
                pady=5
            )

            ctk.CTkButton(
                actions,
                text="Удалить",
                width=105,
                height=34,
                fg_color="#dc2626",
                hover_color="#b91c1c",
                command=(
                    lambda item=equipment:
                    delete_equipment(item)
                )
            ).pack(
                pady=(5, 0)
            )

    def toggle_equipment(equipment):
        equipment["active"] = not equipment.get(
            "active",
            True
        )

        if save_changes():
            render_equipment()

    def delete_equipment(equipment):
        name = equipment.get(
            "name",
            "Оборудование"
        )

        confirmed = messagebox.askyesno(
            "Удаление оборудования",
            (
                "Удалить оборудование?\n\n"
                f"{name}\n\n"
                "Связанные записи контроля "
                "могут стать недоступны."
            ),
            parent=window
        )

        if not confirmed:
            return

        equipment_list.remove(equipment)

        if save_changes():
            render_equipment()

    def open_equipment_form(
        existing_equipment=None
    ):
        is_editing = (
            existing_equipment is not None
        )

        form = ctk.CTkToplevel(window)
        form.title(
            "Изменить оборудование"
            if is_editing
            else "Добавить оборудование"
        )
        form.geometry("650x700")
        form.minsize(600, 650)
        form.lift()
        form.focus_force()
        form.grab_set()

        title = (
            "✏️ Изменить оборудование"
            if is_editing
            else "➕ Новое оборудование"
        )

        ctk.CTkLabel(
            form,
            text=title,
            font=("Arial", 25, "bold")
        ).pack(
            pady=(20, 15)
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

        current = existing_equipment or {}

        add_label("Название оборудования")

        name_entry = ctk.CTkEntry(
            fields,
            height=40,
            placeholder_text=(
                "Например: Холодильник №1"
            )
        )
        name_entry.pack(
            fill="x",
            padx=15
        )
        name_entry.insert(
            0,
            current.get("name", "")
        )

        add_label("Тип оборудования")

        equipment_type = ctk.StringVar(
            value=current.get(
                "type",
                EQUIPMENT_TYPES[0]
            )
        )

        type_menu = ctk.CTkOptionMenu(
            fields,
            values=EQUIPMENT_TYPES,
            variable=equipment_type,
            height=40
        )
        type_menu.pack(
            fill="x",
            padx=15
        )

        add_label("Номер или местонахождение")

        location_entry = ctk.CTkEntry(
            fields,
            height=40,
            placeholder_text=(
                "Например: холодный цех"
            )
        )
        location_entry.pack(
            fill="x",
            padx=15
        )
        location_entry.insert(
            0,
            current.get("location", "")
        )

        add_label("Минимальная температура, °C")

        minimum_entry = ctk.CTkEntry(
            fields,
            height=40,
            placeholder_text="Например: 2"
        )
        minimum_entry.pack(
            fill="x",
            padx=15
        )

        if current.get(
            "temperature_min"
        ) is not None:
            minimum_entry.insert(
                0,
                str(
                    current.get(
                        "temperature_min"
                    )
                )
            )

        add_label("Максимальная температура, °C")

        maximum_entry = ctk.CTkEntry(
            fields,
            height=40,
            placeholder_text="Например: 6"
        )
        maximum_entry.pack(
            fill="x",
            padx=15
        )

        if current.get(
            "temperature_max"
        ) is not None:
            maximum_entry.insert(
                0,
                str(
                    current.get(
                        "temperature_max"
                    )
                )
            )

        add_label("Ответственный")

        responsible_entry = ctk.CTkEntry(
            fields,
            height=40,
            placeholder_text=(
                "ФИО или должность"
            )
        )
        responsible_entry.pack(
            fill="x",
            padx=15
        )
        responsible_entry.insert(
            0,
            current.get(
                "responsible",
                ""
            )
        )

        add_label("Время контроля")

        times_entry = ctk.CTkEntry(
            fields,
            height=40,
            placeholder_text=(
                DEFAULT_CONTROL_TIMES
            )
        )
        times_entry.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        existing_times = current.get(
            "control_times",
            []
        )

        times_entry.insert(
            0,
            (
                ", ".join(existing_times)
                if existing_times
                else DEFAULT_CONTROL_TIMES
            )
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

        def save_equipment():
            name = name_entry.get().strip()

            if not name:
                error_label.configure(
                    text=(
                        "Введите название "
                        "оборудования."
                    )
                )
                return

            try:
                minimum = normalize_temperature(
                    minimum_entry.get()
                )

                maximum = normalize_temperature(
                    maximum_entry.get()
                )

            except ValueError as error:
                error_label.configure(
                    text=str(error)
                )
                return

            if (
                minimum is not None
                and maximum is not None
                and minimum > maximum
            ):
                error_label.configure(
                    text=(
                        "Минимальная температура "
                        "не может быть выше максимальной."
                    )
                )
                return

            control_times = [
                item.strip()
                for item in (
                    times_entry.get().split(",")
                )
                if item.strip()
            ]

            equipment_data = {
                "id": (
                    current.get("id")
                    if is_editing
                    else create_id()
                ),
                "name": name,
                "type": equipment_type.get(),
                "location": (
                    location_entry.get().strip()
                ),
                "temperature_min": minimum,
                "temperature_max": maximum,
                "responsible": (
                    responsible_entry
                    .get()
                    .strip()
                ),
                "control_times": control_times,
                "active": current.get(
                    "active",
                    True
                ),
            }

            if is_editing:
                existing_equipment.clear()
                existing_equipment.update(
                    equipment_data
                )

            else:
                equipment_list.append(
                    equipment_data
                )

            if save_changes():
                form.destroy()
                render_equipment()

        form_buttons = ctk.CTkFrame(
            form,
            fg_color="transparent"
        )
        form_buttons.pack(
            fill="x",
            padx=20,
            pady=(5, 20)
        )

        ctk.CTkButton(
            form_buttons,
            text="💾 Сохранить",
            height=42,
            command=save_equipment
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 6)
        )

        ctk.CTkButton(
            form_buttons,
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

    add_button.configure(
        command=open_equipment_form
    )

    render_equipment()
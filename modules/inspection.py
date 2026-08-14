import json
import uuid
from datetime import date, datetime
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_ROOT / "database"
HACCP_OBJECTS_FILE = DATABASE_DIR / "haccp_objects.json"
INSPECTIONS_FILE = DATABASE_DIR / "inspections.json"

INSPECTION_TYPE = "Проверка на соответствие нормативам"

RESULTS = [
    "Соответствует",
    "Есть нарушения",
    "Нарушения устранены",
]


def create_id():
    return uuid.uuid4().hex


def load_json_list(file_path):
    if not file_path.exists():
        return []

    try:
        with file_path.open(
            "r",
            encoding="utf-8-sig"
        ) as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except Exception as error:
        print(f"Ошибка чтения {file_path.name}:")
        print(error)
        return []


def load_objects():
    return load_json_list(HACCP_OBJECTS_FILE)


def load_inspections():
    return load_json_list(INSPECTIONS_FILE)


def save_inspections(inspections):
    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    temporary_file = INSPECTIONS_FILE.with_suffix(".tmp")

    try:
        with temporary_file.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                inspections,
                file,
                ensure_ascii=False,
                indent=2
            )

        temporary_file.replace(INSPECTIONS_FILE)
        return True

    except Exception as error:
        print("Ошибка сохранения проверок:")
        print(error)

        messagebox.showerror(
            "SanEpi AI",
            f"Не удалось сохранить проверку:\n{error}"
        )
        return False


def build_inspection_page(parent):
    objects = load_objects()
    inspections = load_inspections()

    object_names = {
        str(item.get("name", "Объект")): item
        for item in objects
    }

    ctk.CTkLabel(
        parent,
        text="📄 Проверки",
        font=("Arial", 34, "bold")
    ).pack(
        pady=(20, 5)
    )

    ctk.CTkLabel(
        parent,
        text=INSPECTION_TYPE,
        font=("Arial", 15),
        text_color="#9ca3af"
    ).pack(
        pady=(0, 15)
    )

    main_frame = ctk.CTkFrame(
        parent,
        corner_radius=14
    )
    main_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 20)
    )

    main_frame.grid_columnconfigure(0, weight=3)
    main_frame.grid_columnconfigure(1, weight=2)
    main_frame.grid_rowconfigure(0, weight=1)

    form_panel = ctk.CTkScrollableFrame(
        main_frame,
        corner_radius=12
    )
    form_panel.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=(10, 5),
        pady=10
    )

    history_panel = ctk.CTkFrame(
        main_frame,
        corner_radius=12
    )
    history_panel.grid(
        row=0,
        column=1,
        sticky="nsew",
        padx=(5, 10),
        pady=10
    )

    ctk.CTkLabel(
        form_panel,
        text="Новая проверка",
        font=("Arial", 24, "bold")
    ).pack(
        anchor="w",
        padx=15,
        pady=(15, 12)
    )

    selection_frame = ctk.CTkFrame(
        form_panel,
        fg_color="transparent"
    )
    selection_frame.pack(
        fill="x",
        padx=15
    )

    selection_frame.grid_columnconfigure(0, weight=1)
    selection_frame.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(
        selection_frame,
        text="Объект",
        font=("Arial", 14, "bold")
    ).grid(
        row=0,
        column=0,
        padx=(0, 6),
        pady=(0, 5),
        sticky="w"
    )

    ctk.CTkLabel(
        selection_frame,
        text="Подразделение",
        font=("Arial", 14, "bold")
    ).grid(
        row=0,
        column=1,
        padx=(6, 0),
        pady=(0, 5),
        sticky="w"
    )

    object_variable = ctk.StringVar(
        value=(
            next(iter(object_names))
            if object_names
            else "Объекты не добавлены"
        )
    )

    department_variable = ctk.StringVar(
        value="Выберите подразделение"
    )

    object_menu = ctk.CTkOptionMenu(
        selection_frame,
        variable=object_variable,
        values=(
            list(object_names)
            if object_names
            else ["Объекты не добавлены"]
        ),
        height=38
    )
    object_menu.grid(
        row=1,
        column=0,
        padx=(0, 6),
        sticky="ew"
    )

    department_menu = ctk.CTkOptionMenu(
        selection_frame,
        variable=department_variable,
        values=["Выберите подразделение"],
        height=38
    )
    department_menu.grid(
        row=1,
        column=1,
        padx=(6, 0),
        sticky="ew"
    )

    details_frame = ctk.CTkFrame(
        form_panel,
        fg_color="transparent"
    )
    details_frame.pack(
        fill="x",
        padx=15,
        pady=(14, 0)
    )

    details_frame.grid_columnconfigure(0, weight=1)
    details_frame.grid_columnconfigure(1, weight=1)
    details_frame.grid_columnconfigure(2, weight=1)

    ctk.CTkLabel(
        details_frame,
        text="Дата",
        font=("Arial", 14, "bold")
    ).grid(row=0, column=0, padx=(0, 5), sticky="w")

    ctk.CTkLabel(
        details_frame,
        text="Проверяющий",
        font=("Arial", 14, "bold")
    ).grid(row=0, column=1, padx=5, sticky="w")

    ctk.CTkLabel(
        details_frame,
        text="Результат",
        font=("Arial", 14, "bold")
    ).grid(row=0, column=2, padx=(5, 0), sticky="w")

    date_entry = ctk.CTkEntry(
        details_frame,
        height=38
    )
    date_entry.grid(
        row=1,
        column=0,
        padx=(0, 5),
        pady=(5, 0),
        sticky="ew"
    )
    date_entry.insert(0, date.today().isoformat())

    inspector_entry = ctk.CTkEntry(
        details_frame,
        placeholder_text="Ф.И.О.",
        height=38
    )
    inspector_entry.grid(
        row=1,
        column=1,
        padx=5,
        pady=(5, 0),
        sticky="ew"
    )

    result_variable = ctk.StringVar(
        value=RESULTS[0]
    )

    result_menu = ctk.CTkOptionMenu(
        details_frame,
        variable=result_variable,
        values=RESULTS,
        height=38
    )
    result_menu.grid(
        row=1,
        column=2,
        padx=(5, 0),
        pady=(5, 0),
        sticky="ew"
    )

    def add_textbox(title, placeholder, height=80):
        ctk.CTkLabel(
            form_panel,
            text=title,
            font=("Arial", 14, "bold")
        ).pack(
            anchor="w",
            padx=15,
            pady=(14, 5)
        )

        textbox = ctk.CTkTextbox(
            form_panel,
            height=height,
            font=("Arial", 14),
            wrap="word"
        )
        textbox.pack(
            fill="x",
            padx=15
        )
        textbox.insert("1.0", placeholder)
        return textbox

    checked_text = add_textbox(
        "Что проверено",
        "Например: условия хранения, маркировка, сроки годности..."
    )

    violation_text = add_textbox(
        "Выявленные нарушения",
        "Если нарушений нет, оставьте поле пустым."
    )

    normative_text = add_textbox(
        "Нормативное основание",
        "Укажите приказ, санитарное правило или конкретный пункт."
    )

    corrective_text = add_textbox(
        "Необходимые меры",
        "Что необходимо исправить и кто отвечает."
    )

    ctk.CTkLabel(
        form_panel,
        text="Срок устранения",
        font=("Arial", 14, "bold")
    ).pack(
        anchor="w",
        padx=15,
        pady=(14, 5)
    )

    deadline_entry = ctk.CTkEntry(
        form_panel,
        placeholder_text="ГГГГ-ММ-ДД или не требуется",
        height=38
    )
    deadline_entry.pack(
        fill="x",
        padx=15
    )

    save_button = ctk.CTkButton(
        form_panel,
        text="💾 Сохранить проверку",
        height=44,
        fg_color="#059669",
        hover_color="#047857"
    )
    save_button.pack(
        fill="x",
        padx=15,
        pady=(18, 15)
    )

    history_header = ctk.CTkFrame(
        history_panel,
        fg_color="transparent"
    )
    history_header.pack(
        fill="x",
        padx=15,
        pady=(18, 10)
    )

    history_title = ctk.CTkLabel(
        history_header,
        text="История проверок",
        font=("Arial", 22, "bold")
    )
    history_title.pack(side="left")

    history_list = ctk.CTkScrollableFrame(
        history_panel,
        corner_radius=10
    )
    history_list.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(0, 12)
    )

    def clean_text(textbox, placeholder):
        value = textbox.get("1.0", "end").strip()

        if value == placeholder:
            return ""

        return value

    def get_departments():
        selected_object = object_names.get(
            object_variable.get()
        )

        if not selected_object:
            return []

        return selected_object.get("departments", [])

    def update_departments(_value=None):
        departments = get_departments()
        names = [
            str(item.get("name", "Подразделение"))
            for item in departments
        ]

        if names:
            department_menu.configure(values=names)
            department_variable.set(names[0])
            department_menu.configure(state="normal")
        else:
            department_menu.configure(
                values=["Подразделения не добавлены"]
            )
            department_variable.set(
                "Подразделения не добавлены"
            )
            department_menu.configure(state="disabled")

    def delete_inspection(inspection_id):
        record = next(
            (
                item
                for item in inspections
                if item.get("id") == inspection_id
            ),
            None
        )

        if not record:
            return

        confirmed = messagebox.askyesno(
            "Удаление проверки",
            (
                "Удалить запись проверки?\n\n"
                f"{record.get('date', '')} — "
                f"{record.get('department_name', '')}"
            )
        )

        if not confirmed:
            return

        inspections.remove(record)

        if save_inspections(inspections):
            render_history()

    def render_history():
        for widget in history_list.winfo_children():
            widget.destroy()

        history_title.configure(
            text=f"История проверок: {len(inspections)}"
        )

        if not inspections:
            ctk.CTkLabel(
                history_list,
                text="Проверки пока не проводились.",
                font=("Arial", 14),
                text_color="#9ca3af"
            ).pack(pady=35)
            return

        ordered_records = sorted(
            inspections,
            key=lambda item: (
                str(item.get("date", "")),
                str(item.get("created_at", ""))
            ),
            reverse=True
        )

        colors = {
            "Соответствует": "#22c55e",
            "Есть нарушения": "#ef4444",
            "Нарушения устранены": "#3b82f6",
        }

        for record in ordered_records:
            card = ctk.CTkFrame(
                history_list,
                corner_radius=10,
                border_width=1,
                border_color=colors.get(
                    record.get("result"),
                    "#6b7280"
                )
            )
            card.pack(
                fill="x",
                padx=5,
                pady=6
            )

            result = record.get("result", "-")
            title = (
                f"{record.get('date', '-')} — {result}"
            )

            ctk.CTkLabel(
                card,
                text=title,
                font=("Arial", 15, "bold"),
                text_color=colors.get(result, "#d1d5db"),
                wraplength=390,
                justify="left"
            ).pack(
                anchor="w",
                padx=12,
                pady=(10, 4)
            )

            details = (
                f"Объект: {record.get('object_name', '-')}\n"
                f"Подразделение: "
                f"{record.get('department_name', '-')}\n"
                f"Проверяющий: {record.get('inspector', '-')}\n"
                f"Проверено: {record.get('checked_scope', '-')}"
            )

            violation = str(
                record.get("violation", "")
            ).strip()

            if violation:
                details += f"\nНарушение: {violation}"

            normative_basis = str(
                record.get("normative_basis", "")
            ).strip()

            if normative_basis:
                details += (
                    f"\nНорматив: {normative_basis}"
                )

            ctk.CTkLabel(
                card,
                text=details,
                font=("Arial", 13),
                wraplength=390,
                justify="left"
            ).pack(
                anchor="w",
                padx=12,
                pady=(0, 8)
            )

            ctk.CTkButton(
                card,
                text="Удалить запись",
                height=30,
                fg_color="#dc2626",
                hover_color="#b91c1c",
                command=(
                    lambda record_id=record.get("id"):
                    delete_inspection(record_id)
                )
            ).pack(
                fill="x",
                padx=12,
                pady=(0, 10)
            )

    checked_placeholder = (
        "Например: условия хранения, маркировка, сроки годности..."
    )
    violation_placeholder = (
        "Если нарушений нет, оставьте поле пустым."
    )
    normative_placeholder = (
        "Укажите приказ, санитарное правило или конкретный пункт."
    )
    corrective_placeholder = (
        "Что необходимо исправить и кто отвечает."
    )

    def save_inspection():
        selected_object = object_names.get(
            object_variable.get()
        )

        if not selected_object:
            messagebox.showwarning(
                "SanEpi AI",
                "Сначала добавьте объект в разделе HACCP."
            )
            return

        selected_department = next(
            (
                item
                for item in get_departments()
                if str(item.get("name", ""))
                == department_variable.get()
            ),
            None
        )

        if not selected_department:
            messagebox.showwarning(
                "SanEpi AI",
                "Выберите подразделение."
            )
            return

        inspection_date = date_entry.get().strip()
        inspector = inspector_entry.get().strip()
        checked_scope = clean_text(
            checked_text,
            checked_placeholder
        )
        violation = clean_text(
            violation_text,
            violation_placeholder
        )

        if not inspection_date:
            messagebox.showwarning(
                "SanEpi AI",
                "Введите дату проверки."
            )
            return

        try:
            date.fromisoformat(inspection_date)
        except ValueError:
            messagebox.showwarning(
                "SanEpi AI",
                "Дата должна быть в формате ГГГГ-ММ-ДД."
            )
            return

        if not inspector:
            messagebox.showwarning(
                "SanEpi AI",
                "Введите Ф.И.О. проверяющего."
            )
            return

        if not checked_scope:
            messagebox.showwarning(
                "SanEpi AI",
                "Опишите, что было проверено."
            )
            return

        if (
            result_variable.get() == "Есть нарушения"
            and not violation
        ):
            messagebox.showwarning(
                "SanEpi AI",
                "Опишите выявленное нарушение."
            )
            return

        record = {
            "id": create_id(),
            "inspection_type": INSPECTION_TYPE,
            "object_id": selected_object.get("id"),
            "object_name": selected_object.get("name"),
            "department_id": selected_department.get("id"),
            "department_name": selected_department.get("name"),
            "date": inspection_date,
            "inspector": inspector,
            "result": result_variable.get(),
            "checked_scope": checked_scope,
            "violation": violation,
            "normative_basis": clean_text(
                normative_text,
                normative_placeholder
            ),
            "corrective_action": clean_text(
                corrective_text,
                corrective_placeholder
            ),
            "deadline": deadline_entry.get().strip(),
            "created_at": datetime.now().isoformat(
                timespec="seconds"
            ),
        }

        inspections.append(record)

        if not save_inspections(inspections):
            inspections.remove(record)
            return

        result_variable.set(RESULTS[0])

        for textbox, placeholder in (
            (checked_text, checked_placeholder),
            (violation_text, violation_placeholder),
            (normative_text, normative_placeholder),
            (corrective_text, corrective_placeholder),
        ):
            textbox.delete("1.0", "end")
            textbox.insert("1.0", placeholder)

        deadline_entry.delete(0, "end")
        render_history()

        messagebox.showinfo(
            "SanEpi AI",
            "Проверка сохранена."
        )

    object_menu.configure(
        command=update_departments
    )

    save_button.configure(
        command=save_inspection
    )

    if not objects:
        object_menu.configure(state="disabled")
        department_menu.configure(state="disabled")
        save_button.configure(state="disabled")

        messagebox.showwarning(
            "SanEpi AI",
            (
                "Объекты не найдены. "
                "Сначала добавьте объект в разделе HACCP."
            )
        )
    else:
        update_departments()

    render_history()

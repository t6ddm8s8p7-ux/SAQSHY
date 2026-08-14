import json
import uuid
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from modules.haccp_equipment import open_equipment_window
from modules.haccp_summary import open_haccp_summary
from modules.haccp_missing_measurements import open_missing_measurements_window

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_ROOT / "database"
HACCP_FILE = DATABASE_DIR / "haccp_objects.json"


DEFAULT_OBJECTS = [
    {
        "id": "rixos_water_world_aktau",
        "name": "Rixos Water World Aktau",
        "departments": [
            {
                "id": "turquoise",
                "category": "Рестораны",
                "name": "Turquoise",
                "equipment": [],
            },
            {
                "id": "lezzet",
                "category": "Рестораны",
                "name": "Lezzet",
                "equipment": [],
            },
            {
                "id": "mermaid",
                "category": "Рестораны",
                "name": "Mermaid",
                "equipment": [],
            },
            {
                "id": "tetis_bar",
                "category": "Бары",
                "name": "Tetis",
                "equipment": [],
            },
            {
                "id": "infiniti_bar",
                "category": "Бары",
                "name": "Infiniti",
                "equipment": [],
            },
            {
                "id": "toryish_bar",
                "category": "Бары",
                "name": "Toryish",
                "equipment": [],
            },
            {
                "id": "vitamin_bar",
                "category": "Бары",
                "name": "Vitamin",
                "equipment": [],
            },
            {
                "id": "banquet_kitchen",
                "category": "Кухни",
                "name": "Банкетная кухня",
                "equipment": [],
            },
            {
                "id": "staff_canteen",
                "category": "Кухни",
                "name": "Столовая персонала",
                "equipment": [],
            },
            {
                "id": "food_warehouses",
                "category": "Склады",
                "name": "Продовольственные склады",
                "equipment": [],
            },
            {
                "id": "cold_rooms",
                "category": "Склады",
                "name": "Холодильные камеры",
                "equipment": [],
            },
        ],
    }
]


def create_id():
    return uuid.uuid4().hex


def ensure_database():
    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if not HACCP_FILE.exists():
        save_objects(DEFAULT_OBJECTS)


def load_objects():
    ensure_database()

    try:
        with HACCP_FILE.open(
            "r",
            encoding="utf-8-sig"
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except Exception as error:
        print("Ошибка чтения HACCP:")
        print(error)

    return []


def save_objects(objects):
    DATABASE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    temporary_file = HACCP_FILE.with_suffix(
        ".tmp"
    )

    try:
        with temporary_file.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                objects,
                file,
                ensure_ascii=False,
                indent=2
            )

        temporary_file.replace(
            HACCP_FILE
        )

        return True

    except Exception as error:
        print("Ошибка сохранения HACCP:")
        print(error)

        messagebox.showerror(
            "SanEpi AI",
            f"Не удалось сохранить данные:\n{error}"
        )

        return False


def build_haccp_page(parent):
    objects = load_objects()

    selected_object_id = {
        "value": (
            objects[0].get("id")
            if objects
            else None
        )
    }

    ctk.CTkLabel(
        parent,
        text="📊 HACCP",
        font=("Arial", 34, "bold")
    ).pack(
        pady=(20, 5)
    )

    ctk.CTkLabel(
        parent,
        text=(
            "Управление объектами, подразделениями "
            "и оборудованием пищевой безопасности"
        ),
        font=("Arial", 14),
        text_color="#9ca3af"
    ).pack(
        pady=(0, 15)
    )
    summary_frame = ctk.CTkFrame(
        parent,
        fg_color="transparent"
    )
    summary_frame.pack(
        fill="x",
        padx=20,
        pady=(0, 10)
    )
    ctk.CTkButton(
        summary_frame,
        text="⏰ Контроль замеров",
        width=220,
        height=40,
        fg_color="#d97706",
        hover_color="#b45309",
        command=lambda: open_missing_measurements_window(
            parent
        )
    ).pack(
        side="right",
        padx=(10, 0)
    )
    ctk.CTkButton(
        summary_frame,
        text="📊 Общий журнал",
        width=200,
        height=40,
        fg_color="#059669",
        hover_color="#047857",
        command=lambda: open_haccp_summary(parent)
    ).pack(
        side="right"
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

    main_frame.grid_columnconfigure(
        0,
        weight=2
    )
    main_frame.grid_columnconfigure(
        1,
        weight=4
    )
    main_frame.grid_rowconfigure(
        0,
        weight=1
    )

    object_panel = ctk.CTkFrame(
        main_frame,
        corner_radius=12
    )
    object_panel.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=(10, 5),
        pady=10
    )

    department_panel = ctk.CTkFrame(
        main_frame,
        corner_radius=12
    )
    department_panel.grid(
        row=0,
        column=1,
        sticky="nsew",
        padx=(5, 10),
        pady=10
    )

    ctk.CTkLabel(
        object_panel,
        text="Объекты",
        font=("Arial", 22, "bold")
    ).pack(
        anchor="w",
        padx=15,
        pady=(18, 10)
    )

    object_list = ctk.CTkScrollableFrame(
        object_panel,
        corner_radius=10
    )
    object_list.pack(
        fill="both",
        expand=True,
        padx=12,
        pady=(0, 10)
    )

    object_buttons = ctk.CTkFrame(
        object_panel,
        fg_color="transparent"
    )
    object_buttons.pack(
        fill="x",
        padx=12,
        pady=(0, 12)
    )

    object_buttons.grid_columnconfigure(
        0,
        weight=1
    )
    object_buttons.grid_columnconfigure(
        1,
        weight=1
    )

    add_object_button = ctk.CTkButton(
        object_buttons,
        text="➕ Добавить объект",
        height=40
    )
    add_object_button.grid(
        row=0,
        column=0,
        columnspan=2,
        sticky="ew",
        pady=(0, 6)
    )

    edit_object_button = ctk.CTkButton(
        object_buttons,
        text="✏️ Изменить",
        height=38,
        fg_color="#7c3aed",
        hover_color="#6d28d9"
    )
    edit_object_button.grid(
        row=1,
        column=0,
        sticky="ew",
        padx=(0, 4)
    )

    delete_object_button = ctk.CTkButton(
        object_buttons,
        text="🗑️ Удалить",
        height=38,
        fg_color="#dc2626",
        hover_color="#b91c1c"
    )
    delete_object_button.grid(
        row=1,
        column=1,
        sticky="ew",
        padx=(4, 0)
    )

    department_header = ctk.CTkFrame(
        department_panel,
        fg_color="transparent"
    )
    department_header.pack(
        fill="x",
        padx=18,
        pady=(18, 10)
    )

    department_title = ctk.CTkLabel(
        department_header,
        text="Выберите объект",
        font=("Arial", 24, "bold"),
        wraplength=650,
        justify="left"
    )
    department_title.pack(
        side="left",
        anchor="w"
    )

    add_department_button = ctk.CTkButton(
        department_header,
        text="➕ Добавить подразделение",
        width=220,
        height=38
    )
    add_department_button.pack(
        side="right"
    )

    department_list = ctk.CTkScrollableFrame(
        department_panel,
        corner_radius=10
    )
    department_list.pack(
        fill="both",
        expand=True,
        padx=15,
        pady=(0, 15)
    )

    def get_selected_object():
        object_id = selected_object_id["value"]

        for item in objects:
            if item.get("id") == object_id:
                return item

        return None

    def select_object(object_id):
        selected_object_id["value"] = object_id

        render_objects()
        render_departments()

    def render_objects():
        for widget in (
            object_list.winfo_children()
        ):
            widget.destroy()

        if not objects:
            ctk.CTkLabel(
                object_list,
                text=(
                    "Объекты не добавлены.\n"
                    "Нажмите «Добавить объект»."
                ),
                font=("Arial", 14),
                text_color="#9ca3af",
                justify="center"
            ).pack(
                padx=10,
                pady=30
            )

            edit_object_button.configure(
                state="disabled"
            )
            delete_object_button.configure(
                state="disabled"
            )

            return

        edit_object_button.configure(
            state="normal"
        )
        delete_object_button.configure(
            state="normal"
        )

        for item in objects:
            is_selected = (
                item.get("id")
                == selected_object_id["value"]
            )

            ctk.CTkButton(
                object_list,
                text=(
                    f"🏢 "
                    f"{item.get('name', 'Объект')}"
                ),
                anchor="w",
                height=54,
                fg_color=(
                    "#1d4ed8"
                    if is_selected
                    else "#2563eb"
                ),
                hover_color="#1e40af",
                command=(
                    lambda object_id=item.get("id"):
                    select_object(object_id)
                )
            ).pack(
                fill="x",
                padx=5,
                pady=5
            )

    def open_department_equipment(
        department
    ):
        selected_object = get_selected_object()

        if not selected_object:
            return

        open_equipment_window(
            parent=parent,
            object_name=selected_object.get(
                "name",
                "Объект"
            ),
            department=department,
            save_callback=lambda: save_objects(
                objects
            )
        )

    def render_departments():
        for widget in (
            department_list.winfo_children()
        ):
            widget.destroy()

        selected_object = get_selected_object()

        if not selected_object:
            department_title.configure(
                text="Выберите объект"
            )

            add_department_button.configure(
                state="disabled"
            )

            ctk.CTkLabel(
                department_list,
                text="Сначала добавьте объект.",
                font=("Arial", 15),
                text_color="#9ca3af"
            ).pack(
                pady=40
            )

            return

        add_department_button.configure(
            state="normal"
        )

        department_title.configure(
            text=selected_object.get(
                "name",
                "Объект"
            )
        )

        departments = selected_object.get(
            "departments",
            []
        )

        if not departments:
            ctk.CTkLabel(
                department_list,
                text=(
                    "Подразделения не добавлены.\n"
                    "Нажмите «Добавить подразделение»."
                ),
                font=("Arial", 15),
                text_color="#9ca3af",
                justify="center"
            ).pack(
                pady=40
            )

            return

        categories = {}

        for department in departments:
            department.setdefault(
                "equipment",
                []
            )

            category = str(
                department.get(
                    "category",
                    "Другие"
                )
            ).strip()

            if not category:
                category = "Другие"

            categories.setdefault(
                category,
                []
            ).append(department)

        for category in sorted(categories):
            category_frame = ctk.CTkFrame(
                department_list,
                corner_radius=10
            )
            category_frame.pack(
                fill="x",
                padx=6,
                pady=7
            )

            ctk.CTkLabel(
                category_frame,
                text=f"📁 {category}",
                font=("Arial", 17, "bold")
            ).pack(
                anchor="w",
                padx=14,
                pady=(12, 7)
            )

            for department in categories[category]:
                row = ctk.CTkFrame(
                    category_frame,
                    fg_color="transparent"
                )
                row.pack(
                    fill="x",
                    padx=12,
                    pady=4
                )

                equipment_count = len(
                    department.get(
                        "equipment",
                        []
                    )
                )

                ctk.CTkButton(
                    row,
                    text=(
                        f"🌡️ "
                        f"{department.get('name', '')} "
                        f"({equipment_count})"
                    ),
                    font=("Arial", 15),
                    anchor="w",
                    height=40,
                    fg_color="#374151",
                    hover_color="#4b5563",
                    command=(
                        lambda item=department:
                        open_department_equipment(
                            item
                        )
                    )
                ).pack(
                    side="left",
                    fill="x",
                    expand=True,
                    padx=(5, 8),
                    pady=5
                )

                ctk.CTkButton(
                    row,
                    text="Удалить",
                    width=90,
                    height=40,
                    fg_color="#dc2626",
                    hover_color="#b91c1c",
                    command=(
                        lambda department_id=(
                            department.get("id")
                        ):
                        delete_department(
                            department_id
                        )
                    )
                ).pack(
                    side="right",
                    padx=(0, 5),
                    pady=5
                )

    def add_object():
        dialog = ctk.CTkInputDialog(
            title="Новый объект",
            text=(
                "Введите название объекта:\n"
                "например, TETHYS AKTAU II"
            )
        )

        name = dialog.get_input()

        if not name:
            return

        name = name.strip()

        if not name:
            return

        new_object = {
            "id": create_id(),
            "name": name,
            "departments": [],
        }

        objects.append(new_object)

        if save_objects(objects):
            selected_object_id["value"] = (
                new_object["id"]
            )

            render_objects()
            render_departments()

    def edit_object():
        selected_object = get_selected_object()

        if not selected_object:
            return

        current_name = selected_object.get(
            "name",
            ""
        )

        dialog = ctk.CTkInputDialog(
            title="Изменить объект",
            text=(
                "Введите новое название:\n"
                f"Текущее: {current_name}"
            )
        )

        new_name = dialog.get_input()

        if not new_name:
            return

        new_name = new_name.strip()

        if not new_name:
            return

        selected_object["name"] = new_name

        if save_objects(objects):
            render_objects()
            render_departments()

    def delete_object():
        selected_object = get_selected_object()

        if not selected_object:
            return

        name = selected_object.get(
            "name",
            "Объект"
        )

        confirmed = messagebox.askyesno(
            "Удаление объекта",
            (
                f"Удалить объект?\n\n{name}\n\n"
                "Все подразделения и оборудование "
                "этого объекта также будут удалены."
            )
        )

        if not confirmed:
            return

        objects.remove(selected_object)

        selected_object_id["value"] = (
            objects[0].get("id")
            if objects
            else None
        )

        if save_objects(objects):
            render_objects()
            render_departments()

    def add_department():
        selected_object = get_selected_object()

        if not selected_object:
            return

        category_dialog = ctk.CTkInputDialog(
            title="Категория",
            text=(
                "Введите категорию:\n"
                "например: Рестораны, Бары, "
                "Кухни или Склады"
            )
        )

        category = category_dialog.get_input()

        if not category:
            return

        category = category.strip()

        if not category:
            return

        name_dialog = ctk.CTkInputDialog(
            title="Подразделение",
            text=(
                "Введите название подразделения:"
            )
        )

        name = name_dialog.get_input()

        if not name:
            return

        name = name.strip()

        if not name:
            return

        selected_object.setdefault(
            "departments",
            []
        ).append(
            {
                "id": create_id(),
                "category": category,
                "name": name,
                "equipment": [],
            }
        )

        if save_objects(objects):
            render_departments()

    def delete_department(
        department_id
    ):
        selected_object = get_selected_object()

        if not selected_object:
            return

        departments = selected_object.get(
            "departments",
            []
        )

        department = next(
            (
                item
                for item in departments
                if item.get("id")
                == department_id
            ),
            None
        )

        if not department:
            return

        equipment_count = len(
            department.get(
                "equipment",
                []
            )
        )

        warning = ""

        if equipment_count:
            warning = (
                f"\n\nВ подразделении находится "
                f"оборудование: {equipment_count}."
            )

        confirmed = messagebox.askyesno(
            "Удаление подразделения",
            (
                "Удалить подразделение?\n\n"
                f"{department.get('name', '')}"
                f"{warning}"
            )
        )

        if not confirmed:
            return

        departments.remove(department)

        if save_objects(objects):
            render_departments()

    add_object_button.configure(
        command=add_object
    )

    edit_object_button.configure(
        command=edit_object
    )

    delete_object_button.configure(
        command=delete_object
    )

    add_department_button.configure(
        command=add_department
    )

    render_objects()
    render_departments()
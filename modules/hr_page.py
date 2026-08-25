import customtkinter as ctk

from modules.dashboard_data import load_dashboard_data, get_department
from modules.employee_card import show_employee_card
from modules.translations import tr
from modules.localization import translate_department


def make_stat_card(parent, title, value, color):
    card = ctk.CTkFrame(parent, corner_radius=14)
    card.pack(side="left", padx=8, pady=8, fill="x", expand=True)

    ctk.CTkLabel(
        card,
        text=title,
        font=("Arial", 13, "bold"),
        text_color=color
    ).pack(pady=(10, 4))

    ctk.CTkLabel(
        card,
        text=str(value),
        font=("Arial", 24, "bold")
    ).pack(pady=(0, 10))


def build_hr_page(parent):
    data = load_dashboard_data()
    hr = data["hr"]
    compare = data["compare"]

    only_hr_names = set()
    for emp in compare.get("only_hr", []):
        only_hr_names.add(str(emp.get("Сотрудник", "")).strip().lower())

    departments = sorted(set(get_department(emp) for emp in hr))

    total_hr = len(hr)
    only_hr_count = len(compare.get("only_hr", []))
    exists_count = total_hr - only_hr_count

    all_departments_text = tr("all_departments")
    all_statuses_text = tr("all_statuses")
    exists_text = tr("exists_in_esen")
    not_exists_text = tr("not_in_esen")

    def reload_page():
        for widget in parent.winfo_children():
            widget.destroy()
        build_hr_page(parent)

    def import_hr_excel():
        from modules import excel_employees
        from modules import compare_employees

        employees = excel_employees.choose_excel()

        if employees is None:
            return

        if hasattr(compare_employees, "run_compare"):
            compare_employees.run_compare()
        elif hasattr(compare_employees, "compare_employees"):
            compare_employees.compare_employees()
        elif hasattr(compare_employees, "run"):
            compare_employees.run()

        reload_page()

    def compare_with_esen():
        from modules import compare_employees

        result = compare_employees.run_compare()

        print("✅ Сравнение завершено")
        print(f"Совпали: {len(result['matched'])}")
        print(f"Нет в e-SEN: {len(result['only_hr'])}")
        print(f"Нет в HR: {len(result['only_esen'])}")

        reload_page()

    ctk.CTkLabel(
        parent,
        text=f"👥 {tr('hr_employees')}",
        font=("Arial", 34, "bold")
    ).pack(pady=(20, 10))

    stats_frame = ctk.CTkFrame(parent, corner_radius=14)
    stats_frame.pack(padx=20, pady=10, fill="x")

    make_stat_card(stats_frame, f"👥 {tr('total_hr')}", total_hr, "#60a5fa")
    make_stat_card(stats_frame, f" {exists_text}", exists_count, "#22c55e")
    make_stat_card(stats_frame, f"🔴 {not_exists_text}", only_hr_count, "#ef4444")
    make_stat_card(stats_frame, f"🏢 {tr('departments')}", len(departments), "#a78bfa")

    action_frame = ctk.CTkFrame(parent, corner_radius=14)
    action_frame.pack(padx=20, pady=10, fill="x")

    ctk.CTkButton(
        action_frame,
        text=f"📥 {tr('import_hr_excel')}",
        width=240,
        height=40,
        command=import_hr_excel
    ).pack(side="left", padx=10, pady=10)

    ctk.CTkButton(
        action_frame,
        text=f"⚖️ {tr('compare_with_esen')}",
        width=240,
        height=40,
        command=compare_with_esen
    ).pack(side="left", padx=10, pady=10)

    filter_frame = ctk.CTkFrame(parent, corner_radius=14)
    filter_frame.pack(padx=20, pady=10, fill="x")

    search_var = ctk.StringVar()
    dep_var = ctk.StringVar(value=all_departments_text)
    status_var = ctk.StringVar(value=all_statuses_text)

    ctk.CTkEntry(
        filter_frame,
        textvariable=search_var,
        placeholder_text=f"🔍 {tr('search_hr')}",
        width=350,
        height=38
    ).grid(row=0, column=0, padx=15, pady=15)

    department_values = [all_departments_text] + [
        translate_department(dep) for dep in departments
    ]

    ctk.CTkOptionMenu(
        filter_frame,
        variable=dep_var,
        values=department_values,
        width=250,
        height=38
    ).grid(row=0, column=1, padx=15, pady=15)

    ctk.CTkOptionMenu(
        filter_frame,
        variable=status_var,
        values=[
            all_statuses_text,
            exists_text,
            not_exists_text
        ],
        width=200,
        height=38
    ).grid(row=0, column=2, padx=15, pady=15)

    # ДОБАВЛЕНА ГОРИЗОНТАЛЬНАЯ ПРОКРУТКА ДЛЯ ТАБЛИЦЫ
    table_scroll = ctk.CTkScrollableFrame(
        parent, 
        corner_radius=14, 
        orientation="horizontal",  # Горизонтальная прокрутка
        scrollbar_button_color="#0d3d4b",
        scrollbar_button_hover_color="#155e75",
    )
    table_scroll.pack(padx=20, pady=10, fill="both", expand=True)

    # Внутренний контейнер для таблицы (фиксированная минимальная ширина)
    table = ctk.CTkFrame(table_scroll, fg_color="transparent")
    table.pack(fill="both", expand=True)
    table.configure(width=1200)  # Минимальная ширина таблицы

    def clear_table():
        for widget in table.winfo_children():
            widget.destroy()

    def render():
        clear_table()

        headers = [
            tr("fio"),
            tr("department"),
            tr("position"),
            tr("esen_status")
        ]

        # Увеличенные ширины колонок
        col_widths = [300, 250, 350, 200]

        for col, (header, width) in enumerate(zip(headers, col_widths)):
            ctk.CTkLabel(
                table,
                text=header,
                font=("Arial", 15, "bold"),
                width=width,
                anchor="w"
            ).grid(row=0, column=col, padx=12, pady=8, sticky="w")

        query = search_var.get().strip().lower()
        selected_dep = dep_var.get()
        selected_status = status_var.get()

        row_index = 1

        for emp in hr:
            name = str(emp.get("Сотрудник", "")).strip()
            position = str(emp.get("Должность", "")).strip()
            dep = get_department(emp)

            status_key = "not_in_esen" if name.lower() in only_hr_names else "exists_in_esen"
            status_plain = tr(status_key)
            status_text = f"🔴 {tr('not_in_esen')}" if status_key == "not_in_esen" else f" {tr('exists_in_esen')}"

            if query:
                searchable = f"{name} {position} {dep} {translate_department(dep)}".lower()
                if query not in searchable:
                    continue

            if selected_dep != all_departments_text and translate_department(dep) != selected_dep:
                continue

            if selected_status != all_statuses_text and status_plain != selected_status:
                continue

            values = [
                name,
                translate_department(dep),
                position,
                status_text
            ]

            for col, (value, width) in enumerate(zip(values, col_widths)):
                if col == 0:
                    ctk.CTkButton(
                        table,
                        text=value,
                        width=width,
                        anchor="w",
                        command=lambda e=emp: show_employee_card(e)
                    ).grid(row=row_index, column=col, padx=12, pady=5, sticky="w")
                else:
                    ctk.CTkLabel(
                        table,
                        text=str(value),
                        font=("Arial", 14),
                        width=width,
                        anchor="w",
                        text_color="#ef4444" if status_key == "not_in_esen" and col == 3 else None
                    ).grid(row=row_index, column=col, padx=12, pady=5, sticky="w")

            row_index += 1

        if row_index == 1:
            ctk.CTkLabel(
                table,
                text=tr("nothing_found"),
                font=("Arial", 16)
            ).grid(row=1, column=0, padx=12, pady=20, sticky="w")

    search_var.trace_add("write", lambda *args: render())
    dep_var.trace_add("write", lambda *args: render())
    status_var.trace_add("write", lambda *args: render())

    render()
import tkinter as tk
import customtkinter as ctk

from modules.dashboard_data import load_dashboard_data, get_department
from modules.employee_card import show_employee_card
from modules.translations import tr
from modules.localization import translate_department
from modules.loading_button import run_with_loading


def make_stat_card(parent, title, value, color):
    card = ctk.CTkFrame(parent, corner_radius=14)
    
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
    
    return card


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

    # ✅ ИНДИКАТОР ЗАГРУЗКИ для импорта HR Excel
    def import_hr_excel_with_loading():
        def task():
            from modules import excel_employees
            from modules import compare_employees
            employees = excel_employees.choose_excel()
            if employees is None:
                return False
            if hasattr(compare_employees, "run_compare"):
                compare_employees.run_compare()
            elif hasattr(compare_employees, "compare_employees"):
                compare_employees.compare_employees()
            elif hasattr(compare_employees, "run"):
                compare_employees.run()
            return True
        
        def on_complete():
            reload_page()
        
        run_with_loading(btn_import, task, success_message="✅ HR Excel импортирован!")
        parent.after(1500, on_complete)

    # ✅ ИНДИКАТОР ЗАГРУЗКИ для сравнения с e-SEN
    def compare_with_esen_with_loading():
        def task():
            from modules import compare_employees
            result = compare_employees.run_compare()
            print("✅ Сравнение завершено")
            print(f"Совпали: {len(result['matched'])}")
            print(f"Нет в e-SEN: {len(result['only_hr'])}")
            print(f"Нет в HR: {len(result['only_esen'])}")
        
        run_with_loading(btn_compare, task, success_message="✅ Сравнение с e-SEN завершено!")
        parent.after(1500, reload_page)

    ctk.CTkLabel(
        parent,
        text=f"👥 {tr('hr_employees')}",
        font=("Arial", 34, "bold")
    ).pack(pady=(20, 10))

    stats_frame = ctk.CTkFrame(parent, corner_radius=14)
    stats_frame.pack(padx=20, pady=10, fill="x")
    
    for i in range(4):
        stats_frame.grid_columnconfigure(i, weight=1, minsize=150)

    cards = [
        (f" {tr('total_hr')}", total_hr, "#60a5fa"),
        (f"🟢 {exists_text}", exists_count, "#22c55e"),
        (f" {not_exists_text}", only_hr_count, "#ef4444"),
        (f" {tr('departments')}", len(departments), "#a78bfa"),
    ]

    for i, (title, value, color) in enumerate(cards):
        card = make_stat_card(stats_frame, title, value, color)
        card.grid(row=0, column=i, padx=8, pady=8, sticky="nsew")

    action_frame = ctk.CTkFrame(parent, corner_radius=14)
    action_frame.pack(padx=20, pady=10, fill="x")

    # ✅ Кнопки с сохранением ссылок для блокировки
    btn_import = ctk.CTkButton(
        action_frame,
        text=f"📥 {tr('import_hr_excel')}",
        width=240,
        height=40,
        command=import_hr_excel_with_loading
    )
    btn_import.pack(side="left", padx=10, pady=10)

    btn_compare = ctk.CTkButton(
        action_frame,
        text=f"⚖️ {tr('compare_with_esen')}",
        width=240,
        height=40,
        command=compare_with_esen_with_loading
    )
    btn_compare.pack(side="left", padx=10, pady=10)

    filter_frame = ctk.CTkFrame(parent, corner_radius=14)
    filter_frame.pack(padx=20, pady=10, fill="x")

    search_var = ctk.StringVar()
    dep_var = ctk.StringVar(value=all_departments_text)
    status_var = ctk.StringVar(value=all_statuses_text)

    ctk.CTkEntry(
        filter_frame,
        textvariable=search_var,
        placeholder_text=f" {tr('search_hr')}",
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

    table_outer = ctk.CTkFrame(parent, corner_radius=14, fg_color="#07222b")
    table_outer.pack(padx=20, pady=10, fill="both", expand=True)

    canvas = tk.Canvas(
        table_outer,
        bg="#07222b",
        highlightthickness=0,
        scrollregion=(0, 0, 1500, 5000)
    )
    
    v_scrollbar = ctk.CTkScrollbar(
        table_outer,
        orientation="vertical",
        command=canvas.yview,
        button_color="#0d3d4b",
        button_hover_color="#155e75"
    )
    v_scrollbar.pack(side="right", fill="y")
    
    h_scrollbar = ctk.CTkScrollbar(
        table_outer,
        orientation="horizontal",
        command=canvas.xview,
        button_color="#0d3d4b",
        button_hover_color="#155e75"
    )
    h_scrollbar.pack(side="bottom", fill="x")
    
    canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)

    table_inner = ctk.CTkFrame(canvas, fg_color="transparent")
    canvas.create_window((0, 0), window=table_inner, anchor="nw")

    def clear_table():
        for widget in table_inner.winfo_children():
            widget.destroy()

    def render():
        clear_table()

        headers = [
            tr("fio"),
            tr("department"),
            tr("position"),
            tr("esen_status")
        ]

        col_widths = [300, 250, 350, 200]

        for col, (header, width) in enumerate(zip(headers, col_widths)):
            ctk.CTkLabel(
                table_inner,
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
            status_text = f" {tr('not_in_esen')}" if status_key == "not_in_esen" else f" {tr('exists_in_esen')}"

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
                        table_inner,
                        text=value,
                        width=width,
                        anchor="w",
                        command=lambda e=emp: show_employee_card(e)
                    ).grid(row=row_index, column=col, padx=12, pady=5, sticky="w")
                else:
                    ctk.CTkLabel(
                        table_inner,
                        text=str(value),
                        font=("Arial", 14),
                        width=width,
                        anchor="w",
                        text_color="#ef4444" if status_key == "not_in_esen" and col == 3 else None
                    ).grid(row=row_index, column=col, padx=12, pady=5, sticky="w")

            row_index += 1

        if row_index == 1:
            ctk.CTkLabel(
                table_inner,
                text=tr("nothing_found"),
                font=("Arial", 16)
            ).grid(row=1, column=0, padx=12, pady=20, sticky="w")

        table_inner.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    search_var.trace_add("write", lambda *args: render())
    dep_var.trace_add("write", lambda *args: render())
    status_var.trace_add("write", lambda *args: render())

    render()
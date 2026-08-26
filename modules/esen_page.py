import tkinter as tk
import customtkinter as ctk

from modules.dashboard_data import load_dashboard_data, clear_dashboard_cache
from modules.translations import tr


def make_stat_card(parent, title, value, color):
    card = ctk.CTkFrame(parent, corner_radius=14, height=100)
    card.pack_propagate(False)
    
    ctk.CTkLabel(
        card, 
        text=title, 
        font=("Arial", 11, "bold"),
        text_color=color,
        wraplength=160,
        justify="center"
    ).pack(pady=(10, 5), padx=10)
    
    ctk.CTkLabel(
        card, 
        text=str(value), 
        font=("Arial", 28, "bold"),
    ).pack(pady=(0, 10))

    return card


def build_esen_page(parent):
    data = load_dashboard_data()

    esen_data = data["esen"]
    compare = data["compare"]
    quality = data["quality"]

    total = len(esen_data)
    only_esen = len(compare.get("only_esen", []))
    matched = len(compare.get("matched", []))
    duplicate_count = quality.get("duplicates", 0)
    bad_count = quality.get("bad_records", 0)
    expiring_count = data.get("expiring_count", 0)

    ctk.CTkLabel(
        parent,
        text=f"🏥 {tr('esen_center')}",
        font=("Arial", 34, "bold")
    ).pack(pady=(20, 10))

    stats_frame = ctk.CTkFrame(parent, corner_radius=14)
    stats_frame.pack(fill="x", padx=20, pady=10)

    cards = [
        (f" {tr('total_esen')}", total, "#60a5fa"),
        (f" {tr('exists_in_hr')}", matched, "#22c55e"),
        (f"🟡 {tr('not_in_hr')}", only_esen, "#f59e0b"),
        (f"⏰ {tr('expiring')}", expiring_count, "#f97316"),
        (f"🔄 {tr('medbooks')}", duplicate_count, "#3b82f6"),
        (f"⚠️ {tr('errors')}", bad_count, "#dc2626"),
    ]

    for i, (title, value, color) in enumerate(cards):
        card = make_stat_card(stats_frame, title, value, color)
        card.grid(row=0, column=i, padx=6, pady=8, sticky="nsew")
        stats_frame.grid_columnconfigure(i, weight=1)
    
    for i in range(len(cards)):
        stats_frame.grid_columnconfigure(i, weight=1, minsize=140)

    action_frame = ctk.CTkFrame(parent, corner_radius=14)
    action_frame.pack(fill="x", padx=20, pady=10)

    def rebuild_page():
        for widget in parent.winfo_children():
            widget.destroy()
        build_esen_page(parent)

    def refresh_esen():
        from modules import esen
        esen.open_esen_login()
        clear_dashboard_cache()
        rebuild_page()

    def compare_with_hr():
        from modules import compare_employees
        from modules.export_reports import export_missing_separate_files_by_departments
        export_missing_separate_files_by_departments()
        if hasattr(compare_employees, "run_compare"):
            compare_employees.run_compare()
        elif hasattr(compare_employees, "compare_employees"):
            compare_employees.compare_employees()
        elif hasattr(compare_employees, "run"):
            compare_employees.run()
        clear_dashboard_cache()
        rebuild_page()

    def show_only_esen():
        window = ctk.CTkToplevel()
        window.title(tr("not_in_hr"))
        window.geometry("900x650")
        window.lift()
        window.focus_force()

        ctk.CTkLabel(
            window,
            text=f"🟡 {tr('not_in_hr')}",
            font=("Arial", 28, "bold")
        ).pack(pady=20)

        box = ctk.CTkTextbox(window, width=820, height=520, font=("Arial", 14))
        box.pack(padx=20, pady=10)

        only_esen_list = compare.get("only_esen", [])

        if not only_esen_list:
            box.insert("end", f"✅ {tr('not_in_hr')}: 0\n")
        else:
            for i, emp in enumerate(only_esen_list, start=1):
                box.insert("end", f"{i}. {emp.get('fio', '-')}\n")
                box.insert("end", f"   {tr('position')}: {emp.get('position', '-')}\n")
                box.insert("end", f"   {tr('medical_book')}: {emp.get('medical_book', '-')}\n")
                box.insert("end", f"   {tr('period')}: {emp.get('valid_until', '-')}\n")
                box.insert("end", f"   {tr('status')}: {emp.get('status', '-')}\n")
                box.insert("end", "-" * 80 + "\n")

        box.configure(state="disabled")

    actions = [
        (f"🔄 {tr('update_esen')}", refresh_esen),
        (f"⚖️ {tr('compare_with_hr')}", compare_with_hr),
        (f"🟡 {tr('not_in_hr')}", show_only_esen),
        (f"➕ {tr('add_employees')}", None),
        (f"📄 {tr('export_report')}", None),
    ]

    for i, (text, command) in enumerate(actions):
        ctk.CTkButton(
            action_frame,
            text=text,
            width=200,
            height=42,
            command=command
        ).grid(row=0, column=i, padx=8, pady=10)
    
    action_frame.grid_columnconfigure(0, weight=1)
    action_frame.grid_columnconfigure(1, weight=1)
    action_frame.grid_columnconfigure(2, weight=1)
    action_frame.grid_columnconfigure(3, weight=1)
    action_frame.grid_columnconfigure(4, weight=1)

    search_var = ctk.StringVar(value="")

    search_entry = ctk.CTkEntry(
        parent,
        textvariable=search_var,
        placeholder_text="🔍 Поиск по ФИО, должности, медкнижке, статусу...",
        height=38
    )
    search_entry.pack(fill="x", padx=20, pady=(5, 10))

    # ✅ ГОРИЗОНТАЛЬНАЯ + ВЕРТИКАЛЬНАЯ прокрутка через Canvas
    table_outer = ctk.CTkFrame(parent, corner_radius=14, fg_color="#07222b")
    table_outer.pack(fill="both", expand=True, padx=20, pady=15)

    # Создаем Canvas с двумя скроллбарами
    canvas = tk.Canvas(
        table_outer,
        bg="#07222b",
        highlightthickness=0,
        scrollregion=(0, 0, 1500, 5000)
    )
    
    # Вертикальный скроллбар
    v_scrollbar = ctk.CTkScrollbar(
        table_outer,
        orientation="vertical",
        command=canvas.yview,
        button_color="#0d3d4b",
        button_hover_color="#155e75"
    )
    v_scrollbar.pack(side="right", fill="y")
    
    # Горизонтальный скроллбар
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

    # Внутренний фрейм для таблицы
    table_inner = ctk.CTkFrame(canvas, fg_color="transparent")
    canvas.create_window((0, 0), window=table_inner, anchor="nw")

    headers = [
        tr("fio"),
        tr("position"),
        tr("medical_book"),
        tr("period"),
        tr("status"),
    ]
    
    col_widths = [300, 250, 150, 200, 200]

    def clear_table():
        for widget in table_inner.winfo_children():
            widget.destroy()

    def render_table():
        clear_table()

        for col, (header, width) in enumerate(zip(headers, col_widths)):
            ctk.CTkLabel(
                table_inner,
                text=header,
                font=("Arial", 15, "bold"),
                width=width,
                anchor="w"
            ).grid(row=0, column=col, padx=12, pady=8, sticky="w")

        search = search_var.get().lower().strip()
        row = 1

        for emp in esen_data:
            search_text = (
                str(emp.get("fio", "")) + " " +
                str(emp.get("position", "")) + " " +
                str(emp.get("medical_book", "")) + " " +
                str(emp.get("valid_until", "")) + " " +
                str(emp.get("status", ""))
            ).lower()

            if search and search not in search_text:
                continue

            ctk.CTkButton(
                table_inner,
                text=emp.get("fio", "-"),
                width=col_widths[0],
                anchor="w"
            ).grid(row=row, column=0, padx=10, pady=5, sticky="w")

            ctk.CTkLabel(
                table_inner,
                text=emp.get("position", "-"),
                width=col_widths[1],
                anchor="w"
            ).grid(row=row, column=1, padx=10, pady=5, sticky="w")

            ctk.CTkLabel(
                table_inner,
                text=emp.get("medical_book", "-"),
                width=col_widths[2],
                anchor="w"
            ).grid(row=row, column=2, padx=10, pady=5, sticky="w")

            ctk.CTkLabel(
                table_inner,
                text=emp.get("valid_until", "-"),
                width=col_widths[3],
                anchor="w"
            ).grid(row=row, column=3, padx=10, pady=5, sticky="w")

            status = str(emp.get("status", "-"))

            if "допущ" in status.lower() or "қабылдан" in status.lower():
                color = "#22c55e"
            else:
                color = "#ef4444"

            ctk.CTkLabel(
                table_inner,
                text=status,
                text_color=color,
                width=col_widths[4],
                anchor="w"
            ).grid(row=row, column=4, padx=10, pady=5, sticky="w")

            row += 1

        if row == 1:
            ctk.CTkLabel(
                table_inner,
                text=tr("nothing_found"),
                font=("Arial", 16)
            ).grid(row=1, column=0, padx=12, pady=20, sticky="w")

        # Обновляем область прокрутки после рендера
        table_inner.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

    # Привязка колесика мыши для вертикальной прокрутки
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)

    search_var.trace_add("write", lambda *args: render_table())

    render_table()
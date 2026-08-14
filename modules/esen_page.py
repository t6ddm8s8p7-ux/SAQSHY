import customtkinter as ctk

from modules.dashboard_data import load_dashboard_data, clear_dashboard_cache
from modules.translations import tr


def make_stat_card(parent, title, value, color):
    card = ctk.CTkFrame(parent, corner_radius=14)
    card.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(card, text=title, font=("Arial", 14, "bold"), text_color=color).pack(pady=(10, 5))
    ctk.CTkLabel(card, text=str(value), font=("Arial", 24, "bold")).pack(pady=(0, 10))

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
        (f"👥 {tr('total_esen')}", total, "#60a5fa"),
        (f"🟢 {tr('exists_in_hr')}", matched, "#22c55e"),
        (f"🟡 {tr('not_in_hr')}", only_esen, "#f59e0b"),
        (f"⏰ {tr('expiring')}", expiring_count, "#f97316"),
        (f"🔄 {tr('medbooks')}", duplicate_count, "#3b82f6"),
        (f"⚠️ {tr('errors')}", bad_count, "#dc2626"),
    ]

    for i, (title, value, color) in enumerate(cards):
        card = make_stat_card(stats_frame, title, value, color)
        card.grid(row=0, column=i, padx=8, pady=8, sticky="nsew")
        stats_frame.grid_columnconfigure(i, weight=1)

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
            width=220,
            height=42,
            command=command
        ).grid(row=0, column=i, padx=10, pady=10)

    search_var = ctk.StringVar(value="")

    search_entry = ctk.CTkEntry(
        parent,
        textvariable=search_var,
        placeholder_text="🔍 Поиск по ФИО, должности, медкнижке, статусу...",
        height=38
    )
    search_entry.pack(fill="x", padx=20, pady=(5, 10))

    table = ctk.CTkScrollableFrame(parent, corner_radius=14)
    table.pack(fill="both", expand=True, padx=20, pady=15)

    headers = [
        tr("fio"),
        tr("position"),
        tr("medical_book"),
        tr("period"),
        tr("status"),
    ]

    def clear_table():
        for widget in table.winfo_children():
            widget.destroy()

    def render_table():
        clear_table()

        for col, header in enumerate(headers):
            ctk.CTkLabel(
                table,
                text=header,
                font=("Arial", 15, "bold")
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
                table,
                text=emp.get("fio", "-"),
                width=260,
                anchor="w"
            ).grid(row=row, column=0, padx=10, pady=5, sticky="w")

            ctk.CTkLabel(
                table,
                text=emp.get("position", "-")
            ).grid(row=row, column=1, padx=10, sticky="w")

            ctk.CTkLabel(
                table,
                text=emp.get("medical_book", "-")
            ).grid(row=row, column=2, padx=10, sticky="w")

            ctk.CTkLabel(
                table,
                text=emp.get("valid_until", "-")
            ).grid(row=row, column=3, padx=10, sticky="w")

            status = str(emp.get("status", "-"))

            if "допущ" in status.lower() or "қабылдан" in status.lower():
                color = "#22c55e"
            else:
                color = "#ef4444"

            ctk.CTkLabel(
                table,
                text=status,
                text_color=color
            ).grid(row=row, column=4, padx=10, sticky="w")

            row += 1

        if row == 1:
            ctk.CTkLabel(
                table,
                text=tr("nothing_found"),
                font=("Arial", 16)
            ).grid(row=1, column=0, padx=12, pady=20, sticky="w")

    search_var.trace_add("write", lambda *args: render_table())

    render_table()
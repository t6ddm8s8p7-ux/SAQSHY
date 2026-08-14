import customtkinter as ctk

from modules.dashboard_data import get_department
from modules.localization import translate_department
from modules.translations import tr


def show_department_details(dep, compare):
    window = ctk.CTkToplevel()
    window.title(f"{tr('department')} — {translate_department(dep)}")
    window.geometry("1000x700")
    window.lift()
    window.focus_force()

    ctk.CTkLabel(
        window,
        text=f"🏢 {translate_department(dep)}",
        font=("Arial", 28, "bold")
    ).pack(pady=20)

    tabs = ctk.CTkTabview(window, width=900, height=560)
    tabs.pack(padx=20, pady=10)

    categories = {
        f"🟢 {tr('matched')}": compare.get("matched", []),
        f"🔴 {tr('not_in_esen')}": compare.get("only_hr", []),
    }

    for tab_name, items in categories.items():
        tabs.add(tab_name)

        box = ctk.CTkTextbox(
            tabs.tab(tab_name),
            width=850,
            height=500,
            font=("Arial", 14)
        )
        box.pack(padx=10, pady=10)

        found = False

        for item in items:
            if "🔴" in tab_name:
                hr_emp = item
                esen_name = "-"
                similarity = "-"
            else:
                hr_emp = item.get("hr", {})
                esen_name = item.get("esen_name", "-")
                similarity = item.get("similarity", "-")

            if get_department(hr_emp) != dep:
                continue

            found = True

            box.insert("end", f"{tr('fio')}: {hr_emp.get('Сотрудник', '-')}\n")
            box.insert("end", f"{tr('position')}: {hr_emp.get('Должность', '-')}\n")

            if "🟢" in tab_name:
                box.insert("end", f"e-SEN: {esen_name}\n")
                box.insert("end", f"{tr('matched')}: {similarity}%\n")

            box.insert("end", "-" * 80 + "\n")

        if not found:
            box.insert("end", f"{tr('under_development')}\n")

        box.configure(state="disabled")


def build_department_table(parent, departments, dep_compare, compare):
    headers = [
        tr("department"),
        "HR",
        "🟢",
        "🔴"
    ]

    for col, header in enumerate(headers):
        ctk.CTkLabel(
            parent,
            text=header,
            font=("Arial", 16, "bold")
        ).grid(row=0, column=col, padx=20, pady=10, sticky="w")

    for row_index, (dep, count) in enumerate(departments.most_common(), start=1):
        s = dep_compare.get(dep, {"matched": 0, "only_hr": 0})

        values = [
            dep,
            count,
            s["matched"],
            s["only_hr"]
        ]

        for col, value in enumerate(values):
            if col == 0:
                ctk.CTkButton(
                    parent,
                    text=translate_department(str(value)),
                    width=200,
                    fg_color="#2563eb",
                    command=lambda d=dep: show_department_details(d, compare),
                ).grid(row=row_index, column=col, padx=20, pady=7, sticky="w")
            else:
                ctk.CTkLabel(
                    parent,
                    text=str(value),
                    font=("Arial", 16, "bold")
                ).grid(row=row_index, column=col, padx=20, pady=7, sticky="w")
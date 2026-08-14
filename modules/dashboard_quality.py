import customtkinter as ctk


def show_quality_details(quality):
    window = ctk.CTkToplevel()
    window.title("Качество данных e-SEN")
    window.geometry("1000x700")
    window.lift()
    window.focus_force()

    ctk.CTkLabel(
        window,
        text="⚠️ Качество данных e-SEN",
        font=("Arial", 28, "bold")
    ).pack(pady=20)

    tabs = ctk.CTkTabview(window, width=900, height=560)
    tabs.pack(padx=20, pady=10)

    tabs.add("🔄 Несколько медкнижек")
    tabs.add("⚠️ Ошибки ФИО")

    dup_box = ctk.CTkTextbox(
        tabs.tab("🔄 Несколько медкнижек"),
        width=850,
        height=500,
        font=("Arial", 14)
    )
    dup_box.pack(padx=10, pady=10)

    duplicates = quality.get("duplicates_list", [])

    if not duplicates:
        dup_box.insert("end", "✅ Несколько медкнижек не найдено.\n")
    else:
        for item in duplicates:
            dup_box.insert("end", f"ФИО: {item.get('fio', '-')}\n")
            dup_box.insert("end", f"Используется медкнижка: {item.get('used_medbook', '-')}\n")
            dup_box.insert("end", f"Срок: {item.get('used_valid_until', '-')}\n")
            dup_box.insert("end", f"Старых медкнижек: {len(item.get('old_records', []))}\n")
            dup_box.insert("end", "-" * 80 + "\n")

    dup_box.configure(state="disabled")

    bad_box = ctk.CTkTextbox(
        tabs.tab("⚠️ Ошибки ФИО"),
        width=850,
        height=500,
        font=("Arial", 14)
    )
    bad_box.pack(padx=10, pady=10)

    bad_records = quality.get("bad_records_list", [])

    if not bad_records:
        bad_box.insert("end", "✅ Ошибок ФИО не найдено.\n")
    else:
        for emp in bad_records:
            bad_box.insert("end", f"ФИО: {emp.get('fio', '-')}\n")
            bad_box.insert("end", f"Медкнижка: {emp.get('medical_book', '-')}\n")
            bad_box.insert("end", f"Должность: {emp.get('position', '-')}\n")
            bad_box.insert("end", f"Срок: {emp.get('valid_until', '-')}\n")
            bad_box.insert("end", f"Проблема: {emp.get('data_problem', '-')}\n")
            bad_box.insert("end", "-" * 80 + "\n")

    bad_box.configure(state="disabled")
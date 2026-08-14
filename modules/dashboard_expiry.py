import customtkinter as ctk

from modules.medical_expiry import get_expiring_medbooks


def show_expiring_details():
    expiring = get_expiring_medbooks(30)

    window = ctk.CTkToplevel()
    window.title("Истекающие медкнижки")
    window.geometry("1000x700")
    window.lift()
    window.focus_force()

    ctk.CTkLabel(
        window,
        text="⏰ Медкнижки, истекающие в течение 30 дней",
        font=("Arial", 26, "bold")
    ).pack(pady=20)

    box = ctk.CTkTextbox(window, width=900, height=560, font=("Arial", 14))
    box.pack(padx=20, pady=10)

    if not expiring:
        box.insert("end", "✅ Истекающих медкнижек нет.\n")
    else:
        for emp in expiring:
            box.insert("end", f"ФИО: {emp.get('fio', '-')}\n")
            box.insert("end", f"Должность: {emp.get('position', '-')}\n")
            box.insert("end", f"Медкнижка: {emp.get('medical_book', '-')}\n")
            box.insert("end", f"Группа: {emp.get('group', '-')}\n")
            box.insert("end", f"Срок: {emp.get('valid_until', '-')}\n")
            box.insert("end", f"Осталось дней: {emp.get('days_left', '-')}\n")
            box.insert("end", f"Статус: {emp.get('status', '-')}\n")
            box.insert("end", "-" * 80 + "\n")

    box.configure(state="disabled")
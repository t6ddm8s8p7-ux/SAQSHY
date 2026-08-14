import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime

from modules.suppliers_db import (
    add_supplier,
    delete_supplier,
    get_all_suppliers,
)


def build_suppliers_page(parent):
    """Главная страница контроля поставщиков"""

    ctk.CTkLabel(
        parent,
        text="📦 Контроль поставщиков товаров",
        font=("Arial", 28, "bold")
    ).pack(pady=(20, 10))

    ctk.CTkLabel(
        parent,
        text="Приёмка, сертификаты, оценка качества",
        font=("Arial", 14)
    ).pack(pady=(0, 20))

    tabview = ctk.CTkTabview(parent, width=1100, height=600)
    tabview.pack(pady=10, padx=20, fill="both", expand=True)

    tab_suppliers = tabview.add("🏢 Поставщики")
    tab_receiving = tabview.add("📥 Приёмка товаров")
    tab_certificates = tabview.add("📜 Сертификаты")
    tab_violations = tabview.add("⚠️ Нарушения")

    def refresh_suppliers_tab():
        """Обновляет список поставщиков после добавления/удаления"""
        for widget in tab_suppliers.winfo_children():
            widget.destroy()
        _build_suppliers_tab(tab_suppliers, refresh_suppliers_tab)

    _build_suppliers_tab(tab_suppliers, refresh_suppliers_tab)
    _build_receiving_tab(tab_receiving)
    _build_certificates_tab(tab_certificates)
    _build_violations_tab(tab_violations)


def _build_suppliers_tab(parent, on_refresh):
    """Реестр поставщиков (данные из базы)"""

    btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
    btn_frame.pack(pady=10, fill="x")

    ctk.CTkButton(
        btn_frame,
        text="➕ Добавить поставщика",
        width=200,
        command=lambda: _add_supplier_dialog(parent, on_refresh)
    ).pack(side="left", padx=5)

    ctk.CTkButton(
        btn_frame,
        text="🔄 Обновить список",
        width=160,
        fg_color="gray",
        command=on_refresh
    ).pack(side="left", padx=5)

    table_frame = ctk.CTkScrollableFrame(parent, width=1050, height=450)
    table_frame.pack(pady=10, fill="both", expand=True)

    headers = [
        "🏢 Поставщик",
        "📞 Контакт",
        "📦 Категория",
        "⭐ Рейтинг",
        "📄 Сертификаты",
        "Действия",
    ]

    for i, header in enumerate(headers):
        ctk.CTkLabel(
            table_frame,
            text=header,
            font=("Arial", 13, "bold"),
            anchor="w"
        ).grid(row=0, column=i, padx=10, pady=5, sticky="w")

    suppliers = get_all_suppliers()

    if not suppliers:
        ctk.CTkLabel(
            table_frame,
            text="Пока нет поставщиков.\nНажмите '➕ Добавить поставщика', чтобы внести первого.",
            font=("Arial", 14)
        ).grid(row=1, column=0, columnspan=6, pady=30)
        return

    for i, (sid, name, phone, category, rating, certificates) in enumerate(suppliers, 1):
        ctk.CTkLabel(table_frame, text=name, anchor="w").grid(
            row=i, column=0, padx=10, pady=5, sticky="w"
        )
        ctk.CTkLabel(table_frame, text=phone or "—", anchor="w").grid(
            row=i, column=1, padx=10, pady=5, sticky="w"
        )
        ctk.CTkLabel(table_frame, text=category or "—", anchor="w").grid(
            row=i, column=2, padx=10, pady=5, sticky="w"
        )

        color = "green"
        if "Средне" in rating:
            color = "orange"
        if "Заблокирован" in rating:
            color = "red"

        ctk.CTkLabel(
            table_frame,
            text=rating,
            text_color=color,
            anchor="w"
        ).grid(row=i, column=3, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(table_frame, text=certificates, anchor="w").grid(
            row=i, column=4, padx=10, pady=5, sticky="w"
        )

        row_buttons = ctk.CTkFrame(table_frame, fg_color="transparent")
        row_buttons.grid(row=i, column=5, padx=10, pady=5, sticky="w")

        ctk.CTkButton(
            row_buttons,
            text="🗑️ Удалить",
            width=90,
            height=30,
            fg_color="red",
            font=("Arial", 11),
            command=lambda sid=sid, name=name: _delete_supplier(sid, name, on_refresh)
        ).pack(side="left", padx=2)


def _delete_supplier(supplier_id, name, on_refresh):
    """Удаление поставщика с подтверждением"""
    if messagebox.askyesno(
        "Удаление",
        f"Удалить поставщика '{name}' из базы?"
    ):
        delete_supplier(supplier_id)
        on_refresh()


def _add_supplier_dialog(parent, on_refresh):
    """Диалог добавления поставщика (сохраняет в базу)"""
    dialog = ctk.CTkToplevel(parent)
    dialog.title("Добавить поставщика")
    dialog.geometry("500x650")

    ctk.CTkLabel(
        dialog,
        text="➕ Новый поставщик",
        font=("Arial", 20, "bold")
    ).pack(pady=20)

    fields = [
        "Название компании",
        "БИН/ИИН",
        "ФИО контактного лица",
        "Телефон",
        "Email",
        "Категория товаров",
        "Адрес",
    ]

    entries = {}
    for field in fields:
        ctk.CTkLabel(dialog, text=field).pack(anchor="w", padx=30, pady=(10, 2))
        entries[field] = ctk.CTkEntry(dialog, width=400)
        entries[field].pack(padx=30)

    def save():
        name = entries["Название компании"].get().strip()

        if not name:
            messagebox.showwarning(
                "Ошибка",
                "Введите название компании!"
            )
            return

        add_supplier({
            "name": name,
            "bin_iin": entries["БИН/ИИН"].get().strip(),
            "contact_person": entries["ФИО контактного лица"].get().strip(),
            "phone": entries["Телефон"].get().strip(),
            "email": entries["Email"].get().strip(),
            "category": entries["Категория товаров"].get().strip(),
            "address": entries["Адрес"].get().strip(),
        })

        dialog.destroy()
        on_refresh()
        messagebox.showinfo(
            "Готово",
            f"Поставщик '{name}' добавлен в базу!"
        )

    ctk.CTkButton(
        dialog,
        text="💾 Сохранить",
        width=200,
        fg_color="green",
        command=save
    ).pack(pady=30)


def _build_receiving_tab(parent):
    """Журнал приёмки товаров"""

    form_frame = ctk.CTkFrame(parent)
    form_frame.pack(pady=10, fill="x", padx=10)

    ctk.CTkLabel(
        form_frame,
        text="📥 Новая приёмка товара",
        font=("Arial", 16, "bold")
    ).pack(pady=10)

    grid = ctk.CTkFrame(form_frame, fg_color="transparent")
    grid.pack(pady=10, fill="x")

    fields = [
        ("Дата приёмки:", datetime.now().strftime("%d.%m.%Y")),
        ("Поставщик:", "Выбрать из списка ▼"),
        ("Товар:", "Введите название"),
        ("Количество:", "0 кг/шт"),
        ("Температура при приёмке:", "+__°C"),
        ("Норма температуры:", "+0...+4°C"),
        ("Срок годности:", "дд.мм.гггг"),
        ("Сертификат/Накладная:", "📎 Прикрепить файл"),
    ]

    for i, (label, placeholder) in enumerate(fields):
        row = i // 2
        col = (i % 2) * 2

        ctk.CTkLabel(
            grid,
            text=label,
            font=("Arial", 12, "bold")
        ).grid(row=row, column=col, padx=10, pady=5, sticky="w")

        ctk.CTkEntry(
            grid,
            placeholder_text=placeholder,
            width=250
        ).grid(row=row, column=col + 1, padx=10, pady=5, sticky="w")

    btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
    btn_frame.pack(pady=15)

    ctk.CTkButton(
        btn_frame,
        text="✅ Принять товар",
        width=180,
        fg_color="green",
        font=("Arial", 14, "bold")
    ).pack(side="left", padx=10)

    ctk.CTkButton(
        btn_frame,
        text="❌ Отклонить (брак)",
        width=180,
        fg_color="red",
        font=("Arial", 14, "bold")
    ).pack(side="left", padx=10)

    ctk.CTkButton(
        btn_frame,
        text="📸 Фото товара",
        width=180,
        fg_color="blue"
    ).pack(side="left", padx=10)

    ctk.CTkLabel(
        parent,
        text="📋 Последние приёмки (последние 7 дней):",
        font=("Arial", 14, "bold")
    ).pack(pady=(20, 5), anchor="w", padx=20)

    log_frame = ctk.CTkScrollableFrame(parent, height=200)
    log_frame.pack(fill="both", expand=True, padx=20)

    ctk.CTkLabel(
        log_frame,
        text="Приёмок пока не было. Заполните форму выше.",
        font=("Arial", 12)
    ).pack(pady=10)


def _build_certificates_tab(parent):
    """Контроль сертификатов"""

    ctk.CTkLabel(
        parent,
        text="🚨 Сроки действия сертификатов поставщиков",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    alerts_frame = ctk.CTkFrame(parent, fg_color="#3a2a00")
    alerts_frame.pack(pady=10, fill="x", padx=20)

    ctk.CTkLabel(
        alerts_frame,
        text="⚠️ ТРЕБУЮТ ВНИМАНИЯ:",
        font=("Arial", 14, "bold"),
        text_color="orange"
    ).pack(pady=10)

    ctk.CTkLabel(
        alerts_frame,
        text="Добавьте поставщиков с сертификатами — система сама напомнит о сроках.",
        font=("Arial", 12)
    ).pack(pady=2, padx=20, fill="x")

    ctk.CTkButton(
        parent,
        text="📧 Отправить запросы поставщикам на обновление",
        width=350,
        fg_color="orange"
    ).pack(pady=20)


def _build_violations_tab(parent):
    """Нарушения и рекламации"""

    ctk.CTkLabel(
        parent,
        text="⚠️ Акты нарушений и рекламации поставщикам",
        font=("Arial", 18, "bold")
    ).pack(pady=20)

    ctk.CTkButton(
        parent,
        text="📝 Составить новый акт",
        width=250,
        fg_color="red"
    ).pack(pady=10)

    violations_frame = ctk.CTkScrollableFrame(parent, height=400)
    violations_frame.pack(pady=10, fill="both", expand=True, padx=20)

    ctk.CTkLabel(
        violations_frame,
        text="Нарушений пока не зафиксировано.",
        font=("Arial", 12)
    ).pack(pady=10)
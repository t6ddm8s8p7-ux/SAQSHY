import customtkinter as ctk
from modules.esen_employees import (
    read_current_page,
    save_employees,
    finish_reading,
    open_employees_section,
)
from modules.esen_engine import run_esen_engine
from modules.compare_employees import compare_employees
from modules.dashboard_data import clear_dashboard_cache
from modules.esen_name_fix import apply_name_fixes_to_esen_file


def open_manual_import_window(driver):
    window = ctk.CTkToplevel()
    window.title("Ручной импорт e-SEN")
    window.geometry("520x520")
    window.lift()
    window.focus_force()
    window.attributes("-topmost", True)
    window.after(800, lambda: window.attributes("-topmost", False))

    state = {
        "page": 1,
        "employees": [],
        "pages_read": set(),
    }

    title = ctk.CTkLabel(
        window,
        text="📥 Ручной импорт e-SEN",
        font=("Arial", 26, "bold"),
    )
    title.pack(pady=20)

    page_label = ctk.CTkLabel(
        window,
        text="Страница: 1",
        font=("Arial", 18, "bold"),
    )
    page_label.pack(pady=5)

    count_label = ctk.CTkLabel(
        window,
        text="Считано сотрудников: 0",
        font=("Arial", 18, "bold"),
    )
    count_label.pack(pady=5)

    status_label = ctk.CTkLabel(
        window,
        text=(
            "Убедитесь, что в браузере открыт раздел сотрудников "
            "(Қызметкерлер / Сотрудники), и нажмите «Считать текущую страницу»."
        ),
        font=("Arial", 14),
        wraplength=460,
    )
    status_label.pack(pady=15)

    def update_labels():
        page_label.configure(text=f"Страница: {state['page']}")
        count_label.configure(
            text=f"Считано сотрудников: {len(state['employees'])}"
        )

    def open_section():
        """Автоматически открывает раздел сотрудников в браузере."""
        status_label.configure(text="⏳ Открываю раздел сотрудников...")
        window.update_idletasks()
        if open_employees_section(driver):
            status_label.configure(
                text="✅ Раздел сотрудников открыт. "
                     "Нажмите «Считать текущую страницу»."
            )
        else:
            status_label.configure(
                text="⚠️ Откройте раздел сотрудников ВРУЧНУЮ в браузере "
                     "(кликните Қызметкерлер / Сотрудники), затем «Считать»."
            )

    def read_page():
        page = state["page"]
        if page in state["pages_read"]:
            status_label.configure(
                text="⚠️ Эта страница уже была считана. "
                     "Перейдите в браузере на следующую страницу."
            )
            return
        status_label.configure(text="⏳ Читаю текущую страницу e-SEN...")
        window.update_idletasks()
        employees = read_current_page(driver, page)
        if not employees:
            status_label.configure(
                text="⚠️ Не удалось считать. Убедитесь, что в браузере "
                     "открыта таблица сотрудников, и попробуйте снова."
            )
            return
        state["employees"].extend(employees)
        state["pages_read"].add(page)
        state["page"] += 1
        update_labels()
        status_label.configure(
            text="✅ Страница считана. Перейдите в браузере "
                 "на следующую страницу и снова нажмите кнопку."
        )

    def finish_import():
        status_label.configure(text="⏳ Завершаю импорт, сохраняю базу...")
        window.update_idletasks()
        result = finish_reading(state["employees"])
        saved = save_employees(result, force=True)
        if saved:
            status_label.configure(
                text="⏳ Запускаю ESEN Engine, "
                     "восстанавливаю ФИО и сверяю с HR..."
            )
            window.update_idletasks()
            run_esen_engine()
            fixed = apply_name_fixes_to_esen_file()
            compare_employees()
            clear_dashboard_cache()
            status_label.configure(
                text=(
                    f"✅ Импорт завершён. Сохранено: {len(result)} | "
                    f"ФИО восстановлено: {fixed}"
                )
            )
        else:
            status_label.configure(
                text="⚠️ Импорт не сохранён: новая база меньше предыдущей."
            )

    ctk.CTkButton(
        window,
        text="🌐 Открыть раздел сотрудников",
        width=320,
        height=42,
        fg_color="#7c3aed",
        hover_color="#6d28d9",
        command=open_section,
    ).pack(pady=(0, 10))

    ctk.CTkButton(
        window,
        text="📖 Считать текущую страницу",
        width=320,
        height=45,
        command=read_page,
    ).pack(pady=12)

    ctk.CTkButton(
        window,
        text="✅ Завершить импорт",
        width=320,
        height=45,
        fg_color="#16a34a",
        command=finish_import,
    ).pack(pady=12)
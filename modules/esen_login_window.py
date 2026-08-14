import customtkinter as ctk


def ask_esen_login(default_login="", default_password=""):
    result = {
        "login": None,
        "password": None
    }

    window = ctk.CTkToplevel()
    window.title("e-SEN вход")
    window.geometry("420x300")
    window.lift()
    window.focus_force()
    window.grab_set()

    ctk.CTkLabel(
        window,
        text="🔐 Вход в e-SEN",
        font=("Arial", 24, "bold")
    ).pack(pady=(25, 15))

    login_entry = ctk.CTkEntry(
        window,
        placeholder_text="Логин e-SEN",
        width=320,
        height=38
    )
    login_entry.pack(pady=8)
    login_entry.insert(0, default_login)

    password_entry = ctk.CTkEntry(
        window,
        placeholder_text="Пароль e-SEN",
        width=320,
        height=38,
        show="*"
    )
    password_entry.pack(pady=8)
    password_entry.insert(0, default_password)

    def submit():
        result["login"] = login_entry.get().strip()
        result["password"] = password_entry.get().strip()
        window.destroy()

    def cancel():
        window.destroy()

    ctk.CTkButton(
        window,
        text="✅ Войти",
        width=150,
        height=38,
        command=submit
    ).pack(pady=(18, 6))

    ctk.CTkButton(
        window,
        text="Отмена",
        width=150,
        height=34,
        fg_color="#6b7280",
        command=cancel
    ).pack()

    window.wait_window()

    return result["login"], result["password"]
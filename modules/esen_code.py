import customtkinter as ctk


def ask_sms_code():
    """Окно для ручного ввода 6-значного кода из iCloud"""

    result = {"code": None}

    window = ctk.CTkToplevel()
    window.title("Код подтверждения e-SEN")
    window.geometry("420x260")
    window.grab_set()

    title = ctk.CTkLabel(
        window,
        text="Введите код из iCloud",
        font=("Arial", 24, "bold")
    )
    title.pack(pady=25)

    entry = ctk.CTkEntry(
        window,
        width=220,
        height=40,
        font=("Arial", 22),
        justify="center"
    )
    entry.pack(pady=10)

    status = ctk.CTkLabel(window, text="")
    status.pack(pady=5)

    def submit():
        code = entry.get().strip()

        if len(code) != 6 or not code.isdigit():
            status.configure(text="Введите 6 цифр")
            return

        result["code"] = code
        window.destroy()

    btn = ctk.CTkButton(
        window,
        text="Подтвердить",
        width=200,
        height=40,
        command=submit
    )
    btn.pack(pady=20)

    window.wait_window()

    return result["code"]
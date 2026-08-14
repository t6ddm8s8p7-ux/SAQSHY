"""
Отправка email-уведомлений через Gmail (Google Chrome).

ОТПРАВИТЕЛЬ: ваш Gmail daurenospan079@gmail.com
             (аккаунт, в который вы вошли в Chrome).
ПОЛУЧАТЕЛЬ:  Dauren.OSPAN@rixos.com (рабочая почта).

Письмо открывается в окне создания Gmail с заполненными
получателем, темой и текстом. Длинные письма копируются
в буфер обмена — в Gmail достаточно нажать Ctrl+V.
"""
import webbrowser
from datetime import datetime
from tkinter import messagebox
from urllib.parse import quote

# КОМУ отправляем (рабочая почта)
RECIPIENT_EMAIL = "Dauren.OSPAN@rixos.com"

# ОТ КОГО (ваш Gmail — должен быть открыт в Chrome)
SENDER_EMAIL = "daurenospan079@gmail.com"

SENDER_NAME = "Дәурен Оспан"

SIGNATURE = (
    "\n\nС уважением,\n"
    f"{SENDER_NAME}\n"
    "Главный санитарный врач\n"
    "Санитарно-эпидемиологическая служба"
)


def _copy_to_clipboard(text):
    """Копирует текст в буфер обмена Windows."""
    try:
        import ctypes
        CF_UNICODETEXT = 13
        GMEM_MOVEABLE = 0x0002
        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        user32.OpenClipboard(0)
        user32.EmptyClipboard()
        data = text.encode("utf-16-le") + b"\x00\x00"
        handle = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
        pointer = kernel32.GlobalLock(handle)
        ctypes.memmove(pointer, data, len(data))
        kernel32.GlobalUnlock(handle)
        user32.SetClipboardData(CF_UNICODETEXT, handle)
        user32.CloseClipboard()
        return True
    except Exception as e:
        print("Буфер обмена:", e)
        return False


def _open_in_chrome(url):
    """Открывает ссылку в Chrome, при неудаче — в браузере по умолчанию."""
    try:
        browser = webbrowser.get("chrome")
        browser.open(url, new=2)
        return True
    except Exception:
        try:
            webbrowser.open(url, new=2)
            return True
        except Exception as e:
            print("Браузер:", e)
            return False


def send_email_notification(subject, body, recipient=None):
    """
    Открывает Gmail с готовым письмом.
    Отправитель — ваш Gmail (daurenospan079@gmail.com),
    получатель — Dauren.OSPAN@rixos.com.
    """
    if not recipient:
        recipient = RECIPIENT_EMAIL

    full_body = body + SIGNATURE
    base = "https://mail.google.com/mail/?view=cm&fs=1"
    head = f"{base}&to={quote(recipient)}&su={quote(subject)}"
    url_with_body = f"{head}&body={quote(full_body)}"

    if len(url_with_body) <= 1800:
        # Короткое письмо — текст подставляется сразу
        url = url_with_body
        note = "Письмо открыто в Gmail — проверьте и нажмите «Отправить»."
    else:
        # Длинное письмо — текст в буфер обмена
        copied = _copy_to_clipboard(full_body)
        if copied:
            short_body = (
                "Здравствуйте!\n\n"
                "Полный текст письма скопирован в буфер обмена.\n"
                "Нажмите Ctrl+V, чтобы вставить его в это поле."
            ) + SIGNATURE
            url = f"{head}&body={quote(short_body)}"
            note = (
                "Письмо длинное, поэтому текст скопирован в буфер обмена.\n"
                "В окне Gmail нажмите Ctrl+V в теле письма и отправьте."
            )
        else:
            truncated = full_body[:1500] + "\n… (полный список — в SanEpi AI)"
            url = f"{head}&body={quote(truncated)}"
            note = "Текст письма сокращён для автозаполнения."

    opened = _open_in_chrome(url)
    if not opened:
        note = "Не удалось открыть браузер. Откройте Gmail вручную."

    messagebox.showinfo(
        "SanEpi AI",
        f"✅ {note}\n\n"
        f"От кого: {SENDER_EMAIL}\n"
        f"Кому: {recipient}\n"
        f"Тема: {subject}",
    )

    return {
        "status": "sent" if opened else "error",
        "sender": SENDER_EMAIL,
        "recipient": recipient,
        "subject": subject,
        "note": note,
        "timestamp": datetime.now().isoformat(),
    }
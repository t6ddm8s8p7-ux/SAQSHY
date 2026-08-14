import json
import os
import subprocess
import sys
import threading
import webbrowser
from pathlib import Path
from tkinter import messagebox

import customtkinter as ctk

from modules.ai_assistant import ask_ai
from modules.document_manager import DocumentManager
from modules.translations import tr
from modules.update_knowledge_base import update_knowledge_base


REGISTRY_FILE = Path("knowledge_base/registry.json")
TITLES_FILE = Path("knowledge_base/document_titles.json")

document_manager = DocumentManager()


def load_registry():
    if not REGISTRY_FILE.exists():
        return []

    try:
        with REGISTRY_FILE.open(
            "r",
            encoding="utf-8-sig"
        ) as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except Exception as error:
        print("Ошибка чтения registry.json:")
        print(error)
        return []


def load_document_titles():
    if not TITLES_FILE.exists():
        TITLES_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )
        save_document_titles({})

    try:
        with TITLES_FILE.open(
            "r",
            encoding="utf-8-sig"
        ) as file:
            data = json.load(file)

        return data if isinstance(data, dict) else {}

    except Exception as error:
        print("Ошибка чтения document_titles.json:")
        print(error)
        return {}


def save_document_titles(titles):
    TITLES_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    try:
        with TITLES_FILE.open(
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                titles,
                file,
                ensure_ascii=False,
                indent=2
            )

        return True

    except Exception as error:
        print("Ошибка сохранения названий:")
        print(error)
        return False


def get_document_key(document):
    document_id = str(
        document.get("id", "")
    ).strip()

    if document_id:
        return document_id

    return str(
        document.get("relative_path", "")
    ).strip()


def get_document_title(
    document,
    document_titles
):
    key = get_document_key(document)

    saved_title = str(
        document_titles.get(key, "")
    ).strip()

    if saved_title:
        return saved_title

    return str(
        document.get("file_name", "Документ")
    ).strip()


def language_name(language):
    names = {
        "rus": "Русский",
        "ru": "Русский",
        "kaz": "Қазақша",
        "kk": "Қазақша",
        "unknown": "Не определён",
    }

    language = str(language).lower()

    return names.get(
        language,
        language
    )


def format_file_size(size_bytes):
    try:
        size = int(size_bytes)
    except Exception:
        return "0 байт"

    if size < 1024:
        return f"{size} байт"

    if size < 1024 * 1024:
        return f"{size / 1024:.1f} КБ"

    return (
        f"{size / (1024 * 1024):.1f} МБ"
    )


def get_document_path(document):
    absolute_path = str(
        document.get("absolute_path", "")
    ).strip()

    if absolute_path:
        file_path = Path(absolute_path)

        if file_path.exists():
            return file_path

    relative_path = str(
        document.get("relative_path", "")
    ).strip()

    if relative_path:
        file_path = (
            Path("knowledge_base")
            / relative_path
        )

        if file_path.exists():
            return file_path

    return None


def open_document(document):
    file_path = get_document_path(document)

    if not file_path:
        messagebox.showerror(
            "SanEpi AI",
            "Файл документа не найден."
        )
        return

    try:
        if os.name == "nt":
            os.startfile(str(file_path))

        elif sys.platform == "darwin":
            subprocess.Popen(
                ["open", str(file_path)]
            )

        else:
            subprocess.Popen(
                ["xdg-open", str(file_path)]
            )

    except Exception:
        try:
            webbrowser.open(
                file_path.resolve().as_uri()
            )

        except Exception as error:
            messagebox.showerror(
                "Ошибка открытия документа",
                str(error)
            )


def open_title_editor(
    parent,
    document,
    document_titles,
    on_saved
):
    key = get_document_key(document)

    if not key:
        return

    current_title = get_document_title(
        document,
        document_titles
    )

    window = ctk.CTkToplevel(parent)
    window.title("Название документа")
    window.geometry("650x330")
    window.minsize(580, 300)
    window.lift()
    window.focus_force()
    window.grab_set()

    ctk.CTkLabel(
        window,
        text="✏️ Название документа",
        font=("Arial", 24, "bold")
    ).pack(
        pady=(25, 10)
    )

    ctk.CTkLabel(
        window,
        text=(
            "Введите понятное название, которое "
            "будет отображаться в SanEpi AI."
        ),
        font=("Arial", 14),
        wraplength=580
    ).pack(
        padx=25,
        pady=(0, 15)
    )

    title_entry = ctk.CTkEntry(
        window,
        width=580,
        height=44,
        font=("Arial", 15)
    )
    title_entry.pack(
        padx=25,
        pady=10
    )
    title_entry.insert(
        0,
        current_title
    )
    title_entry.focus()
    title_entry.select_range(
        0,
        "end"
    )

    message_label = ctk.CTkLabel(
        window,
        text="",
        font=("Arial", 13),
        text_color="#ef4444"
    )
    message_label.pack(
        pady=(0, 5)
    )

    def save_title():
        new_title = title_entry.get().strip()

        if not new_title:
            message_label.configure(
                text="Введите название документа."
            )
            return

        document_titles[key] = new_title

        if save_document_titles(
            document_titles
        ):
            window.destroy()
            on_saved()

    buttons = ctk.CTkFrame(
        window,
        fg_color="transparent"
    )
    buttons.pack(
        fill="x",
        padx=25,
        pady=(10, 20)
    )

    ctk.CTkButton(
        buttons,
        text="💾 Сохранить",
        height=40,
        command=save_title
    ).pack(
        side="left",
        fill="x",
        expand=True,
        padx=(0, 6)
    )

    ctk.CTkButton(
        buttons,
        text="Отмена",
        height=40,
        fg_color="#6b7280",
        hover_color="#4b5563",
        command=window.destroy
    ).pack(
        side="left",
        fill="x",
        expand=True,
        padx=(6, 0)
    )

    window.bind(
        "<Return>",
        lambda event: save_title()
    )


def open_text_search(
    parent,
    document
):
    document_name = str(
        document.get("file_name", "Документ")
    )

    relative_path = str(
        document.get("relative_path", "")
    )

    window = ctk.CTkToplevel(parent)
    window.title("Поиск по тексту")
    window.geometry("850x650")
    window.minsize(700, 550)
    window.lift()
    window.focus_force()
    window.grab_set()

    ctk.CTkLabel(
        window,
        text="🔎 Поиск по тексту приказа",
        font=("Arial", 26, "bold")
    ).pack(
        pady=(20, 8)
    )

    ctk.CTkLabel(
        window,
        text=(
            "Поиск только по документу:\n"
            f"{document_name}"
        ),
        font=("Arial", 14),
        text_color="#9ca3af",
        wraplength=760,
        justify="center"
    ).pack(
        padx=20,
        pady=(0, 15)
    )

    question_text = ctk.CTkTextbox(
        window,
        height=110,
        font=("Arial", 15),
        wrap="word"
    )
    question_text.pack(
        fill="x",
        padx=25,
        pady=(0, 12)
    )

    question_text.insert(
        "1.0",
        "Введите слова или описание для поиска..."
    )

    result_text = ctk.CTkTextbox(
        window,
        font=("Arial", 14),
        wrap="word"
    )
    result_text.pack(
        fill="both",
        expand=True,
        padx=25,
        pady=(0, 12)
    )
    result_text.configure(
        state="disabled"
    )

    search_status = ctk.CTkLabel(
        window,
        text="",
        font=("Arial", 13),
        text_color="#f59e0b"
    )
    search_status.pack(
        padx=25,
        pady=(0, 8)
    )

    def show_result(result):
        result_text.configure(
            state="normal"
        )
        result_text.delete(
            "1.0",
            "end"
        )
        result_text.insert(
            "1.0",
            result["answer"]
        )
        result_text.configure(
            state="disabled"
        )

        search_button.configure(
            state="normal",
            text="🔎 Найти в тексте"
        )

        search_status.configure(
            text="✅ Поиск завершён",
            text_color="#22c55e"
        )

    def show_error(error):
        search_button.configure(
            state="normal",
            text="🔎 Найти в тексте"
        )

        search_status.configure(
            text="❌ Ошибка поиска",
            text_color="#ef4444"
        )

        messagebox.showerror(
            "Ошибка поиска",
            str(error)
        )

    def start_search():
        question = question_text.get(
            "1.0",
            "end"
        ).strip()

        if (
            not question
            or question
            == "Введите слова или описание для поиска..."
        ):
            messagebox.showwarning(
                "SanEpi AI",
                "Введите текст для поиска."
            )
            return

        search_button.configure(
            state="disabled",
            text="⏳ Поиск..."
        )

        search_status.configure(
            text="Поиск по выбранному приказу...",
            text_color="#f59e0b"
        )

        def worker():
            try:
                result = ask_ai(
                    question=question,
                    selected_relative_path=relative_path
                )

                window.after(
                    0,
                    lambda: show_result(result)
                )

            except Exception as error:
                window.after(
                    0,
                    lambda err=error: show_error(err)
                )

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    search_button = ctk.CTkButton(
        window,
        text="🔎 Найти в тексте",
        height=44,
        command=start_search
    )
    search_button.pack(
        fill="x",
        padx=25,
        pady=(0, 20)
    )


def build_laws_page(parent):
    registry = load_registry()
    document_titles = load_document_titles()

    ctk.CTkLabel(
        parent,
        text=f"📚 {tr('laws')}",
        font=("Arial", 34, "bold")
    ).pack(
        pady=(20, 10)
    )

    document_types = sorted(
        {
            str(
                item.get("document_type", "")
            ).strip()
            for item in registry
            if str(
                item.get("document_type", "")
            ).strip()
        }
    )

    if not document_types:
        document_types = [
            "manual_documents"
        ]

    selected_type = ctk.StringVar(
        value=(
            "manual_documents"
            if "manual_documents"
            in document_types
            else document_types[0]
        )
    )

    selected_topic = ctk.StringVar(
        value="Все разделы"
    )

    search_var = ctk.StringVar(
        value=""
    )

    control_frame = ctk.CTkFrame(
        parent,
        corner_radius=14
    )
    control_frame.pack(
        fill="x",
        padx=20,
        pady=10
    )

    ctk.CTkLabel(
        control_frame,
        text="Тип документа",
        font=("Arial", 14, "bold")
    ).grid(
        row=0,
        column=0,
        padx=10,
        pady=(10, 4),
        sticky="w"
    )

    type_menu = ctk.CTkOptionMenu(
        control_frame,
        variable=selected_type,
        values=document_types,
        width=240
    )
    type_menu.grid(
        row=1,
        column=0,
        padx=10,
        pady=(0, 10),
        sticky="ew"
    )

    ctk.CTkLabel(
        control_frame,
        text="Раздел",
        font=("Arial", 14, "bold")
    ).grid(
        row=0,
        column=1,
        padx=10,
        pady=(10, 4),
        sticky="w"
    )

    topic_menu = ctk.CTkOptionMenu(
        control_frame,
        variable=selected_topic,
        values=["Все разделы"],
        width=240
    )
    topic_menu.grid(
        row=1,
        column=1,
        padx=10,
        pady=(0, 10),
        sticky="ew"
    )

    ctk.CTkLabel(
        control_frame,
        text="Поиск по названию",
        font=("Arial", 14, "bold")
    ).grid(
        row=0,
        column=2,
        padx=10,
        pady=(10, 4),
        sticky="w"
    )

    search_entry = ctk.CTkEntry(
        control_frame,
        textvariable=search_var,
        placeholder_text="Номер или название...",
        height=36
    )
    search_entry.grid(
        row=1,
        column=2,
        padx=10,
        pady=(0, 10),
        sticky="ew"
    )

    add_button = ctk.CTkButton(
        control_frame,
        text="➕ Добавить приказ",
        width=170,
        height=36
    )
    add_button.grid(
        row=1,
        column=3,
        padx=10,
        pady=(0, 10),
        sticky="ew"
    )

    update_button = ctk.CTkButton(
        control_frame,
        text="🔄 Обновить базу",
        width=170,
        height=36
    )
    update_button.grid(
        row=1,
        column=4,
        padx=10,
        pady=(0, 10),
        sticky="ew"
    )

    status_label = ctk.CTkLabel(
        control_frame,
        text="",
        font=("Arial", 12),
        text_color="#f59e0b"
    )
    status_label.grid(
        row=2,
        column=0,
        columnspan=5,
        padx=10,
        pady=(0, 8),
        sticky="w"
    )

    control_frame.grid_columnconfigure(
        0,
        weight=1
    )
    control_frame.grid_columnconfigure(
        1,
        weight=1
    )
    control_frame.grid_columnconfigure(
        2,
        weight=2
    )

    main_frame = ctk.CTkFrame(
        parent,
        corner_radius=14
    )
    main_frame.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 15)
    )

    main_frame.grid_columnconfigure(
        0,
        weight=2
    )
    main_frame.grid_columnconfigure(
        1,
        weight=3
    )
    main_frame.grid_rowconfigure(
        0,
        weight=1
    )

    document_frame = ctk.CTkScrollableFrame(
        main_frame,
        corner_radius=12
    )
    document_frame.grid(
        row=0,
        column=0,
        sticky="nsew",
        padx=(10, 5),
        pady=10
    )

    info_frame = ctk.CTkFrame(
        main_frame,
        corner_radius=12
    )
    info_frame.grid(
        row=0,
        column=1,
        sticky="nsew",
        padx=(5, 10),
        pady=10
    )

    info_title = ctk.CTkLabel(
        info_frame,
        text="Выберите документ",
        font=("Arial", 24, "bold"),
        wraplength=560,
        justify="left"
    )
    info_title.pack(
        anchor="w",
        padx=20,
        pady=(25, 15)
    )

    info_text = ctk.CTkTextbox(
        info_frame,
        font=("Arial", 15),
        wrap="word"
    )
    info_text.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 15)
    )
    info_text.configure(
        state="disabled"
    )

    buttons_frame = ctk.CTkFrame(
        info_frame,
        fg_color="transparent"
    )
    buttons_frame.pack(
        fill="x",
        padx=20,
        pady=(0, 20)
    )

    buttons_frame.grid_columnconfigure(
        0,
        weight=1
    )
    buttons_frame.grid_columnconfigure(
        1,
        weight=1
    )

    open_button = ctk.CTkButton(
        buttons_frame,
        text="📄 Открыть документ",
        height=42,
        state="disabled"
    )
    open_button.grid(
        row=0,
        column=0,
        sticky="ew",
        padx=(0, 6),
        pady=(0, 6)
    )

    rename_button = ctk.CTkButton(
        buttons_frame,
        text="✏️ Изменить название",
        height=42,
        state="disabled",
        fg_color="#7c3aed",
        hover_color="#6d28d9"
    )
    rename_button.grid(
        row=0,
        column=1,
        sticky="ew",
        padx=(6, 0),
        pady=(0, 6)
    )

    text_search_button = ctk.CTkButton(
        buttons_frame,
        text="🔎 Поиск по тексту",
        height=42,
        state="disabled",
        fg_color="#059669",
        hover_color="#047857"
    )
    text_search_button.grid(
        row=1,
        column=0,
        sticky="ew",
        padx=(0, 6),
        pady=(6, 0)
    )

    delete_button = ctk.CTkButton(
        buttons_frame,
        text="🗑️ Удалить приказ",
        height=42,
        state="disabled",
        fg_color="#dc2626",
        hover_color="#b91c1c"
    )
    delete_button.grid(
        row=1,
        column=1,
        sticky="ew",
        padx=(6, 0),
        pady=(6, 0)
    )

    selected_document = {
        "value": None
    }

    def get_topics():
        current_type = selected_type.get()

        topics = sorted(
            {
                str(
                    item.get("topic", "")
                ).strip()
                for item in registry
                if (
                    item.get("document_type")
                    == current_type
                    and str(
                        item.get("topic", "")
                    ).strip()
                )
            }
        )

        return [
            "Все разделы"
        ] + topics

    def clear_document_info():
        selected_document["value"] = None

        info_title.configure(
            text="Выберите документ"
        )

        info_text.configure(
            state="normal"
        )
        info_text.delete(
            "1.0",
            "end"
        )
        info_text.configure(
            state="disabled"
        )

        open_button.configure(
            state="disabled"
        )
        rename_button.configure(
            state="disabled"
        )
        text_search_button.configure(
            state="disabled"
        )
        delete_button.configure(
            state="disabled"
        )

    def render_documents(_value=None):
        for widget in (
            document_frame.winfo_children()
        ):
            widget.destroy()

        current_type = selected_type.get()
        current_topic = selected_topic.get()
        query = search_var.get().strip().lower()

        filtered = []

        for document in registry:
            if (
                document.get("document_type")
                != current_type
            ):
                continue

            if (
                current_topic != "Все разделы"
                and document.get("topic")
                != current_topic
            ):
                continue

            title = get_document_title(
                document,
                document_titles
            )

            searchable_text = (
                title
                + " "
                + str(
                    document.get("file_name", "")
                )
                + " "
                + str(
                    document.get("relative_path", "")
                )
            ).lower()

            if query and query not in searchable_text:
                continue

            filtered.append(document)

        ctk.CTkLabel(
            document_frame,
            text=(
                f"Найдено документов: "
                f"{len(filtered)}"
            ),
            font=("Arial", 15, "bold")
        ).pack(
            anchor="w",
            padx=10,
            pady=(5, 12)
        )

        if not filtered:
            ctk.CTkLabel(
                document_frame,
                text="Документы не найдены.",
                font=("Arial", 15)
            ).pack(
                anchor="w",
                padx=10,
                pady=20
            )
            return

        for document in filtered:
            title = get_document_title(
                document,
                document_titles
            )

            language = language_name(
                document.get(
                    "language",
                    "unknown"
                )
            )

            ctk.CTkButton(
                document_frame,
                text=(
                    f"📄 {title}\n"
                    f"🌐 {language}"
                ),
                anchor="w",
                height=64,
                command=(
                    lambda doc=document:
                    show_document_info(doc)
                )
            ).pack(
                fill="x",
                padx=8,
                pady=5
            )

    def update_topics(_value=None):
        topics = get_topics()

        topic_menu.configure(
            values=topics
        )
        selected_topic.set(
            "Все разделы"
        )

        clear_document_info()
        render_documents()

    def refresh_registry_in_ui():
        nonlocal registry
        nonlocal document_types

        registry = load_registry()

        document_types = sorted(
            {
                str(
                    item.get("document_type", "")
                ).strip()
                for item in registry
                if str(
                    item.get("document_type", "")
                ).strip()
            }
        )

        if not document_types:
            document_types = [
                "manual_documents"
            ]

        type_menu.configure(
            values=document_types
        )

        if (
            selected_type.get()
            not in document_types
        ):
            selected_type.set(
                document_types[0]
            )

        update_topics()

    def refresh_after_title_change():
        current_document = (
            selected_document["value"]
        )

        render_documents()

        if current_document:
            show_document_info(
                current_document
            )

    def delete_manual_document(document):
        title = get_document_title(
            document,
            document_titles
        )

        confirmed = messagebox.askyesno(
            "Удаление приказа",
            (
                "Удалить выбранный приказ?\n\n"
                f"{title}\n\n"
                "Это действие нельзя отменить."
            )
        )

        if not confirmed:
            return

        delete_button.configure(
            state="disabled",
            text="⏳ Удаление..."
        )

        try:
            result = (
                document_manager.delete_document(
                    document=document,
                    progress_callback=(
                        lambda message:
                        status_label.configure(
                            text=message
                        )
                    )
                )
            )

            key = get_document_key(document)

            document_titles.pop(
                key,
                None
            )
            save_document_titles(
                document_titles
            )

            refresh_registry_in_ui()
            clear_document_info()

            status_label.configure(
                text="✅ Приказ удалён",
                text_color="#22c55e"
            )

            messagebox.showinfo(
                "SanEpi AI",
                result["message"]
            )

        except Exception as error:
            status_label.configure(
                text="❌ Ошибка удаления",
                text_color="#ef4444"
            )

            messagebox.showerror(
                "Ошибка удаления приказа",
                str(error)
            )

        finally:
            delete_button.configure(
                state="disabled",
                text="🗑️ Удалить приказ"
            )

    def show_document_info(document):
        selected_document["value"] = document

        title = get_document_title(
            document,
            document_titles
        )

        info_title.configure(
            text=title
        )

        details = (
            f"Название:\n{title}\n\n"
            f"Тип документа:\n"
            f"{document.get('document_type', '-')}\n\n"
            f"Раздел:\n"
            f"{document.get('topic', '-')}\n\n"
            f"Язык:\n"
            f"{language_name(document.get('language', 'unknown'))}\n\n"
            f"Формат:\n"
            f"{document.get('extension', '-')}\n\n"
            f"Размер файла:\n"
            f"{format_file_size(document.get('size_bytes', 0))}\n\n"
            f"Дата изменения:\n"
            f"{document.get('modified_at', '-')}\n\n"
            f"Исходное имя:\n"
            f"{document.get('file_name', '-')}\n\n"
            f"Путь:\n"
            f"{document.get('relative_path', '-')}"
        )

        info_text.configure(
            state="normal"
        )
        info_text.delete(
            "1.0",
            "end"
        )
        info_text.insert(
            "1.0",
            details
        )
        info_text.configure(
            state="disabled"
        )

        open_button.configure(
            state="normal",
            command=lambda doc=document: (
                open_document(doc)
            )
        )

        rename_button.configure(
            state="normal",
            command=lambda doc=document: (
                open_title_editor(
                    parent,
                    doc,
                    document_titles,
                    refresh_after_title_change
                )
            )
        )

        text_search_button.configure(
            state="normal",
            command=lambda doc=document: (
                open_text_search(
                    parent,
                    doc
                )
            )
        )

        if (
            document.get("document_type")
            == "manual_documents"
        ):
            delete_button.configure(
                state="normal",
                command=lambda doc=document: (
                    delete_manual_document(doc)
                )
            )

        else:
            delete_button.configure(
                state="disabled"
            )

    def show_update_result(result):
        update_button.configure(
            state="normal",
            text="🔄 Обновить базу"
        )

        status_label.configure(
            text="✅ Обновление завершено",
            text_color="#22c55e"
        )

        refresh_registry_in_ui()

        messagebox.showinfo(
            "SanEpi AI",
            (
                "Обновление базы завершено.\n\n"
                f"Всего документов: "
                f"{result['total_documents']}\n"
                f"PDF: "
                f"{result['pdf_documents']}\n"
                f"Добавлено: "
                f"{result['added']}\n"
                f"Обновлено: "
                f"{result['updated']}\n"
                f"Удалено: "
                f"{result['removed']}\n"
                f"Ошибок: "
                f"{result['errors']}"
            )
        )

    def show_update_error(error):
        update_button.configure(
            state="normal",
            text="🔄 Обновить базу"
        )

        status_label.configure(
            text="❌ Ошибка обновления",
            text_color="#ef4444"
        )

        messagebox.showerror(
            "Ошибка обновления",
            str(error)
        )

    def refresh_knowledge_base():
        update_button.configure(
            state="disabled",
            text="⏳ Обновление..."
        )

        status_label.configure(
            text="Обновление базы...",
            text_color="#f59e0b"
        )

        def progress_callback(message):
            parent.after(
                0,
                lambda text=message:
                status_label.configure(
                    text=text
                )
            )

        def worker():
            try:
                result = update_knowledge_base(
                    progress_callback=(
                        progress_callback
                    )
                )

                parent.after(
                    0,
                    lambda: show_update_result(
                        result
                    )
                )

            except Exception as error:
                parent.after(
                    0,
                    lambda err=error:
                    show_update_error(err)
                )

        threading.Thread(
            target=worker,
            daemon=True
        ).start()

    def add_manual_document():
        add_button.configure(
            state="disabled",
            text="⏳ Добавление..."
        )

        status_label.configure(
            text="Выберите PDF-приказ...",
            text_color="#f59e0b"
        )

        try:
            result = document_manager.add_pdf(
                parent=parent,
                progress_callback=(
                    lambda message:
                    status_label.configure(
                        text=message
                    )
                )
            )

            if result["status"] == "cancelled":
                status_label.configure(
                    text="Добавление отменено.",
                    text_color="#f59e0b"
                )
                return

            if result["status"] == "duplicate":
                status_label.configure(
                    text="Этот приказ уже добавлен.",
                    text_color="#f59e0b"
                )

                messagebox.showinfo(
                    "SanEpi AI",
                    result["message"]
                )
                return

            refresh_registry_in_ui()

            if (
                "manual_documents"
                in document_types
            ):
                selected_type.set(
                    "manual_documents"
                )
                update_topics()

            status_label.configure(
                text="✅ Приказ добавлен",
                text_color="#22c55e"
            )

            messagebox.showinfo(
                "SanEpi AI",
                result["message"]
            )

        except Exception as error:
            status_label.configure(
                text="❌ Ошибка добавления",
                text_color="#ef4444"
            )

            messagebox.showerror(
                "Ошибка добавления приказа",
                str(error)
            )

        finally:
            add_button.configure(
                state="normal",
                text="➕ Добавить приказ"
            )

    add_button.configure(
        command=add_manual_document
    )
    update_button.configure(
        command=refresh_knowledge_base
    )
    type_menu.configure(
        command=update_topics
    )
    topic_menu.configure(
        command=render_documents
    )

    search_var.trace_add(
        "write",
        lambda *args: render_documents()
    )

    update_topics()
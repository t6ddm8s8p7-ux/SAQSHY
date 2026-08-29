# -*- coding: utf-8 -*-
"""Утилита для кнопок с индикатором загрузки."""
import threading
import customtkinter as ctk
from tkinter import messagebox


def run_with_loading(button, task_func, success_message=None, error_title="Ошибка"):
    """
    Выполняет долгую задачу с индикатором загрузки на кнопке.
    
    :param button: CTkButton - кнопка, на которой показать загрузку
    :param task_func: callable - функция для выполнения в фоне
    :param success_message: str - сообщение об успехе (если None, не показывать)
    :param error_title: str - заголовок окна ошибки
    """
    # Сохраняем исходное состояние
    original_text = button.cget("text")
    original_state = button.cget("state")
    original_fg = button.cget("fg_color")
    
    # Блокируем кнопку и показываем загрузку
    button.configure(
        text="⏳ Загрузка...",
        state="disabled",
        fg_color="#6b7280"
    )
    
    def worker():
        try:
            result = task_func()
            
            # Возвращаем кнопку в исходное состояние
            button.configure(
                text=original_text,
                state=original_state,
                fg_color=original_fg
            )
            
            if success_message:
                messagebox.showinfo("Успех", success_message)
            
            return result
        except Exception as e:
            # Возвращаем кнопку в исходное состояние даже при ошибке
            button.configure(
                text=original_text,
                state=original_state,
                fg_color=original_fg
            )
            messagebox.showerror(error_title, f"Произошла ошибка:\n{e}")
            raise
    
    # Запускаем задачу в отдельном потоке
    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
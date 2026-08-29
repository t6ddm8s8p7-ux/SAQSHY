# -*- coding: utf-8 -*-
"""Шифрование чувствительных данных (пароли, логины)."""
import os
from pathlib import Path
from cryptography.fernet import Fernet

KEY_FILE = Path("database/.encryption_key")

def get_or_create_key():
    """Получить существующий ключ или создать новый."""
    if KEY_FILE.exists():
        with open(KEY_FILE, "rb") as f:
            return f.read()
    else:
        key = Fernet.generate_key()
        KEY_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(KEY_FILE, "wb") as f:
            f.write(key)
        return key

def encrypt_text(plain_text):
    """Зашифровать текст."""
    if not plain_text:
        return ""
    key = get_or_create_key()
    f = Fernet(key)
    return f.encrypt(plain_text.encode()).decode()

def decrypt_text(encrypted_text):
    """Расшифровать текст."""
    if not encrypted_text:
        return ""
    try:
        key = get_or_create_key()
        f = Fernet(key)
        return f.decrypt(encrypted_text.encode()).decode()
    except Exception:
        # Если не удалось расшифровать — возможно, это открытый текст
        return encrypted_text

def is_encrypted(text):
    """Проверить, зашифрован ли текст (Fernet токены начинаются с 'gAAAAA')."""
    return text.startswith("gAAAAA") if text else False
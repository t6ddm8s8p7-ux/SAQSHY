import json
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from tkinter import messagebox

from modules.esen_login_window import ask_esen_login
from modules.esen_code import ask_sms_code
from modules.esen_employees import (
    close_intro,
    open_employees,
    open_employees_section,
)
from modules.esen_engine import run_esen_engine
from modules.compare_employees import compare_employees
from modules.esen_manual_import import open_manual_import_window
from modules.translations import tr
from modules.crypto import encrypt_text, decrypt_text, is_encrypted

ESEN_DRIVER = None
CONFIG_FILE = "config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return {}

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def open_esen_login():
    global ESEN_DRIVER
    config = load_config()

    url = config.get("esen_url", "https://e-sen.kz")
    
    # ✅ ДЕШИФРОВКА пароля (если он зашифрован)
    encrypted_login = config.get("esen_login", "")
    encrypted_password = config.get("esen_password", "")
    
    login = decrypt_text(encrypted_login)
    password = decrypt_text(encrypted_password)
    
    login, password = ask_esen_login(login, password)

    if not login or not password:
        print(tr("esen_login_cancelled"))
        return None

    # ✅ ШИФРОВАНИЕ и сохранение новых данных
    config["esen_login"] = encrypt_text(login)
    config["esen_password"] = encrypt_text(password)
    save_config(config)

    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    ESEN_DRIVER = driver
    wait = WebDriverWait(driver, 30)

    driver.get(url)
    time.sleep(3)

    try:
        login_button = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Кіру') or contains(., 'Войти') or contains(., 'Login')]")
            )
        )
        driver.execute_script("arguments[0].click();", login_button)
    except Exception:
        print("⚠️ Кнопка входа не найдена, возможно, мы уже на странице входа.")
    
    time.sleep(2)

    try:
        login_field = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//input[@name='login' or @name='username' or @id='login' or contains(@placeholder, 'Логин') or contains(@placeholder, 'ЖСН') or contains(@placeholder, 'БСН')]")
        ))
        login_field.clear()
        login_field.send_keys(login)
    except Exception:
        visible_inputs = [el for el in driver.find_elements(By.TAG_NAME, "input") if el.is_displayed()]
        if visible_inputs:
            visible_inputs[0].clear()
            visible_inputs[0].send_keys(login)

    try:
        password_field = driver.find_element(
            By.XPATH, "//input[@type='password' or @name='password' or @id='password' or contains(@placeholder, 'Пароль') or contains(@placeholder, 'Құпия сөз')]"
        )
        password_field.clear()
        password_field.send_keys(password)
    except Exception:
        visible_inputs = [el for el in driver.find_elements(By.TAG_NAME, "input") if el.is_displayed()]
        if len(visible_inputs) > 1:
            visible_inputs[1].clear()
            visible_inputs[1].send_keys(password)

    time.sleep(1)

    try:
        submit_btn = driver.find_element(
            By.XPATH, "//button[contains(., 'Кіру') or contains(., 'Войти') or contains(., 'Login') or @type='submit']"
        )
        driver.execute_script("arguments[0].click();", submit_btn)
    except Exception:
        pass

    time.sleep(3)

    code = ask_sms_code()
    if code:
        try:
            code_inputs = driver.find_elements(By.XPATH, "//input[@maxlength='1' or contains(@class, 'sms-code') or contains(@id, 'code')]")
            
            if len(code_inputs) >= 6:
                for i, digit in enumerate(code[:6]):
                    code_inputs[i].send_keys(digit)
            else:
                single_code_input = driver.find_element(By.XPATH, "//input[@maxlength='6' or @name='code' or contains(@id, 'code') or contains(@placeholder, 'код') or contains(@placeholder, 'code')]")
                single_code_input.clear()
                single_code_input.send_keys(code)

            time.sleep(1)
            
            confirm_btn = driver.find_element(
                By.XPATH, "//*[contains(text(),'Растау') or contains(text(),'Подтвердить') or contains(text(),'Confirm')]"
            )
            driver.execute_script("arguments[0].click();", confirm_btn)
        except Exception as e:
            print(f"⚠️ Не удалось автоматически ввести код: {e}")
            print("Введите код вручную в открывшемся браузере.")

    print(tr("waiting_for_login"))

    try:
        wait.until(lambda d: "/profile" in d.current_url or "/dashboard" in d.current_url or "welcome" in d.current_url.lower())
    except Exception:
        print("⚠️ Таймаут ожидания перехода в профиль. Проверьте вход вручную.")

    print(tr("esen_login_successful"))

    try:
        close_intro(driver)
    except Exception:
        pass

    try:
        print(tr("trying_to_open_employees_section"))
        if open_employees_section(driver):
            print(tr("employees_section_opened"))
        else:
            print(tr("auto_redirect_failed"))
            print(tr("open_section_manually"))
    except Exception as e:
        print(f"{tr('auto_redirect_error')} {e}")

    print(tr("opening_manual_esen_import"))
    try:
        open_manual_import_window(driver)
        print(tr("manual_esen_import_opened"))
    except Exception as e:
        print(f"⚠️ Не удалось открыть ручной импорт: {e}")

    return driver
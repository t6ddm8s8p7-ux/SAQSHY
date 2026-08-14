import json
import os
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
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

ESEN_DRIVER = None

CONFIG_FILE = "config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return {}


def open_esen_login():
    global ESEN_DRIVER
    config = load_config()

    url = config.get("esen_url", "https://e-sen.kz")
    login = config.get("esen_login", "")
    password = config.get("esen_password", "")
    login, password = ask_esen_login(login, password)

    if not login or not password:
        print("❌ Вход в e-SEN отменён")
        return None

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install())
    )

    ESEN_DRIVER = driver
    wait = WebDriverWait(driver, 30)

    driver.get(url)
    time.sleep(3)

    login_button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//*[contains(text(),'Кіру') or contains(text(),'Войти')]")
        )
    )
    driver.execute_script("arguments[0].click();", login_button)
    time.sleep(3)

    wait.until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "input"))
    )

    inputs = driver.find_elements(By.TAG_NAME, "input")

    inputs[0].clear()
    inputs[0].send_keys(login)

    inputs[1].clear()
    inputs[1].send_keys(password)

    time.sleep(1)

    submit = driver.find_element(
        By.XPATH,
        "//button[contains(., 'Кіру') or contains(., 'Войти')]"
    )
    driver.execute_script("arguments[0].click();", submit)

    time.sleep(3)

    code = ask_sms_code()

    if code:
        code_inputs = driver.find_elements(By.TAG_NAME, "input")

        for i, digit in enumerate(code):
            code_inputs[-6 + i].send_keys(digit)

        time.sleep(1)

        confirm_btn = driver.find_element(
            By.XPATH,
            "//*[contains(text(),'Растау') or contains(text(),'Подтвердить')]"
        )
        driver.execute_script("arguments[0].click();", confirm_btn)

    print("Жду входа в личный кабинет...")

    wait.until(lambda d: "/profile" in d.current_url)

    print("✅ Вход в e-SEN выполнен")

    close_intro(driver)

    # Пробуем открыть раздел сотрудников (меню kk/ru или URL).
    # Если не вышло — не страшно: откроете вручную в браузере.
    try:
        print("📥 Пробую открыть раздел сотрудников...")
        if open_employees_section(driver):
            print("✅ Раздел сотрудников открыт")
        else:
            print("⚠️ Авто-переход не удался.")
            print("Откройте раздел вручную: Қызметкерлер / Сотрудники.")
    except Exception as e:
        print("Ошибка авто-перехода:", e)

    print("📥 Открываю ручной импорт e-SEN...")
    open_manual_import_window(driver)

    print("✅ Ручной импорт e-SEN открыт")

    return driver
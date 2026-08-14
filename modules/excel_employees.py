import json
import os
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def close_intro(driver):
    """Закрывает подсказки сайта на казахском, русском или английском."""
    wait = WebDriverWait(driver, 5)
    try:
        next_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH,
                "//*[contains(text(),'Келесі') or contains(text(),'Далее') or contains(text(),'Next')]"
            ))
        )
        driver.execute_script("arguments[0].click();", next_btn)
        time.sleep(1)
    except Exception:
        pass
    try:
        done_btn = wait.until(
            EC.element_to_be_clickable((By.XPATH,
                "//*[contains(text(),'Аяқтау') or contains(text(),'Аяқталды') "
                "or contains(text(),'Завершить') or contains(text(),'Finish')]"
            ))
        )
        driver.execute_script("arguments[0].click();", done_btn)
        time.sleep(1)
    except Exception:
        pass


def read_current_page(driver, page_number=1):
    for attempt in range(3):
        try:
            employees_data = []
            WebDriverWait(driver, 45).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            WebDriverWait(driver, 45).until(
                lambda d: d.execute_script("""
                    const rows = document.querySelectorAll("table tbody tr");
                    if (!rows.length) return false;
                    const text = Array.from(rows)
                        .map(row => row.innerText.trim())
                        .join(" ");
                    return text.length > 20;
                """)
            )
            time.sleep(2)
            rows_data = driver.execute_script("""
                const rows = document.querySelectorAll("table tbody tr");
                return Array.from(rows).map(row => {
                    const cells = row.querySelectorAll("td");
                    return Array.from(cells).map(cell => cell.innerText.trim());
                });
            """)
            print("=" * 60)
            print("СОТРУДНИКИ / ҚЫЗМЕТКЕРЛЕР")
            print("=" * 60)
            for index, cols in enumerate(rows_data, start=1):
                while len(cols) < 7:
                    cols.append("-")
                emp = {
                    "fio": cols[0],
                    "workplace": cols[1],
                    "position": cols[2],
                    "medical_book": cols[3],
                    "group": cols[4],
                    "valid_until": cols[5],
                    "status": cols[6],
                    "page_number": page_number,
                    "row_number": index,
                    "raw_data": cols,
                }
                if not emp["fio"]:
                    emp["fio"] = f"Строка e-SEN без ФИО / страница {page_number}, строка {index}"
                    emp["status"] = "Нет информации"
                    emp["no_fio"] = True
                else:
                    emp["no_fio"] = False
                employees_data.append(emp)
                print("ФИО:", emp["fio"])
            print(f"✅ На странице найдено: {len(employees_data)}")
            return employees_data
        except Exception as e:
            print(f"⚠️ Ошибка чтения страницы. Попытка {attempt + 1}/3")
            print(e)
            time.sleep(3)
    print("❌ Не удалось прочитать страницу после 3 попыток.")
    return []


def get_pagination_text(driver):
    try:
        items = driver.find_elements(
            By.XPATH,
            "//*[contains(text(),'из') or contains(text(),'of') "
            "or contains(text(),'ішінен') or contains(text(),'дан')]"
        )
    except Exception:
        return ""
    for item in items:
        text = item.text.strip()
        if text:
            return text
    return ""


def get_next_button(driver):
    try:
        buttons = driver.find_elements(By.TAG_NAME, "button")
    except Exception:
        return None
    for btn in buttons:
        try:
            label = (btn.get_attribute("aria-label") or "").lower()
            title = (btn.get_attribute("title") or "").lower()
            if (
                "next page" in label
                or "go to next page" in label
                or "next page" in title
                or "go to next page" in title
                or "келесі" in label
                or "келесі" in title
                or "далее" in label
                or "далее" in title
                or "следующ" in label
                or "следующ" in title
            ):
                return btn
        except Exception:
            continue
    try:
        candidates = driver.find_elements(
            By.XPATH,
            "//button[.//*[name()='svg']]"
        )
        if candidates:
            return candidates[-1]
    except Exception:
        pass
    return None


def is_next_disabled(btn):
    try:
        if btn.get_attribute("disabled"):
            return True
        if btn.get_attribute("aria-disabled") == "true":
            return True
        class_name = (btn.get_attribute("class") or "").lower()
        if "disabled" in class_name:
            return True
    except Exception:
        return False
    return False


def click_next_page(driver):
    for attempt in range(3):
        try:
            old_text = get_pagination_text(driver)
            next_btn = get_next_button(driver)
            if not next_btn:
                print("✅ Кнопка следующей страницы не найдена.")
                return False
            if is_next_disabled(next_btn):
                print("✅ Кнопка следующей страницы отключена.")
                return False
            driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});",
                next_btn
            )
            time.sleep(1)
            next_btn = get_next_button(driver)
            if not next_btn or is_next_disabled(next_btn):
                print("✅ Следующая страница недоступна.")
                return False
            driver.execute_script("arguments[0].click();", next_btn)
            try:
                WebDriverWait(driver, 20).until(
                    lambda d: get_pagination_text(d) != old_text
                )
            except Exception:
                pass
            time.sleep(4)
            new_text = get_pagination_text(driver)
            if new_text == old_text:
                print("✅ Пагинация не изменилась. Вероятно, последняя страница.")
                return False
            return True
        except Exception as e:
            print(f"⚠️ Ошибка перехода ({attempt + 1}/3)")
            print(e)
            time.sleep(3)
    print("⚠️ Не удалось перейти дальше после 3 попыток.")
    return False


def finish_reading(all_employees):
    unique = {}
    for emp in all_employees:
        fio = emp.get("fio", "").strip()
        med = emp.get("medical_book", "").strip()
        page = emp.get("page_number", "")
        row = emp.get("row_number", "")
        if not fio and not med:
            continue
        if emp.get("no_fio"):
            key = f"NO_FIO_{page}{row}{med}"
        else:
            key = f"{fio}_{med}"
        unique[key] = emp
    result = list(unique.values())
    print(f"✅ Всего уникальных сотрудников e-SEN: {len(result)}")
    return result


def read_all_pages(driver):
    all_employees = []
    page = 1
    max_pages = 200
    while page <= max_pages:
        print(f"\n📄 Читаю страницу: {page}")
        current_page_employees = read_current_page(driver, page)
        all_employees.extend(current_page_employees)
        moved = click_next_page(driver)
        if not moved:
            print("✅ Последняя страница успешно прочитана.")
            break
        page += 1
    return finish_reading(all_employees)


def save_employees(employees_data, force=False):
    os.makedirs("database", exist_ok=True)
    file_path = "database/esen_employees.json"
    old_count = 0
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                old_data = json.load(f)
                old_count = len(old_data) if isinstance(old_data, list) else 0
        except Exception:
            old_count = 0
    new_count = len(employees_data)
    if old_count > 0 and new_count < old_count and not force:
        print("⚠️ ВНИМАНИЕ: новая база меньше предыдущей.")
        print(f"Предыдущая база: {old_count}")
        print(f"Новая база: {new_count}")
        print("❌ Сохранение отменено, чтобы не потерять данные.")
        return False
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(employees_data, f, ensure_ascii=False, indent=2)
    print(f"✅ Сохранено сотрудников: {new_count}")
    return True


def open_employees(driver):
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    time.sleep(2)
    close_intro(driver)

    # Страница сотрудников: kk или ru
    opened = False
    for url in [
        "https://e-sen.kz/kk/employees/250128",
        "https://e-sen.kz/ru/employees/250128",
    ]:
        driver.get(url)
        time.sleep(7)
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "table"))
            )
            print(f"✅ Открыта страница сотрудников: {url}")
            opened = True
            break
        except Exception:
            print(f"⚠️ Нет таблицы на {url}, пробую другой язык...")
    if not opened:
        print("❌ Страница сотрудников не открылась.")
        return driver

    employees_data = read_all_pages(driver)
    save_employees(employees_data)
    return driver
import json
import os
import re
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def close_intro(driver):
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


def _has_table(driver, seconds=10):
    try:
        WebDriverWait(driver, seconds).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )
        return True
    except Exception:
        return False


def open_employees_section(driver):
    for text in ["Қызметкерлер", "Сотрудники", "Employees"]:
        try:
            found = driver.execute_script("""
                const text = arguments[0];
                const els = Array.from(
                    document.querySelectorAll('a, button, div, span, li')
                );
                const el = els.find(e =>
                    e.innerText && e.innerText.trim().includes(text)
                );
                if (el) { el.click(); return true; }
                return false;
            """, text)
            if found:
                time.sleep(5)
                if _has_table(driver, 8):
                    print(f"✅ Раздел сотрудников открыт через меню: {text}")
                    return True
        except Exception:
            continue

    for url in [
        "https://e-sen.kz/kk/employees/250128",
        "https://e-sen.kz/ru/employees/250128",
    ]:
        try:
            driver.get(url)
            time.sleep(5)
            if _has_table(driver, 8):
                print(f"✅ Раздел сотрудников открыт: {url}")
                return True
        except Exception:
            continue

    print("⚠️ Таблица не найдена — буду читать карточки как текст.")
    return False


# ============================================================
# СТРАТЕГИЯ 2: чтение из текста карточек (новый дизайн e-SEN)
# ============================================================
def read_from_text(driver, page_number=1):
    try:
        body = driver.find_element(By.TAG_NAME, "body").text
    except Exception:
        return []
    lines = [ln.strip() for ln in body.split("\n") if ln.strip()]
    med_re = re.compile(r"\b[A-Z]{2}\d{6}\b")
    date_re = re.compile(r"\d{4}-\d{2}-\d{2}\s*-\s*\d{4}-\d{2}-\d{2}")

    employees = []
    for i, line in enumerate(lines):
        m = med_re.search(line)
        if not m:
            continue
        med = m.group(0)

        # ФИО ищем выше: строка из заглавных букв
        name = ""
        for cand in lines[max(0, i - 8):i]:
            letters = [c for c in cand if c.isalpha()]
            if len(cand) >= 8 and letters and cand == cand.upper():
                name = cand
                break

        # Даты и статус ищем рядом
        valid = ""
        status = ""
        for cand in lines[max(0, i - 6):min(len(lines), i + 6)]:
            if not valid:
                d = date_re.search(cand)
                if d:
                    valid = d.group(0)
            if ("Қабылданды" in cand or "Кабылданды" in cand
                    or "Принят" in cand):
                status = "Қабылданды"

        employees.append({
            "fio": name or f"Строка e-SEN без ФИО / страница {page_number}",
            "workplace": "-",
            "position": "-",
            "medical_book": med,
            "group": "-",
            "valid_until": valid or "-",
            "status": status or "-",
            "page_number": page_number,
            "row_number": i,
            "raw_data": [name, "-", "-", med, "-", valid, status],
            "no_fio": not name,
        })
    return employees


# ============================================================
# СТРАТЕГИЯ 1: таблица (старый дизайн)
# ============================================================
def read_from_table(driver, page_number=1):
    rows_data = driver.execute_script("""
        const rows = document.querySelectorAll("table tbody tr");
        return Array.from(rows).map(row => {
            const cells = row.querySelectorAll("td");
            return Array.from(cells).map(cell => cell.innerText.trim());
        });
    """)
    employees = []
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
        employees.append(emp)
    return employees


def read_current_page(driver, page_number=1):
    for attempt in range(3):
        try:
            # Стратегия 1: таблица
            if _has_table(driver, 12):
                WebDriverWait(driver, 30).until(
                    lambda d: d.execute_script("""
                        const rows = document.querySelectorAll("table tbody tr");
                        if (!rows.length) return false;
                        const text = Array.from(rows)
                            .map(row => row.innerText.trim()).join(" ");
                        return text.length > 20;
                    """)
                )
                time.sleep(2)
                employees = read_from_table(driver, page_number)
                if employees:
                    print(f"✅ На странице найдено: {len(employees)} (таблица)")
                    return employees

            # Стратегия 2: карточки (новый дизайн)
            time.sleep(3)
            employees = read_from_text(driver, page_number)
            if employees:
                print(f"✅ На странице найдено: {len(employees)} (карточки)")
                return employees

            # Диагностика: выводим текст страницы в терминал
            print("⚠️ Не распознано. ДИАГНОСТИКА СТРАНИЦЫ:")
            print("table элементов:", driver.execute_script(
                "return document.querySelectorAll('table').length"
            ))
            body = driver.find_element(By.TAG_NAME, "body").text
            print("---- ТЕКСТ СТРАНИЦЫ (первые 3000 символов) ----")
            print(body[:3000])
            print("---- КОНЕЦ ТЕКСТА ----")
            raise Exception("Структура страницы не распознана")
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
    open_employees_section(driver)
    employees_data = read_all_pages(driver)
    save_employees(employees_data)
    return driver
"""
Генератор официальных писем для руководства.
Шаблоны для различных ситуаций: медосмотры, нарушения, отчёты.
"""
from datetime import date, datetime


def generate_medical_expiring_letter(expiring_employees, days_threshold=30):
    """
    Генерирует письмо об истекающих медосмотрах.
    expiring_employees: список словарей с полями:
        fio, department, medical_book, valid_until, days_left
    """
    if not expiring_employees:
        return None, None

    today = date.today().strftime("%d.%m.%Y")

    # Заголовок
    subject = f"⚠️ Истекающие медосмотры ({len(expiring_employees)} чел.) — {today}"

    # Начало письма
    body = f"Уважаемый руководитель!\n\n"
    body += f"Довожу до Вашего сведения, что по состоянию на {today} "
    body += f"у {len(expiring_employees)} сотрудников истекает срок действия "
    body += f"медицинских книжек в ближайшие {days_threshold} дней или уже просрочен.\n\n"

    # Группировка по отделам
    by_department = {}
    for emp in expiring_employees:
        dept = emp.get("department", "Не указан")
        if dept not in by_department:
            by_department[dept] = []
        by_department[dept].append(emp)

    body += "Список сотрудников:\n\n"
    for dept, employees in sorted(by_department.items()):
        body += f"📍 {dept} ({len(employees)} чел.):\n"
        for emp in employees:
            status = "🔴 ПРОСРОЧЕНО" if emp["days_left"] < 0 else "🟡 Истекает"
            days_text = (
                f"{abs(emp['days_left'])} дн. назад"
                if emp["days_left"] < 0
                else f"{emp['days_left']} дн."
            )
            body += f"   • {emp['fio']} — до {emp['valid_until']} ({days_text}) [{status}]\n"
        body += "\n"

    # Рекомендации
    body += "Необходимые мероприятия:\n"
    body += "1. Организовать прохождение периодических медицинских осмотров указанными сотрудниками.\n"
    body += "2. Не допускать к работе сотрудников с просроченными медицинскими книжками.\n"
    body += "3. Обеспечить своевременное продление медицинских книжек во избежание нарушений санитарного законодательства.\n\n"

    body += "Приложение: реестр истекающих медосмотров (Excel).\n"

    return subject, body


def generate_violation_letter(violation_type, details, affected_count):
    """
    Генерирует письмо о нарушении.
    violation_type: тип нарушения (например, "e-SEN", "HACCP", "СанПиН")
    details: описание нарушения
    affected_count: количество затронутых сотрудников/объектов
    """
    today = date.today().strftime("%d.%m.%Y")

    subject = f"🚨 Нарушение: {violation_type} ({affected_count} случаев) — {today}"

    body = f"Уважаемый руководитель!\n\n"
    body += f"Довожу до Вашего сведения выявленное нарушение санитарно-эпидемиологических требований.\n\n"
    body += f"Дата выявления: {today}\n"
    body += f"Тип нарушения: {violation_type}\n"
    body += f"Количество случаев: {affected_count}\n\n"
    body += f"Описание:\n{details}\n\n"
    body += "Необходимые мероприятия:\n"
    body += "1. Провести анализ причин нарушения.\n"
    body += "2. Разработать и реализовать план corrective actions.\n"
    body += "3. Обеспечить контроль за устранением нарушения.\n"
    body += "4. Предоставить отчёт о проведённых мероприятиях в течение 5 рабочих дней.\n\n"
    body += "Нарушение требует немедленного реагирования во избежание штрафных санкций.\n"

    return subject, body


def generate_esen_missing_letter(missing_employees):
    """
    Генерирует письмо о сотрудниках, отсутствующих в e-SEN.
    """
    if not missing_employees:
        return None, None

    today = date.today().strftime("%d.%m.%Y")

    subject = f"⚠️ Сотрудники не зарегистрированы в e-SEN ({len(missing_employees)} чел.) — {today}"

    body = f"Уважаемый руководитель!\n\n"
    body += f"По результатам сверки базы данных HR с системой e-SEN на {today} "
    body += f"выявлено {len(missing_employees)} сотрудников, не зарегистрированных "
    body += f"в системе электронного санитарно-эпидемиологического надзора.\n\n"

    # Группировка по отделам
    by_department = {}
    for emp in missing_employees:
        dept = emp.get("Отдел", emp.get("department", "Не указан"))
        if dept not in by_department:
            by_department[dept] = []
        by_department[dept].append(emp)

    body += "Список сотрудников по отделам:\n\n"
    for dept, employees in sorted(by_department.items()):
        body += f"📍 {dept} ({len(employees)} чел.):\n"
        for emp in employees:
            fio = emp.get("Сотрудник", emp.get("fio", "Не указано"))
            position = emp.get("Должность", emp.get("position", "-"))
            body += f"   • {fio} — {position}\n"
        body += "\n"

    body += "Необходимые мероприятия:\n"
    body += "1. Зарегистрировать указанных сотрудников в системе e-SEN в срок до [указать дату].\n"
    body += "2. Обеспечить своевременную регистрацию новых сотрудников в день приёма на работу.\n"
    body += "3. Провести инструктаж руководителей подразделений о порядке регистрации в e-SEN.\n\n"

    body += "Отсутствие регистрации в e-SEN является нарушением санитарного законодательства.\n"

    return subject, body


def generate_weekly_report_letter(report_data):
    """
    Генерирует еженедельный сводный отчёт.
    report_data: словарь с метриками
    """
    today = date.today().strftime("%d.%m.%Y")

    subject = f"📊 Еженедельный отчёт СанЭпи — {today}"

    body = f"Уважаемый руководитель!\n\n"
    body += f"Направляю еженедельный отчёт о состоянии санитарно-эпидемиологического контроля "
    body += f"по состоянию на {today}.\n\n"

    body += "📈 Ключевые показатели:\n\n"
    body += f"1. Сверка HR ↔ e-SEN:\n"
    body += f"   • Всего сотрудников HR: {report_data.get('total_hr', 0)}\n"
    body += f"   • Зарегистрировано в e-SEN: {report_data.get('matched', 0)}\n"
    body += f"   • Процент соответствия: {report_data.get('match_percent', 0)}%\n"
    body += f"   • Не зарегистрированы: {report_data.get('only_hr', 0)}\n\n"

    body += f"2. Медицинские осмотры:\n"
    body += f"   • Истекают в 30 дней: {report_data.get('expiring_30', 0)}\n"
    body += f"   • Просрочено: {report_data.get('expired', 0)}\n\n"

    body += f"3. HACCP:\n"
    body += f"   • Температурных замеров: {report_data.get('haccp_records', 0)}\n"
    body += f"   • Пропусков графика: {report_data.get('missed_checks', 0)}\n\n"

    body += "4. Рекомендации:\n"
    if report_data.get("only_hr", 0) > 0:
        body += f"   • Зарегистрировать {report_data['only_hr']} сотрудников в e-SEN.\n"
    if report_data.get("expiring_30", 0) > 0:
        body += f"   • Организовать медосмотр для {report_data['expiring_30']} сотрудников.\n"
    if report_data.get("missed_checks", 0) > 0:
        body += f"   • Устранить {report_data['missed_checks']} пропусков замеров HACCP.\n"

    body += "\nПриложение: детализированный отчёт (Excel).\n"

    return subject, body
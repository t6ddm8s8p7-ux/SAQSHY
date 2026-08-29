# -*- coding: utf-8 -*-
"""Локализация SanEpi AI: RU / KK / EN / TR."""
import json
import os

LANG_FILE = os.path.join(os.path.dirname(__file__), "..", "database", "language.json")

current_language = "ru"

LANGUAGES = {
    "ru": "RU Русский",
    "kk": "KZ Қазақша",
    "en": "GB English",
    "tr": "TR Türkçe",
}

TEXT = {
    "app_title": {
        "ru": "SanEpi AI",
        "kk": "SanEpi AI",
        "en": "SanEpi AI",
        "tr": "SanEpi AI",
    },
    "language": {
        "ru": "Язык",
        "kk": "Тіл",
        "en": "Language",
        "tr": "Dil",
    },
    "dashboard": {
        "ru": "Dashboard",
        "kk": "Басқару панелі",
        "en": "Dashboard",
        "tr": "Gösterge paneli",
    },
    "sync": {
        "ru": "Синхронизация",
        "kk": "Синхрондау",
        "en": "Synchronization",
        "tr": "Senkronizasyon",
    },
    "hr": {
        "ru": "HR",
        "kk": "HR",
        "en": "HR",
        "tr": "HR",
    },
    "esen": {
        "ru": "e-SEN",
        "kk": "e-SEN",
        "en": "e-SEN",
        "tr": "e-SEN",
    },
    "medical": {
        "ru": "Медосмотр",
        "kk": "Медициналық қарап-тексеру",
        "en": "Medical exam",
        "tr": "Tıbbi muayene",
    },
    "laws": {
        "ru": "Приказы",
        "kk": "Бұйрықтар",
        "en": "Regulations",
        "tr": "Mevzuat",
    },
    "haccp": {
        "ru": "HACCP",
        "kk": "HACCP",
        "en": "HACCP",
        "tr": "HACCP",
    },
    "suppliers": {
        "ru": "Поставщики",
        "kk": "Жеткізушілер",
        "en": "Suppliers",
        "tr": "Tedarikçiler",
    },
    "suppliers_title": {
        "ru": "📦 Контроль поставщиков товаров",
        "kk": "📦 Тауар жеткізушілерін бақылау",
        "en": "📦 Supplier Control",
        "tr": "📦 Tedarikçi Kontrolü",
    },
    "suppliers_subtitle": {
        "ru": "Приёмка, сертификаты, оценка качества",
        "kk": "Қабылдау, сертификаттар, сапаны бағалау",
        "en": "Receiving, certificates, quality assessment",
        "tr": "Kabul, sertifikalar, kalite değerlendirmesi",
    },
    "add_supplier": {
        "ru": "➕ Добавить поставщика",
        "kk": "➕ Жеткізушіні қосу",
        "en": "➕ Add supplier",
        "tr": "➕ Tedarikçi ekle",
    },
    "receiving_goods": {
        "ru": "📥 Приёмка товаров",
        "kk": "📥 Тауарларды қабылдау",
        "en": "📥 Receiving goods",
        "tr": "📥 Mal kabulü",
    },
    "certificates": {
        "ru": "📜 Сертификаты",
        "kk": "📜 Сертификаттар",
        "en": "📜 Certificates",
        "tr": "📜 Sertifikalar",
    },
    "violations": {
        "ru": "⚠️ Нарушения",
        "kk": "⚠️ Бұзушылықтар",
        "en": "⚠️ Violations",
        "tr": "⚠️ İhlaller",
    },
    "supplier_name": {
        "ru": "Название поставщика",
        "kk": "Жеткізушінің атауы",
        "en": "Supplier name",
        "tr": "Tedarikçi adı",
    },
    "category": {
        "ru": "Категория",
        "kk": "Санат",
        "en": "Category",
        "tr": "Kategori",
    },
    "rating": {
        "ru": "Рейтинг",
        "kk": "Рейтинг",
        "en": "Rating",
        "tr": "Puan",
    },
    "excellent": {
        "ru": "Отлично",
        "kk": "Тамаша",
        "en": "Excellent",
        "tr": "Mükemmel",
    },
    "blocked": {
        "ru": "Заблокирован",
        "kk": "Бұғатталған",
        "en": "Blocked",
        "tr": "Engellendi",
    },
    "accept_goods": {
        "ru": "✅ Принять товар",
        "kk": "✅ Тауарды қабылдау",
        "en": "✅ Accept goods",
        "tr": "✅ Malı kabul et",
    },
    "reject_goods": {
        "ru": "❌ Отклонить (брак)",
        "kk": "❌ Кері қайтару (ақау)",
        "en": "❌ Reject (defect)",
        "tr": "❌ Reddet (kusurlu)",
    },
    "temperature_on_receipt": {
        "ru": "Температура при приёмке",
        "kk": "Қабылдау кезіндегі температура",
        "en": "Temperature on receipt",
        "tr": "Teslim alma sıcaklığı",
    },
    "expiry_date": {
        "ru": "Срок годности",
        "kk": "Жарамдылық мерзімі",
        "en": "Expiry date",
        "tr": "Son kullanma tarihi",
    },
    "inspections": {
        "ru": "Проверки",
        "kk": "Тексерістер",
        "en": "Inspections",
        "tr": "Denetimler",
    },
    "letters": {
        "ru": "Письма",
        "kk": "Хаттар",
        "en": "Letters",
        "tr": "Yazılar",
    },
    "reports": {
        "ru": "Отчёты",
        "kk": "Есептер",
        "en": "Reports",
        "tr": "Raporlar",
    },
    "settings": {
        "ru": "Настройки",
        "kk": "Баптаулар",
        "en": "Settings",
        "tr": "Ayarlar",
    },
    "under_development": {
        "ru": "Раздел находится в разработке",
        "kk": "Бөлім әзірлену үстінде",
        "en": "This section is under development",
        "tr": "Bu bölüm geliştirme aşamasındadır",
    },
    "matched": {
        "ru": "Совпали",
        "kk": "Сәйкес келді",
        "en": "Matched",
        "tr": "Eşleşti",
    },
    "extra": {
        "ru": "Лишние",
        "kk": "Артық",
        "en": "Extra",
        "tr": "Fazla",
    },
    "medbooks": {
        "ru": "Медкнижки",
        "kk": "Медкітапшалар",
        "en": "Medical books",
        "tr": "Sağlık karneleri",
    },
    "errors": {
        "ru": "Ошибки",
        "kk": "Қателер",
        "en": "Errors",
        "tr": "Hatalar",
    },
    "departments": {
        "ru": "Отделов",
        "kk": "Бөлімдер",
        "en": "Departments",
        "tr": "Bölümler",
    },
    "export_excel": {
        "ru": "Экспорт отсутствующих в Excel",
        "kk": "Жоқ қызметкерлерді Excel-ге шығару",
        "en": "Export missing employees to Excel",
        "tr": "Eksik personeli Excel'e aktar",
    },
    "department_statistics": {
        "ru": "Статистика по отделам HR",
        "kk": "HR бөлімдері бойынша статистика",
        "en": "HR department statistics",
        "tr": "HR bölüm istatistikleri",
    },
    "employee_card": {
        "ru": "Карточка сотрудника",
        "kk": "Қызметкер карточкасы",
        "en": "Employee card",
        "tr": "Personel kartı",
    },
    "fio": {
        "ru": "ФИО",
        "kk": "Аты-жөні",
        "en": "Full name",
        "tr": "Ad Soyad",
    },
    "department": {
        "ru": "Отдел",
        "kk": "Бөлім",
        "en": "Department",
        "tr": "Bölüm",
    },
    "position": {
        "ru": "Должность",
        "kk": "Лауазымы",
        "en": "Position",
        "tr": "Görev",
    },
    "medical_book": {
        "ru": "Медкнижка",
        "kk": "Медициналық кітапша",
        "en": "Medical book",
        "tr": "Sağlık karnesi",
    },
    "status": {
        "ru": "Статус",
        "kk": "Статус",
        "en": "Status",
        "tr": "Durum",
    },
    "period": {
        "ru": "Период действия",
        "kk": "Жарамдылық кезеңі",
        "en": "Validity period",
        "tr": "Geçerlilik süresi",
    },
    "condition": {
        "ru": "Состояние",
        "kk": "Жағдайы",
        "en": "Condition",
        "tr": "Durum",
    },
    "admitted": {
        "ru": "Допущен",
        "kk": "Жіберілген",
        "en": "Admitted",
        "tr": "Uygun",
    },
    "not_admitted": {
        "ru": "Не допущен",
        "kk": "Жіберілмеген",
        "en": "Not admitted",
        "tr": "Uygun değil",
    },
    "not_in_esen": {
        "ru": "Нет в e-SEN",
        "kk": "e-SEN-де жоқ",
        "en": "Not in e-SEN",
        "tr": "e-SEN'de yok",
    },
    "expired": {
        "ru": "Просрочено",
        "kk": "Мерзімі өткен",
        "en": "Expired",
        "tr": "Süresi geçmiş",
    },
    "expiring": {
        "ru": "Истекает",
        "kk": "Мерзімі аяқталуға жақын",
        "en": "Expiring soon",
        "tr": "Yakında sona erecek",
    },
    "ai_analysis": {
        "ru": "AI Анализ",
        "kk": "AI талдау",
        "en": "AI analysis",
        "tr": "AI analizi",
    },
    "days_left": {
        "ru": "Осталось дней",
        "kk": "Қалған күн",
        "en": "Days left",
        "tr": "Kalan gün",
    },
    "esen_center": {
        "ru": "e-SEN Center",
        "kk": "e-SEN орталығы",
        "en": "e-SEN Center",
        "tr": "e-SEN Merkezi",
    },
    "total_esen": {
        "ru": "Всего e-SEN",
        "kk": "Барлық e-SEN",
        "en": "Total e-SEN",
        "tr": "Toplam e-SEN",
    },
    "exists_in_hr": {
        "ru": "Есть в HR",
        "kk": "HR-де бар",
        "en": "In HR",
        "tr": "HR'de var",
    },
    "not_in_hr": {
        "ru": "Нет в HR",
        "kk": "HR-де жоқ",
        "en": "Not in HR",
        "tr": "HR'de yok",
    },
    "update_esen": {
        "ru": "Обновить e-SEN",
        "kk": "e-SEN жаңарту",
        "en": "Update e-SEN",
        "tr": "e-SEN'i güncelle",
    },
    "compare_with_hr": {
        "ru": "Сравнить с HR",
        "kk": "HR-мен салыстыру",
        "en": "Compare with HR",
        "tr": "HR ile karşılaştır",
    },
    "add_employees": {
        "ru": "Добавить сотрудников",
        "kk": "Қызметкерлерді қосу",
        "en": "Add employees",
        "tr": "Personel ekle",
    },
    "export_report": {
        "ru": "Экспорт отчёта",
        "kk": "Есепті экспорттау",
        "en": "Export report",
        "tr": "Raporu dışa aktar",
    },
    "hr_employees": {
        "ru": "HR сотрудники",
        "kk": "HR қызметкерлері",
        "en": "HR employees",
        "tr": "HR personeli",
    },
    "total_hr": {
        "ru": "Всего HR",
        "kk": "Барлық HR",
        "en": "Total HR",
        "tr": "Toplam HR",
    },
    "exists_in_esen": {
        "ru": "Есть в e-SEN",
        "kk": "e-SEN-де бар",
        "en": "In e-SEN",
        "tr": "e-SEN'de var",
    },
    "all_departments": {
        "ru": "Все отделы",
        "kk": "Барлық бөлімдер",
        "en": "All departments",
        "tr": "Tüm bölümler",
    },
    "all_statuses": {
        "ru": "Все статусы",
        "kk": "Барлық статустар",
        "en": "All statuses",
        "tr": "Tüm durumlar",
    },
    "search_hr": {
        "ru": "Поиск по ФИО, должности или отделу",
        "kk": "Аты-жөні, лауазымы немесе бөлімі бойынша іздеу",
        "en": "Search by name, position or department",
        "tr": "Ad, görev veya bölüme göre ara",
    },
    "esen_status": {
        "ru": "Статус e-SEN",
        "kk": "e-SEN статусы",
        "en": "e-SEN status",
        "tr": "e-SEN durumu",
    },
    "nothing_found": {
        "ru": "Ничего не найдено",
        "kk": "Ештеңе табылмады",
        "en": "Nothing found",
        "tr": "Hiçbir şey bulunamadı",
    },
    "save": {
        "ru": "Сохранить",
        "kk": "Сақтау",
        "en": "Save",
        "tr": "Kaydet",
    },
    "cancel": {
        "ru": "Отмена",
        "kk": "Бас тарту",
        "en": "Cancel",
        "tr": "İptal",
    },
    "close": {
        "ru": "Закрыть",
        "kk": "Жабу",
        "en": "Close",
        "tr": "Kapat",
    },
    "login": {
        "ru": "Логин",
        "kk": "Логин",
        "en": "Login",
        "tr": "Kullanıcı",
    },
    "password": {
        "ru": "Пароль",
        "kk": "Құпия сөз",
        "en": "Password",
        "tr": "Şifre",
    },
    "url": {
        "ru": "Ссылка",
        "kk": "Сілтеме",
        "en": "URL",
        "tr": "Bağlantı",
    },
    "check_connection": {
        "ru": "Проверить подключение",
        "kk": "Қосылымды тексеру",
        "en": "Check connection",
        "tr": "Bağlantıyı kontrol et",
    },
    "connected": {
        "ru": "Подключено",
        "kk": "Қосылған",
        "en": "Connected",
        "tr": "Bağlandı",
    },
    "not_connected": {
        "ru": "Нет подключения",
        "kk": "Қосылмаған",
        "en": "Not connected",
        "tr": "Bağlantı yok",
    },
    "esen_settings": {
        "ru": "Настройки e-SEN",
        "kk": "e-SEN баптаулары",
        "en": "e-SEN Settings",
        "tr": "e-SEN Ayarları",
    },
    "esen_login": {
        "ru": "Логин e-SEN",
        "kk": "e-SEN логині",
        "en": "e-SEN Login",
        "tr": "e-SEN Kullanıcı",
    },
    "esen_password": {
        "ru": "Пароль e-SEN",
        "kk": "e-SEN құпия сөзі",
        "en": "e-SEN Password",
        "tr": "e-SEN Şifresi",
    },
    "esen_url": {
        "ru": "Ссылка e-SEN",
        "kk": "e-SEN сілтемесі",
        "en": "e-SEN URL",
        "tr": "e-SEN Bağlantısı",
    },
    "settings_saved": {
        "ru": "Настройки сохранены",
        "kk": "Баптаулар сақталды",
        "en": "Settings saved",
        "tr": "Ayarlar kaydedildi",
    },
    "esen_opened": {
        "ru": "e-SEN открыт. После входа код вводится вручную.",
        "kk": "e-SEN ашылды. Кіру кодын қолмен енгізіңіз.",
        "en": "e-SEN opened. Enter the login code manually.",
        "tr": "e-SEN açıldı. Giriş kodunu manuel girin.",
    },
    "import_hr_excel": {
        "ru": "Загрузить HR Excel",
        "kk": "HR Excel жүктеу",
        "en": "Import HR Excel",
        "tr": "HR Excel içe aktar",
    },
    "compare_with_esen": {
        "ru": "Сравнить с e-SEN",
        "kk": "e-SEN-мен салыстыру",
        "en": "Compare with e-SEN",
        "tr": "e-SEN ile karşılaştır",
    },
    "risk_level": {
        "ru": "Уровень риска",
        "kk": "Тәуекел деңгейі",
        "en": "Risk level",
        "tr": "Risk seviyesi",
    },
    "high": {
        "ru": "Высокий",
        "kk": "Жоғары",
        "en": "High",
        "tr": "Yüksek",
    },
    "medium": {
        "ru": "Средний",
        "kk": "Орташа",
        "en": "Medium",
        "tr": "Orta",
    },
    "low": {
        "ru": "Низкий",
        "kk": "Төмен",
        "en": "Low",
        "tr": "Düşük",
    },
    "problem_departments": {
        "ru": "Наиболее проблемные отделы",
        "kk": "Ең проблемалы бөлімдер",
        "en": "Most problematic departments",
        "tr": "En sorunlu departments",
    },
    "ai_recommendations": {
        "ru": "Рекомендации SanEpi AI",
        "kk": "SanEpi AI ұсыныстары",
        "en": "SanEpi AI Recommendations",
        "tr": "SanEpi AI Önerileri",
    },
    "no_problem_departments": {
        "ru": "Проблемные отделы не выявлены",
        "kk": "Проблемалы бөлімдер анықталмады",
        "en": "No problematic departments found",
        "tr": "Sorunlu departman bulunmadı",
    },
    "employees_not_in_esen": {
        "ru": "сотрудников нет в e-SEN",
        "kk": "қызметкер e-SEN-де жоқ",
        "en": "employees are not in e-SEN",
        "tr": "personel e-SEN'de yok",
    },
    "register_missing_employees": {
        "ru": "Зарегистрировать сотрудников, отсутствующих в e-SEN",
        "kk": "e-SEN-де жоқ қызметкерлерді тіркеу",
        "en": "Register employees missing in e-SEN",
        "tr": "e-SEN'de olmayan personeli kaydet",
    },
    "extend_expiring_medbooks": {
        "ru": "Организовать продление медицинских книжек с истекающим сроком",
        "kk": "Мерзімі аяқталуға жақын медициналық кітапшаларды ұзартуды ұйымдастыру",
        "en": "Arrange renewal of expiring medical books",
        "tr": "Süresi dolmak üzere olan sağlık karnelerini yenile",
    },
    "control_new_employees": {
        "ru": "Контролировать регистрацию новых сотрудников сразу после приема на работу",
        "kk": "Жаңа қызметкерлерді жұмысқа қабылданғаннан кейін бірден тіркеуді бақылау",
        "en": "Control registration of new employees immediately after hiring",
        "tr": "Yeni personelin işe alımdan hemen sonra kaydını kontrol et",
    },
    "repeat_sync": {
        "ru": "Повторно выполнить сверку после обновления HR и e-SEN",
        "kk": "HR және e-SEN жаңартылғаннан кейін салыстыруды қайта орындау",
        "en": "Repeat comparison after updating HR and e-SEN",
        "tr": "HR ve e-SEN güncellendikten sonra karşılaştırmayı tekrarla",
    },
    "no_action_required": {
        "ru": "Действий не требуется",
        "kk": "Әрекет қажет емес",
        "en": "No action required",
        "tr": "İşlem gerekmez",
    },
    "no_violations_found": {
        "ru": "Нарушений не выявлено.",
        "kk": "Бұзушылықтар анықталған жоқ.",
        "en": "No violations detected.",
        "tr": "Herhangi bir ihlal tespit edilmedi.",
    },
    "employee_can_work": {
        "ru": "Сотрудник может быть допущен к работе.",
        "kk": "Қызметкерді жұмысқа жіберуге болады.",
        "en": "The employee may be allowed to work.",
        "tr": "Çalışanın işe başlamasına izin verilebilir.",
    },
    "check": {
        "ru": "Проверка",
        "kk": "Тексеру",
        "en": "Check",
        "tr": "Kontrol",
    },
    "employee_must_be_checked_and_registered": {
        "ru": "Сотрудника необходимо проверить и зарегистрировать в e-SEN.",
        "kk": "Қызметкерді тексеріп, e-SEN жүйесіне тіркеу қажет.",
        "en": "The employee must be checked and registered in e-SEN.",
        "tr": "Personel kontrol edilmeli ve e-SEN'e kaydedilmelidir.",
    },
    "medical_book_expired": {
        "ru": "Срок действия медицинской книжки истек.",
        "kk": "Медициналық кітапшаның мерзімі аяқталған.",
        "en": "Medical book has expired.",
        "tr": "Sağlık karnesinin süresi dolmuştur.",
    },
    "employee_not_allowed": {
        "ru": "Сотрудника нельзя допускать к работе до обновления данных.",
        "kk": "Деректер жаңартылғанға дейін қызметкерді жұмысқа жіберуге болмайды.",
        "en": "Employee must not be allowed to work until records are updated.",
        "tr": "Bilgiler güncellenene kadar çalışmasına izin verilmemelidir.",
    },
    "medical_book_expiring": {
        "ru": "Срок действия медицинской книжки скоро истекает.",
        "kk": "Медициналық кітапшаның мерзімі жақында аяқталады.",
        "en": "Medical book will expire soon.",
        "tr": "Sağlık karnesinin süresi yakında dolacak.",
    },
    "renew_recommended": {
        "ru": "Рекомендуется заранее организовать продление.",
        "kk": "Мерзімін алдын ала ұзарту ұсынылады.",
        "en": "Renewal is recommended in advance.",
        "tr": "Önceden yenilenmesi tavsiye edilir.",
    },
    "medical_book_unknown": {
        "ru": "Срок действия медицинской книжки не определён.",
        "kk": "Медициналық кітапшаның мерзімі анықталмаған.",
        "en": "Medical book validity is unknown.",
        "tr": "Sağlık karnesinin geçerlilik süresi bilinmiyor.",
    },
    "check_employee_data": {
        "ru": "Рекомендуется проверить данные сотрудника.",
        "kk": "Қызметкердің деректерін тексеру ұсынылады.",
        "en": "Employee data should be verified.",
        "tr": "Çalışan bilgileri kontrol edilmelidir.",
    },
    "unknown": {
        "ru": "Не определён",
        "kk": "Анықталмаған",
        "en": "Unknown",
        "tr": "Bilinmiyor",
    },
    "register_in_esen": {
        "ru": "Сотрудника необходимо проверить и зарегистрировать в e-SEN.",
        "kk": "Қызметкерді тексеріп, e-SEN жүйесіне тіркеу қажет.",
        "en": "The employee must be verified and registered in e-SEN.",
        "tr": "Çalışan kontrol edilmeli ve e-SEN sistemine kaydedilmelidir.",
    },
    "organize_med_exam_before_expiry": {
        "ru": "Организовать прохождение периодического медицинского осмотра до окончания срока действия.",
        "kk": "Жарамдылық мерзімі аяқталғанға дейін мерзімдік медициналық қарап-тексеруден өтуді ұйымдастыру қажет.",
        "en": "Arrange the periodic medical examination before the validity period expires.",
        "tr": "Geçerlilik süresi dolmadan periyodik sağlık muayenesinin yapılmasını organize edin.",
    },
    "avoid_gap_between_medbooks": {
        "ru": "Не допускать перерыва между окончанием текущей медицинской книжки и оформлением новой.",
        "kk": "Қолданыстағы медициналық кітапшаның мерзімі аяқталуы мен жаңасының рәсімделуі арасында үзіліске жол бермеу қажет.",
        "en": "Do not allow a gap between the expiration of the current medical book and issuing a new one.",
        "tr": "Mevcut sağlık karnesinin süresinin bitmesi ile yenisinin düzenlenmesi arasında boşluk oluşmasına izin vermeyin.",
    },
    "medical_under_development": {
        "ru": "Модуль медицинских осмотров находится в разработке.",
        "kk": "Медициналық қарап-тексеру модулі әзірлену үстінде.",
        "en": "The medical examination module is under development.",
        "tr": "Tıbbi muayene modülü geliştirme aşamasındadır.",
    },
    "valid": {
        "ru": "Действует",
        "kk": "Жарамды",
        "en": "Valid",
        "tr": "Geçerli",
    },
    "hygiene_training": {
        "ru": "Гигиеническое обучение",
        "kk": "Гигиеналық оқыту",
        "en": "Hygiene training",
        "tr": "Hijyen eğitimi",
    },
    "not_used_yet": {
        "ru": "Пока не используется",
        "kk": "Әзірге қолданылмайды",
        "en": "Not used yet",
        "tr": "Henüz kullanılmıyor",
    },
    "ai_assistant": {
        "ru": "AI Помощник",
        "kk": "AI Көмекші",
        "en": "AI Assistant",
        "tr": "AI Asistanı",
    },
    "ai_select_laws": {
        "ru": "Нормативы для анализа",
        "kk": "Талдауға арналған нормативтер",
        "en": "Regulations to analyze",
        "tr": "Analiz edilecek mevzuat",
    },
    "ai_question": {
        "ru": "Вопрос для AI",
        "kk": "AI-ға сұрақ",
        "en": "Question for AI",
        "tr": "AI için soru",
    },
    "ai_analyze": {
        "ru": "Анализировать",
        "kk": "Талдау жасау",
        "en": "Analyze",
        "tr": "Analiz et",
    },
    "ai_save_memory": {
        "ru": "Сохранить ответ в память",
        "kk": "Жауапты есте сақтау",
        "en": "Save answer to memory",
        "tr": "Yanıtı hafızaya kaydet",
    },
    "data_as_of": {
        "ru": "Данные по состоянию на",
        "kk": "Деректер күні",
        "en": "Data as of",
        "tr": "Veri tarihi",
    },
    "search": {
        "ru": "Поиск",
        "kk": "Іздеу",
        "en": "Search",
        "tr": "Arama",
    },
    "all": {
        "ru": "Все",
        "kk": "Барлығы",
        "en": "All",
        "tr": "Tümü",
    },
    "file_not_found": {"ru": "Файл не найден: {path}", "kk": "Файл табылмады: {path}", "en": "File not found: {path}", "tr": "Dosya bulunamadı: {path}"},
    "select_hr_file": {"ru": "Выберите файл HR (Excel или CSV)", "kk": "HR файлын таңдаңыз (Excel немесе CSV)", "en": "Select HR file (Excel or CSV)", "tr": "HR dosyasını seçin (Excel veya CSV)"},
    "read_error": {"ru": "Ошибка чтения", "kk": "Оқу қатесі", "en": "Read error", "tr": "Okuma hatası"},
    "failed_to_read_file": {"ru": "Не удалось прочитать файл:\n{e}", "kk": "Файлды оқу мүмкін болмады:\n{e}", "en": "Failed to read file:\n{e}", "tr": "Dosya okunamadı:\n{e}"},
    "warning": {"ru": "Внимание", "kk": "Назар аударыңыз", "en": "Warning", "tr": "Uyarı"},
    "employees_not_found_check_fio": {"ru": "Сотрудники не найдены. Проверьте, что в файле есть колонка с ФИО.", "kk": "Қызметкерлер табылмады. Файлда А.Т.Ж. бағаны бар екенін тексеріңіз.", "en": "Employees not found. Check that the file has a Full Name column.", "tr": "Çalışanlar bulunamadı. Dosyada Ad Soyad sütunu olduğunu kontrol edin."},
    "success": {"ru": "Успех", "kk": "Сәтті", "en": "Success", "tr": "Başarılı"},
    "loaded_employees_and_departments": {"ru": "✅ Загружено сотрудников: {count}\n🏢 Отделов: {deps}", "kk": "✅ Жүктелген қызметкерлер: {count}\n🏢 Бөлімдер: {deps}", "en": "✅ Loaded employees: {count}\n🏢 Departments: {deps}", "tr": "✅ Yüklenen çalışanlar: {count}\n🏢 Departmanlar: {deps}"},
    "esen_login_cancelled": {"ru": "❌ Вход в e-SEN отменён", "kk": "❌ e-SEN-ге кіру болдырылмады", "en": "❌ e-SEN login cancelled", "tr": "❌ e-SEN girişi iptal edildi"},
    "waiting_for_login": {"ru": "Жду входа в личный кабинет...", "kk": "Жеке кабинетке кіруді күтудемін...", "en": "Waiting for login to personal account...", "tr": "Kişisel hesaba giriş bekleniyor..."},
    "esen_login_successful": {"ru": "✅ Вход в e-SEN выполнен", "kk": "✅ e-SEN-ге кіру орындалды", "en": "✅ e-SEN login successful", "tr": "✅ e-SEN girişi başarılı"},
    "trying_to_open_employees_section": {"ru": "📥 Пробую открыть раздел сотрудников...", "kk": "📥 Қызметкерлер бөлімін ашуға тырысудамын...", "en": "📥 Trying to open employees section...", "tr": "📥 Çalışanlar bölümünü açmaya çalışıyorum..."},
    "employees_section_opened": {"ru": "✅ Раздел сотрудников открыт", "kk": "✅ Қызметкерлер бөлімі ашылды", "en": "✅ Employees section opened", "tr": "✅ Çalışanlar bölümü açıldı"},
    "auto_redirect_failed": {"ru": "⚠️ Авто-переход не удался.", "kk": "⚠️ Авто-өту сәтсіз аяқталды.", "en": "⚠️ Auto-redirect failed.", "tr": "⚠️ Otomatik yönlendirme başarısız."},
    "open_section_manually": {"ru": "Откройте раздел вручную: Қызметкерлер / Сотрудники.", "kk": "Бөлімді қолмен ашыңыз: Қызметкерлер / Сотрудники.", "en": "Open section manually: Employees.", "tr": "Bölümü manuel olarak açın: Çalışanlar."},
    "auto_redirect_error": {"ru": "Ошибка авто-перехода:", "kk": "Авто-өту қатесі:", "en": "Auto-redirect error:", "tr": "Otomatik yönlendirme hatası:"},
    "opening_manual_esen_import": {"ru": "📥 Открываю ручной импорт e-SEN...", "kk": "📥 e-SEN қолмен импортын ашудамын...", "en": "📥 Opening manual e-SEN import...", "tr": "📥 Manuel e-SEN içe aktarımı açılıyor..."},
    "manual_esen_import_opened": {"ru": "✅ Ручной импорт e-SEN открыт", "kk": "✅ e-SEN қолмен импорты ашылды", "en": "✅ Manual e-SEN import opened", "tr": "✅ Manuel e-SEN içe aktarımı açıldı"},
    "comparison_completed": {"ru": "✅ Сверка завершена", "kk": "✅ Салыстыру аяқталды", "en": "✅ Comparison completed", "tr": "✅ Karşılaştırma tamamlandı"},
    "hr_excel_count": {"ru": "HR Excel: {count}", "kk": "HR Excel: {count}", "en": "HR Excel: {count}", "tr": "HR Excel: {count}"},
    "esen_count": {"ru": "e-SEN: {count}", "kk": "e-SEN: {count}", "en": "e-SEN: {count}", "tr": "e-SEN: {count}"},
    "matched_count": {"ru": "Совпали: {count}", "kk": "Сәйкес келді: {count}", "en": "Matched: {count}", "tr": "Eşleşen: {count}"},
    "only_hr_count": {"ru": "Есть в HR, но нет в e-SEN: {count}", "kk": "HR-де бар, бірақ e-SEN-де жоқ: {count}", "en": "In HR but not in e-SEN: {count}", "tr": "HR'de var ama e-SEN'de yok: {count}"},
    "only_esen_count": {"ru": "Есть в e-SEN, но нет в HR: {count}", "kk": "e-SEN-де бар, бірақ HR-де жоқ: {count}", "en": "In e-SEN but not in HR: {count}", "tr": "e-SEN'de var ama HR'de yok: {count}"},
}


def set_language(lang):
    global current_language
    if lang in LANGUAGES:
        current_language = lang
        try:
            os.makedirs(os.path.dirname(LANG_FILE), exist_ok=True)
            with open(LANG_FILE, "w", encoding="utf-8") as f:
                json.dump({"language": lang}, f)
        except Exception:
            pass


def get_language():
    return current_language


def tr(key):
    item = TEXT.get(key)
    if not item:
        return key
    return item.get(current_language, item.get("ru", key))


def _load_language():
    global current_language
    try:
        with open(LANG_FILE, encoding="utf-8") as f:
            lang = json.load(f).get("language", "ru")
        if lang in LANGUAGES:
            current_language = lang
    except Exception:
        pass


_load_language()
# -*- coding: utf-8 -*-
"""Переводы для журнала жалоб и других модулей."""

COMPLAINT_TRANSLATIONS = {
    # === Источники (SOURCES) ===
    "Внутренний аудит": {
        "ru": "Внутренний аудит",
        "kk": "Ішкі аудит",
        "en": "Internal audit",
        "tr": "İç denetim"
    },
    "Комментарии гостей (карточки отеля)": {
        "ru": "Комментарии гостей (карточки отеля)",
        "kk": "Қонақтардың пікірлері (отель карталары)",
        "en": "Guest comments (hotel cards)",
        "tr": "Misafir yorumları (otel kartları)"
    },
    
    # === Категории (CATEGORIES) ===
    "Бассейн / Аквапарк": {
        "ru": "Бассейн / Аквапарк",
        "kk": "Бассейн / Су паркі",
        "en": "Pool / Waterpark",
        "tr": "Havuz / Su parkı"
    },
    "Питание /Restaurant": {
        "ru": "Питание /Restaurant",
        "kk": "Тамақтану /Restaurant",
        "en": "Food /Restaurant",
        "tr": "Yemek /Restoran"
    },
    
    # === Статусы (STATUSES) ===
    "🆕 Новая": {
        "ru": "🆕 Новая",
        "kk": "🆕 Жаңа",
        "en": "🆕 New",
        "tr": "🆕 Yeni"
    },
    "✅ Решена": {
        "ru": "✅ Решена",
        "kk": "✅ Шешілді",
        "en": "✅ Resolved",
        "tr": "✅ Çözüldü"
    },
    
    # === Приоритеты (PRIORITIES) ===
    "🟡 Средняя": {
        "ru": "🟡 Средняя",
        "kk": "🟡 Орташа",
        "en": "🟡 Medium",
        "tr": "🟡 Orta"
    },
    
    # === Типы жалоб (COMPLAINT_TYPES) ===
    "Бассейн: температура / чистота воды": {
        "ru": "Бассейн: температура / чистота воды",
        "kk": "Бассейн: температура / судың тазалығы",
        "en": "Pool: temperature / water cleanliness",
        "tr": "Havuz: sıcaklık / su temizliği"
    },
    "Пищевое отравление / подозрение на отравление": {
        "ru": "Пищевое отравление / подозрение на отравление",
        "kk": "Тамақтан улану / улануға күдік",
        "en": "Food poisoning / suspected poisoning",
        "tr": "Gıda zehirlenmesi / şüpheli zehirlenme"
    },
    
    # === DD_SERVICES (Дезинфекция/Дератизация) ===
    "Дезинсекция — ползающие насекомые": {
        "ru": "Дезинсекция — ползающие насекомые",
        "kk": "Дезинсекция — жорғалаушы жәндіктер",
        "en": "Disinsection — crawling insects",
        "tr": "Dezinseksiyon — sürünen böcekler"
    },
    "Дезинсекция — летающие (снаружи зданий)": {
        "ru": "Дезинсекция — летающие (снаружи зданий)",
        "kk": "Дезинсекция — ұшатын (ғимарат сыртында)",
        "en": "Disinsection — flying (outside buildings)",
        "tr": "Dezinseksiyon — uçan (bina dışında)"
    },
    "Дератизация": {
        "ru": "Дератизация",
        "kk": "Дератизация",
        "en": "Deratization",
        "tr": "Deratizasyon"
    },
    "Дезинфекция (разовая по заявке)": {
        "ru": "Дезинфекция (разовая по заявке)",
        "kk": "Дезинфекция (өтінім бойынша бір реттік)",
        "en": "Disinfection (one-time by request)",
        "tr": "Dezenfeksiyon (talep üzerine tek seferlik)"
    },
    "Дезинсекция — летающие (внутри зданий)": {
        "ru": "Дезинсекция — летающие (внутри зданий)",
        "kk": "Дезинсекция — ұшатын (ғимарат ішінде)",
        "en": "Disinsection — flying (inside buildings)",
        "tr": "Dezinseksiyon — uçan (bina içinde)"
    },
    "внутри": {
        "ru": "внутри",
        "kk": "ішінде",
        "en": "inside",
        "tr": "içinde"
    },
    "снаружи": {
        "ru": "снаружи",
        "kk": "сыртында",
        "en": "outside",
        "tr": "dışında"
    },
    
    # === HYGIENE_TRAININGS (Обучение гигиене) ===
    "Личная гигиена персонала": {
        "ru": "Личная гигиена персонала",
        "kk": "Қызметкерлердің жеке гигиенасы",
        "en": "Personal hygiene of staff",
        "tr": "Personel hijyeni"
    },
    "Не определен": {
        "ru": "Не определен",
        "kk": "Анықталмаған",
        "en": "Not defined",
        "tr": "Tanımlanmamış"
    },
    
    # === HACCP_TEMPERATURE_RECORDS (Статус) ===
    "Норма": {
        "ru": "Норма",
        "kk": "Қалыпты",
        "en": "Normal",
        "tr": "Normal"
    },
}

def get_complaint_translation(key, lang="ru"):
    """Получить перевод для элемента списка."""
    if key in COMPLAINT_TRANSLATIONS:
        return COMPLAINT_TRANSLATIONS[key].get(lang, key)
    return key

def translate_list(items, lang="ru"):
    """Перевести список элементов."""
    from modules.translations import get_language
    current_lang = lang or get_language()
    return [get_complaint_translation(item, current_lang) for item in items]
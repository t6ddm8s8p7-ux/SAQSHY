from modules.translations import get_language


DEPARTMENTS = {
    "операционный отдел": {
        "ru": "Операционный отдел",
        "kk": "Операциялық бөлім",
        "en": "Operations Department",
        "tr": "Operasyon Bölümü",
    },
    "отдел водной безопасности": {
        "ru": "Отдел водной безопасности",
        "kk": "Су қауіпсіздігі бөлімі",
        "en": "Water Safety Department",
        "tr": "Su Güvenliği Bölümü",
    },
    "отдел гостиничного хозяйства": {
        "ru": "Отдел гостиничного хозяйства",
        "kk": "Қонақ үй шаруашылығы бөлімі",
        "en": "Housekeeping Department",
        "tr": "Kat Hizmetleri Bölümü",
    },
    "отдел досуга и развлечений": {
        "ru": "Отдел досуга и развлечений",
        "kk": "Демалыс және ойын-сауық бөлімі",
        "en": "Leisure & Entertainment Department",
        "tr": "Eğlence ve Aktivite Bölümü",
    },
    "отдел закупа": {
        "ru": "Отдел закупа",
        "kk": "Сатып алу бөлімі",
        "en": "Procurement Department",
        "tr": "Satın Alma Bölümü",
    },
    "ас үй бөлімі": {
        "ru": "Отдел кухни",
        "kk": "Ас үй бөлімі",
        "en": "Kitchen Department",
        "tr": "Mutfak Bölümü",
    },
    "отдел кухни": {
        "ru": "Отдел кухни",
        "kk": "Ас үй бөлімі",
        "en": "Kitchen Department",
        "tr": "Mutfak Bölümü",
    },
    "отдел мойщиков посуды": {
        "ru": "Отдел мойщиков посуды",
        "kk": "Ыдыс жуушылар бөлімі",
        "en": "Stewarding Department",
        "tr": "Bulaşıkhane Bölümü",
    },
    "отдел питания и напитков": {
        "ru": "Отдел питания и напитков",
        "kk": "Тамақтану және сусындар бөлімі",
        "en": "Food & Beverage Department",
        "tr": "Yiyecek ve İçecek Bölümü",
    },
    "отдел по работе с гостями": {
        "ru": "Отдел по работе с гостями",
        "kk": "Қонақтармен жұмыс бөлімі",
        "en": "Guest Relations Department",
        "tr": "Misafir İlişkileri Bölümü",
    },
    "кір жуу бөлімі": {
        "ru": "Отдел прачечной",
        "kk": "Кір жуу бөлімі",
        "en": "Laundry Department",
        "tr": "Çamaşırhane Bölümü",
    },
    "отдел прачечной": {
        "ru": "Отдел прачечной",
        "kk": "Кір жуу бөлімі",
        "en": "Laundry Department",
        "tr": "Çamaşırhane Bölümü",
    },
    "отдел приема и размещения гостей": {
        "ru": "Отдел приема и размещения гостей",
        "kk": "Қонақтарды қабылдау және орналастыру бөлімі",
        "en": "Front Office Department",
        "tr": "Ön Büro Bölümü",
    },
    "отдел спа": {
        "ru": "Отдел СПА",
        "kk": "СПА бөлімі",
        "en": "SPA Department",
        "tr": "SPA Bölümü",
    },
    "отдел технический": {
        "ru": "Технический отдел",
        "kk": "Техникалық бөлім",
        "en": "Technical Department",
        "tr": "Teknik Bölüm",
    },
    "отдел управление номерным фондом": {
        "ru": "Отдел управления номерным фондом",
        "kk": "Нөмірлік қорды басқару бөлімі",
        "en": "Rooms Division Department",
        "tr": "Odalar Bölümü",
    },
}


def translate_department(name):
    lang = get_language()
    key = str(name).strip().lower()

    item = DEPARTMENTS.get(key)

    if item:
        return item.get(lang, name)

    return name
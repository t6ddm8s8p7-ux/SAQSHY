# -*- coding: utf-8 -*-
"""ПОЛНАЯ проверка всех переводов в базе и интерфейсе."""
import sqlite3
import json
import re
from pathlib import Path
from modules.translations import LANGUAGES

# Загружаем существующие переводы
try:
    from modules.complaint_translations import COMPLAINT_TRANSLATIONS
except ImportError:
    COMPLAINT_TRANSLATIONS = {}

PROJECT_ROOT = Path(__file__).resolve().parent
DB_PATH = PROJECT_ROOT / "database" / "sanepi.db"
MODULES_DIR = PROJECT_ROOT / "modules"

def get_db():
    return sqlite3.connect(DB_PATH)

def check_all_database_tables():
    """Проверка только полей со статичными данными."""
    print("\n" + "="*70)
    print("🔍 ПРОВЕРКА БАЗЫ ДАННЫХ (только статичные данные)")
    print("="*70)
    
    conn = get_db()
    cursor = conn.cursor()
    
    # Поля СО СТАТИЧНЫМИ данными (категории, типы, статусы)
    static_fields = {
        'complaints': ['source', 'category', 'status', 'priority', 'description'],
        'dd_services': ['title', 'service_type', 'location'],
        'hygiene_trainings': ['topic'],
        'pools': ['pool_type'],
        'violations': ['status'],
        'lab_records': ['sample_type', 'lab_type', 'status'],
        'haccp_temperature_records': ['status'],
    }
    
    text_types = ['TEXT', 'VARCHAR', 'CHAR', 'NVARCHAR', 'NCHAR']
    all_missing = {}
    
    for table, fields_to_check in static_fields.items():
        # Проверяем существование таблицы
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
        if not cursor.fetchone():
            continue
        
        print(f"\n📁 Таблица: {table}")
        table_missing = {}
        
        for col in fields_to_check:
            # Проверяем существование колонки
            cursor.execute(f"PRAGMA table_info(\"{table}\")")
            columns = [c[1] for c in cursor.fetchall()]
            
            if col not in columns:
                continue
            
            cursor.execute(f"""
                SELECT DISTINCT "{col}" 
                FROM "{table}" 
                WHERE "{col}" IS NOT NULL 
                AND "{col}" != '' 
                AND LENGTH("{col}") > 0
            """)
            values = [row[0] for row in cursor.fetchall() if row[0]]
            
            if not values:
                continue
            
            missing_values = []
            for val in values:
                val_str = str(val).strip()
                
                # Пропускаем технические коды
                if re.match(r'^[a-z_]+$', val_str) and len(val_str) < 20:
                    continue
                
                # Пропускаем прочерки
                if val_str in ['-', '--', '—', '']:
                    continue
                
                if val_str not in COMPLAINT_TRANSLATIONS:
                    missing_values.append(val_str)
            
            if missing_values:
                table_missing[col] = missing_values
                print(f"  ❌ {col}: {len(missing_values)} не переведено")
                for v in missing_values:
                    print(f"      • \"{v}\"")
        
        if table_missing:
            all_missing[table] = table_missing
    
    conn.close()
    return all_missing

def generate_translation_template(db_missing):
    """Генерация шаблона переводов."""
    if not db_missing:
        return
    
    print("\n" + "="*70)
    print("📝 ШАБЛОН ДЛЯ complaint_translations.py")
    print("="*70)
    print("\n# Добавьте эти переводы:\n")
    
    for table, fields in db_missing.items():
        print(f"\n# {table.upper()}")
        for field, values in fields.items():
            for val in values:
                print(f'    "{val}": {{')
                print(f'        "ru": "{val}",')
                print(f'        "kk": "TODO",')
                print(f'        "en": "TODO",')
                print(f'        "tr": "TODO"')
                print(f'    }},')

def main():
    print("="*70)
    print("🔍 ПОЛНАЯ ПРОВЕРКА ПЕРЕВОДОВ")
    print("="*70)
    print(f"База: {DB_PATH}")
    print(f"Языки: {', '.join(LANGUAGES.values())}")
    
    db_missing = check_all_database_tables()
    
    generate_translation_template(db_missing)
    
    total_db = sum(len(values) for fields in db_missing.values() for values in fields.values())
    
    print("\n" + "="*70)
    print("📊 ИТОГИ")
    print("="*70)
    print(f"🗄️  База данных: {total_db} непереведенных значений")
    print(f"{'✅ ВСЁ переведено!' if total_db == 0 else '⚠️  Нужно добавить переводы'}")
    print("\n💡 Совет: Запускайте этот скрипт после каждого изменения")

if __name__ == "__main__":
    main()
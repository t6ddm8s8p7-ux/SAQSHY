# -*- coding: utf-8 -*-
"""Поиск статических текстов интерфейса для перевода."""
import re
from pathlib import Path

MODULES_DIR = Path("modules")

def find_static_texts():
    """Найти все статические тексты в UI файлах."""
    
    files_to_check = list(MODULES_DIR.glob("*.py"))
    all_texts = {}
    
    print("\n" + "="*70)
    print("🔍 ПОИСК СТАТИЧЕСКИХ ТЕКСТОВ ИНТЕРФЕЙСА")
    print("="*70)
    
    for file_path in files_to_check:
        if file_path.name in ['translations.py', 'complaint_translations.py']:
            continue
        
        if not file_path.exists():
            continue
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Паттерны для поиска текстов
        patterns = [
            r'text=["\']([^"\']{3,})["\']',
            r'title=["\']([^"\']{3,})["\']',
            r'placeholder_text=["\']([^"\']{3,})["\']',
            r'placeholder=["\']([^"\']{3,})["\']',
        ]
        
        texts = set()
        for pattern in patterns:
            matches = re.findall(pattern, content)
            for m in matches:
                # Пропускаем переменные и форматированные строки
                if '{' not in m and 'f"' not in m and "f'" not in m:
                    # Пропускаем очень длинные тексты
                    if len(m) < 100:
                        texts.add(m.strip())
        
        if texts:
            all_texts[file_path.name] = sorted(texts)
            print(f"\n📄 {file_path.name}: {len(texts)} текстов")
            for t in sorted(texts):
                print(f"  • {t}")
    
    return all_texts

def generate_translation_template(all_texts):
    """Генерация шаблона для translations.py"""
    
    print("\n" + "="*70)
    print("📝 ШАБЛОН ДЛЯ modules/translations.py")
    print("="*70)
    print("\n# Добавьте в словарь TEXT:\n")
    
    for filename, texts in all_texts.items():
        print(f"\n# === {filename.upper()} ===")
        for text in texts:
            # Создаем ключ из текста
            key = re.sub(r'[^\w\s]', '', text.lower())[:40].strip().replace(' ', '_')
            if not key:
                key = f"text_{hash(text) % 10000}"
            
            print(f'    "{key}": {{')
            print(f'        "ru": "{text}",')
            print(f'        "kk": "TODO",')
            print(f'        "en": "TODO",')
            print(f'        "tr": "TODO"')
            print(f'    }},')

def main():
    all_texts = find_static_texts()
    
    total = sum(len(v) for v in all_texts.values())
    
    print(f"\n{'='*70}")
    print(f"📊 ВСЕГО НАЙДЕНО: {total} текстов для перевода")
    print("="*70)
    
    if all_texts:
        generate_translation_template(all_texts)

if __name__ == "__main__":
    main()
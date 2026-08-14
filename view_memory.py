# -*- coding: utf-8 -*-
"""Просмотр сохранённой памяти AI."""
import os
import json
from datetime import datetime

def load_memory():
    path = os.path.join(os.path.dirname(__file__), "database", "ai_memory.json")
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def main():
    memory = load_memory()
    print("=" * 70)
    print("ПАМЯТЬ AI — Сохранённые вопросы и ответы")
    print("=" * 70)
    
    if not memory:
        print("\n📭 Память пуста. Сохраняйте ответы через кнопку '💾 Сохранить в память'.\n")
        return
    
    print(f"\nВсего записей: {len(memory)}\n")
    for i, item in enumerate(memory, 1):
        q = item.get("question", "")[:80]
        created = item.get("created_at", "")[:10]
        used = item.get("used_count", 0)
        sources = len(item.get("sources", []))
        
        print(f"{i}. [{item.get('id', '?')}] {q}...")
        print(f"   Создан: {created} | Использован: {used} раз | Источников: {sources}")
        print()


if __name__ == "__main__":
    main()
    input("\nНажмите Enter для выхода...")
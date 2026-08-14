# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path

conn = sqlite3.connect(Path(__file__).resolve().parent / "database" / "sanepi.db")
print("ТАБЛИЦЫ И КОЛОНКИ sanepi.db")
print("=" * 50)
for (name,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
    print(f"\n=== {name} ===")
    for row in conn.execute(f"PRAGMA table_info({name})"):
        print("  ", row[1], "-", row[2])
conn.close()
input("\nНажмите Enter...")
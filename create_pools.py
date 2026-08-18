# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / "database" / "sanepi.db"
conn = sqlite3.connect(DB)
conn.executescript("""
CREATE TABLE IF NOT EXISTS pools (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    pool_type TEXT DEFAULT 'adult',
    notes TEXT
);
CREATE TABLE IF NOT EXISTS pool_water_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pool_id INTEGER,
    date TEXT,
    time TEXT,
    free_chlorine TEXT,
    ph TEXT,
    temperature TEXT,
    status TEXT DEFAULT 'Норма',
    responsible TEXT,
    corrective_action TEXT,
    created_at TEXT DEFAULT (datetime('now','localtime'))
);
""")
conn.commit()
conn.close()
print("✅ Таблицы бассейнов готовы")
input("Enter...")
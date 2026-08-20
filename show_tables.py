# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path

c = sqlite3.connect(Path(__file__).resolve().parent / "database" / "sanepi.db")
for (n,) in c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"):
    cnt = c.execute(f'SELECT COUNT(*) FROM "{n}"').fetchone()[0]
    print(f"{n}  ->  записей: {cnt}")
input("Enter...")
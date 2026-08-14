# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent / "database" / "sanepi.db"
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM dd_services WHERE service_type='disinfection'")
if cur.fetchone()[0] == 0:
    row = cur.execute("SELECT id FROM dd_contracts ORDER BY id LIMIT 1").fetchone()
    cid = row[0] if row else None
    cur.execute(
        "INSERT INTO dd_services (contract_id,title,service_type,location,per_month,time_window,notes) VALUES (?,?,?,?,?,?,?)",
        (cid, "Дезинфекция (разовая по заявке)", "disinfection", "", 0, "", ""))
    conn.commit()
    print("✅ Дезинфекция добавлена!")
else:
    print("✅ Дезинфекция уже есть")
conn.close()
input("Enter...")
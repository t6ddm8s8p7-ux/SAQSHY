# -*- coding: utf-8 -*-
"""Миграция ДД v2: без жёстких дней — контроль по количеству в месяц."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "database" / "sanepi.db"

def main():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # таблицы пока пустые — пересоздаём начисто
    cur.execute("DROP TABLE IF EXISTS dd_treatments")
    cur.execute("DROP TABLE IF EXISTS dd_services")
    cur.execute("DROP TABLE IF EXISTS dd_contracts")

    cur.executescript("""
    CREATE TABLE dd_contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contractor TEXT NOT NULL,
        contract_number TEXT,
        contract_date TEXT,
        valid_until TEXT,
        notes TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    );
    CREATE TABLE dd_services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_id INTEGER,
        title TEXT NOT NULL,
        service_type TEXT NOT NULL,
        location TEXT,
        per_month INTEGER DEFAULT 2,
        time_window TEXT,
        notes TEXT
    );
    CREATE TABLE dd_treatments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_id INTEGER,
        service_id INTEGER,
        treatment_type TEXT NOT NULL DEFAULT 'planned',
        planned_date TEXT,
        actual_date TEXT,
        status TEXT DEFAULT 'planned',
        act_pdf_path TEXT,
        request_reason TEXT,
        notes TEXT,
        performed_by TEXT,
        created_at TEXT DEFAULT (datetime('now','localtime'))
    );
    CREATE INDEX idx_dd_treat_date ON dd_treatments(actual_date);
    CREATE INDEX idx_dd_treat_status ON dd_treatments(status);
    """)

    cur.execute("INSERT INTO dd_contracts (contractor, notes) VALUES (?,?)",
                ("Подрядчик по договору ДД (Rixos Water World Aktau)",
                 "Номер и срок договора укажите на странице раздела"))
    cid = cur.lastrowid

    services = [
        (cid, "Дезинсекция — ползающие насекомые", "dis_crawling", "внутри", 2, "", ""),
        (cid, "Дезинсекция — летающие (внутри зданий)", "dis_flying", "внутри", 3, "", ""),
        (cid, "Дезинсекция — летающие (снаружи зданий)", "dis_flying", "снаружи", 2, "22:00–04:00", ""),
        (cid, "Дератизация", "deratization", "", 2, "", ""),
    ]
    cur.executemany(
        "INSERT INTO dd_services (contract_id,title,service_type,location,per_month,time_window,notes) VALUES (?,?,?,?,?,?,?)",
        services)

    conn.commit()
    conn.close()
    print("✅ База ДД v2 готова (контроль по количеству в месяц):")
    print("   • Ползающие: 2 р/мес")
    print("   • Летающие внутри: 3 р/мес")
    print("   • Летающие снаружи: 2 р/мес (22:00–04:00)")
    print("   • Дератизация: 2 р/мес")
    input("\nEnter для выхода...")

if __name__ == "__main__":
    main()
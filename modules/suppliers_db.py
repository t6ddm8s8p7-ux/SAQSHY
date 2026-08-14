import sqlite3
import os

DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "database",
    "suppliers.db"
)


def get_connection():
    os.makedirs(
        os.path.dirname(DB_PATH),
        exist_ok=True
    )
    return sqlite3.connect(DB_PATH)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            bin_iin TEXT,
            contact_person TEXT,
            phone TEXT,
            email TEXT,
            category TEXT,
            address TEXT,
            rating TEXT DEFAULT '🟢 Отлично',
            certificates TEXT DEFAULT 'Действуют',
            created_at TEXT DEFAULT (datetime('now','localtime'))
        )
    """)
    conn.commit()
    conn.close()


def get_all_suppliers():
    init_db()
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, name, phone, category, rating, certificates
        FROM suppliers
        ORDER BY name
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows


def add_supplier(data):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO suppliers
        (name, bin_iin, contact_person, phone, email,
         category, address, rating, certificates)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["name"],
        data.get("bin_iin", ""),
        data.get("contact_person", ""),
        data.get("phone", ""),
        data.get("email", ""),
        data.get("category", ""),
        data.get("address", ""),
        data.get("rating", "🟢 Отлично"),
        data.get("certificates", "Действуют"),
    ))
    conn.commit()
    conn.close()


def delete_supplier(supplier_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM suppliers WHERE id = ?",
        (supplier_id,)
    )
    conn.commit()
    conn.close()
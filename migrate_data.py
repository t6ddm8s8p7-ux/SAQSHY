# -*- coding: utf-8 -*-
import json, sqlite3, re
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_DIR = BASE / "database"
DB_PATH = DB_DIR / "sanepi.db"

FILES = ["hr_employees.json", "esen_employees.json", "compare_result.json",
         "haccp_temperature_records.json", "haccp_objects.json", "ses_objects.json",
         "inspections.json", "sync_history.json", "esen_name_fixes.json",
         "esen_quality_report.json", "ai_memory.json"]

def safe_name(s):
    s = re.sub(r"[^a-zA-Z0-9_а-яА-Я]+", "_", str(s).strip())
    return ("col_" + s) if s and s[0].isdigit() else (s or "col")

def to_val(v):
    if v is None or isinstance(v, (int, float, str)): return v
    if isinstance(v, bool): return int(v)
    return json.dumps(v, ensure_ascii=False)

def migrate_list(conn, table, rows):
    dicts = [r for r in rows if isinstance(r, dict)]
    if not dicts: return 0
    pairs, seen = [], set()
    for r in dicts:
        for k in r.keys():
            c = safe_name(k)
            if c not in seen: seen.add(c); pairs.append((k, c))
    cols_sql = ", ".join(f'"{c}" TEXT' for _, c in pairs)
    quoted = ", ".join(f'"{c}"' for _, c in pairs)
    conn.execute(f'DROP TABLE IF EXISTS "{table}"')
    conn.execute(f'CREATE TABLE "{table}" ({cols_sql})')
    for r in dicts:
        conn.execute(f'INSERT INTO "{table}" ({quoted}) VALUES ({",".join("?" for _ in pairs)})',
                     [to_val(r.get(k)) for k, _ in pairs])
    return len(dicts)

def main():
    DB_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    print("Миграция данных начата...")
    total = 0
    for f in FILES:
        p = DB_DIR / f
        if not p.exists():
            print(f"  [пропуск] {f} - файл не найден"); continue
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  [ошибка] {f}: {e}"); continue
        table = safe_name(p.stem)
        if isinstance(data, list):
            n = migrate_list(conn, table, data)
            print(f"  [ок] {f} -> {table}: {n} записей")
        elif isinstance(data, dict):
            conn.execute(f'DROP TABLE IF EXISTS "{table}_kv"')
            conn.execute(f'CREATE TABLE "{table}_kv" (key TEXT PRIMARY KEY, value TEXT)')
            for k, v in data.items():
                conn.execute(f'INSERT OR REPLACE INTO "{table}_kv" (key, value) VALUES (?,?)',
                             (str(k), v if isinstance(v, (str, int, float)) else json.dumps(v, ensure_ascii=False)))
            n = len(data)
            print(f"  [ок] {f} -> {table}_kv: {n} ключей")
        else:
            n = 0; print(f"  [пропуск] {f} - неизвестный формат")
        total += n
    conn.commit(); conn.close()
    print(f"\nГотово! Перенесено записей: {total}")
    print(f"База создана: {DB_PATH}")

if __name__ == "__main__":
    main()
    input("\nНажмите Enter, чтобы закрыть...")
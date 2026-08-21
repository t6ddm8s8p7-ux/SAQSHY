# -*- coding: utf-8 -*-
import sqlite3
from pathlib import Path

c = sqlite3.connect(Path(__file__).resolve().parent / "database" / "sanepi.db")

for t in ["hygiene_training", "hr_employees", "ses_objects"]:
    try:
        n = c.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        if n == 0:
            c.execute(f"DROP TABLE {t}")
            print(f"🗑️ Удалён пустой дубль: {t}")
        else:
            print(f"⚠️ {t} не пустая ({n}) — НЕ удалена, проверим вручную")
    except Exception as e:
        print("—", t, e)

c.commit()
print("\n✅ Итоговая структура базы:")
for (n,) in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"):
    cnt = c.execute(f'SELECT COUNT(*) FROM "{n}"').fetchone()[0]
    print(f"   {n} -> {cnt}")
c.close()
input("\nEnter...")
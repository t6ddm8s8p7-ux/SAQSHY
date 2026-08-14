# -*- coding: utf-8 -*-
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
files = [ROOT / "app.py"] + sorted((ROOT / "modules").glob("*.py"))
strings = set()
for p in files:
    try:
        src = p.read_text(encoding="utf-8")
    except Exception:
        continue
    for line in src.splitlines():
        for m in re.finditer(r'"([^"\n]*[А-Яа-яЁё][^"\n]*)"', line):
            strings.add(m.group(1).strip())
        for m in re.finditer(r"'([^'\n]*[А-Яа-яЁё][^'\n]*)'", line):
            strings.add(m.group(1).strip())

print("\n".join(sorted(s for s in strings if s)))
print("\nУникальных фраз:", len(strings))
input("\nНажмите Enter, чтобы закрыть...")
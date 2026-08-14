# -*- coding: utf-8 -*-
"""Аудит структуры проекта SanEpi AI."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent
modules = ROOT / "modules"

print("=" * 60)
print("СТРУКТУРА ПРОЕКТА SanEpi AI")
print("=" * 60)

print(f"\n📁 Корень проекта: {ROOT.name}")
root_files = sorted(f.name for f in ROOT.glob("*.py"))
print(f"   Python-файлов в корне: {len(root_files)}")
for f in root_files:
    print(f"   • {f}")

print(f"\n📁 modules/")
if modules.exists():
    py_files = sorted(f.name for f in modules.glob("*.py"))
    print(f"   Python-файлов: {len(py_files)}")
    for f in py_files:
        size = (modules / f).stat().st_size
        print(f"   • {f:<40} ({size:>6} байт)")
else:
    print("   ❌ Папка не найдена")

print(f"\n📁 database/")
db = ROOT / "database"
if db.exists():
    files = sorted(f.name for f in db.iterdir() if f.is_file())
    print(f"   Файлов: {len(files)}")
    for f in files:
        size = (db / f).stat().st_size
        print(f"   • {f:<40} ({size:>6} байт)")
else:
    print("   ❌ Папка не найдена")

print("\n" + "=" * 60)
input("Нажмите Enter для выхода...")
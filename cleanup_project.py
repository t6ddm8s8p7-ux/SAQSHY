"""Очистка проекта от старых файлов.
Всё переносится в резервную папку _legacy_backup_...,
ничего не удаляется безвозвратно.
"""
import shutil
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / ("_legacy_backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))

LEGACY_ROOT_FILES = [
    "qt_app.py",
    "test_keyboard.py",
    "test_pyside_keyboard.py",
    "test_openai.py",
    "laws_registry.json",
    "clean_knowledge_base.py",
]

LEGACY_MODULES = [
    "i18n.py",
    "laws.py",
    "pdf_reader.py",
    "employees.py",
    "esen_cleaner.py",
    "qt_laws_page.py",
    "project_manager.py",
    "project_selector.py",
    "knowledge_graph.py",
    "checklist_table_extractor.py",
    "checklist_batch_extractor.py",
    "requirement_linker.py",
    "inspection_engine.py",
    "sanepi_knowledge_expert.py",
]

LEGACY_KB_FOLDERS = [
    "codes",
    "orders",
    "technical_regulations",
    "snip_architecture",
    "guidelines",
    "written_responses",
    "documents",
    "attachments",
    "texts",
    "index",
    "metadata",
    "relations",
    "inspections",
    "Ведения реестра продукции",
]

LEGACY_DATABASE = [
    "employees.json",
]


def move(src: Path, dst_dir: Path) -> bool:
    if not src.exists():
        return False
    dst_dir.mkdir(parents=True, exist_ok=True)
    shutil.move(str(src), str(dst_dir / src.name))
    print(f"📦 Перенесено: {src.name}")
    return True


def main():
    count = 0
    print("=== Очистка проекта SanEpi AI ===\n")

    for name in LEGACY_ROOT_FILES:
        count += move(ROOT / name, BACKUP / "root")

    for name in LEGACY_MODULES:
        count += move(ROOT / "modules" / name, BACKUP / "modules")

    for name in LEGACY_KB_FOLDERS:
        count += move(
            ROOT / "knowledge_base" / name,
            BACKUP / "knowledge_base",
        )

    for name in LEGACY_DATABASE:
        count += move(ROOT / "database" / name, BACKUP / "database")

    print(f"\n✅ Готово. Перенесено объектов: {count}")
    print(f"🗂️ Резервная папка: {BACKUP}")
    print("Когда убедитесь, что всё работает,")
    print("удалите эту папку навсегда.")


if __name__ == "__main__":
    main()
import json
from datetime import datetime
from pathlib import Path
print("=== BUILD REGISTRY START ===")

KNOWLEDGE_BASE_DIR = Path("knowledge_base")
REGISTRY_FILE = KNOWLEDGE_BASE_DIR / "registry.json"

SUPPORTED_EXTENSIONS = {
    ".pdf",
    ".txt",
    ".docx",
    ".doc",
    ".xlsx",
    ".xls",
}

EXCLUDED_TOP_LEVEL_FOLDERS = {
    "texts",
    "index",
    "metadata",
    "_pycache_",
}


def detect_language(file_name: str) -> str:
    name = file_name.lower()

    if ".kaz." in name or "_kaz." in name or "-kaz." in name:
        return "kaz"

    if ".rus." in name or "_rus." in name or "-rus." in name:
        return "rus"

    return "unknown"


def get_document_type(relative_path: Path) -> str:
    if not relative_path.parts:
        return "other"

    first_folder = relative_path.parts[0].lower()

    type_names = {
        "codes": "Кодексы",
        "orders": "Приказы",
        "technical_regulations": "Технические регламенты",
        "snip_architecture": "СНиП и архитектура",
        "guidelines": "Методические рекомендации",
        "written_responses": "Письменные ответы",
        "documents": "Документы",
        "attachments": "Приложения",
    }

    return type_names.get(
        first_folder,
        relative_path.parts[0]
    )


def get_topic(relative_path: Path) -> str:
    parts = relative_path.parts

    if len(parts) >= 3:
        return parts[1]

    if len(parts) == 2:
        return "Общие"

    return "Без категории"


def build_registry() -> list[dict]:
    print("Функция build_registry запущена")
    KNOWLEDGE_BASE_DIR.mkdir(parents=True, exist_ok=True)

    documents = []

    for file_path in KNOWLEDGE_BASE_DIR.rglob("*"):
        if not file_path.is_file():
            continue

        if file_path == REGISTRY_FILE:
            continue

        if file_path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            continue

        relative_path = file_path.relative_to(KNOWLEDGE_BASE_DIR)
        if (
            relative_path.parts
            and relative_path.parts[0].lower() in EXCLUDED_TOP_LEVEL_FOLDERS
        ):
            continue

        stat = file_path.stat()

        document = {
            "id": str(relative_path.with_suffix(""))
            .replace("\\", "__")
            .replace("/", "__"),
            "document_type": get_document_type(relative_path),
            "topic": get_topic(relative_path),
            "language": detect_language(file_path.name),
            "file_name": file_path.name,
            "extension": file_path.suffix.lower(),
            "relative_path": relative_path.as_posix(),
            "absolute_path": str(file_path.resolve()),
            "size_bytes": stat.st_size,
            "modified_at": datetime.fromtimestamp(
                stat.st_mtime
            ).isoformat(timespec="seconds"),
            "indexed_at": datetime.now().isoformat(
                timespec="seconds"
            ),
            "status": "indexed",
        }

        documents.append(document)

    documents.sort(
        key=lambda item: (
            item["document_type"].lower(),
            item["topic"].lower(),
            item["file_name"].lower(),
        )
    )

    with open(REGISTRY_FILE, "w", encoding="utf-8") as file:
        json.dump(
            documents,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("=" * 60)
    print("✅ Реестр нормативной базы создан")
    print(f"📚 Найдено документов: {len(documents)}")
    print(f"📄 Файл реестра: {REGISTRY_FILE}")
    print("=" * 60)

    counts = {}

    for document in documents:
        key = (
            document["document_type"],
            document["topic"]
        )
        counts[key] = counts.get(key, 0) + 1

    for (document_type, topic), count in sorted(counts.items()):
        print(
            f"{document_type} → {topic}: {count}"
        )

    return documents


def load_registry() -> list[dict]:
    if not REGISTRY_FILE.exists():
        return build_registry()

    try:
        with open(
            REGISTRY_FILE,
            "r",
            encoding="utf-8-sig"
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except Exception as error:
        print("⚠️ Ошибка чтения registry.json:")
        print(error)

    return build_registry()


if __name__ == "__main__":
    print("Запуск из main")
    build_registry()
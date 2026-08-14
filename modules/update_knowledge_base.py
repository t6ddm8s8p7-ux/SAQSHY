import json
from datetime import datetime
from pathlib import Path

from modules.build_registry import build_registry
from modules.extract_law_texts import (
    extract_pdf_text,
    get_pdf_path,
    get_text_output_path,
)


KNOWLEDGE_BASE_DIR = Path("knowledge_base")
REGISTRY_FILE = KNOWLEDGE_BASE_DIR / "registry.json"


def load_registry() -> list[dict]:
    if not REGISTRY_FILE.exists():
        return []

    try:
        with open(
            REGISTRY_FILE,
            "r",
            encoding="utf-8-sig"
        ) as file:
            data = json.load(file)

        return data if isinstance(data, list) else []

    except Exception as error:
        print("❌ Ошибка чтения registry.json:")
        print(error)
        return []


def save_registry(registry: list[dict]) -> None:
    with open(
        REGISTRY_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            registry,
            file,
            ensure_ascii=False,
            indent=2
        )


def document_key(document: dict) -> str:
    return str(
        document.get("relative_path", "")
    ).strip().lower()


def update_knowledge_base(
    progress_callback=None
) -> dict:
    """
    Обновляет реестр и извлекает текст только
    из новых или изменённых PDF.
    """

    def progress(message):
        print(message)

        if progress_callback:
            progress_callback(message)

    progress("🔄 Начинается обновление нормативной базы...")

    old_registry = load_registry()

    old_by_path = {
        document_key(document): document
        for document in old_registry
        if document_key(document)
    }

    progress("📂 Сканирование папок...")
    new_registry = build_registry()

    added_count = 0
    updated_count = 0
    unchanged_count = 0
    error_count = 0
    removed_count = 0

    new_paths = {
        document_key(document)
        for document in new_registry
        if document_key(document)
    }

    for old_document in old_registry:
        old_key = document_key(old_document)

        if old_key and old_key not in new_paths:
            removed_count += 1

    pdf_documents = [
        document
        for document in new_registry
        if str(
            document.get("extension", "")
        ).lower() == ".pdf"
    ]

    total = len(pdf_documents)

    for index, document in enumerate(
        pdf_documents,
        start=1
    ):
        key = document_key(document)
        old_document = old_by_path.get(key)

        is_new = old_document is None

        is_changed = False

        if old_document:
            old_modified = str(
                old_document.get("modified_at", "")
            )
            new_modified = str(
                document.get("modified_at", "")
            )

            old_size = old_document.get(
                "size_bytes"
            )
            new_size = document.get(
                "size_bytes"
            )

            is_changed = (
                old_modified != new_modified
                or old_size != new_size
            )

        old_text_ready = (
            old_document
            and old_document.get("text_status") == "ready"
            and old_document.get("text_file")
            and (KNOWLEDGE_BASE_DIR / str(old_document.get("text_file"))).is_file()
        )

        if not is_new and not is_changed and old_text_ready:
            document.update({
                "text_file": old_document.get("text_file"),
                "text_status": old_document.get("text_status"),
                "text_page_count": old_document.get("text_page_count"),
                "text_empty_pages": old_document.get("text_empty_pages"),
                "text_characters": old_document.get("text_characters"),
                "text_extracted_at": old_document.get("text_extracted_at"),
            })

            unchanged_count += 1

            progress(
                f"[{index}/{total}] "
                f"Без изменений: "
                f"{document.get('file_name', 'Документ')}"
            )
            continue

        pdf_path = get_pdf_path(document)

        if not pdf_path:
            document["text_status"] = "file_not_found"
            document["text_error"] = "PDF-файл не найден"

            error_count += 1

            progress(
                f"[{index}/{total}] "
                f"❌ Не найден PDF: "
                f"{document.get('file_name', 'Документ')}"
            )
            continue

        output_path = get_text_output_path(
            document
        )

        try:
            result = extract_pdf_text(
                pdf_path,
                output_path
            )

            relative_text_path = (
                output_path
                .relative_to(
                    KNOWLEDGE_BASE_DIR
                )
                .as_posix()
            )

            document["text_file"] = relative_text_path
            document["text_status"] = "ready"
            document["text_page_count"] = result["page_count"]
            document["text_empty_pages"] = result["empty_pages"]
            document["text_characters"] = result["characters"]
            document["text_extracted_at"] = (
                datetime.now().isoformat(
                    timespec="seconds"
                )
            )
            document.pop(
                "text_error",
                None
            )

            if is_new:
                added_count += 1
                action = "Добавлен"
            else:
                updated_count += 1
                action = "Обновлён"

            progress(
                f"[{index}/{total}] "
                f"✅ {action}: "
                f"{document.get('file_name', 'Документ')}"
            )

        except Exception as error:
            document["text_status"] = "error"
            document["text_error"] = str(error)

            error_count += 1

            progress(
                f"[{index}/{total}] "
                f"❌ Ошибка: "
                f"{document.get('file_name', 'Документ')}"
            )

    save_registry(new_registry)

    result = {
        "total_documents": len(new_registry),
        "pdf_documents": total,
        "added": added_count,
        "updated": updated_count,
        "unchanged": unchanged_count,
        "removed": removed_count,
        "errors": error_count,
    }

    progress("✅ Обновление нормативной базы завершено.")

    return result


if __name__ == "__main__":
    result = update_knowledge_base()

    print()
    print("=" * 60)
    print(f"Всего документов: {result['total_documents']}")
    print(f"PDF: {result['pdf_documents']}")
    print(f"Добавлено: {result['added']}")
    print(f"Обновлено: {result['updated']}")
    print(f"Без изменений: {result['unchanged']}")
    print(f"Удалено из реестра: {result['removed']}")
    print(f"Ошибок: {result['errors']}")
    print("=" * 60)
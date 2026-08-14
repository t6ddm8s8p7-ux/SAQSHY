import json
import re
from datetime import datetime
from pathlib import Path
import pymupdf

KNOWLEDGE_BASE_DIR = Path("knowledge_base")
REGISTRY_FILE = KNOWLEDGE_BASE_DIR / "registry.json"
TEXTS_DIR = KNOWLEDGE_BASE_DIR / "texts"


def safe_file_name(value: str) -> str:
    value = str(value).strip()
    value = re.sub(r'[\\/:*?"<>|]', "_", value)
    value = re.sub(r"\s+", "_", value)
    return value[:180]


def load_registry() -> list[dict]:
    if not REGISTRY_FILE.exists():
        print("❌ registry.json не найден.")
        return []
    try:
        with open(REGISTRY_FILE, "r", encoding="utf-8-sig") as file:
            data = json.load(file)
        if isinstance(data, list):
            return data
    except Exception as error:
        print(f"❌ Ошибка чтения registry.json: {error}")
    return []


def save_registry(registry: list[dict]) -> None:
    with open(REGISTRY_FILE, "w", encoding="utf-8") as file:
        json.dump(registry, file, ensure_ascii=False, indent=2)


def get_pdf_path(document: dict) -> Path | None:
    absolute_path = str(document.get("absolute_path", "")).strip()
    if absolute_path:
        file_path = Path(absolute_path)
        if file_path.exists():
            return file_path
    relative_path = str(document.get("relative_path", "")).strip()
    if relative_path:
        file_path = KNOWLEDGE_BASE_DIR / relative_path
        if file_path.exists():
            return file_path
    return None


def get_text_output_path(document: dict) -> Path:
    document_type = safe_file_name(document.get("document_type", "Без типа"))
    topic = safe_file_name(document.get("topic", "Без раздела"))
    source_file_name = str(document.get("file_name", "document.pdf")).strip()
    short_name = safe_file_name(Path(source_file_name).stem)
    output_dir = TEXTS_DIR / document_type / topic
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / f"{short_name}.txt"


def extract_table_rows(table) -> list[str]:
    """Превращает таблицу PDF в читаемые строки: ячейки через |"""
    rows = []
    try:
        raw_rows = table.extract()
    except Exception:
        return rows
    for raw in raw_rows:
        cells = [str(c or "").replace("\n", " ").strip() for c in raw]
        while cells and not cells[-1]:
            cells.pop()
        if cells and any(cells):
            rows.append(" | ".join(cells))
    return rows


def page_text_without_tables(page, table_rects) -> str:
    """Текст страницы без областей таблиц."""
    words = page.get_text("words")
    kept = []
    for w in words:
        x = (w[0] + w[2]) / 2
        y = (w[1] + w[3]) / 2
        inside = False
        for r in table_rects:
            if r.x0 - 2 <= x <= r.x1 + 2 and r.y0 - 2 <= y <= r.y1 + 2:
                inside = True
                break
        if not inside:
            kept.append(w)
    lines_map = {}
    for w in kept:
        key = round((w[1] + w[3]) / 2 / 4)
        lines_map.setdefault(key, []).append(w)
    ordered = []
    for key in sorted(lines_map):
        ws = sorted(lines_map[key], key=lambda w: w[0])
        ordered.append(" ".join(w[4] for w in ws))
    return "\n".join(ordered)


def extract_pdf_text(pdf_path: Path, output_path: Path) -> dict:
    pages_text = []
    total_characters = 0
    empty_pages = 0
    with pymupdf.open(pdf_path) as pdf:
        page_count = len(pdf)
        for page_number, page in enumerate(pdf, start=1):
            table_rows = []
            table_rects = []
            try:
                tables = page.find_tables()
                for table in tables.tables:
                    table_rects.append(table.bbox)
                    table_rows.extend(extract_table_rows(table))
            except Exception:
                table_rows = []
                table_rects = []

            if table_rects:
                text = page_text_without_tables(page, table_rects)
            else:
                text = page.get_text("text", sort=True).strip()

            page_text = text
            if table_rows:
                page_text += "\n" + "\n".join(
                    f"[TAB_ROW] {row}" for row in table_rows
                )

            if not page_text.strip():
                empty_pages += 1
                page_text = "[Текст на странице не распознан]"

            total_characters += len(page_text)
            pages_text.append(
                "\n" + "=" * 80
                + f"\nСТРАНИЦА {page_number}\n"
                + "=" * 80 + "\n"
                + page_text + "\n"
            )

        header = (
            f"Исходный PDF: {pdf_path.name}\n"
            f"Полный путь: {pdf_path}\n"
            f"Количество страниц: {page_count}\n"
            f"Страниц без распознанного текста: {empty_pages}\n"
            f"Дата извлечения: "
            f"{datetime.now().isoformat(timespec='seconds')}\n"
            + "=" * 80 + "\n"
        )
        with open(output_path, "w", encoding="utf-8") as file:
            file.write(header)
            file.write("".join(pages_text))
    return {
        "page_count": page_count,
        "empty_pages": empty_pages,
        "characters": total_characters,
    }


def extract_all_texts() -> list[dict]:
    print("=" * 70)
    print("📚 SanEpi AI — извлечение текста нормативов")
    print("=" * 70)
    registry = load_registry()
    if not registry:
        return []
    TEXTS_DIR.mkdir(parents=True, exist_ok=True)
    pdf_documents = [
        d for d in registry
        if str(d.get("extension", "")).lower() == ".pdf"
    ]
    print(f"Найдено PDF-документов: {len(pdf_documents)}")
    processed = []
    success_count = 0
    error_count = 0
    for number, document in enumerate(pdf_documents, start=1):
        pdf_path = get_pdf_path(document)
        print()
        print(f"[{number}/{len(pdf_documents)}] {document.get('file_name', 'Документ')}")
        if not pdf_path:
            print("❌ PDF-файл не найден.")
            document["text_status"] = "file_not_found"
            document["text_error"] = "Исходный PDF не найден"
            error_count += 1
            continue
        output_path = get_text_output_path(document)
        try:
            result = extract_pdf_text(pdf_path, output_path)
            relative_text_path = output_path.relative_to(KNOWLEDGE_BASE_DIR).as_posix()
            document["text_file"] = relative_text_path
            document["text_status"] = "ready"
            document["text_page_count"] = result["page_count"]
            document["text_empty_pages"] = result["empty_pages"]
            document["text_characters"] = result["characters"]
            document["text_extracted_at"] = datetime.now().isoformat(timespec="seconds")
            document.pop("text_error", None)
            success_count += 1
            print(f"✅ Извлечено страниц: {result['page_count']}")
            print(f"📄 Текст сохранён: {relative_text_path}")
            processed.append(document)
        except Exception as error:
            error_count += 1
            document["text_status"] = "error"
            document["text_error"] = str(error)
            print("❌ Ошибка извлечения:")
            print(error)
        save_registry(registry)
    print()
    print("=" * 70)
    print("✅ Извлечение завершено")
    print(f"Успешно: {success_count}")
    print(f"Ошибок: {error_count}")
    print(f"Тексты: {TEXTS_DIR}")
    print("=" * 70)
    return processed


if __name__ == "__main__":
    extract_all_texts()
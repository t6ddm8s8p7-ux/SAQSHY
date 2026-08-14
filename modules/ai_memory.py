import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_ROOT / "database"
MEMORY_FILE = DATABASE_DIR / "ai_memory.json"


def ensure_memory_file() -> None:
    """Создаёт папку database и файл памяти, если их ещё нет."""
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)

    if not MEMORY_FILE.exists():
        MEMORY_FILE.write_text(
            json.dumps([], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


def load_memory() -> list[dict[str, Any]]:
    """Загружает все сохранённые ответы AI."""
    ensure_memory_file()

    try:
        data = json.loads(MEMORY_FILE.read_text(encoding="utf-8"))

        if isinstance(data, list):
            return data

    except (json.JSONDecodeError, OSError):
        pass

    return []


def save_memory(records: list[dict[str, Any]]) -> None:
    """Сохраняет список записей памяти."""
    ensure_memory_file()

    MEMORY_FILE.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def normalize_text(text: str) -> str:
    """
    Нормализует текст для сравнения вопросов:
    - приводит к нижнему регистру;
    - убирает лишние знаки;
    - сокращает повторные пробелы.
    """
    text = str(text or "").lower().strip()
    text = text.replace("ё", "е")
    text = re.sub(r"[^\w\s\-№]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def calculate_similarity(first_text: str, second_text: str) -> float:
    """
    Простое сравнение вопросов по совпадающим словам.
    Возвращает число от 0 до 1.
    """
    first_words = set(normalize_text(first_text).split())
    second_words = set(normalize_text(second_text).split())

    if not first_words or not second_words:
        return 0.0

    intersection = first_words.intersection(second_words)
    union = first_words.union(second_words)

    return len(intersection) / len(union)


def add_memory_record(
    question: str,
    answer: str,
    source_document: str = "",
    source_point: str = "",
    status: str = "draft",
    verified_by: str = "",
) -> dict[str, Any]:
    """
    Добавляет новую запись в память AI.

    Допустимые статусы:
    - draft
    - verified
    - approved
    """
    records = load_memory()

    now = datetime.now().isoformat(timespec="seconds")

    record = {
        "id": f"memory_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
        "question": question.strip(),
        "normalized_question": normalize_text(question),
        "answer": answer.strip(),
        "source_document": source_document.strip(),
        "source_point": source_point.strip(),
        "status": status,
        "verified_by": verified_by.strip(),
        "created_at": now,
        "updated_at": now,
        "use_count": 0,
        "helpful_count": 0,
        "not_helpful_count": 0,
    }

    records.append(record)
    save_memory(records)

    return record


def find_similar_answers(
    question: str,
    minimum_similarity: float = 0.35,
    limit: int = 5,
    approved_only: bool = False,
) -> list[dict[str, Any]]:
    """
    Ищет похожие ранее сохранённые вопросы.
    """
    records = load_memory()
    results: list[dict[str, Any]] = []

    for record in records:
        status = record.get("status", "draft")

        if approved_only and status not in {"verified", "approved"}:
            continue

        similarity = calculate_similarity(
            question,
            record.get("question", ""),
        )

        if similarity < minimum_similarity:
            continue

        result = dict(record)
        result["similarity"] = round(similarity, 3)
        results.append(result)

    results.sort(
        key=lambda item: (
            item.get("status") == "approved",
            item.get("status") == "verified",
            item.get("similarity", 0),
            item.get("helpful_count", 0),
            item.get("use_count", 0),
        ),
        reverse=True,
    )

    return results[:limit]


def get_memory_record(record_id: str) -> dict[str, Any] | None:
    """Получает одну запись по её ID."""
    for record in load_memory():
        if record.get("id") == record_id:
            return record

    return None


def update_memory_record(
    record_id: str,
    **changes: Any,
) -> dict[str, Any] | None:
    """Изменяет существующую запись."""
    records = load_memory()

    for record in records:
        if record.get("id") != record_id:
            continue

        allowed_fields = {
            "question",
            "answer",
            "source_document",
            "source_point",
            "status",
            "verified_by",
            "use_count",
            "helpful_count",
            "not_helpful_count",
        }

        for field, value in changes.items():
            if field in allowed_fields:
                record[field] = value

        if "question" in changes:
            record["normalized_question"] = normalize_text(
                str(changes["question"])
            )

        record["updated_at"] = datetime.now().isoformat(
            timespec="seconds"
        )

        save_memory(records)
        return record

    return None


def mark_as_used(record_id: str) -> bool:
    """Увеличивает счётчик использования ответа."""
    record = get_memory_record(record_id)

    if not record:
        return False

    current_count = int(record.get("use_count", 0))

    update_memory_record(
        record_id,
        use_count=current_count + 1,
    )

    return True


def mark_helpful(record_id: str) -> bool:
    """Отмечает ответ как полезный."""
    record = get_memory_record(record_id)

    if not record:
        return False

    current_count = int(record.get("helpful_count", 0))

    update_memory_record(
        record_id,
        helpful_count=current_count + 1,
    )

    return True


def mark_not_helpful(record_id: str) -> bool:
    """Отмечает ответ как неточный или бесполезный."""
    record = get_memory_record(record_id)

    if not record:
        return False

    current_count = int(record.get("not_helpful_count", 0))

    update_memory_record(
        record_id,
        not_helpful_count=current_count + 1,
    )

    return True


def approve_record(
    record_id: str,
    verified_by: str,
) -> dict[str, Any] | None:
    """Присваивает записи статус утверждённого ответа."""
    return update_memory_record(
        record_id,
        status="approved",
        verified_by=verified_by,
    )


if __name__ == "__main__":
    ensure_memory_file()

    print("Память SanEpi AI готова.")
    print(f"Файл: {MEMORY_FILE}")
    print(f"Количество записей: {len(load_memory())}")
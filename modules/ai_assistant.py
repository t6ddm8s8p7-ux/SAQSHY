import json
import re
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
REGISTRY_FILE = KNOWLEDGE_BASE_DIR / "registry.json"

MANUAL_DOCUMENT_TYPE = "manual_documents"
MAX_DOCUMENT_RESULTS = 5

STOP_WORDS = {
    "как",
    "что",
    "где",
    "когда",
    "какой",
    "какая",
    "какие",
    "кто",
    "для",
    "при",
    "или",
    "это",
    "его",
    "ее",
    "её",
    "их",
    "есть",
    "нужно",
    "надо",
    "можно",
    "должен",
    "должна",
    "должны",
    "требования",
}


def load_registry() -> list[dict[str, Any]]:
    """Загружает реестр нормативных документов."""
    if not REGISTRY_FILE.exists():
        return []

    try:
        with REGISTRY_FILE.open(
            "r",
            encoding="utf-8-sig",
        ) as file:
            data = json.load(file)

        if isinstance(data, list):
            return data

    except (OSError, json.JSONDecodeError) as error:
        print("Ошибка чтения registry.json:")
        print(error)

    return []


def is_manual_document(
    document: dict[str, Any],
) -> bool:
    """Проверяет, добавлен ли документ вручную."""
    document_type = str(
        document.get("document_type", "")
    ).strip().lower()

    relative_path = str(
        document.get("relative_path", "")
    ).strip().replace("\\", "/").lower()

    return (
        document_type == MANUAL_DOCUMENT_TYPE
        or relative_path.startswith(
            f"{MANUAL_DOCUMENT_TYPE}/"
        )
    )


def normalize_relative_path(value: str) -> str:
    """Нормализует относительный путь для сравнения."""
    return (
        str(value or "")
        .strip()
        .replace("\\", "/")
        .lower()
    )


def get_text_file_path(
    document: dict[str, Any],
) -> Path | None:
    """Возвращает путь к извлечённому тексту документа."""
    text_file = str(
        document.get("text_file", "")
    ).strip()

    if not text_file:
        return None

    text_path = Path(text_file)

    if not text_path.is_absolute():
        text_path = KNOWLEDGE_BASE_DIR / text_path

    if not text_path.exists():
        return None

    if not text_path.is_file():
        return None

    return text_path


def get_manual_documents(
    selected_relative_path: str | None = None,
) -> list[dict[str, Any]]:
    """
    Возвращает вручную добавленные документы.

    Если передан selected_relative_path,
    возвращает только выбранный документ.
    """
    registry = load_registry()

    selected_path = normalize_relative_path(
        selected_relative_path or ""
    )

    documents = []

    for document in registry:
        if not is_manual_document(document):
            continue

        if selected_path:
            document_path = normalize_relative_path(
                document.get("relative_path", "")
            )

            if document_path != selected_path:
                continue

        if document.get("text_status") != "ready":
            continue

        if not get_text_file_path(document):
            continue

        documents.append(document)

    return documents


def split_words(text: str) -> list[str]:
    """
    Разбивает запрос на значимые слова.
    Поддерживает русский и казахский алфавиты.
    """
    words = re.findall(
        r"[а-яёәіңғүұқөһa-z0-9№\-]+",
        str(text or "").lower(),
        flags=re.IGNORECASE,
    )

    return [
        word
        for word in words
        if len(word) >= 3
        and word not in STOP_WORDS
    ]


def find_best_position(
    text: str,
    question_words: list[str],
) -> int:
    """Находит наиболее подходящее место в документе."""
    lower_text = text.lower()

    best_position = 0
    best_score = -1

    for word in question_words:
        position = lower_text.find(word)

        if position < 0:
            continue

        count = lower_text.count(word)

        if count > best_score:
            best_score = count
            best_position = position

    return best_position


def create_fragment(
    text: str,
    position: int,
    before: int = 500,
    after: int = 1800,
) -> str:
    """Создаёт читаемый фрагмент документа."""
    start = max(
        0,
        position - before,
    )

    end = min(
        len(text),
        position + after,
    )

    fragment = text[start:end].strip()

    if start > 0:
        fragment = "… " + fragment

    if end < len(text):
        fragment += " …"

    return fragment


def search_documents(
    question: str,
    selected_relative_path: str | None = None,
    limit: int = MAX_DOCUMENT_RESULTS,
) -> list[dict[str, Any]]:
    """
    Ищет информацию только во вручную добавленных приказах.

    Если передан selected_relative_path,
    поиск проводится только в выбранном приказе.
    """
    question_words = split_words(question)

    if not question_words:
        return []

    manual_documents = get_manual_documents(
        selected_relative_path=selected_relative_path
    )

    results: list[dict[str, Any]] = []

    for document in manual_documents:
        text_path = get_text_file_path(document)

        if not text_path:
            continue

        try:
            text = text_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

        except OSError as error:
            print(
                "Не удалось прочитать текст:",
                text_path,
                error,
            )
            continue

        lower_text = text.lower()

        score = 0
        matched_words: list[str] = []

        for word in question_words:
            count = lower_text.count(word)

            if count <= 0:
                continue

            matched_words.append(word)

            score += 10
            score += min(count, 20)

        if not matched_words:
            continue

        score += len(matched_words) * 15

        position = find_best_position(
            text,
            matched_words,
        )

        fragment = create_fragment(
            text,
            position,
        )

        results.append(
            {
                "score": score,
                "document_id": document.get("id", ""),
                "file": document.get(
                    "file_name",
                    text_path.name,
                ),
                "relative_path": document.get(
                    "relative_path",
                    "",
                ),
                "text_file": document.get(
                    "text_file",
                    "",
                ),
                "matched_words": matched_words,
                "fragment": fragment,
            }
        )

    results.sort(
        key=lambda item: (
            item["score"],
            len(item["matched_words"]),
        ),
        reverse=True,
    )

    return results[:limit]


def format_results(
    results: list[dict[str, Any]],
) -> str:
    """Формирует текст результата для интерфейса."""
    if not results:
        return (
            "В выбранном приказе подходящая информация "
            "не найдена.\n\n"
            "Попробуйте уточнить запрос или использовать "
            "формулировку из приказа."
        )

    parts = []

    for index, item in enumerate(
        results,
        start=1,
    ):
        matched_words = ", ".join(
            item.get("matched_words", [])
        )

        parts.append(
            f"{index}. Документ: {item['file']}\n"
            f"Найдены слова: {matched_words}\n"
            f"Оценка совпадения: {item['score']}\n\n"
            f"{item['fragment']}"
        )

    return "\n\n" + ("=" * 60) + "\n\n".join(
        f"\n{part}\n"
        for part in parts
    )


def ask_ai(
    question: str,
    selected_relative_path: str | None = None,
) -> dict[str, Any]:
    """
    Ищет информацию только во вручную добавленных приказах.

    selected_relative_path позволяет выполнять поиск
    исключительно по выбранному в интерфейсе приказу.
    """
    question = str(question or "").strip()

    if not question:
        return {
            "question": "",
            "selected_relative_path": selected_relative_path,
            "document_results": [],
            "answer": "Введите описание возможного нарушения.",
        }

    document_results = search_documents(
        question=question,
        selected_relative_path=selected_relative_path,
    )

    answer = format_results(
        document_results
    )

    return {
        "question": question,
        "selected_relative_path": selected_relative_path,
        "document_results": document_results,
        "answer": answer,
    }


if __name__ == "__main__":
    user_question = input(
        "Введите описание возможного нарушения: "
    )

    result = ask_ai(user_question)

    print()
    print(result["answer"])
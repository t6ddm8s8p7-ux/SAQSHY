"""
Локальный AI-движок SanEpi AI — версия 8.
• IDF-веса, нормализация "й"="и", таблицы [TAB_ROW];
• НОВОЕ: для каждого найденного пункта запоминается
  номер страницы и путь к PDF — клик открывает приказ
  на нужной странице.
"""
import json
import math
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"
REGISTRY_FILE = KNOWLEDGE_BASE_DIR / "registry.json"
TITLES_FILE = KNOWLEDGE_BASE_DIR / "document_titles.json"

STOP_WORDS = {
    "как", "что", "где", "когда", "какой", "какая", "какие", "кто",
    "для", "при", "или", "это", "его", "ее", "её", "их", "есть",
    "нужно", "надо", "можно", "должен", "должна", "должны",
    "требования", "требование", "требований", "согласно",
}

ENDINGS = (
    "ующий", "ующая", "ущее", "ующие", "ующего", "ующей",
    "ующих", "ующим", "ующихся", "ующимися",
    "иями", "ями", "ами", "ого", "ему", "ому", "ыми", "ими",
    "иях", "ах", "ях", "ование", "ования",
    "ий", "ый", "ая", "ое", "ые", "ие", "ия", "ию", "ии",
    "иям", "ей", "ой", "ам", "ям", "ом", "ем", "ов", "ев",
    "уют", "ите", "ете", "ует", "ит", "ат", "ят", "ут", "ют",
    "ла", "ло", "ли", "ть", "ся", "сь",
    "у", "ю", "а", "я", "ы", "и", "е",
)

SUGGESTED_ORDERS = [
    ("медосмотр",
     "ҚР ДСМ-131/2020 «Обязательные медицинские осмотры»",
     "https://adilet.zan.kz/rus/docs/V2000021443"),
    ("гигиеническ",
     "ҚР ДСМ-195/2020 «Гигиеническое обучение»",
     "https://adilet.zan.kz/rus/docs/V2000021654"),
    ("бассейн",
     "ҚР ДСМ-67 «Требования к объектам коммунального назначения»",
     "https://adilet.zan.kz/rus/docs/V2200028925"),
    ("маркиров",
     "ҚР ДСМ-16 «Требования к объектам общественного питания»",
     "https://adilet.zan.kz/rus/docs/V2200026866"),
    ("температур",
     "ҚР ДСМ-16 «Требования к объектам общественного питания»",
     "https://adilet.zan.kz/rus/docs/V2200026866"),
    ("хранени",
     "ҚР ДСМ-16 «Требования к объектам общественного питания»",
     "https://adilet.zan.kz/rus/docs/V2200026866"),
]

IMPORTANT_PATTERNS = [
    r"\bпункт\b", r"\bп\.\s*\d+", r"\bстатья\b", r"\bст\.\s*\d+",
    r"\bне допускается\b", r"\bзапрещается\b", r"\bразрешается\b",
    r"\bобязан", r"\bсанитарн",
]


def normalize_text(text):
    text = str(text or "").lower()
    text = text.replace("ё", "е")
    text = text.replace("й", "и")
    text = re.sub(r"[^\w\sа-яәіңғүұқөһ№-]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def word_stem(word):
    for ending in ENDINGS:
        if word.endswith(ending) and len(word) - len(ending) >= 4:
            return word[:len(word) - len(ending)]
    return word


def tokenize(text):
    words = re.findall(r"[а-яёәіңғүұқөһa-z0-9№-]+", normalize_text(text))
    return {word_stem(w) for w in words if len(w) >= 3 and w not in STOP_WORDS}


def stems_match(a, b):
    if a == b:
        return True
    short, long = (a, b) if len(a) <= len(b) else (b, a)
    if len(short) >= 6 and long.startswith(short) and len(long) - len(short) <= 3:
        return True
    common = 0
    for ca, cb in zip(a, b):
        if ca != cb:
            break
        common += 1
    return common >= 7


def get_question_phrases(question):
    words = [
        w for w in re.findall(r"[а-яёa-z0-9№-]+", str(question).lower())
        if len(w) >= 4 and w not in STOP_WORDS
    ]
    return [f"{words[i]} {words[i + 1]}" for i in range(len(words) - 1)]


def _load_kb_registry():
    if not REGISTRY_FILE.exists():
        return []
    try:
        with open(REGISTRY_FILE, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _load_titles():
    if not TITLES_FILE.exists():
        return {}
    try:
        with open(TITLES_FILE, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _get_title(doc, titles):
    key = str(doc.get("id", "")).strip() or str(doc.get("relative_path", "")).strip()
    saved = str(titles.get(key, "")).strip()
    if saved:
        return saved
    return str(doc.get("file_name", "Документ")).strip()


def _get_pdf_path(doc):
    absolute_path = str(doc.get("absolute_path", "")).strip()
    if absolute_path and Path(absolute_path).is_file():
        return str(Path(absolute_path))
    relative_path = str(doc.get("relative_path", "")).strip()
    if relative_path:
        path = KNOWLEDGE_BASE_DIR / relative_path
        if path.is_file():
            return str(path)
    return ""


def is_manual(doc):
    rel = str(doc.get("relative_path", "")).replace("\\", "/").lower()
    doc_type = str(doc.get("document_type", "")).strip().lower()
    return rel.startswith("manual_documents/") or doc_type in ("manual_documents", "приказы")


def load_manual_documents():
    titles = _load_titles()
    docs = []
    for doc in _load_kb_registry():
        if not is_manual(doc):
            continue
        if doc.get("text_status") != "ready" or not doc.get("text_file"):
            continue
        docs.append({
            "id": str(doc.get("relative_path", "")),
            "name": _get_title(doc, titles),
            "text_file": str(doc.get("text_file", "")),
            "pdf_path": _get_pdf_path(doc),
        })
    docs.sort(key=lambda d: d["name"].lower())
    return docs


def read_doc_text(doc):
    path = KNOWLEDGE_BASE_DIR / doc.get("text_file", "")
    if not path.is_file():
        return None
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return None


def clean_text(text):
    text = re.sub(r"={3,}", " ", text)
    text = re.sub(r"-{3,}", " ", text)
    text = re.sub(r"\bСТРАНИЦА\s+\d+\b", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_by_pages(text):
    """Разбивает текст на (номер_страницы, кусок_текста)."""
    pages = []
    current_page = 1
    current_lines = []
    for line in str(text).split("\n"):
        m = re.match(r"\s*СТРАНИЦА\s+(\d+)\s*$", line)
        if m:
            if current_lines:
                pages.append((current_page, "\n".join(current_lines)))
            current_page = int(m.group(1))
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines:
        pages.append((current_page, "\n".join(current_lines)))
    return pages or [(1, str(text))]


def split_sentences(text):
    table_rows = []
    plain_lines = []
    for line in str(text).split("\n"):
        s = line.strip()
        if s.startswith("[TAB_ROW]"):
            row = s[len("[TAB_ROW]"):].strip()
            if 20 <= len(row) <= 700:
                table_rows.append(row)
        else:
            plain_lines.append(line)

    plain = clean_text(" ".join(plain_lines))
    parts = re.split(r"(?<=[.!?;])\s+(?=[А-ЯӘІҢҒҮҰҚӨҺA-Z0-9])", plain)

    sentences = list(table_rows)
    pending_number = ""
    for part in parts:
        p = part.strip()
        if not p:
            continue
        if re.fullmatch(r"\d{1,3}(?:[.-]\d+)*[.)]?", p):
            pending_number = p.rstrip(".)") + ". "
            continue
        if 30 <= len(p) <= 600:
            sentences.append(pending_number + p)
            pending_number = ""
    return sentences


def _doc_quick_score(text_lower, question_stems):
    score = 0
    for stem in question_stems:
        if len(stem) >= 5:
            count = text_lower.count(stem)
            if count > 0:
                score += 10 + min(count, 15)
    return score


def analyze_manual_documents(
    selected_ids,
    user_question="",
    search_all=False,
    max_sentences=7,
):
    docs = load_manual_documents()

    if not docs:
        return {
            "status": "no_texts",
            "answer": (
                "⚠️ В базе пока нет ваших приказов.\n\n"
                "Добавьте приказ: «📑 Приказы» → «➕ Добавить приказ»."
            ),
            "sources": [],
            "sentences": [],
            "source_infos": [],
        }

    if not search_all and selected_ids:
        docs = [d for d in docs if d["id"] in selected_ids]

    question = str(user_question or "").strip()
    question_stems = tokenize(question)
    question_phrases = get_question_phrases(question)

    candidates = []
    for doc in docs:
        text = read_doc_text(doc)
        if text:
            candidates.append((doc, text))

    if not candidates:
        return {
            "status": "no_texts",
            "answer": "⚠️ Не удалось прочитать тексты приказов.",
            "sources": [],
            "sentences": [],
            "source_infos": [],
        }

    # Шаг 1: выбор документов
    if question_stems and (search_all or len(candidates) > 6):
        ranked = []
        for doc, text in candidates:
            ranked.append((_doc_quick_score(text.lower(), question_stems), doc, text))
        ranked.sort(key=lambda x: x[0], reverse=True)
        top = [(d, t) for s, d, t in ranked if s > 0][:6]
        if not top:
            top = [(d, t) for s, d, t in ranked[:3]]
    else:
        top = candidates[:6]

    # Шаг 2: предложения с номерами страниц
    all_sentences = []
    for doc, text in top:
        for page_number, chunk in split_by_pages(text):
            for sentence in split_sentences(chunk):
                all_sentences.append({
                    "doc": doc["name"],
                    "pdf_path": doc["pdf_path"],
                    "page": page_number,
                    "sentence": sentence,
                    "tokens": tokenize(sentence),
                })

    # Шаг 3: IDF-веса
    weights = {}
    for q in question_stems:
        df = sum(
            1 for item in all_sentences
            if any(stems_match(q, t) for t in item["tokens"])
        )
        weights[q] = 1.0 / (1.0 + math.log(1.0 + df))

    # Шаг 4: оценка
    scored = []
    for item in all_sentences:
        lower = item["sentence"].lower()
        matched = {}
        for q in question_stems:
            tf = sum(1 for t in item["tokens"] if stems_match(q, t))
            if tf:
                matched[q] = tf
        if not matched:
            continue
        score = 40.0 * sum(weights[q] * min(tf, 2) for q, tf in matched.items())
        coverage = len(matched) / len(question_stems)
        if coverage >= 0.99:
            score += 12
        elif coverage >= 0.5:
            score += 8
        for phrase in question_phrases:
            if phrase in lower:
                score += 30
        for pattern in IMPORTANT_PATTERNS:
            if re.search(pattern, lower):
                score += 3
        if " | " in item["sentence"]:
            score += 10
        if re.search(r"\b\d+(\.\d+)+\b", item["sentence"]):
            score += 4
        if score > 0:
            scored.append({
                "sentence": item["sentence"],
                "score": score,
                "doc": item["doc"],
                "pdf_path": item["pdf_path"],
                "page": item["page"],
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    top_sentences = []
    seen = set()
    for item in scored:
        key = normalize_text(item["sentence"])
        if key in seen:
            continue
        seen.add(key)
        top_sentences.append(item)
        if len(top_sentences) >= max_sentences:
            break

    if not top_sentences:
        hint = ""
        low = question.lower()
        for marker, name, url in SUGGESTED_ORDERS:
            if marker in low:
                hint = (
                    f"\n\n💡 Похоже, вам нужен приказ:\n{name}\n"
                    f"Скачайте его на adilet.zan.kz и добавьте:\n{url}\n\n"
                    "«📑 Приказы» → «➕ Добавить приказ» — "
                    "и AI начнёт отвечать по нему."
                )
                break
        return {
            "status": "no_results",
            "answer": (
                "ℹ️ В добавленных приказах не найдено информации по запросу."
                + hint
            ),
            "sources": [],
            "sentences": [],
            "source_infos": [],
        }

    by_doc = {}
    for item in top_sentences:
        by_doc.setdefault(item["doc"], []).append(item)

    parts = []
    if question:
        parts.append(f"📋 Вопрос: {question}\n")
    parts.append("📚 Ответ на основании ваших приказов:\n")
    for doc_name, items in by_doc.items():
        parts.append(f"\n━━━ {doc_name} ━━━")
        for i, item in enumerate(items, 1):
            parts.append(f"\n{i}. [стр. {item['page']}] {item['sentence']}")

    parts.append("\n\n📑 Источники:")
    for name in by_doc.keys():
        parts.append(f"\n• {name}")

    source_infos = []
    seen_docs = set()
    for item in top_sentences:
        if item["doc"] not in seen_docs:
            seen_docs.add(item["doc"])
            source_infos.append({
                "name": item["doc"],
                "pdf_path": item["pdf_path"],
            })

    return {
        "status": "ok",
        "answer": "\n".join(parts),
        "sources": list(by_doc.keys()),
        "sentences": top_sentences,
        "source_infos": source_infos,
    }
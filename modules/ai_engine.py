# -*- coding: utf-8 -*-
import os
import re
import json
import hashlib
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    print("⚠️ WARNING: OPENAI_API_KEY not found in .env file")

client = OpenAI(api_key=API_KEY) if API_KEY else None

SYSTEM_PROMPT = """Ты — AI-ассистент главного санитарного врача, Казахстан.
ВАЖНО: Отвечай СТРОГО на основе предоставленных нормативных документов.
Если в документах нет информации по вопросу — честно скажи об этом.
Отвечай:
- Кратко и структурированно
- Со ссылками на конкретные пункты (если они есть в тексте)
- Давай практические рекомендации для отеля
- Используй списки и заголовки для удобства чтения
- Отвечай на языке вопроса (русский, қазақша, English или Türkçe)."""

STOPWORDS = {
    "который", "которая", "которые", "какой", "какая", "какие", "сколько",
    "почему", "зачем", "нужно", "надо", "можно", "должен", "должна", "должны",
    "такой", "такая", "этого", "этом", "если", "когда", "чего", "чем", "что",
    "как", "или", "при", "для", "этом", "том", "это", "есть", "быть", "будет",
}


def get_registry_path():
    return os.path.join(os.path.dirname(__file__), "..", "laws_registry.json")


def load_laws_registry():
    try:
        with open(get_registry_path(), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки laws_registry.json: {e}")
        return []


def save_laws_registry(registry):
    try:
        with open(get_registry_path(), "w", encoding="utf-8") as f:
            json.dump(registry, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения laws_registry.json: {e}")
        return False


def add_law_to_registry(name, number, url="", status="active"):
    registry = load_laws_registry()
    base_id = re.sub(r'[^a-z0-9]', '_', name.lower())
    new_id = base_id
    counter = 1
    while any(doc["id"] == new_id for doc in registry):
        new_id = f"{base_id}_{counter}"
        counter += 1
    registry.append({"id": new_id, "name": name, "number": number, "url": url, "status": status})
    return save_laws_registry(registry)


def delete_law_from_registry(law_id):
    registry = load_laws_registry()
    registry = [doc for doc in registry if doc["id"] != law_id]
    return save_laws_registry(registry)


# ============================================================
# Поиск текстов через knowledge_base/registry.json
# ============================================================

def _normalize(s):
    return re.sub(r"\s+", " ", str(s or "").lower().replace("ё", "е")).strip()


def _load_kb_registry():
    path = os.path.join(os.path.dirname(__file__), "..", "knowledge_base", "registry.json")
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _read_text_file(rel_path):
    base = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")
    path = os.path.join(base, str(rel_path))
    if not os.path.isfile(path):
        return None
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()
    except Exception:
        return None


def find_text_in_knowledge_base(doc_info):
    """Ищет текст норматива в базе знаний по номеру и названию."""
    number = str(doc_info.get("number", "")).strip()
    name = _normalize(doc_info.get("name", ""))
    digits = [d for d in re.findall(r"\d+", number) if len(d) >= 2]
    name_words = {w for w in re.findall(r"[а-яa-z0-9№]+", name) if len(w) >= 4}

    best_doc = None
    best_score = 0
    for doc in _load_kb_registry():
        if doc.get("text_status") != "ready" or not doc.get("text_file"):
            continue
        fname = _normalize(doc.get("file_name", ""))
        stem = _normalize(os.path.splitext(fname)[0])
        score = 0
        if digits and any(d in fname for d in digits):
            score += 3
        score += len(name_words & set(re.findall(r"[а-яa-z0-9№]+", stem))) * 2
        if score > best_score:
            best_score = score
            best_doc = doc

    if best_doc and best_score >= 3:
        text = _read_text_file(best_doc.get("text_file"))
        if text:
            return text, best_doc
    return None, None


def load_document_text(doc_id):
    """Загружает текст документа: сначала напрямую, затем через registry.json."""
    base_path = os.path.join(os.path.dirname(__file__), "..", "knowledge_base")
    for ext in [".txt", ""]:
        file_path = os.path.join(base_path, f"{doc_id}{ext}")
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            except Exception as e:
                return f"[Ошибка чтения файла: {e}]"

    doc_info = next((d for d in load_laws_registry() if d["id"] == doc_id), None)
    if doc_info:
        text, _ = find_text_in_knowledge_base(doc_info)
        if text:
            return text
    return f"[Текст документа {doc_id} не найден. Нажмите '🔄 Обновить базу' в разделе Приказы.]"


# ============================================================
# УМНЫЙ ПОИСК: только релевантные абзацы (дешевле и быстрее)
# ============================================================

def _question_words(question):
    words = re.findall(r"[а-яa-zәіңғүұқөһ0-9№]+", _normalize(question))
    return {w for w in words if len(w) >= 4 and w not in STOPWORDS}


def _split_paragraphs(text, size=1200):
    """Разбивает текст на абзацы по границам предложений (не рвёт смысл)."""
    compact = re.sub(r"\s+", " ", text)
    parts = []
    pos = 0
    while pos < len(compact):
        end = min(pos + size, len(compact))
        if end < len(compact):
            half = pos + size // 2
            cut = max(compact.rfind(". ", half, end),
                      compact.rfind("; ", half, end),
                      compact.rfind(") ", half, end))
            if cut > pos:
                end = cut + 1
        parts.append(compact[pos:end].strip())
        pos = end
    return [p for p in parts if p]


def _select_fragments(text, question, limit=5, size=1200):
    """Выбирает только 5 самых релевантных абзацев вместо всего текста."""
    qw = _question_words(question)
    nums = set(re.findall(r"\d+", question or ""))
    if not qw:
        return text[:size * limit]
    parts = _split_paragraphs(text, size)
    ranked = []
    for index, part in enumerate(parts):
        pw = set(re.findall(r"[а-яa-zәіңғүұқөһ0-9№]+", _normalize(part)))
        score = len(qw & pw)
        if nums:
            for n in nums:
                if re.search(r"(?:^|\D)" + n + r"(?:-\d+)?\)", part):
                    score += 5
        if score > 0:
            ranked.append((score, index, part))
    if not ranked:
        return text[:size * limit]
    ranked.sort(key=lambda x: x[0], reverse=True)
    chosen = ranked[:limit]
    chosen.sort(key=lambda x: x[1])  # сохраняем исходный порядок абзацев
    return "\n[...]\n".join(p for _, _, p in chosen)


def analyze_selected_laws(selected_ids, user_question=""):
    """Анализирует выбранные нормативы и отвечает на вопрос."""
    if not client:
        return "❌ Ошибка: API ключ OpenAI не настроен. Проверьте файл .env"
    if not selected_ids:
        return "⚠️ Выберите хотя бы один норматив для анализа"

    registry = load_laws_registry()
    documents_text = []
    total_len = 0
    MAX_TOTAL = 30000

    for doc_id in selected_ids:
        doc_info = next((d for d in registry if d["id"] == doc_id), None)
        if not doc_info:
            continue
        text = load_document_text(doc_id)
        if user_question and len(text) > 8000:
            text = _select_fragments(text, user_question)
        if total_len + len(text) > MAX_TOTAL:
            text = text[:MAX_TOTAL - total_len] + "\n[...текст сокращён...]"
        total_len += len(text)
        documents_text.append(f"=== {doc_info['name']} ({doc_info['number']}) ===\n{text}")

    if not documents_text:
        return "⚠️ Не удалось загрузить тексты выбранных документов"

    combined_text = "\n".join(documents_text)
    if user_question:
        prompt = (
            f"Вот выбранные нормативные документы:\n{combined_text}\n\n"
            f"Вопрос пользователя: {user_question}\n"
            "Проанализируй документы и ответь на вопрос, ссылаясь на конкретные пункты."
        )
    else:
        prompt = (
            f"Вот выбранные нормативные документы:\n{combined_text}\n\n"
            "Сделай краткий анализ: основные требования, ключевые моменты для отеля, "
            "что проверить в первую очередь, практические рекомендации."
        )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2000,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        error_msg = str(e)
        if "rate_limit" in error_msg.lower():
            return "⚠️ Превышен лимит запросов. Подождите минуту."
        elif "context_length" in error_msg.lower():
            return "⚠️ Документы слишком длинные. Выберите меньше нормативов."
        return f"❌ Ошибка API: {error_msg}"


# ============================================================
# ГИБРИД для AI-помощника (ваши приказы + OpenAI)
# ============================================================

def analyze_provided_documents(documents, user_question=""):
    """
    Принимает готовые тексты документов и делает OpenAI-синтез.
    documents: список словарей {"name": ..., "text": ...}
    Используется кнопкой «🤖 Гибрид + OpenAI» на странице AI-помощника.
    """
    if not client:
        return "❌ Ошибка: API ключ OpenAI не настроен. Проверьте файл .env"
    if not documents:
        return "⚠️ Нет документов для анализа"

    parts = []
    total = 0
    for doc in documents:
        text = str(doc.get("text", ""))
        if user_question and len(text) > 8000:
            text = _select_fragments(text, user_question)
        if total + len(text) > 30000:
            break
        total += len(text)
        parts.append(f"=== {doc.get('name', 'Документ')} ===\n{text}")

    combined = "\n".join(parts)
    if user_question:
        prompt = (
            f"Вот нормативные документы пользователя:\n{combined}\n\n"
            f"Вопрос: {user_question}\n"
            "Ответь строго по этим документам, со ссылками на пункты."
        )
    else:
        prompt = (
            f"Вот нормативные документы пользователя:\n{combined}\n\n"
            "Сделай краткий анализ: основные требования и что проверить в отеле."
        )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2000,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Ошибка API: {e}"


def test_connection():
    if not client:
        return False
    try:
        client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5,
        )
        return True
    except Exception:
        return False


# ============================================================
# ПАМЯТЬ AI: сохраняет вопросы и ответы для мгновенных ответов
# ============================================================

def get_memory_path():
    return os.path.join(os.path.dirname(__file__), "..", "database", "ai_memory.json")


def load_memory():
    """Загружает все сохранённые Q&A пары."""
    path = get_memory_path()
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception as e:
        print(f"Ошибка загрузки памяти: {e}")
        return []


def save_memory(memory):
    """Сохраняет память на диск."""
    path = get_memory_path()
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(memory, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения памяти: {e}")
        return False


def _question_hash(question):
    """Создаёт хеш нормализованного вопроса."""
    normalized = _normalize(question)
    return hashlib.md5(normalized.encode()).hexdigest()


def _similarity_score(q1, q2):
    """Оценивает схожесть двух вопросов (0.0 - 1.0)."""
    words1 = set(re.findall(r"[а-яa-zәіңғүұқөһ0-9]+", _normalize(q1)))
    words2 = set(re.findall(r"[а-яa-zәіңғүұқөһ0-9]+", _normalize(q2)))
    if not words1 or not words2:
        return 0.0
    intersection = words1 & words2
    union = words1 | words2
    return len(intersection) / len(union) if union else 0.0


def find_in_memory(question, threshold=0.6):
    """
    Ищет похожий вопрос в памяти.
    Возвращает ответ, если найдено совпадение >= threshold, иначе None.
    """
    memory = load_memory()
    best_match = None
    best_score = 0.0
    
    for item in memory:
        saved_q = item.get("question", "")
        score = _similarity_score(question, saved_q)
        if score > best_score:
            best_score = score
            best_match = item
    
    if best_match and best_score >= threshold:
        # Увеличиваем счётчик использований
        best_match["used_count"] = best_match.get("used_count", 0) + 1
        best_match["last_used"] = datetime.now().isoformat()
        save_memory(memory)
        
        return {
            "answer": best_match.get("answer", ""),
            "sources": best_match.get("sources", []),
            "similarity": best_score,
            "from_memory": True,
        }
    return None


def save_to_memory(question, answer, sources=None):
    """Сохраняет новый Q&A в память."""
    memory = load_memory()
    
    # Проверяем, нет ли уже такого вопроса
    q_hash = _question_hash(question)
    for item in memory:
        if _question_hash(item.get("question", "")) == q_hash:
            # Обновляем существующий
            item["answer"] = answer
            item["sources"] = sources or []
            item["updated_at"] = datetime.now().isoformat()
            save_memory(memory)
            return True
    
    # Добавляем новый
    memory.append({
        "id": q_hash[:8],
        "question": question,
        "answer": answer,
        "sources": sources or [],
        "created_at": datetime.now().isoformat(),
        "last_used": datetime.now().isoformat(),
        "used_count": 0,
    })
    save_memory(memory)
    return True


def delete_from_memory(question_hash):
    """Удаляет запись из памяти по хешу."""
    memory = load_memory()
    memory = [m for m in memory if m.get("id") != question_hash]
    return save_memory(memory)
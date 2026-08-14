import threading
import webbrowser
import tkinter
import pymupdf as fitz
import customtkinter as ctk
from tkinter import messagebox

from modules import local_ai_engine
from modules import ai_memory


def _has_openai_key():
    try:
        import os
        from dotenv import load_dotenv
        load_dotenv()
        return bool(os.getenv("OPENAI_API_KEY"))
    except Exception:
        return False


def open_pdf_viewer(pdf_path, start_page=1):
    """Встроенный просмотрщик PDF: открывает нужную страницу."""
    from pathlib import Path

    try:
        doc = fitz.open(str(pdf_path))
    except Exception as error:
        messagebox.showerror("SanEpi AI", f"Не удалось открыть PDF:\n{error}")
        return

    total = len(doc)
    state = {"page": min(max(1, int(start_page)), total)}

    window = ctk.CTkToplevel()
    window.title(f"📄 {Path(str(pdf_path)).name}")
    window.geometry("980x1100")
    window.lift()
    window.focus_force()

    top = ctk.CTkFrame(window, fg_color="transparent")
    top.pack(fill="x", padx=10, pady=8)

    def go_prev():
        if state["page"] > 1:
            state["page"] -= 1
            render()

    def go_next():
        if state["page"] < total:
            state["page"] += 1
            render()

    ctk.CTkButton(
        top, text="◀", width=44, height=36, command=go_prev
    ).pack(side="left", padx=4)

    page_info = ctk.CTkLabel(top, text="", font=("Arial", 15, "bold"))
    page_info.pack(side="left", padx=10)

    ctk.CTkButton(
        top, text="▶", width=44, height=36, command=go_next
    ).pack(side="left", padx=4)

    def open_external():
        try:
            import os
            os.startfile(str(pdf_path))
        except Exception:
            webbrowser.open(Path(str(pdf_path)).resolve().as_uri())

    ctk.CTkButton(
        top,
        text="🌐 Внешний просмотрщик",
        width=220,
        height=36,
        fg_color="#4b5563",
        hover_color="#374151",
        command=open_external,
    ).pack(side="right", padx=4)

    canvas_frame = ctk.CTkFrame(window, corner_radius=8)
    canvas_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    canvas = tkinter.Canvas(
        canvas_frame, bg="#2b2d31", highlightthickness=0
    )
    v_scroll = ctk.CTkScrollbar(canvas_frame, command=canvas.yview)
    canvas.configure(yscrollcommand=v_scroll.set)
    v_scroll.pack(side="right", fill="y")
    canvas.pack(fill="both", expand=True)

    holder = {"photo": None}

    def render():
        page = doc.load_page(state["page"] - 1)
        zoom = 940 / page.rect.width
        pixmap = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom))
        holder["photo"] = tkinter.PhotoImage(data=pixmap.tobytes("png"))
        canvas.delete("all")
        canvas.create_image(0, 0, anchor="nw", image=holder["photo"])
        canvas.configure(scrollregion=canvas.bbox("all"))
        canvas.yview_moveto(0)
        page_info.configure(text=f"Страница {state['page']} из {total}")

    def on_close():
        try:
            doc.close()
        except Exception:
            pass
        window.destroy()

    window.protocol("WM_DELETE_WINDOW", on_close)
    render()


def open_pdf_at_page(pdf_path, page):
    """Открывает PDF во встроенном просмотрщике на нужной странице."""
    from pathlib import Path

    if not pdf_path:
        messagebox.showinfo("SanEpi AI", "PDF-файл не найден.")
        return
    if not Path(str(pdf_path)).is_file():
        messagebox.showwarning(
            "SanEpi AI",
            f"PDF-файл не найден:\n{pdf_path}\n\n"
            "Добавьте приказ заново через «📑 Приказы».",
        )
        return
    open_pdf_viewer(pdf_path, page)


def _bind_click_recursive(widget, handler):
    try:
        widget.bind("<Button-1>", handler)
        widget.configure(cursor="hand2")
    except Exception:
        pass
    for child in widget.winfo_children():
        _bind_click_recursive(child, handler)


def build_ai_assistant_page(parent):
    state = {"question": "", "answer": "", "sources": []}

    ctk.CTkLabel(
        parent, text="🤖 AI Помощник", font=("Arial", 34, "bold")
    ).pack(pady=(20, 5))

    has_key = _has_openai_key()
    ctk.CTkLabel(
        parent,
        text=(
            "🟢 Режим: ГИБРИД (ваши приказы + OpenAI)"
            if has_key
            else "🟡 Режим: ЛОКАЛЬНЫЙ (поиск по вашим приказам, бесплатно)"
        ),
        font=("Arial", 13, "bold"),
        text_color="#22c55e" if has_key else "#f59e0b",
    ).pack(pady=(0, 5))

    ctk.CTkLabel(
        parent,
        text=(
            "AI отвечает только по приказам, которые вы добавили сами. "
            "Клик по найденному пункту открывает приказ на нужной странице."
        ),
        font=("Arial", 14),
        text_color="#9ca3af",
    ).pack(pady=(0, 10))

    body = ctk.CTkFrame(parent, corner_radius=14)
    body.pack(fill="both", expand=True, padx=20, pady=(0, 15))
    body.grid_columnconfigure(0, weight=2)
    body.grid_columnconfigure(1, weight=3)
    body.grid_rowconfigure(0, weight=1)

    # ================= ЛЕВАЯ КОЛОНКА =================
    left = ctk.CTkFrame(body, corner_radius=12)
    left.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)

    ctk.CTkLabel(
        left, text="📑 Мои приказы", font=("Arial", 18, "bold")
    ).pack(anchor="w", padx=15, pady=(15, 8))

    kb_all_var = ctk.BooleanVar(value=True)
    ctk.CTkCheckBox(
        left,
        text=" Искать во ВСЕХ моих приказах",
        variable=kb_all_var,
        font=("Arial", 13, "bold"),
        height=36,
        fg_color="#059669",
    ).pack(anchor="w", padx=12, pady=(0, 8))

    ctk.CTkLabel(
        left,
        text="Или только выбранные:",
        font=("Arial", 12),
        text_color="#9ca3af",
    ).pack(anchor="w", padx=15, pady=(0, 4))

    documents = local_ai_engine.load_manual_documents()
    checkboxes = []

    laws_scroll = ctk.CTkScrollableFrame(left, corner_radius=10)
    laws_scroll.pack(fill="both", expand=True, padx=12, pady=(0, 8))

    if not documents:
        ctk.CTkLabel(
            laws_scroll,
            text="База приказов пуста.\n\nДобавьте приказ:\n«📑 Приказы» →\n«➕ Добавить приказ»",
            font=("Arial", 14),
            text_color="#9ca3af",
            justify="center",
        ).pack(pady=30)
    else:
        for doc in documents:
            var = ctk.BooleanVar(value=False)
            label = doc["name"]
            if len(label) > 55:
                label = label[:52] + "…"
            ctk.CTkCheckBox(
                laws_scroll,
                text=label,
                variable=var,
                font=("Arial", 13),
                height=28,
            ).pack(anchor="w", padx=8, pady=4)
            checkboxes.append((doc, var))

    def select_all(value):
        for _, var in checkboxes:
            var.set(value)

    sel_frame = ctk.CTkFrame(left, fg_color="transparent")
    sel_frame.pack(fill="x", padx=12, pady=(0, 12))
    ctk.CTkButton(
        sel_frame, text="✅ Все", width=100,
        command=lambda: select_all(True),
    ).pack(side="left", padx=(0, 6))
    ctk.CTkButton(
        sel_frame, text="⬜ Сброс", width=100, fg_color="#6b7280",
        command=lambda: select_all(False),
    ).pack(side="left")

    # ================= ПРАВАЯ КОЛОНКА =================
    right = ctk.CTkFrame(body, corner_radius=12)
    right.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
    right.grid_rowconfigure(4, weight=1)
    right.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(
        right, text="❓ Вопрос для AI", font=("Arial", 18, "bold")
    ).grid(row=0, column=0, sticky="w", padx=15, pady=(15, 8))

    question_box = ctk.CTkTextbox(right, height=80, font=("Arial", 14), wrap="word")
    question_box.grid(row=1, column=0, sticky="ew", padx=15)

    quick_frame = ctk.CTkFrame(right, fg_color="transparent")
    quick_frame.grid(row=2, column=0, sticky="ew", padx=15, pady=(6, 6))
    quick_questions = [
        ("Температура хранения", "Какие требования к температуре хранения?"),
        ("Сроки медосмотра", "Как часто проводить медосмотр?"),
        ("Маркировка", "Требования к маркировке продуктов?"),
        ("Гигиена", "Требования к личной гигиене персонала?"),
    ]

    def ask_quick(q):
        question_box.delete("1.0", "end")
        question_box.insert("1.0", q)

    for i, (label, q) in enumerate(quick_questions):
        ctk.CTkButton(
            quick_frame,
            text=label,
            width=190,
            height=28,
            font=("Arial", 11),
            fg_color="#4b5563",
            hover_color="#374151",
            command=lambda q=q: ask_quick(q),
        ).grid(row=0, column=i, padx=2)

    status_label = ctk.CTkLabel(right, text="", font=("Arial", 13), text_color="#f59e0b")
    status_label.grid(row=3, column=0, sticky="n", pady=(4, 4))

    # Кликабельная область ответа
    answer_scroll = ctk.CTkScrollableFrame(right, corner_radius=10)
    answer_scroll.grid(row=4, column=0, sticky="nsew", padx=15, pady=(0, 8))

    def render_result(result):
        for widget in answer_scroll.winfo_children():
            widget.destroy()

        if result["status"] != "ok":
            ctk.CTkLabel(
                answer_scroll,
                text=result["answer"],
                font=("Arial", 14),
                justify="left",
                wraplength=860,
            ).pack(anchor="w", padx=12, pady=12)
            return

        if state["question"]:
            ctk.CTkLabel(
                answer_scroll,
                text=f"📋 Вопрос: {state['question']}",
                font=("Arial", 15, "bold"),
            ).pack(anchor="w", padx=12, pady=(12, 4))

        ctk.CTkLabel(
            answer_scroll,
            text="📚 Нажмите на пункт, чтобы открыть приказ на нужной странице:",
            font=("Arial", 12),
            text_color="#9ca3af",
        ).pack(anchor="w", padx=12, pady=(0, 6))

        by_doc = {}
        for item in result["sentences"]:
            by_doc.setdefault(item["doc"], []).append(item)

        number = 1
        for doc_name, items in by_doc.items():
            ctk.CTkLabel(
                answer_scroll,
                text=f"━━━ {doc_name} ━━━",
                font=("Arial", 15, "bold"),
            ).pack(anchor="w", padx=12, pady=(10, 2))

            for item in items:
                row = ctk.CTkFrame(answer_scroll, corner_radius=8)
                row.pack(fill="x", padx=10, pady=4)

                ctk.CTkLabel(
                    row,
                    text=f"{number}. {item['sentence']}",
                    font=("Arial", 13),
                    anchor="w",
                    justify="left",
                    wraplength=780,
                ).pack(anchor="w", padx=12, pady=(8, 0))

                hint = ctk.CTkLabel(
                    row,
                    text=f"📄 страница {item.get('page', 1)} — открыть приказ",
                    font=("Arial", 11),
                    text_color="#60a5fa",
                )
                hint.pack(anchor="w", padx=12, pady=(0, 8))

                handler = lambda e, it=item: open_pdf_at_page(
                    it.get("pdf_path", ""), it.get("page", 1)
                )
                _bind_click_recursive(row, handler)
                number += 1

        ctk.CTkLabel(
            answer_scroll,
            text="📑 Источники:",
            font=("Arial", 14, "bold"),
        ).pack(anchor="w", padx=12, pady=(12, 2))
        for src in result.get("source_infos", []):
            s = ctk.CTkLabel(
                answer_scroll,
                text=f"• {src['name']} — открыть PDF",
                font=("Arial", 12),
                text_color="#60a5fa",
            )
            s.pack(anchor="w", padx=16, pady=2)
            s.bind(
                "<Button-1>",
                lambda e, p=src["pdf_path"]: open_pdf_at_page(p, 1),
            )

    def get_selected_ids():
        return [doc["id"] for doc, var in checkboxes if var.get()]

    def run_local_analysis():
        question = question_box.get("1.0", "end").strip()
        search_all = kb_all_var.get()
        selected = get_selected_ids()

        if not search_all and not selected:
            messagebox.showwarning(
                "SanEpi AI",
                "Включите «Искать во ВСЕХ моих приказах»\nили выберите приказы галочками.",
            )
            return

        analyze_button.configure(state="disabled")
        status_label.configure(text="🔍 AI анализирует ваши приказы...", text_color="#f59e0b")

        def worker():
            if question:
                similar = ai_memory.find_similar_answers(question, approved_only=True)
                if similar and similar[0].get("similarity", 0) >= 0.5:
                    record = similar[0]
                    ai_memory.mark_as_used(record["id"])
                    answer = "✅ ПРОВЕРЕННЫЙ ОТВЕТ ИЗ ПАМЯТИ:\n\n" + record["answer"]
                    parent.after(0, lambda: finish_memory(answer))
                    return

            result = local_ai_engine.analyze_manual_documents(
                selected, question, search_all=search_all
            )
            parent.after(
                0,
                lambda: finish(
                    result,
                    "#22c55e" if result["status"] == "ok" else "#f59e0b",
                    f"✅ Найдено фрагментов: {len(result['sentences'])}",
                ),
            )

        def finish_memory(answer):
            state["question"] = question
            state["answer"] = answer
            for widget in answer_scroll.winfo_children():
                widget.destroy()
            ctk.CTkLabel(
                answer_scroll,
                text=answer,
                font=("Arial", 14),
                justify="left",
                wraplength=860,
            ).pack(anchor="w", padx=12, pady=12)
            status_label.configure(text="✅ Ответ из памяти AI", text_color="#22c55e")
            analyze_button.configure(state="normal")

        def finish(result, color, status_text):
            state["question"] = question
            state["answer"] = result["answer"]
            state["sources"] = result.get("sources", [])
            render_result(result)
            status_label.configure(text=status_text, text_color=color)
            analyze_button.configure(state="normal")

        threading.Thread(target=worker, daemon=True).start()

    def run_hybrid_analysis():
        if not _has_openai_key():
            messagebox.showwarning(
                "SanEpi AI",
                "OpenAI API ключ не настроен.\nДобавьте OPENAI_API_KEY в файл .env",
            )
            return

        question = question_box.get("1.0", "end").strip()
        search_all = kb_all_var.get()
        selected = get_selected_ids()

        if not search_all and not selected:
            messagebox.showwarning(
                "SanEpi AI",
                "Включите «Искать во ВСЕХ моих приказах»\nили выберите приказы галочками.",
            )
            return

        hybrid_button.configure(state="disabled")
        status_label.configure(text="🤖 Гибрид: ваши приказы + OpenAI...", text_color="#f59e0b")

        def worker():
            local_result = local_ai_engine.analyze_manual_documents(
                selected, question, search_all=search_all
            )
            if local_result["status"] not in ("ok", "no_results"):
                parent.after(
                    0,
                    lambda: finish(local_result, "#f59e0b", "⚠️ Приказы не найдены"),
                )
                return
            try:
                from modules import ai_engine
                analyzer = getattr(ai_engine, "analyze_provided_documents", None)
                if analyzer is None:
                    raise AttributeError("В ai_engine нет analyze_provided_documents")
                docs = []
                source_docs = local_ai_engine.load_manual_documents()
                if not search_all and selected:
                    source_docs = [d for d in source_docs if d["id"] in selected]
                for d in source_docs[:5]:
                    text = local_ai_engine.read_doc_text(d)
                    if text:
                        docs.append({"name": d["name"], "text": text})
                enhanced = analyzer(docs, question)
                local_result["answer"] = (
                    "🤖 ОТВЕТ OPENAI по вашим приказам:\n\n"
                    + enhanced
                    + "\n\n━━━ Локальные фрагменты ━━━\n"
                    + local_result["answer"]
                )
                parent.after(
                    0,
                    lambda: finish(local_result, "#22c55e", "✅ Гибридный анализ завершён"),
                )
            except Exception as e:
                parent.after(
                    0,
                    lambda: finish(local_result, "#f59e0b", "⚠️ Только локальный ответ"),
                )

        def finish(result, color, status_text):
            state["question"] = question
            state["answer"] = result["answer"]
            state["sources"] = result.get("sources", [])
            render_result(result)
            status_label.configure(text=status_text, text_color=color)
            hybrid_button.configure(state="normal")

        threading.Thread(target=worker, daemon=True).start()

    buttons_frame = ctk.CTkFrame(right, fg_color="transparent")
    buttons_frame.grid(row=5, column=0, sticky="ew", padx=15, pady=(0, 6))

    analyze_button = ctk.CTkButton(
        buttons_frame,
        text="🔍 Анализировать (локально)",
        height=44,
        fg_color="#7c3aed",
        hover_color="#6d28d9",
        command=run_local_analysis,
    )
    analyze_button.pack(side="left", fill="x", expand=True, padx=(0, 6))

    hybrid_button = ctk.CTkButton(
        buttons_frame,
        text="🤖 Гибрид + OpenAI",
        height=44,
        fg_color="#059669" if has_key else "#6b7280",
        hover_color="#047857" if has_key else "#4b5563",
        command=run_hybrid_analysis,
    )
    hybrid_button.pack(side="left", fill="x", expand=True, padx=(6, 0))

    def save_to_memory():
        if not state["answer"] or state["answer"].startswith(("⚠️", "❌", "ℹ️")):
            messagebox.showwarning("SanEpi AI", "Нет полезного ответа для сохранения.")
            return
        ai_memory.add_memory_record(
            question=state["question"],
            answer=state["answer"],
            source_document=", ".join(state.get("sources", [])),
            status="draft",
        )
        messagebox.showinfo(
            "SanEpi AI",
            "✅ Ответ сохранён в память (черновик).\n"
            "После проверки смените статус на approved — "
            "и AI будет отвечать им автоматически.",
        )

    ctk.CTkButton(
        right,
        text="💾 Сохранить ответ в память",
        height=38,
        fg_color="#1d4ed8",
        hover_color="#1e40af",
        command=save_to_memory,
    ).grid(row=6, column=0, sticky="ew", padx=15, pady=(0, 15))
"""
Блок СЭС: классификация объектов по эпидемической значимости
(приказ ҚР ДСМ-220/2020, пункты 3 и 4) + лабораторные исследования
(ҚР ДСМ-336 прил. 8 и приказ № 62 прил. 1).
«Мои объекты» — иерархия: основной объект → вложенные объекты,
у каждого кнопка протокола производственного контроля.
"""
import json
from datetime import datetime
from pathlib import Path
from tkinter import messagebox
import customtkinter as ctk

from modules.ses_lab_data import find_lab_categories
from modules.ses_protocol import open_protocol_window

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_DIR = PROJECT_ROOT / "database"
SES_FILE = DATABASE_DIR / "ses_objects.json"

ORDER_REF = "Приказ ҚР ДСМ-220/2020, Перечень"

HIGH_SIGNIFICANCE = [
    "1) детские молочные кухни;",
    "2) объекты дошкольного воспитания и обучения всех видов;",
    "3) объекты образования и воспитания с проживанием детей и подростков всех видов и типов;",
    "4) объекты общественного питания и торговли в организованных коллективах (дошкольные объекты, детские дома, объекты образования, интернатные организации, оздоровительные, санаторные объекты, объекты здравоохранения, реабилитационные центры; вахтовые поселки, промышленные объекты, строительные площадки);",
    "5) объекты по производству кремовых кондитерских изделий;",
    "6) объекты по производству, изготовлению лекарственных средств;",
    "7) объекты общественного питания на транспорте (железнодорожном, воздушном, водном и автомобильном), объекты бортового питания;",
    "8) организации и транспортные средства (железнодорожные, водные, воздушные), осуществляющие перевозку пассажиров;",
    "9) радиационно-опасные объекты;",
    "10) лечебно-косметологические объекты, салоны красоты, косметологические центры, оказывающие услуги с нарушением кожных и слизистых покровов, в том числе татуаж и татуировки;",
    "11) объекты здравоохранения: амбулаторно-поликлиническая, консультативно-диагностическая, стационарная и стационарозамещающая помощь, стоматологические услуги; экспертиза временной нетрудоспособности; донорство, заготовка крови и производство препаратов крови;",
    "12) объекты медико-социальной реабилитации;",
    "13) объекты образования без проживания детей и подростков, общежития объектов образования;",
    "14) специальные, коррекционные кабинеты (центры) воспитания и образования, реабилитационные центры для детей и подростков;",
    "15) объекты общественного питания с производством, переработкой и реализацией пищевой продукции с числом более 50 посадочных мест;",
    "16) молокоперерабатывающие объекты, объекты по производству готовой молочной продукции;",
    "17) мясоперерабатывающие объекты, объекты по производству мяса и мясных полуфабрикатов и (или) готовой мясной продукции;",
    "18) рыбоперерабатывающие объекты, объекты по производству рыбы и рыбных полуфабрикатов и (или) готовой рыбной продукции;",
    "19) птицеперерабатывающие объекты, объекты по производству полуфабрикатов из мяса птицы и (или) готовой продукции из мяса птицы;",
    "20) объекты по производству масложировой продукции;",
    "21) объекты по производству алкогольной, безалкогольной продукции, питьевой воды (в том числе минеральной), расфасованной в емкости;",
    "22) плодоперерабатывающие объекты, объекты по переработке сельхозпродукции растительного происхождения, в том числе соевой;",
    "23) объекты по производству, хранению и (или) реализации специализированных пищевых продуктов;",
    "24) объекты по производству поваренной и йодированной соли;",
    "25) мукомольные объекты;",
    "26) объекты по выпечке хлеба и хлебобулочных изделий;",
    "27) объекты по производству сахара;",
    "28) объекты оптового хранения и (или) реализации пищевой продукции;",
    "29) виды деятельности 1–2 классов опасности; стационарные передающие радиотехнические объекты с диапазоном 30 кГц – 300 ГГц в селитебной территории (кроме базовых станций сотовой и спутниковой связи);",
    "30) склады для хранения химических веществ, агрохимикатов и пестицидов; объекты хранения и транспортировки вакцин и иммунологических лекарственных препаратов;",
    "30-1) объекты хранения средств дезинфекции, дезинсекции, дератизации, приготовления и расфасовки приманок, ловушек, рабочих растворов;",
    "31) объекты спортивно-оздоровительного назначения, бассейны, бани и сауны вместимостью 20 и более мест;",
    "32) вахтовые поселки;",
    "33) водные объекты 2 категории (культурно-бытового назначения), места отдыха (пляжи);",
    "34) водоисточники, места водозабора для хозяйственно-питьевого водоснабжения;",
    "35) нецентрализованные системы хозяйственно-питьевого водоснабжения;",
    "36) централизованные системы хозяйственно-питьевого водоснабжения;",
    "37) оздоровительные и санаторные объекты (сезонные, круглогодичные), базы и места отдыха;",
    "38) лаборатории: обращение с патогенными биологическими агентами I–IV групп патогенности; лабораторная диагностика по пункту 15 Перечня разрешений первой категории.",
]

LOW_SIGNIFICANCE = [
    "1) объекты технического, профессионального, послесреднего и высшего образования;",
    "2) объекты досуга, физического воспитания и развития творческих способностей детей и подростков, центры творчества, музыкальные, спортивные и художественные школы, детско-юношеские центры, дворовые клубы, станции юных натуралистов, внешкольные организации;",
    "3) объекты по изготовлению, хранению и реализации продукции для детей и подростков (обувь, одежда, игрушки);",
    "4) объекты по оказанию услуг населению посредством компьютеров и видеотерминалов (компьютерные клубы);",
    "5) объекты общественного питания с числом 50 и менее посадочных мест, предприятия по производству заказных блюд без посадочных мест, кулинарных изделий;",
    "6) объекты по обслуживанию транспортных средств и пассажиров;",
    "7) аппараты для автоматического приготовления и реализации пищевой продукции;",
    "8) объекты по производству безкремовых кондитерских изделий;",
    "9) объекты по производству мучных полуфабрикатов, макаронных изделий;",
    "10) объекты по производству чипсов, сухариков, кукурузных палочек, казинаков, семечек, сухих завтраков, слайсов, сахарной ваты, попкорна, жареных орехов;",
    "11) объекты по фасовке готовых пищевых продуктов;",
    "12) объекты по производству пищевых концентратов и пищевых кислот;",
    "13) объекты по производству чая, дрожжей и желатина;",
    "14) объекты по производству крахмалопаточной продукции, крахмала;",
    "15) объекты здравоохранения, осуществляющие деятельность в сфере судебной медицины и патологической анатомии;",
    "16) объекты, осуществляющие реабилитацию для взрослых (кроме подпункта 11) пункта 3);",
    "17) объекты хранения, оптовой и розничной реализации лекарственных средств, изделий медицинского назначения, медицинской техники;",
    "18) объекты здравоохранения, оказывающие скорую медицинскую помощь, в том числе с привлечением медицинской авиации;",
    "19) объекты здравоохранения медицины катастроф;",
    "20) объекты здравоохранения, оказывающие паллиативную помощь и сестринский уход на дому;",
    "21) объекты традиционной медицины и целительства;",
    "22) объекты по изготовлению, производству, переработке и реализации вакцин и иммунологических лекарственных и диагностических препаратов;",
    "22-1) объекты по производству, переработке, реализации средств и (или) препаратов дезинфекции, дезинсекции, дератизации;",
    "23) парикмахерские, салоны красоты, косметологические центры, оказывающие косметические услуги без нарушения кожных и слизистых покровов, в том числе маникюр и педикюр;",
    "24) объекты спортивно-оздоровительного назначения, бани, сауны вместимостью до 20 мест;",
    "25) объекты социально-бытовой инфраструктуры (культурно-зрелищные объекты, кладбища, объекты похоронного назначения, гостиницы, мотели, кемпинги, общежития, хостелы; административные и жилые здания; организации по эксплуатации зданий и офисов; сбор и вывоз ТБО; контейнерные площадки; общественные туалеты; прачечные; химчистки; очистные сооружения);",
    "26) объекты по обслуживанию водопроводных, канализационных, тепловых систем, котельные;",
    "27) канализационные очистные сооружения и сети (в том числе ливневой канализации);",
    "28) виды деятельности 3–5 классов опасности; радиотехнические объекты вне селитебной территории; радиорелейные станции; базовые станции сотовой и спутниковой связи;",
    "29) парки в населенных пунктах;",
    "30) радиационные объекты с источниками ионизирующего излучения, радиоактивные отходы с минимально значимой активностью;",
    "31) организации и транспортные средства, осуществляющие перевозку пищевых продуктов, продовольственного сырья, хозяйственно-питьевой воды, опасных грузов;",
    "32) склады для хранения парфюмерно-косметической продукции, средств гигиены;",
    "33) объекты производства парфюмерно-косметической продукции и средств гигиены;",
    "34) продовольственные рынки, объекты оптовой и розничной торговли;",
    "35) все виды лабораторий (кроме подпункта 38) пункта 3);",
    "36) объекты хранения материальных ценностей государственного материального резерва, в том числе продуктов питания;",
    "37) пункты забора и приема биологического материала;",
    "38) специальные социальные услуги.",
]


def _load_my_objects():
    if not SES_FILE.exists():
        return []
    try:
        with open(SES_FILE, "r", encoding="utf-8-sig") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def _save_my_objects(items):
    DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    with open(SES_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)


def open_lab_window(parent, item_text, is_high):
    """Окно с лабораторными исследованиями по объекту."""
    window = ctk.CTkToplevel(parent)
    window.title("🔬 Лабораторные исследования")
    window.geometry("900x720")
    window.minsize(760, 560)
    window.lift()
    window.focus_force()

    ctk.CTkLabel(window, text="🔬 Лабораторные исследования по объекту", font=("Arial", 22, "bold")).pack(pady=(16, 4))
    ctk.CTkLabel(window, text=item_text, font=("Arial", 14, "bold"), text_color="#60a5fa", wraplength=820, justify="left").pack(padx=20, pady=(0, 10))

    scroll = ctk.CTkScrollableFrame(window, corner_radius=12)
    scroll.pack(fill="both", expand=True, padx=16, pady=(0, 16))

    cats = find_lab_categories(item_text, is_high)

    ctk.CTkLabel(
        scroll,
        text="🧪 А. Для санитарно-эпидемиологического заключения\n(ҚР ДСМ-336/2020, приложение 8)",
        font=("Arial", 16, "bold"),
        text_color="#ef4444" if is_high else "#9ca3af",
        justify="left",
    ).pack(anchor="w", padx=10, pady=(8, 6))

    if not is_high:
        ctk.CTkLabel(
            scroll,
            text="🟡 Объект НЕЗНАЧИТЕЛЬНОЙ эпидемической значимости:\nсан-эпид заключение не требуется — подаётся УВЕДОМЛЕНИЕ\nо начале деятельности (Закон «О разрешениях и уведомлениях»).",
            font=("Arial", 13), text_color="#f59e0b", justify="left",
        ).pack(anchor="w", padx=14, pady=(0, 8))
    else:
        shown = [c for c in cats if c.get("sanepid")]
        if not shown:
            ctk.CTkLabel(scroll, text="Перечень исследований уточняется по категории объекта\n(приложение 8 ҚР ДСМ-336/2020).", font=("Arial", 13), text_color="#9ca3af", justify="left").pack(anchor="w", padx=14, pady=(0, 8))
        for cat in shown:
            ctk.CTkLabel(scroll, text=f"▸ {cat['title']}", font=("Arial", 14, "bold")).pack(anchor="w", padx=14, pady=(6, 2))
            for line in cat["sanepid"]:
                ctk.CTkLabel(scroll, text=f"   • {line}", font=("Arial", 13), anchor="w", justify="left", wraplength=800).pack(anchor="w", padx=18, pady=1)

    ctk.CTkLabel(
        scroll,
        text="🏭 Б. Производственный контроль (самоконтроль)\n(приказ № 62 от 07.04.2023, приложение 1)",
        font=("Arial", 16, "bold"), text_color="#22c55e", justify="left",
    ).pack(anchor="w", padx=10, pady=(14, 6))

    shown_pc = [c for c in cats if c.get("prodcontrol")]
    if not shown_pc:
        ctk.CTkLabel(scroll, text="Программа производственного контроля разрабатывается\nс учётом характеристик объекта и вредных факторов\n(пункты 8–12 Санитарных правил, приказ № 62).", font=("Arial", 13), text_color="#9ca3af", justify="left").pack(anchor="w", padx=14, pady=(0, 8))
    for cat in shown_pc:
        ctk.CTkLabel(scroll, text=f"▸ {cat['title']}", font=("Arial", 14, "bold")).pack(anchor="w", padx=14, pady=(6, 2))
        for line in cat["prodcontrol"]:
            ctk.CTkLabel(scroll, text=f"   • {line}", font=("Arial", 13), anchor="w", justify="left", wraplength=800).pack(anchor="w", padx=18, pady=1)


def build_ses_page(parent):
    ctk.CTkLabel(parent, text="🏛️ СЭС: эпидемическая значимость объектов", font=("Arial", 30, "bold")).pack(pady=(20, 5))
    ctk.CTkLabel(parent, text=f"Классификация по {ORDER_REF} (пункты 3 и 4). 🔬 — лаборатории, 📄 — протокол ПК.", font=("Arial", 13), text_color="#9ca3af").pack(pady=(0, 10))

    search_var = ctk.StringVar(value="")
    ctk.CTkEntry(parent, textvariable=search_var, placeholder_text="🔍 Поиск по Перечню (например: бассейн, гостиница, лаборатория)...", height=38).pack(fill="x", padx=20, pady=(0, 10))

    tabs = ctk.CTkTabview(parent, corner_radius=14)
    tabs.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    tab_high = tabs.add("🔴 Высокая значимость")
    tab_low = tabs.add("🟡 Незначительная значимость")
    tab_my = tabs.add("🏢 Мои объекты")

    high_scroll = ctk.CTkScrollableFrame(tab_high, corner_radius=10)
    high_scroll.pack(fill="both", expand=True, padx=8, pady=8)
    low_scroll = ctk.CTkScrollableFrame(tab_low, corner_radius=10)
    low_scroll.pack(fill="both", expand=True, padx=8, pady=8)

    def render_lists(*_):
        query = search_var.get().strip().lower()
        for scroll, items, is_high, color in (
            (high_scroll, HIGH_SIGNIFICANCE, True, "#ef4444"),
            (low_scroll, LOW_SIGNIFICANCE, False, "#f59e0b"),
        ):
            for w in scroll.winfo_children():
                w.destroy()
            ctk.CTkLabel(scroll, text=("Пункт 3 — объекты ВЫСОКОЙ эпидемической значимости" if is_high else "Пункт 4 — объекты НЕЗНАЧИТЕЛЬНОЙ эпидемической значимости"), font=("Arial", 15, "bold"), text_color=color).pack(anchor="w", padx=10, pady=(5, 8))
            shown = 0
            for text in items:
                if query and query not in text.lower():
                    continue
                shown += 1
                row = ctk.CTkFrame(scroll, corner_radius=8)
                row.pack(fill="x", padx=6, pady=3)
                ctk.CTkLabel(row, text=text, font=("Arial", 13), anchor="w", justify="left", wraplength=700).pack(side="left", padx=10, pady=6, fill="x", expand=True)
                ctk.CTkButton(row, text="🔬", width=46, height=32, fg_color="#0d9488", hover_color="#0f766e", command=lambda t=text, h=is_high: open_lab_window(parent, t, h)).pack(side="right", padx=8, pady=6)
            if not shown:
                ctk.CTkLabel(scroll, text="Ничего не найдено.", font=("Arial", 14), text_color="#9ca3af").pack(pady=20)

    search_var.trace_add("write", render_lists)
    render_lists()

    # ================= МОИ ОБЪЕКТЫ (ИЕРАРХИЯ) =================
    header = ctk.CTkFrame(tab_my, corner_radius=10)
    header.pack(fill="x", padx=8, pady=8)
    header.grid_columnconfigure(0, weight=1)

    main_name_entry = ctk.CTkEntry(header, height=38, placeholder_text="Название основного объекта (например: Rixos Water World Aktau)")
    main_name_entry.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
    ctk.CTkButton(header, text="➕ Добавить основной объект", height=38, command=lambda: add_main()).grid(row=0, column=1, padx=(0, 10), pady=10)

    my_scroll = ctk.CTkScrollableFrame(tab_my, corner_radius=10)
    my_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def add_main():
        name = main_name_entry.get().strip()
        if not name:
            messagebox.showwarning("SanEpi AI", "Введите название основного объекта.")
            return
        items = _load_my_objects()
        items.append({
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "name": name,
            "category": "",
            "note": "",
            "created_at": datetime.now().isoformat(timespec="seconds"),
            "children": [],
        })
        _save_my_objects(items)
        main_name_entry.delete(0, "end")
        render_my()

    def delete_main(main_id):
        if not messagebox.askyesno("Удаление объекта", "Удалить основной объект вместе со всеми вложенными?"):
            return
        _save_my_objects([x for x in _load_my_objects() if x.get("id") != main_id])
        render_my()

    def delete_child(main_id, child_id):
        if not messagebox.askyesno("Удаление объекта", "Удалить вложенный объект?"):
            return
        items = _load_my_objects()
        for m in items:
            if m.get("id") == main_id:
                m["children"] = [c for c in m.get("children", []) if c.get("id") != child_id]
        _save_my_objects(items)
        render_my()

    def add_child_dialog(main_obj):
        dlg = ctk.CTkToplevel(tab_my)
        dlg.title("Вложенный объект")
        dlg.geometry("540x340")
        dlg.lift()
        dlg.focus_force()
        dlg.grab_set()
        ctk.CTkLabel(dlg, text=f"➕ Вложенный объект для:\n{main_obj.get('name', '')}", font=("Arial", 16, "bold"), justify="left").pack(padx=20, pady=(16, 8))
        name_e = ctk.CTkEntry(dlg, height=38, placeholder_text="Название (ресторан, бассейн, прачечная...)")
        name_e.pack(padx=20, pady=6, fill="x")
        cat_var = ctk.StringVar(value="Высокая значимость")
        ctk.CTkOptionMenu(dlg, variable=cat_var, values=["Высокая значимость", "Незначительная значимость"], height=36).pack(padx=20, pady=6, fill="x")
        note_e = ctk.CTkEntry(dlg, height=38, placeholder_text="Примечание (необязательно)")
        note_e.pack(padx=20, pady=6, fill="x")

        def save():
            nm = name_e.get().strip()
            if not nm:
                messagebox.showwarning("SanEpi AI", "Введите название вложенного объекта.")
                return
            items = _load_my_objects()
            for m in items:
                if m.get("id") == main_obj.get("id"):
                    m.setdefault("children", []).append({
                        "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
                        "name": nm,
                        "category": cat_var.get(),
                        "note": note_e.get().strip(),
                    })
            _save_my_objects(items)
            dlg.destroy()
            render_my()

        ctk.CTkButton(dlg, text="💾 Сохранить", height=38, fg_color="#059669", hover_color="#047857", command=save).pack(padx=20, pady=(8, 16), fill="x")

    def render_my():
        for w in my_scroll.winfo_children():
            w.destroy()
        items = _load_my_objects()
        if not items:
            ctk.CTkLabel(my_scroll, text="Основные объекты ещё не добавлены.\nВведите название сверху и нажмите «➕ Добавить основной объект».", font=("Arial", 14), text_color="#9ca3af", justify="center").pack(pady=25)
            return
        for m in items:
            card = ctk.CTkFrame(my_scroll, corner_radius=12, border_width=1, border_color="#334155")
            card.pack(fill="x", padx=6, pady=6)
            head = ctk.CTkFrame(card, fg_color="transparent")
            head.pack(fill="x", padx=10, pady=(10, 4))
            ctk.CTkLabel(head, text=f"🏢 {m.get('name', '-')}", font=("Arial", 16, "bold")).pack(side="left", padx=4)
            btns = ctk.CTkFrame(head, fg_color="transparent")
            btns.pack(side="right")
            ctk.CTkButton(btns, text="➕", width=44, height=30, fg_color="#0d9488", hover_color="#0f766e", command=lambda mm=m: add_child_dialog(mm)).pack(side="left", padx=3)
            ctk.CTkButton(btns, text="📄", width=44, height=30, fg_color="#1d4ed8", hover_color="#1e40af", command=lambda mm=m: open_protocol_window(tab_my, mm)).pack(side="left", padx=3)
            ctk.CTkButton(btns, text="🗑️", width=44, height=30, fg_color="#dc2626", hover_color="#b91c1c", command=lambda mm=m: delete_main(mm.get("id"))).pack(side="left", padx=3)
            children = m.get("children", [])
            if not children:
                ctk.CTkLabel(card, text="   Вложенных объектов нет — нажмите «➕».", font=("Arial", 12), text_color="#9ca3af").pack(anchor="w", padx=12, pady=(0, 10))
            for ch in children:
                high = ch.get("category") == "Высокая значимость"
                row = ctk.CTkFrame(card, fg_color="transparent")
                row.pack(fill="x", padx=16, pady=3)
                ctk.CTkLabel(row, text=f"{'🔴' if high else '🟡'} {ch.get('name', '-')}", font=("Arial", 14), anchor="w").pack(side="left", padx=4, fill="x", expand=True)
                ctk.CTkButton(row, text="🔬", width=44, height=30, fg_color="#0d9488", hover_color="#0f766e", command=lambda cc=ch, hh=high: open_lab_window(tab_my, cc.get("name", ""), hh)).pack(side="left", padx=3)
                ctk.CTkButton(row, text="📄", width=44, height=30, fg_color="#1d4ed8", hover_color="#1e40af", command=lambda cc=ch: open_protocol_window(tab_my, cc)).pack(side="left", padx=3)
                ctk.CTkButton(row, text="🗑️", width=44, height=30, fg_color="#dc2626", hover_color="#b91c1c", command=lambda mm=m, cc=ch: delete_child(mm.get("id"), cc.get("id"))).pack(side="left", padx=3)
            ctk.CTkLabel(card, text="", height=6).pack()

    render_my()
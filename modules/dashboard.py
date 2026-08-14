import customtkinter as ctk
from modules.export_reports import export_missing_to_excel
from modules.dashboard_data import load_dashboard_data
from modules.dashboard_cards import build_stats_cards
from modules.dashboard_quality import show_quality_details
from modules.dashboard_expiry import show_expiring_details
from modules.dashboard_departments import build_department_table
from modules.translations import tr
from modules.localization import translate_department


def get_risk_level(data):
    total_hr = data["total_hr"]
    missing = data["only_hr"]
    expiring = data["expiring_count"]

    if total_hr == 0:
        return "⚪", tr("no_data"), "#6b7280"

    missing_percent = (missing / total_hr) * 100

    if missing_percent >= 30 or expiring >= 20:
        return "🔴", tr("high"), "#dc2626"

    if missing_percent >= 10 or expiring >= 5:
        return "🟡", tr("medium"), "#f59e0b"

    return "🟢", tr("low"), "#22c55e"


def build_ai_analysis(parent, data):
    icon, level, color = get_risk_level(data)

    analysis_frame = ctk.CTkFrame(parent, corner_radius=16)
    analysis_frame.pack(padx=20, pady=15, fill="x")

    ctk.CTkLabel(
        analysis_frame,
        text="🤖 SanEpi AI Executive Analysis",
        font=("Arial", 24, "bold")
    ).pack(pady=(18, 8))

    ctk.CTkLabel(
        analysis_frame,
        text=f"{icon} {tr('risk_level')}: {level}",
        font=("Arial", 22, "bold"),
        text_color=color
    ).pack(pady=(0, 12))

    summary = (
        f"👥 HR: {data['total_hr']}     "
        f"🏥 e-SEN: {data['total_esen']}     "
        f"🔴 Нет в e-SEN: {data['only_hr']}     "
        f"⏰ Истекают: {data['expiring_count']}"
    )

    ctk.CTkLabel(
        analysis_frame,
        text=summary,
        font=("Arial", 16, "bold")
    ).pack(pady=8)

    problem_departments = []
    for dep, stat in data["dep_compare"].items():
        missing = stat.get("only_hr", 0)
        if missing > 0:
            problem_departments.append((dep, missing))

    problem_departments = sorted(
        problem_departments,
        key=lambda x: x[1],
        reverse=True
    )[:5]

    text_box = ctk.CTkTextbox(
        analysis_frame,
        width=1000,
        height=210,
        font=("Arial", 15)
    )
    text_box.pack(padx=20, pady=15, fill="x")

    text_box.insert(
        "end",
        f"{tr('problem_departments')}:\n\n"
    )

    if problem_departments:
        for i, (dep, count) in enumerate(problem_departments, start=1):
            text_box.insert(
                "end",
                f"{i}. {translate_department(dep)} — {count} {tr('employees_not_in_esen')}\n"
            )
    else:
        text_box.insert(
            "end",
            f"{tr('no_problem_departments')}.\n"
        )

    text_box.insert(
        "end",
        f"\n{tr('ai_recommendations')}:\n\n"
    )

    if data["only_hr"] > 0:
        text_box.insert(
            "end",
            f"• {tr('register_missing_employees')} ({data['only_hr']}).\n"
        )

    if data["expiring_count"] > 0:
        text_box.insert(
            "end",
            f"• {tr('extend_expiring_medbooks')} ({data['expiring_count']}).\n"
        )

    text_box.insert(
        "end",
        f"• {tr('control_new_employees')}.\n"
    )

    text_box.insert(
        "end",
        f"• {tr('repeat_sync')}.\n"
    )

    text_box.configure(state="disabled")


def build_dashboard_content(parent):
    data = load_dashboard_data()

    ctk.CTkLabel(
        parent,
        text=f"📊 {tr('dashboard')}",
        font=("Arial", 34, "bold")
    ).pack(pady=(20, 5))

    ctk.CTkLabel(
        parent,
        text=f"{tr('sync')} HR ↔️ e-SEN: {data['match_percent']}%",
        font=("Arial", 18, "bold"),
        text_color="#22c55e" if data["match_percent"] >= 80 else "#f97316"
    ).pack(pady=(0, 10))

    progress = ctk.CTkProgressBar(parent, width=500)
    progress.pack(pady=(0, 15))
    progress.set(data["match_percent"] / 100)

    synced_at = data["compare"].get("synced_at", "")
    if synced_at:
        ctk.CTkLabel(
            parent,
            text=f"🕒 {tr('data_as_of')}: {synced_at}",
            font=("Arial", 13),
            text_color="#9ca3af"
        ).pack(pady=(0, 10))

    stats_frame = ctk.CTkFrame(parent, corner_radius=16)
    stats_frame.pack(padx=20, pady=10, fill="x")

    stats = [
        ("👥 HR", data["total_hr"], "#60a5fa", None),
        ("🏥 e-SEN", data["total_esen"], "#38bdf8", None),
        (f"🟢 {tr('matched')}", data["matched"], "#22c55e", None),
        (f"🔴 {tr('not_in_esen')}", data["only_hr"], "#ef4444", None),
        (f"🟡 {tr('extra')}", data["only_esen"], "#f59e0b", None),
        (f"⏰ {tr('expiring')}", data["expiring_count"], "#f97316", show_expiring_details),
        (f"⚠️ {tr('errors')}", data["bad_count"], "#dc2626",
         lambda: show_quality_details(data["quality"])),
        (f"🏢 {tr('departments')}", len(data["departments"]), "#a78bfa", None),
    ]

    build_stats_cards(stats_frame, stats)

    ctk.CTkButton(
        parent,
        text=f"📄 {tr('export_excel')}",
        width=330,
        height=42,
        command=export_missing_to_excel
    ).pack(pady=12)

    build_ai_analysis(parent, data)

    ctk.CTkLabel(
        parent,
        text=f"🏢 {tr('department_statistics')}",
        font=("Arial", 24, "bold")
    ).pack(pady=15)

    table_frame = ctk.CTkFrame(parent, corner_radius=16)
    table_frame.pack(padx=20, pady=10, fill="x")

    build_department_table(
        table_frame,
        data["departments"],
        data["dep_compare"],
        data["compare"]
    )


def build_dashboard_page(parent):
    build_dashboard_content(parent)


def dashboard_window():
    window = ctk.CTkToplevel()
    window.title("SanEpi AI Dashboard")
    window.geometry("1350x880")
    window.lift()
    window.focus_force()
    window.attributes("-topmost", True)
    window.after(1000, lambda: window.attributes("-topmost", False))
    build_dashboard_content(window)
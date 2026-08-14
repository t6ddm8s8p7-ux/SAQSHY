# -*- coding: utf-8 -*-
"""Синхронизация замеров HACCP с мобильного сайта (Supabase)."""
import os
import json
import sqlite3
import urllib.request
import urllib.error
from pathlib import Path

import customtkinter as ctk
from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "database" / "sanepi.db"

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")
SUPABASE_EMAIL = os.getenv("SUPABASE_EMAIL", "")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD", "")

_token_cache = {"token": ""}


def _login(log=print):
    """Вход в Supabase по email/паролю (как на сайте)."""
    log("🔐 Входим в Supabase под вашим аккаунтом...")
    req = urllib.request.Request(
        f"{SUPABASE_URL}/auth/v1/token?grant_type=password",
        data=json.dumps({"email": SUPABASE_EMAIL, "password": SUPABASE_PASSWORD}).encode("utf-8"),
        headers={"apikey": SUPABASE_KEY, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r).get("access_token", "")


def _get_token(log=print):
    if not _token_cache["token"]:
        if not (SUPABASE_EMAIL and SUPABASE_PASSWORD):
            raise RuntimeError(
                "В .env не указаны SUPABASE_EMAIL и SUPABASE_PASSWORD "
                "(почта и пароль от сайта HACCP)."
            )
        _token_cache["token"] = _login(log)
    return _token_cache["token"]


def _sb_get(table, query="", log=print):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{query}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {_get_token(log)}"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def _name_map(table, log=print):
    rows = _sb_get(table, "select=id,name", log)
    return {str(x["id"]): x["name"] for x in rows} if isinstance(rows, list) else {}


def sync_measurements(log=print):
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("В .env не указаны SUPABASE_URL и SUPABASE_KEY")
    log("⬇️ Читаем замеры с сайта...")
    records = _sb_get(
        "haccp_temperature_records",
        "select=*&order=measurement_date.desc,measurement_time.desc&limit=500",
        log,
    )
    if not isinstance(records, list):
        raise RuntimeError(f"Ответ Supabase: {records}")
    log(f"   получено записей: {len(records)}")

    log("📖 Читаем справочники (объекты/подразделения/оборудование)...")
    objects = _name_map("haccp_objects", log)
    departments = _name_map("haccp_departments", log)
    equipment = _name_map("haccp_equipment", log)

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    new = 0
    for r in records:
        rid = str(r.get("id") or "")
        if not rid:
            continue
        cur.execute("SELECT 1 FROM haccp_temperature_records WHERE id=?", (rid,))
        if cur.fetchone():
            continue  # уже есть — не дублируем
        eq_id = str(r.get("equipment_id") or "")
        cur.execute(
            """INSERT INTO haccp_temperature_records
            (id, object_name, department_name, equipment_id, equipment_name,
             date, time, temperature, temperature_min, temperature_max,
             status, responsible, corrective_action, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                rid,
                objects.get(str(r.get("object_id") or ""), ""),
                departments.get(str(r.get("department_id") or ""), ""),
                eq_id,
                equipment.get(eq_id, ""),
                r.get("measurement_date") or "",
                (r.get("measurement_time") or "")[:5],
                str(r.get("temperature") or ""),
                str(r.get("temperature_min") or ""),
                str(r.get("temperature_max") or ""),
                r.get("status") or "",
                r.get("responsible") or "",
                r.get("corrective_action") or "",
                r.get("created_at") or "",
            ),
        )
        new += 1
    conn.commit()
    conn.close()
    log(f"✅ Добавлено новых замеров: {new}")
    return new


def open_sync_window():
    win = ctk.CTkToplevel()
    win.title("🔄 Сайт HACCP — синхронизация")
    win.geometry("620x460")
    win.grab_set()
    ctk.CTkLabel(
        win,
        text="🔄 Синхронизация замеров с мобильного сайта",
        font=ctk.CTkFont(size=16, weight="bold"),
    ).pack(pady=(14, 4))
    ctk.CTkLabel(
        win,
        text="Забирает новые замеры поваров из Supabase в программу.",
        text_color="gray",
    ).pack()
    box = ctk.CTkTextbox(win)
    box.pack(fill="both", expand=True, padx=14, pady=(12, 14))

    def log(line):
        box.insert("end", line + "\n")
        box.see("end")
        win.update_idletasks()

    def run():
        box.configure(state="normal")
        box.delete("1.0", "end")
        try:
            n = sync_measurements(log)
            log(f"\n🎉 Готово! Новых замеров: {n}")
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read().decode("utf-8", errors="ignore")[:300]
            except Exception:
                pass
            log(f"\n❌ Ошибка HTTP {e.code}: {e.reason}")
            log(f"   {body}")
            if "Invalid login credentials" in body:
                log("\n💡 Неверная почта или пароль от сайта — проверьте .env")
        except Exception as e:
            log(f"\n❌ Ошибка: {e}")

    ctk.CTkButton(
        win,
        text="🔄 Забрать замеры с сайта",
        command=run,
        fg_color="#16A34A",
        hover_color="#15803D",
        height=40,
    ).pack(pady=(0, 14))
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ╔══════════════════════════════════════════════════════════════════════╗
# ║           🚀 SUPER BOT — Barcha funksiyalar bitta joyda 🚀          ║
# ║  🎬 Kino | 🎵 Musiqa | 💳 Donat | 📥 YouTube/IG | 🤖 AI | 📄 PDF   ║
# ╚══════════════════════════════════════════════════════════════════════╝

import logging
import sqlite3
import time
import os
import re
import threading
from datetime import datetime, timedelta
from typing import Optional

import telebot
from telebot import types
from telebot.types import (
    InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton
)

# yt-dlp va boshqa kutubxonalar mavjudligini tekshirish
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                        ⚙️ ASOSIY SOZLAMALAR                          ║
# ╚══════════════════════════════════════════════════════════════════════╝

BOT_TOKEN = "8945290924:AAGQS7G0-h4HGSjv9vIFaSvT571NfMvzZ4c"
ADMIN_IDS = [8383029735]
ADMIN_USERNAME = "@khidirov_garant"

# Majburiy obuna kanallar
REQUIRED_CHANNELS = [
    {"id": "@khidirov_garand1",           "name": "Khidirov Garant",          "url": "https://t.me/khidirov_garand1"},
    {"id": "@freefireakkauntsavdokhidirov","name": "Free Fire Akkaunt Savdo",  "url": "https://t.me/freefireakkauntsavdokhidirov"},
    {"id": "@khidirovotzif",               "name": "Khidirov Otziv",           "url": "https://t.me/khidirovotzif"},
]

# AI uchun Together.ai API (bepul tarif) - yoki Stability AI
# Agar yo'q bo'lsa placeholder rasm yuboriladi
TOGETHER_API_KEY = ""  # https://api.together.xyz dan oling (bepul)
STABILITY_API_KEY = ""  # https://stability.ai dan oling
ANTHROPIC_API_KEY = ""  # https://console.anthropic.com dan oling (AI chat uchun)

# 🎁 TELEGRAM GIFTLAR (Hadya sotib olish)
# Narxlar: 15 stars=5 TJS, 25 stars=8 TJS, 50 stars=13 TJS, 100 stars=25 TJS
GIFTLAR = [
    {"nomi": "💝 Sevgi Yuragi",    "stars": 15,  "narx_tjs": 5,  "emoji": "💝"},
    {"nomi": "🧸 Teddy Bear",      "stars": 15,  "narx_tjs": 5,  "emoji": "🧸"},
    {"nomi": "🎁 Sovg'a Qutisi",   "stars": 25,  "narx_tjs": 8,  "emoji": "🎁"},
    {"nomi": "🌹 Qizil Atirgul",   "stars": 25,  "narx_tjs": 8,  "emoji": "🌹"},
    {"nomi": "🎂 Tort",            "stars": 50,  "narx_tjs": 13, "emoji": "🎂"},
    {"nomi": "💐 Guldasta",        "stars": 50,  "narx_tjs": 13, "emoji": "💐"},
    {"nomi": "🚀 Raketa",          "stars": 50,  "narx_tjs": 13, "emoji": "🚀"},
    {"nomi": "🏆 Kubok",           "stars": 100, "narx_tjs": 25, "emoji": "🏆"},
    {"nomi": "💍 Uzuk",            "stars": 100, "narx_tjs": 25, "emoji": "💍"},
]

# To'lov kartalar
KARTALAR = [
    {"nomi": "💳 Visa",         "raqam": "4444 8888 1215 6721", "egasi": "Khidirov"},
    {"nomi": "🏦 Eskhata Bank", "raqam": "5058 2704 3064 6116", "egasi": "Eskhata"},
    {"nomi": "🏦 DC Bank",      "raqam": "+992 907 061 220",    "egasi": "DC Bank"},
    {"nomi": "📱 Alif Mobi",    "raqam": "+992 906 770 462",    "egasi": "Alif"},
]

# Donat narxlari
DONATLAR = {
    "ff_almaz": {
        "nomi": "🔥 Free Fire — Almazlar 💠",
        "oyun": "Free Fire",
        "variantlar": [
            {"miqdor": "25 Almaz 💠",   "narx": 5},
            {"miqdor": "105 Almaz 💠",  "narx": 11},
            {"miqdor": "330 Almaz 💠",  "narx": 33},
            {"miqdor": "550 Almaz 💠",  "narx": 55},
            {"miqdor": "1100 Almaz 💠", "narx": 110},
            {"miqdor": "2200 Almaz 💠", "narx": 220},
            {"miqdor": "6060 Almaz 💠", "narx": 600},
        ]
    },
    "ff_waucher": {
        "nomi": "🔥 Free Fire — Waucherlar 🎫",
        "oyun": "Free Fire",
        "variantlar": [
            {"miqdor": "Kunlik Waucher 🎟️",         "narx": 6},
            {"miqdor": "Haftalik Waucher 🎫",        "narx": 20},
            {"miqdor": "Oylik Waucher 🎫",           "narx": 111},
            {"miqdor": "Booyah Pass 🎫",             "narx": 33},
            {"miqdor": "Evo 3 kun 🕹️",              "narx": 6},
            {"miqdor": "Evo 7 kun 🕹️",              "narx": 10},
            {"miqdor": "Evo 30 kun 🕹️",             "narx": 20},
            {"miqdor": "800 Almaz bir marttalik 💠", "narx": 33},
        ]
    },
    "pubg_uc": {
        "nomi": "🎮 PUBG Mobile — UC 🎫",
        "oyun": "PUBG Mobile",
        "variantlar": [
            {"miqdor": "60 UC 🎫",                      "narx": 10},
            {"miqdor": "325 UC 🎫",                     "narx": 33},
            {"miqdor": "660 UC 🎫",                     "narx": 66},
            {"miqdor": "1800 UC 🎫",                    "narx": 150},
            {"miqdor": "Weekly Deal Pack 🎟️",           "narx": 11},
            {"miqdor": "PUBG Prime (1 oy) 🎟️",         "narx": 12},
            {"miqdor": "PUBG Prime (3 oy) 🎟️",         "narx": 20},
        ]
    },
    "roblox": {
        "nomi": "🧩 Roblox — Robux & Gift Card",
        "oyun": "Roblox",
        "variantlar": [
            {"miqdor": "200 Robux Gift Card (GLOBAL) 🧩", "narx": 55},
            {"miqdor": "400 Robux Gift Card (GLOBAL) 🧩", "narx": 111},
            {"miqdor": "800 Robux Gift Card (GLOBAL) 🧩", "narx": 666},
            {"miqdor": "Roblox 10 USD Gift Card 🌸",      "narx": 160},
            {"miqdor": "Roblox 25 USD Gift Card 🌸",      "narx": 333},
            {"miqdor": "Roblox 50 USD Gift Card 🌸",      "narx": 777},
        ]
    },
}

# Premium narxlari (TJS)
PREMIUM_NARXLAR = {
    "1_oy":  {"narx": 15,  "kun": 30,  "nomi": "1 Oy Premium"},
    "3_oy":  {"narx": 35,  "kun": 90,  "nomi": "3 Oy Premium"},
    "6_oy":  {"narx": 60,  "kun": 180, "nomi": "6 Oy Premium"},
    "1_yil": {"narx": 99,  "kun": 365, "nomi": "1 Yil Premium"},
}

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                        📊 LOG SOZLAMALARI                            ║
# ╚══════════════════════════════════════════════════════════════════════╝

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler("super_bot.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                        🤖 BOT YARATISH                               ║
# ╚══════════════════════════════════════════════════════════════════════╝

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    🗄️ MA'LUMOTLAR BAZASI                             ║
# ╚══════════════════════════════════════════════════════════════════════╝

DB_FILE = "super_bot.db"

def get_conn():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def create_database():
    conn = get_conn()
    c = conn.cursor()

    # Foydalanuvchilar
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            status TEXT DEFAULT 'free',
            premium_until TEXT,
            referral_code TEXT UNIQUE,
            referred_by INTEGER,
            referral_count INTEGER DEFAULT 0,
            bonus_points INTEGER DEFAULT 0,
            balance REAL DEFAULT 0.0,
            last_bonus_date TEXT,
            ai_image_used_at TEXT,
            ai_image_count INTEGER DEFAULT 0,
            spam_count INTEGER DEFAULT 0,
            last_spam_time REAL DEFAULT 0,
            registered_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Balans to'ldirish so'rovlari
    c.execute("""
        CREATE TABLE IF NOT EXISTS balance_requests (
            req_id TEXT PRIMARY KEY,
            user_id INTEGER,
            user_name TEXT,
            username TEXT,
            amount REAL,
            photo_id TEXT,
            status TEXT DEFAULT 'kutilmoqda',
            sana TEXT
        )
    """)

    # Kinolar
    c.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            file_id TEXT NOT NULL,
            file_type TEXT DEFAULT 'video',
            category TEXT DEFAULT 'Umumiy',
            is_premium INTEGER DEFAULT 0,
            views INTEGER DEFAULT 0,
            rating_sum INTEGER DEFAULT 0,
            rating_count INTEGER DEFAULT 0,
            added_by INTEGER,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Musiqalar
    c.execute("""
        CREATE TABLE IF NOT EXISTS musics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            artist TEXT,
            file_id TEXT NOT NULL,
            duration INTEGER DEFAULT 0,
            is_premium INTEGER DEFAULT 0,
            views INTEGER DEFAULT 0,
            added_by INTEGER,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Buyurtmalar (donat)
    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            user_id INTEGER,
            user_name TEXT,
            username TEXT,
            oyun TEXT,
            donat_tur TEXT,
            donat_miqdor TEXT,
            narx INTEGER,
            player_id TEXT,
            photo_id TEXT,
            status TEXT DEFAULT 'kutilmoqda',
            sana TEXT
        )
    """)

    # Reytinglar
    c.execute("""
        CREATE TABLE IF NOT EXISTS ratings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_code TEXT,
            item_type TEXT,
            rating INTEGER,
            UNIQUE(user_id, item_code, item_type)
        )
    """)

    # AI rasm loglari
    c.execute("""
        CREATE TABLE IF NOT EXISTS ai_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            prompt TEXT,
            status TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Eski DB ga yangi ustunlarni qo'shish (migration)
    try:
        c.execute("ALTER TABLE users ADD COLUMN balance REAL DEFAULT 0.0")
    except Exception:
        pass  # ustun allaqachon mavjud
    conn.commit()
    conn.close()
    logger.info("✅ Ma'lumotlar bazasi tayyor")

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    👤 FOYDALANUVCHI FUNKSIYALARI                      ║
# ╚══════════════════════════════════════════════════════════════════════╝

def get_user(user_id: int) -> Optional[dict]:
    conn = get_conn()
    row = conn.execute("SELECT * FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def register_user(user_id, username, full_name, referred_by=None):
    import random, string
    ref_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
    conn = get_conn()
    try:
        conn.execute(
            "INSERT OR IGNORE INTO users (user_id,username,full_name,referral_code,referred_by) VALUES (?,?,?,?,?)",
            (user_id, username, full_name, ref_code, referred_by)
        )
        if referred_by:
            conn.execute(
                "UPDATE users SET referral_count=referral_count+1, bonus_points=bonus_points+100 WHERE user_id=?",
                (referred_by,)
            )
        conn.commit()
    finally:
        conn.close()

ALLOWED_USER_COLUMNS = {
    "username", "full_name", "status", "premium_until", "referral_code",
    "referred_by", "referral_count", "bonus_points", "balance", "last_bonus_date",
    "ai_image_used_at", "ai_image_count", "spam_count", "last_spam_time"
}

def update_user(user_id, **kwargs):
    conn = get_conn()
    for k, v in kwargs.items():
        if k not in ALLOWED_USER_COLUMNS:
            logger.warning(f"update_user: noma'lum ustun '{k}' o'tkazib yuborildi")
            continue
        conn.execute(f"UPDATE users SET {k}=? WHERE user_id=?", (v, user_id))
    conn.commit()
    conn.close()

def is_premium(user_id: int) -> bool:
    user = get_user(user_id)
    if not user:
        return False
    if user["status"] in ("premium", "admin"):
        if user["status"] == "admin":
            return True
        if user["premium_until"]:
            try:
                until = datetime.strptime(user["premium_until"], "%Y-%m-%d")
                if until >= datetime.now():
                    return True
                else:
                    update_user(user_id, status="free")
            except Exception:
                pass
    return False

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

def get_all_users():
    conn = get_conn()
    rows = conn.execute("SELECT user_id FROM users").fetchall()
    conn.close()
    return [r[0] for r in rows]

def get_stats():
    conn = get_conn()
    total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    premium_count = conn.execute("SELECT COUNT(*) FROM users WHERE status='premium'").fetchone()[0]
    movies = conn.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
    musics = conn.execute("SELECT COUNT(*) FROM musics").fetchone()[0]
    orders = conn.execute("SELECT COUNT(*) FROM orders WHERE status='tasdiqlangan'").fetchone()[0]
    conn.close()
    return {"total": total, "premium": premium_count, "movies": movies,
            "musics": musics, "confirmed_orders": orders}

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    🎬 KINO FUNKSIYALARI                               ║
# ╚══════════════════════════════════════════════════════════════════════╝

def get_movie(code):
    conn = get_conn()
    row = conn.execute("SELECT * FROM movies WHERE code=?", (code.strip(),)).fetchone()
    conn.close()
    return dict(row) if row else None

def add_movie(code, title, description, file_id, file_type, category, is_prem, added_by):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO movies (code,title,description,file_id,file_type,category,is_premium,added_by) VALUES (?,?,?,?,?,?,?,?)",
            (code, title, description, file_id, file_type, category, is_prem, added_by)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_movie(code):
    conn = get_conn()
    c = conn.execute("DELETE FROM movies WHERE code=?", (code,))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0

def search_movies(q):
    conn = get_conn()
    rows = conn.execute(
        "SELECT code,title,category,is_premium FROM movies WHERE title LIKE ? OR description LIKE ? LIMIT 15",
        (f"%{q}%", f"%{q}%")
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_popular_movies(limit=10):
    conn = get_conn()
    rows = conn.execute("SELECT code,title,views,category,is_premium FROM movies ORDER BY views DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_latest_movies(limit=10):
    conn = get_conn()
    rows = conn.execute("SELECT code,title,added_at,category,is_premium FROM movies ORDER BY added_at DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_categories():
    conn = get_conn()
    rows = conn.execute("SELECT DISTINCT category, COUNT(*) as cnt FROM movies GROUP BY category").fetchall()
    conn.close()
    return [(r["category"], r["cnt"]) for r in rows]

def get_movies_by_category(category):
    conn = get_conn()
    rows = conn.execute("SELECT code,title,views,is_premium FROM movies WHERE category=?", (category,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def increment_movie_views(code):
    conn = get_conn()
    conn.execute("UPDATE movies SET views=views+1 WHERE code=?", (code,))
    conn.commit()
    conn.close()

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    🎵 MUSIQA FUNKSIYALARI                             ║
# ╚══════════════════════════════════════════════════════════════════════╝

def get_music(code):
    conn = get_conn()
    row = conn.execute("SELECT * FROM musics WHERE code=?", (code.strip(),)).fetchone()
    conn.close()
    return dict(row) if row else None

def add_music(code, title, artist, file_id, duration, is_prem, added_by):
    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO musics (code,title,artist,file_id,duration,is_premium,added_by) VALUES (?,?,?,?,?,?,?)",
            (code, title, artist, file_id, duration, is_prem, added_by)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def delete_music(code):
    conn = get_conn()
    c = conn.execute("DELETE FROM musics WHERE code=?", (code,))
    conn.commit()
    affected = c.rowcount
    conn.close()
    return affected > 0

def search_musics(q):
    conn = get_conn()
    rows = conn.execute(
        "SELECT code,title,artist,is_premium FROM musics WHERE title LIKE ? OR artist LIKE ? LIMIT 15",
        (f"%{q}%", f"%{q}%")
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_popular_musics(limit=10):
    conn = get_conn()
    rows = conn.execute("SELECT code,title,artist,views,is_premium FROM musics ORDER BY views DESC LIMIT ?", (limit,)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def increment_music_views(code):
    conn = get_conn()
    conn.execute("UPDATE musics SET views=views+1 WHERE code=?", (code,))
    conn.commit()
    conn.close()

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    💳 BUYURTMA FUNKSIYALARI                           ║
# ╚══════════════════════════════════════════════════════════════════════╝

_order_id_lock = threading.Lock()

def next_order_id():
    with _order_id_lock:
        conn = get_conn()
        row = conn.execute("SELECT order_id FROM orders ORDER BY CAST(order_id AS INTEGER) DESC LIMIT 1").fetchone()
        conn.close()
        if row:
            try:
                return str(int(row[0]) + 1)
            except Exception:
                pass
        return "1001"

def save_order(order: dict):
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO orders (order_id,user_id,user_name,username,oyun,donat_tur,donat_miqdor,narx,player_id,photo_id,status,sana) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
        (order["order_id"], order["user_id"], order["user_name"], order["username"],
         order["oyun"], order["donat_tur"], order["donat_miqdor"], order["narx"],
         order["player_id"], order["photo_id"], order["status"], order["sana"])
    )
    conn.commit()
    conn.close()

def get_order(order_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM orders WHERE order_id=?", (order_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_order_status(order_id, status):
    conn = get_conn()
    conn.execute("UPDATE orders SET status=? WHERE order_id=?", (status, order_id))
    conn.commit()
    conn.close()

def get_user_orders(user_id, limit=5):
    conn = get_conn()
    rows = conn.execute("SELECT * FROM orders WHERE user_id=? ORDER BY sana DESC LIMIT ?", (user_id, limit)).fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_pending_orders():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM orders WHERE status='kutilmoqda' ORDER BY sana DESC LIMIT 20").fetchall()
    conn.close()
    return [dict(r) for r in rows]

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    💰 BALANS FUNKSIYALARI                             ║
# ╚══════════════════════════════════════════════════════════════════════╝

_balance_req_lock = threading.Lock()

def next_balance_req_id():
    with _balance_req_lock:
        conn = get_conn()
        row = conn.execute("SELECT req_id FROM balance_requests ORDER BY CAST(req_id AS INTEGER) DESC LIMIT 1").fetchone()
        conn.close()
        if row:
            try:
                return str(int(row[0]) + 1)
            except Exception:
                pass
        return "2001"

def save_balance_request(req: dict):
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO balance_requests (req_id,user_id,user_name,username,amount,photo_id,status,sana) VALUES (?,?,?,?,?,?,?,?)",
        (req["req_id"], req["user_id"], req["user_name"], req["username"],
         req["amount"], req["photo_id"], req["status"], req["sana"])
    )
    conn.commit()
    conn.close()

def get_balance_request(req_id):
    conn = get_conn()
    row = conn.execute("SELECT * FROM balance_requests WHERE req_id=?", (req_id,)).fetchone()
    conn.close()
    return dict(row) if row else None

def update_balance_request_status(req_id, status):
    conn = get_conn()
    conn.execute("UPDATE balance_requests SET status=? WHERE req_id=?", (status, req_id))
    conn.commit()
    conn.close()

def get_user_balance(user_id):
    user = get_user(user_id)
    if not user:
        return 0.0
    return float(user.get("balance") or 0.0)

def add_user_balance(user_id, amount):
    cur = get_user_balance(user_id)
    update_user(user_id, balance=round(cur + amount, 2))

def deduct_user_balance(user_id, amount):
    cur = get_user_balance(user_id)
    new_bal = round(cur - amount, 2)
    if new_bal < 0:
        return False
    update_user(user_id, balance=new_bal)
    return True

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    🤖 AI RASM FUNKSIYALARI                            ║
# ╚══════════════════════════════════════════════════════════════════════╝

def can_generate_ai_image(user_id: int) -> tuple:
    """
    Premium: cheksiz
    Free: 2 soatda 1 ta rasm
    """
    if is_premium(user_id) or is_admin(user_id):
        return True, "premium"

    user = get_user(user_id)
    if not user:
        return False, "notfound"

    last_used = user.get("ai_image_used_at")
    if not last_used:
        return True, "ok"

    try:
        last_dt = datetime.strptime(last_used, "%Y-%m-%d %H:%M:%S")
        diff = datetime.now() - last_dt
        if diff.total_seconds() >= 7200:  # 2 soat = 7200 sekund
            return True, "ok"
        remaining = timedelta(seconds=7200) - diff
        mins = int(remaining.total_seconds() // 60)
        secs = int(remaining.total_seconds() % 60)
        return False, f"{mins} daqiqa {secs} sekund"
    except Exception:
        return True, "ok"

def _prompt_to_english(prompt: str) -> str:
    """O'zbek/rus promptlarni ingliz tiliga tarjima qilish (Pollinations text API orqali)."""
    uz_chars = set("qg'ʻo'O'G'")
    has_cyrillic = any('\u0400' <= c <= '\u04FF' for c in prompt)
    has_uzbek = any(c in uz_chars for c in prompt) or any(
        w in prompt.lower() for w in ["burger", "kfc", "pizza", "car", "cat", "dog", "man", "woman"]
    )
    # Agar allaqachon inglizcha so'zlar ko'p bo'lsa — tarjima shart emas
    latin_ratio = sum(1 for c in prompt if c.isalpha() and ord(c) < 128) / max(len(prompt), 1)
    if not has_cyrillic and latin_ratio > 0.7:
        return prompt  # Inglizcha allaqachon

    try:
        import urllib.parse
        trans_prompt = f"Translate this image prompt to English, return ONLY the translated prompt, nothing else: {prompt}"
        enc = urllib.parse.quote(trans_prompt, safe='')
        resp = requests.get(
            f"https://text.pollinations.ai/{enc}?model=openai&seed=42",
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        if resp.status_code == 200:
            translated = resp.text.strip().strip('"').strip("'")
            bad = ["sorry", "error", "cannot", "<!doctype", "<html"]
            if translated and len(translated) > 3 and not any(b in translated.lower() for b in bad):
                logger.info(f"Prompt tarjima: '{prompt}' → '{translated}'")
                return translated
    except Exception as e:
        logger.error(f"Prompt tarjima xatosi: {e}")
    return prompt


def generate_ai_image(prompt: str, user_id: int) -> Optional[bytes]:
    """AI rasm generatsiya qilish — prompt bo'yicha to'g'ri rasm."""
    if not REQUESTS_AVAILABLE:
        return None

    import urllib.parse, random

    # Promptni ingliz tiliga o'girish (agar kerak bo'lsa)
    eng_prompt = _prompt_to_english(prompt)
    # Sifatni oshirish uchun qo'shimcha kalit so'zlar
    enhanced = f"{eng_prompt}, high quality, detailed, sharp focus, professional photography"

    # ── 1. Together.ai FLUX (agar key mavjud) ────────────────────────────
    if TOGETHER_API_KEY:
        try:
            resp = requests.post(
                "https://api.together.xyz/v1/images/generations",
                headers={"Authorization": f"Bearer {TOGETHER_API_KEY}",
                         "Content-Type": "application/json"},
                json={
                    "model": "black-forest-labs/FLUX.1-schnell-Free",
                    "prompt": enhanced,
                    "width": 1024, "height": 1024, "n": 1,
                    "steps": 4,
                },
                timeout=90
            )
            if resp.status_code == 200:
                img_url = resp.json()["data"][0].get("url")
                if img_url:
                    r2 = requests.get(img_url, timeout=30)
                    if r2.status_code == 200 and len(r2.content) > 10000:
                        return r2.content
        except Exception as e:
            logger.error(f"Together.ai xatosi: {e}")

    # ── 2. Stability AI ───────────────────────────────────────────────────
    if STABILITY_API_KEY:
        try:
            resp = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={"Authorization": f"Bearer {STABILITY_API_KEY}",
                         "Content-Type": "application/json"},
                json={
                    "text_prompts": [{"text": enhanced, "weight": 1}],
                    "cfg_scale": 7, "width": 1024, "height": 1024, "samples": 1,
                },
                timeout=60
            )
            if resp.status_code == 200:
                import base64
                return base64.b64decode(resp.json()["artifacts"][0]["base64"])
        except Exception as e:
            logger.error(f"Stability AI xatosi: {e}")

    # ── 3. Pollinations.ai — asosiy bepul usul ───────────────────────────
    # MUHIM: eng_prompt ishlatiladi, tasodifiy seed EMAS — har xil modellar sinab ko'riladi
    clean = eng_prompt.strip().replace("\n", " ")
    encoded = urllib.parse.quote(clean, safe='')

    # Har bir model uchun bir xil seed (promptga bog'liq) — izchillik uchun
    base_seed = abs(hash(clean)) % 999983

    models_cfg = [
        ("flux",         base_seed),
        ("flux-realism", base_seed + 1),
        ("flux",         base_seed + 7),   # ikkinchi urinish boshqa seed bilan
        ("turbo",        base_seed + 3),
    ]

    for model, seed in models_cfg:
        url_p = (
            f"https://image.pollinations.ai/prompt/{encoded}"
            f"?model={model}&seed={seed}"
            f"&width=1024&height=1024&nologo=true&enhance=true&safe=false"
        )
        try:
            hdrs = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "image/webp,image/*,*/*",
                "Referer": "https://pollinations.ai/",
                "Cache-Control": "no-cache",
            }
            resp = requests.get(url_p, timeout=120, allow_redirects=True, headers=hdrs)
            logger.info(f"Pollinations {model} seed={seed}: status={resp.status_code}, size={len(resp.content)}, ct={resp.headers.get('content-type','')}")
            if resp.status_code == 200:
                content = resp.content
                ct = resp.headers.get("content-type", "")
                is_png = content[:4] == b'\x89PNG'
                is_jpg = content[:2] == b'\xff\xd8'
                is_webp = content[:4] == b'RIFF'
                is_img_ct = "image" in ct and "html" not in ct
                if (is_png or is_jpg or is_webp or is_img_ct) and len(content) > 20000:
                    logger.info(f"✅ Pollinations {model} muvaffaqiyatli: {len(content)} bayt")
                    return content
                else:
                    logger.warning(f"Pollinations {model}: rasm yetarli emas ({len(content)} bayt, ct={ct})")
            time.sleep(1)
        except Exception as e:
            logger.error(f"Pollinations {model} xatosi: {e}")
            time.sleep(2)

    # ── 4. Hugging Face Inference API (bepul, ro'yxatsiz) ─────────────────
    try:
        hf_url = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        hf_resp = requests.post(
            hf_url,
            headers={"Content-Type": "application/json"},
            json={"inputs": eng_prompt, "parameters": {"num_inference_steps": 20}},
            timeout=90
        )
        if hf_resp.status_code == 200:
            ct = hf_resp.headers.get("content-type", "")
            content = hf_resp.content
            if "image" in ct and len(content) > 20000:
                logger.info(f"✅ HuggingFace muvaffaqiyatli: {len(content)} bayt")
                return content
    except Exception as e:
        logger.error(f"HuggingFace xatosi: {e}")

    logger.error(f"Barcha AI rasm usullari muvaffaqiyatsiz: '{prompt}'")
    return None

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    🤖 AI CHAT (CLAUDE)                                ║
# ╚══════════════════════════════════════════════════════════════════════╝

def ask_claude_ai(user_message: str) -> str:
    """AI orqali savollarga javob berish — bir nechta bepul API."""
    if not REQUESTS_AVAILABLE:
        return "❌ Requests kutubxonasi yo'q."

    system_msg = "Sen foydali AI yordamchisan. Foydalanuvchi qaysi tilda yozsa shu tilda (o'zbek, rus yoki ingliz) qisqa va aniq javob ber. Maksimum 300 so'z."

    # ── 1. Anthropic API (agar key mavjud bo'lsa) ──────────────────────────
    if ANTHROPIC_API_KEY:
        try:
            resp = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-haiku-4-5-20251001",
                    "max_tokens": 1024,
                    "system": system_msg,
                    "messages": [{"role": "user", "content": user_message}]
                },
                timeout=30
            )
            if resp.status_code == 200:
                return resp.json()["content"][0]["text"]
        except Exception as e:
            logger.error(f"Claude AI xatosi: {e}")

    # ── 2. Groq API — Tez va bepul (https://console.groq.com dan bepul key oling) ──
    GROQ_API_KEY = ""  # https://console.groq.com dan bepul oling
    if GROQ_API_KEY:
        try:
            resp = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama-3.1-8b-instant",
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_message[:3000]}
                    ],
                    "max_tokens": 800,
                    "temperature": 0.7,
                },
                timeout=20
            )
            if resp.status_code == 200:
                content = resp.json()["choices"][0]["message"]["content"].strip()
                if content and len(content) > 5:
                    return content
        except Exception as e:
            logger.error(f"Groq API xatosi: {e}")

    # ── 3. OpenRouter — bepul modellar ────────────────────────────────────
    openrouter_models = [
        "google/gemma-3-12b-it:free",
        "meta-llama/llama-3.3-8b-instruct:free",
        "mistralai/mistral-7b-instruct:free",
        "microsoft/phi-3-mini-128k-instruct:free",
        "meta-llama/llama-3.2-3b-instruct:free",
    ]
    for model in openrouter_models:
        try:
            resp = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://t.me/khidirov_garant",
                    "X-Title": "Khidirov Bot",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_msg},
                        {"role": "user", "content": user_message[:2000]}
                    ],
                    "max_tokens": 600,
                    "temperature": 0.7,
                },
                timeout=20
            )
            if resp.status_code == 200:
                data = resp.json()
                choices = data.get("choices", [])
                if choices:
                    content = choices[0].get("message", {}).get("content", "").strip()
                    if content and len(content) > 5:
                        # Xato javoblarni filter qilish
                        bad = ["error", "unavailable", "rate limit", "sorry", "i cannot", "i'm unable"]
                        if not any(b in content.lower()[:100] for b in bad):
                            if len(content) > 3000:
                                content = content[:3000] + "...\n_(Javob qisqartirildi)_"
                            return content
            elif resp.status_code == 429:
                time.sleep(1)
                continue
        except Exception as e:
            logger.error(f"OpenRouter {model}: {e}")
            continue

    # ── 4. Pollinations.ai text (fallback) ───────────────────────────────
    import urllib.parse
    try:
        combined = f"{system_msg}\n\nFoydalanuvchi savoli: {user_message[:500]}\n\nJavob:"
        msg_enc = urllib.parse.quote(combined, safe='')
        req_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/plain, */*",
        }
        for model in ["openai", "openai-large", "mistral"]:
            try:
                seed = hash(user_message) % 99999
                url_p = f"https://text.pollinations.ai/{msg_enc}?model={model}&seed={seed}&json=false"
                resp = requests.get(url_p, timeout=40, headers=req_headers)
                if resp.status_code == 200:
                    answer = resp.text.strip()
                    bad_words = ["error", "unavailable", "403", "429", "500", "<!doctype", "<html", "too many", "rate limit"]
                    if answer and len(answer) > 15 and not any(b in answer.lower() for b in bad_words):
                        if len(answer) > 3000:
                            answer = answer[:3000] + "...\n_(Javob qisqartirildi)_"
                        return answer
            except Exception as e:
                logger.error(f"Pollinations {model}: {e}")
                time.sleep(1)
                continue
    except Exception as e:
        logger.error(f"Pollinations fallback: {e}")

    # ── 5. DuckDuckGo AI Chat (oxirgi fallback) ──────────────────────────
    try:
        # DuckDuckGo AI Chat token olish
        session = requests.Session()
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "*/*",
        })
        vqd_resp = session.get("https://duckduckgo.com/duckchat/v1/status", headers={"x-vqd-accept": "1"}, timeout=10)
        vqd = vqd_resp.headers.get("x-vqd-4", "")
        if vqd:
            chat_resp = session.post(
                "https://duckduckgo.com/duckchat/v1/chat",
                headers={
                    "Content-Type": "application/json",
                    "x-vqd-4": vqd,
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [{"role": "user", "content": f"{system_msg}\n\n{user_message[:1500]}"}]
                },
                timeout=30
            )
            if chat_resp.status_code == 200:
                # SSE javobini parse qilish
                full_text = ""
                for line in chat_resp.text.split('\n'):
                    if line.startswith('data: ') and line != 'data: [DONE]':
                        try:
                            chunk = __import__('json').loads(line[6:])
                            msg_chunk = chunk.get("message", "")
                            if msg_chunk:
                                full_text += msg_chunk
                        except Exception:
                            pass
                if full_text and len(full_text) > 10:
                    return full_text
    except Exception as e:
        logger.error(f"DuckDuckGo AI xatosi: {e}")

    return "❌ AI hozir vaqtincha band. Iltimos, 1-2 daqiqadan keyin qayta urinib ko'ring."

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    📄 PDF / FAYL YARATISH                             ║
# ╚══════════════════════════════════════════════════════════════════════╝

def create_pdf_from_text(text: str, style: str = "standart", filename: str = "hujjat.pdf") -> Optional[str]:
    """Matndan PDF yaratish — turli stillar bilan."""
    filepath = f"/tmp/{filename}"

    if REPORTLAB_AVAILABLE:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas as rl_canvas
            from reportlab.lib import colors

            c = rl_canvas.Canvas(filepath, pagesize=A4)
            width, height = A4
            margin = 50

            # ── Stil sozlamalari ──────────────────────────────────────────
            if style == "qiyshiq":
                # Italic uslub: matn biroz o'ngga siljigan, italic font
                font_name = "Helvetica-Oblique"
                font_size = 12
                line_height = 18
                text_color = colors.HexColor("#2c3e50")
                bg_color = colors.HexColor("#fdfcfb")
                title_font = "Helvetica-BoldOblique"
                title_size = 16
                margin_left = 70
                margin_right = 50

            elif style == "chunmaydigan":
                # Katta, qalin shrift — oson o'qiladi
                font_name = "Helvetica-Bold"
                font_size = 14
                line_height = 22
                text_color = colors.HexColor("#1a1a2e")
                bg_color = colors.HexColor("#e8f4f8")
                title_font = "Helvetica-Bold"
                title_size = 20
                margin_left = 60
                margin_right = 60

            elif style == "classic":
                # Klassik qora-oq, Times uslubi
                font_name = "Times-Roman"
                font_size = 12
                line_height = 17
                text_color = colors.black
                bg_color = colors.white
                title_font = "Times-Bold"
                title_size = 18
                margin_left = 72
                margin_right = 72

            elif style == "pro":
                # Professional: qoʻshimcha ramka, zamonaviy ko'rinish
                font_name = "Helvetica"
                font_size = 11
                line_height = 16
                text_color = colors.HexColor("#222222")
                bg_color = colors.HexColor("#f9f9f9")
                title_font = "Helvetica-Bold"
                title_size = 15
                margin_left = 55
                margin_right = 55

            else:
                # Standart
                font_name = "Helvetica"
                font_size = 12
                line_height = 16
                text_color = colors.black
                bg_color = colors.white
                title_font = "Helvetica-Bold"
                title_size = 14
                margin_left = 50
                margin_right = 50

            def draw_page_bg():
                if bg_color != colors.white:
                    c.setFillColor(bg_color)
                    c.rect(0, 0, width, height, fill=1, stroke=0)
                if style == "pro":
                    c.setStrokeColor(colors.HexColor("#3498db"))
                    c.setLineWidth(3)
                    c.rect(20, 20, width - 40, height - 40, fill=0, stroke=1)

            draw_page_bg()

            # Sahifa raqami va sana
            from datetime import datetime as _dt
            date_str = _dt.now().strftime("%d.%m.%Y")
            c.setFillColor(colors.grey)
            c.setFont("Helvetica", 8)
            c.drawString(margin_left, 30, f"Sana: {date_str}")
            c.drawRightString(width - margin_right, 30, "Khidirov Bot tomonidan yaratildi")

            # Sarlavha — birinchi satr yoki "Hujjat"
            lines_all = text.split("\n")
            y = height - margin - 10
            c.setFillColor(colors.HexColor("#2980b9") if style == "pro" else text_color)
            c.setFont(title_font, title_size)
            c.drawString(margin_left, y, "📄 Hujjat")
            y -= title_size + 10

            # Ajratuvchi chiziq
            c.setStrokeColor(colors.HexColor("#3498db") if style == "pro" else colors.grey)
            c.setLineWidth(1)
            c.line(margin_left, y, width - margin_right, y)
            y -= 12

            c.setFont(font_name, font_size)
            c.setFillColor(text_color)

            usable_width = width - margin_left - margin_right

            for paragraph in lines_all:
                if not paragraph.strip():
                    y -= line_height // 2
                    if y < 60:
                        c.showPage()
                        draw_page_bg()
                        c.setFont(font_name, font_size)
                        c.setFillColor(text_color)
                        y = height - margin - 10
                    continue
                words = paragraph.split()
                line = ""
                for word in words:
                    test_line = line + word + " "
                    if c.stringWidth(test_line, font_name, font_size) > usable_width:
                        if line:
                            c.drawString(margin_left, y, line.strip())
                            y -= line_height
                            if y < 60:
                                c.showPage()
                                draw_page_bg()
                                c.setFont(font_name, font_size)
                                c.setFillColor(text_color)
                                y = height - margin - 10
                        line = word + " "
                    else:
                        line = test_line
                if line:
                    c.drawString(margin_left, y, line.strip())
                    y -= line_height
                y -= 4
                if y < 60:
                    c.showPage()
                    draw_page_bg()
                    c.setFont(font_name, font_size)
                    c.setFillColor(text_color)
                    y = height - margin - 10

            c.save()
            return filepath
        except Exception as e:
            logger.error(f"ReportLab PDF xatosi: {e}")

    # Fallback: oddiy txt fayl
    try:
        txt_path = filepath.replace(".pdf", ".txt")
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        return txt_path
    except Exception as e:
        logger.error(f"TXT fallback xatosi: {e}")
    return None

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    📥 VIDEO YUKLAB OLISH (YT/IG)                      ║
# ╚══════════════════════════════════════════════════════════════════════╝

def download_video(url: str, user_id: int, is_audio=False) -> Optional[str]:
    """Instagram video/audio yuklab olish — ko'p usul bilan."""
    url = url.strip()
    url = re.sub(r'(https?://(?:www\.)?instagram\.com/(?:reel|p|tv)/[\w-]+)/.*', r'\1/', url)
    url = url.rstrip('/')

    ext = "mp3" if is_audio else "mp4"
    output_path = f"/tmp/video_{user_id}_{int(time.time())}.{ext}"

    # ── 1. yt-dlp bilan urinish (cookie fayl bo'lsa ishlatiladi) ──────────
    if YT_DLP_AVAILABLE:
        ydl_opts = {
            "outtmpl": output_path,
            "quiet": True,
            "no_warnings": True,
            "max_filesize": 50 * 1024 * 1024,
            "socket_timeout": 60,
            "retries": 3,
            "nocheckcertificate": True,
            "extractor_retries": 3,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
            },
        }

        # Cookie fayl mavjud bo'lsa qo'shamiz
        cookie_file = "instagram_cookies.txt"
        if os.path.exists(cookie_file):
            ydl_opts["cookiefile"] = cookie_file

        if is_audio:
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            })
        else:
            ydl_opts["format"] = "best[filesize<50M]/bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            if os.path.exists(output_path):
                return output_path
            base = output_path.rsplit(".", 1)[0]
            for try_ext in [".mp4", ".mkv", ".webm", ".avi", ".mp3", ".m4a", ".opus"]:
                candidate = base + try_ext
                if os.path.exists(candidate):
                    return candidate
        except Exception as e:
            logger.error(f"yt-dlp Instagram xatosi: {e}")

    # ── 2. Savefrom.net API orqali urinish ────────────────────────────────
    if REQUESTS_AVAILABLE:
        try:
            api_url = f"https://api.savefrom.net/api/convert?url={url}&lang=en"
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json",
                "Referer": "https://savefrom.net/",
            }
            resp = requests.get(api_url, headers=headers, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                video_url = None
                if isinstance(data, dict):
                    links = data.get("url", [])
                    if isinstance(links, list) and links:
                        for lnk in links:
                            if isinstance(lnk, dict) and lnk.get("url"):
                                video_url = lnk["url"]
                                break
                    elif isinstance(links, str):
                        video_url = links
                if video_url:
                    r2 = requests.get(video_url, timeout=60, stream=True)
                    if r2.status_code == 200:
                        with open(output_path, "wb") as f:
                            for chunk in r2.iter_content(chunk_size=8192):
                                f.write(chunk)
                        if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
                            return output_path
        except Exception as e:
            logger.error(f"Savefrom API xatosi: {e}")

    # ── 3. Instasave.io API orqali urinish ───────────────────────────────
    if REQUESTS_AVAILABLE:
        try:
            api_headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Content-Type": "application/x-www-form-urlencoded",
                "Referer": "https://instasave.website/",
                "Origin": "https://instasave.website",
            }
            resp = requests.post(
                "https://instasave.website/api",
                data={"url": url},
                headers=api_headers,
                timeout=30,
            )
            if resp.status_code == 200:
                data = resp.json()
                media_list = data.get("data", [])
                if isinstance(media_list, list) and media_list:
                    video_url = None
                    for item in media_list:
                        if isinstance(item, dict) and item.get("url"):
                            video_url = item["url"]
                            break
                    if video_url:
                        r2 = requests.get(video_url, timeout=60, stream=True, headers={
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        })
                        if r2.status_code == 200:
                            with open(output_path, "wb") as f:
                                for chunk in r2.iter_content(chunk_size=8192):
                                    f.write(chunk)
                            if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
                                return output_path
        except Exception as e:
            logger.error(f"Instasave API xatosi: {e}")

    # ── 4. Reelsaver API ─────────────────────────────────────────────────
    if REQUESTS_AVAILABLE:
        try:
            import urllib.parse
            api_headers = {
                "User-Agent": "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36",
                "Accept": "application/json, text/plain, */*",
                "Referer": "https://reelsaver.net/",
                "Origin": "https://reelsaver.net",
            }
            resp = requests.post(
                "https://reelsaver.net/api/fetch",
                json={"url": url},
                headers=api_headers,
                timeout=30,
            )
            if resp.status_code == 200:
                data = resp.json()
                video_url = (
                    data.get("video_url")
                    or data.get("url")
                    or (data.get("medias", [{}])[0].get("url") if data.get("medias") else None)
                )
                if video_url:
                    r2 = requests.get(video_url, timeout=60, stream=True)
                    if r2.status_code == 200:
                        with open(output_path, "wb") as f:
                            for chunk in r2.iter_content(chunk_size=8192):
                                f.write(chunk)
                        if os.path.exists(output_path) and os.path.getsize(output_path) > 10000:
                            return output_path
        except Exception as e:
            logger.error(f"Reelsaver API xatosi: {e}")

    logger.error(f"Barcha usullar muvaffaqiyatsiz: {url}")
    return None


def get_video_info(url: str) -> Optional[dict]:
    """Instagram video haqida ma'lumot olish — yt-dlp yoki to'g'ridan URL tekshirish."""
    url = url.strip()
    url = re.sub(r'(https?://(?:www\.)?instagram\.com/(?:reel|p|tv)/[\w-]+)/.*', r'\1/', url)
    url = url.rstrip('/')

    # ── 1. yt-dlp bilan urinish ───────────────────────────────────────────
    if YT_DLP_AVAILABLE:
        try:
            ydl_opts = {
                "quiet": True,
                "no_warnings": True,
                "skip_download": True,
                "format": "best",
                "socket_timeout": 20,
                "nocheckcertificate": True,
                "extractor_retries": 2,
                "http_headers": {
                    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
                    "Accept-Language": "en-US,en;q=0.9",
                },
            }
            cookie_file = "instagram_cookies.txt"
            if os.path.exists(cookie_file):
                ydl_opts["cookiefile"] = cookie_file

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info:
                    if info.get("_type") == "playlist" and info.get("entries"):
                        info = info["entries"][0]
                    return {
                        "title": info.get("title", "Instagram Video"),
                        "duration": info.get("duration", 0),
                        "uploader": info.get("uploader") or info.get("channel", "Instagram"),
                        "thumbnail": info.get("thumbnail"),
                        "url": url,
                    }
        except Exception as e:
            logger.error(f"yt-dlp info xatosi: {e}")

    # ── 2. Agar yt-dlp ishlamasa — URL mavjudligini tekshirib info qaytarish
    # (foydalanuvchi uchun "yuklab olish" tugmasi ko'rinadi, yuklab olish vaqtida API ishlatiladi)
    if REQUESTS_AVAILABLE:
        try:
            resp = requests.head(url, timeout=10, allow_redirects=True, headers={
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15",
            })
            if resp.status_code in (200, 302, 301):
                # URL mavjud — asosiy info qaytaramiz
                shortcode = url.rstrip('/').split('/')[-1]
                return {
                    "title": f"Instagram Video ({shortcode})",
                    "duration": 0,
                    "uploader": "Instagram",
                    "thumbnail": None,
                    "url": url,
                }
        except Exception as e:
            logger.error(f"URL tekshirishda xato: {e}")

    return None

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    🔔 OBUNA TEKSHIRISH                                ║
# ╚══════════════════════════════════════════════════════════════════════╝

def check_subscription(user_id: int):
    not_sub = []
    for ch in REQUIRED_CHANNELS:
        try:
            member = bot.get_chat_member(ch["id"], user_id)
            if member.status in ("left", "kicked"):
                not_sub.append(ch)
        except Exception:
            not_sub.append(ch)
    return len(not_sub) == 0, not_sub

def check_spam(user_id: int) -> bool:
    conn = get_conn()
    row = conn.execute("SELECT spam_count, last_spam_time FROM users WHERE user_id=?", (user_id,)).fetchone()
    conn.close()
    if not row:
        return False
    spam_count, last_spam_time = row["spam_count"], row["last_spam_time"]
    now = time.time()
    # 60 soniyadan o'tgan bo'lsa — hisobni noldan boshlaymiz
    if now - (last_spam_time or 0) > 60:
        update_user(user_id, spam_count=1, last_spam_time=now)
        return False
    # Limit: 60 soniyada 15 ta xabar
    if spam_count >= 15:
        return True
    update_user(user_id, spam_count=spam_count + 1, last_spam_time=now)
    return False

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    🎹 HOLAT BOSHQARISH (STATE)                        ║
# ╚══════════════════════════════════════════════════════════════════════╝

user_states = {}

def set_state(user_id, state, data=None):
    user_states[user_id] = {"state": state, "data": data or {}}

def get_state(user_id):
    return user_states.get(user_id, {})

def clear_state(user_id):
    user_states.pop(user_id, None)

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    ⌨️ KLAVIATURA FUNKSIYALARI                         ║
# ╚══════════════════════════════════════════════════════════════════════╝

def main_keyboard(user_id: int) -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        KeyboardButton("🎬 Kinolar"),
        KeyboardButton("🎵 Musiqa")
    )
    kb.add(
        KeyboardButton("💳 Donat"),
        KeyboardButton("📥 Video Yuklab Olish")
    )
    kb.add(
        KeyboardButton("🤖 AI Rasm Yasash"),
        KeyboardButton("💬 AI Chat")
    )
    kb.add(
        KeyboardButton("📄 Matndan PDF/Fayl"),
        KeyboardButton("🎁 Giftlar")
    )
    kb.add(
        KeyboardButton("👤 Profilim"),
        KeyboardButton("💎 Premium")
    )
    kb.add(
        KeyboardButton("🎁 Kunlik Bonus"),
        KeyboardButton("🧮 Kalkulyator")
    )
    kb.add(KeyboardButton("💰 Balans To'ldirish"))
    if is_admin(user_id):
        kb.add(KeyboardButton("⚙️ Admin Panel"))
    return kb

def movie_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        KeyboardButton("🔍 Kino Qidirish"),
        KeyboardButton("⭐ Mashhur Kinolar")
    )
    kb.add(
        KeyboardButton("🆕 Yangi Kinolar"),
        KeyboardButton("📂 Kategoriyalar")
    )
    kb.add(KeyboardButton("🔙 Bosh Menyu"))
    return kb

def music_keyboard() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        KeyboardButton("🔍 Musiqa Qidirish"),
        KeyboardButton("🔥 Mashhur Musiqalar")
    )
    kb.add(KeyboardButton("🔙 Bosh Menyu"))
    return kb

def get_sub_keyboard(channels):
    kb = InlineKeyboardMarkup(row_width=1)
    for ch in channels:
        kb.add(InlineKeyboardButton(f"📢 {ch['name']}", url=ch["url"]))
    kb.add(InlineKeyboardButton("✅ Tekshirish", callback_data="check_sub"))
    return kb

def rating_keyboard(code, item_type="movie"):
    kb = InlineKeyboardMarkup(row_width=5)
    kb.add(*[InlineKeyboardButton("⭐" * i, callback_data=f"rate_{item_type}_{code}_{i}") for i in range(1, 6)])
    return kb

def donat_oyun_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton("🔥 Free Fire — Almazlar",   callback_data="donat_ff_almaz"))
    kb.add(InlineKeyboardButton("🔥 Free Fire — Waucherlar", callback_data="donat_ff_waucher"))
    kb.add(InlineKeyboardButton("🎮 PUBG Mobile — UC",        callback_data="donat_pubg_uc"))
    kb.add(InlineKeyboardButton("🧩 Roblox",                  callback_data="donat_roblox"))
    kb.add(InlineKeyboardButton("🏠 Bosh menyuga",            callback_data="back_main"))
    return kb

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    🚀 START HANDLER                                   ║
# ╚══════════════════════════════════════════════════════════════════════╝

@bot.message_handler(commands=["start"])
def start_handler(message):
    user_id = message.from_user.id
    username = message.from_user.username or ""
    full_name = message.from_user.full_name or "Mehmon"

    # /start bosilganda har doim state tozalansin
    clear_state(user_id)

    # Referal tekshirish
    referred_by = None
    parts = message.text.split()
    if len(parts) > 1 and parts[1].startswith("ref_"):
        try:
            rb = int(parts[1].replace("ref_", ""))
            if rb != user_id:
                referred_by = rb
        except ValueError:
            pass

    user = get_user(user_id)
    if not user:
        register_user(user_id, username, full_name, referred_by)
        if referred_by:
            try:
                bot.send_message(
                    referred_by,
                    f"🎉 <b>Yangi referal!</b>\n👤 {full_name} siz orqali ro'yxatdan o'tdi!\n💰 +100 ball qo'shildi!"
                )
            except Exception:
                pass

    # Obuna tekshirish
    if REQUIRED_CHANNELS:
        is_sub, not_sub = check_subscription(user_id)
        if not is_sub:
            bot.send_message(
                user_id,
                f"👋 Salom, <b>{full_name}</b>!\n\n"
                "⚠️ Botdan foydalanish uchun kanallarga obuna bo'ling:\n\n"
                + "\n".join(f"➡️ {ch['name']}" for ch in not_sub) +
                "\n\n✅ Obuna bo'lgach <b>Tekshirish</b> tugmasini bosing.",
                reply_markup=get_sub_keyboard(not_sub)
            )
            return

    user = get_user(user_id)
    prem = is_premium(user_id)
    status_emoji = "💎" if prem else "👑" if is_admin(user_id) else "👤"
    status_name = "Premium" if prem else "Admin" if is_admin(user_id) else "Free"

    welcome = (
        f"🚀 <b>SUPER BOT</b> — Hamma narsa bitta joyda!\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👋 Xush kelibsiz, <b>{full_name}</b>!\n"
        f"{status_emoji} Status: <b>{status_name}</b>\n\n"
        f"🎬 <b>Kinolar</b> — kod orqali kino oling\n"
        f"🎵 <b>Musiqa</b> — musiqa tinglang\n"
        f"💳 <b>Donat</b> — o'yinlarga donat xizmati\n"
        f"📥 <b>Video Yuklab Olish</b> — Instagram\n"
        f"🤖 <b>AI Rasm</b> — prompt orqali rasm oling\n"
        f"📄 <b>PDF/Fayl</b> — matndan hujjat yarating\n\n"
        f"💎 Free: <i>ba'zi funksiyalar cheklangan</i>\n"
        f"👑 Premium: <i>hamma narsa cheksiz!</i>"
    )
    bot.send_message(user_id, welcome, reply_markup=main_keyboard(user_id))

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    🎬 KINO HANDLERLARI                                ║
# ╚══════════════════════════════════════════════════════════════════════╝

def send_movie_to_user(chat_id, movie, user_id):
    prem = is_premium(user_id)
    if movie["is_premium"] and not prem and not is_admin(user_id):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("💎 Premium Olish", callback_data="premium_info"))
        bot.send_message(
            chat_id,
            "💎 <b>Bu kino faqat Premium foydalanuvchilar uchun!</b>\n\n"
            "Premium olib, barcha imkoniyatlardan foydalaning! 🚀",
            reply_markup=kb
        )
        return

    rating = 0
    if movie.get("rating_count", 0) > 0:
        rating = movie["rating_sum"] / movie["rating_count"]

    stars = "⭐" * round(rating) if rating > 0 else "Baholanmagan"
    prem_badge = "💎 PREMIUM" if movie["is_premium"] else "🆓 Bepul"

    caption = (
        f"🎬 <b>{movie['title']}</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n"
        f"📝 {movie.get('description') or 'Tavsif yoq'}\n"
        f"📂 Kategoriya: {movie['category']}\n"
        f"🔢 Kod: <code>{movie['code']}</code>\n"
        f"👁 Ko'rishlar: {movie['views']}\n"
        f"⭐ Reyting: {stars} ({rating:.1f}/5)\n"
        f"🏷 {prem_badge}"
    )

    kb = rating_keyboard(movie["code"], "movie")
    try:
        if movie["file_type"] == "video":
            bot.send_video(chat_id, video=movie["file_id"], caption=caption, reply_markup=kb)
        elif movie["file_type"] == "document":
            bot.send_document(chat_id, document=movie["file_id"], caption=caption, reply_markup=kb)
        elif movie["file_type"] == "photo":
            bot.send_photo(chat_id, photo=movie["file_id"], caption=caption, reply_markup=kb)
        else:
            bot.send_message(chat_id, caption, reply_markup=kb)
        increment_movie_views(movie["code"])
    except Exception as e:
        logger.error(f"Kino yuborishda xato: {e}")
        bot.send_message(chat_id, "❌ Kino yuborishda xatolik yuz berdi!")

def send_music_to_user(chat_id, music, user_id):
    prem = is_premium(user_id)
    if music["is_premium"] and not prem and not is_admin(user_id):
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("💎 Premium Olish", callback_data="premium_info"))
        bot.send_message(
            chat_id,
            "💎 <b>Bu musiqa faqat Premium foydalanuvchilar uchun!</b>",
            reply_markup=kb
        )
        return

    dur = music.get("duration", 0)
    dur_str = f"{dur // 60}:{dur % 60:02d}" if dur else "N/A"
    prem_badge = "💎 PREMIUM" if music["is_premium"] else "🆓 Bepul"
    artist_name = music.get("artist") or "Noma'lum"
    caption = (
        f"🎵 <b>{music['title']}</b>\n"
        f"🎤 Artist: {artist_name}\n"
        f"⏱ Davomiylik: {dur_str}\n"
        f"🔢 Kod: <code>{music['code']}</code>\n"
        f"👁 Tinglashlar: {music['views']}\n"
        f"🏷 {prem_badge}"
    )

    try:
        kb = rating_keyboard(music["code"], "music")
        bot.send_audio(chat_id, audio=music["file_id"], caption=caption,
                       title=music["title"], performer=music.get("artist", ""),
                       reply_markup=kb)
        increment_music_views(music["code"])
    except Exception as e:
        logger.error(f"Musiqa yuborishda xato: {e}")
        bot.send_message(chat_id, "❌ Musiqani yuborishda xatolik!")

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    📨 ASOSIY MATN HANDLER                             ║
# ╚══════════════════════════════════════════════════════════════════════╝

@bot.message_handler(content_types=["text"])
def text_handler(message):
    user_id = message.from_user.id
    text = message.text.strip()

    # /start komandalarini o'tkazib yuborish
    if text.startswith("/"):
        return

    # Spam tekshirish
    if check_spam(user_id):
        bot.send_message(user_id, "⚠️ Juda ko'p xabar yubordingiz. 1 daqiqa kuting.")
        return

    # Foydalanuvchi ro'yxatdan o'tgan bo'lishi shart
    user = get_user(user_id)
    if not user:
        register_user(user_id, message.from_user.username or "", message.from_user.full_name or "")

    # Obuna tekshirish
    if REQUIRED_CHANNELS:
        is_sub, not_sub = check_subscription(user_id)
        if not is_sub:
            bot.send_message(user_id, "⚠️ Avval kanallarga obuna bo'ling!", reply_markup=get_sub_keyboard(not_sub))
            return

    state = get_state(user_id)

    # ── KALKULYATOR (eng avval) ────────────────────────────────────────
    if state.get("state") == "calculator":
        # Menyu tugmasi bosilsa — stateni tozalab davom et
        menu_buttons_set = {
            "🎬 Kinolar", "🎵 Musiqa", "💳 Donat", "📥 Video Yuklab Olish",
            "🤖 AI Rasm Yasash", "💬 AI Chat", "📄 Matndan PDF/Fayl",
            "🎁 Giftlar", "👤 Profilim", "💎 Premium", "🎁 Kunlik Bonus",
            "🧮 Kalkulyator", "💰 Balans To'ldirish", "🔙 Bosh Menyu",
            "⚙️ Admin Panel"
        }
        if text in menu_buttons_set or text.startswith("/"):
            clear_state(user_id)
            # Davom etib menyu tugmasini qayta ishlaydi
        else:
            import math
            expr = text.strip()
            if not expr:
                return
            # Unicode operatorlarini ASCII ga almashtirish
            expr_clean = (
                expr
                .replace("×", "*").replace("✕", "*").replace("✖", "*")
                .replace("÷", "/").replace("∕", "/")
                .replace("−", "-").replace("–", "-").replace("—", "-")
                .replace("²", "**2").replace("³", "**3")
                .replace(",", ".").replace(" ", "")
                .replace("^", "**")
            )
            try:
                allowed_names = {
                    "sqrt": math.sqrt, "abs": abs, "round": round,
                    "sin": math.sin, "cos": math.cos, "tan": math.tan,
                    "log": math.log, "log10": math.log10, "log2": math.log2,
                    "pi": math.pi, "e": math.e, "ceil": math.ceil,
                    "floor": math.floor, "pow": pow, "int": int, "float": float,
                    "factorial": math.factorial, "degrees": math.degrees,
                    "radians": math.radians,
                }
                result = eval(expr_clean, {"__builtins__": {}}, allowed_names)
                # Natijani chiroyli ko'rsatish
                if isinstance(result, float):
                    if result == int(result) and abs(result) < 1e15:
                        result_str = str(int(result))
                    else:
                        result_str = f"{result:.6g}"
                else:
                    result_str = str(result)
                bot.send_message(
                    user_id,
                    f"🧮 <b>Natija:</b>\n"
                    f"<code>{expr}</code>\n"
                    f"= <b>{result_str}</b>\n\n"
                    f"💡 Yana misol yozing yoki /start bosing"
                )
            except ZeroDivisionError:
                bot.send_message(user_id, "❌ Nolga bo'lish mumkin emas!")
            except Exception:
                bot.send_message(
                    user_id,
                    "❌ Noto'g'ri ifoda!\n\n"
                    "Misollar:\n"
                    "• <code>25 × 4</code>\n"
                    "• <code>100 ÷ 5</code>\n"
                    "• <code>2 ** 8</code> (daraja)\n"
                    "• <code>sqrt(256)</code>\n"
                    "• <code>(5 + 3) × 2</code>"
                )
            return

    # ── BALANS TO'LDIRISH MIQDORI ──────────────────────────────────────
    if state.get("state") == "topup_amount":
        menu_buttons_set = {
            "🎬 Kinolar", "🎵 Musiqa", "💳 Donat", "📥 Video Yuklab Olish",
            "🤖 AI Rasm Yasash", "💬 AI Chat", "📄 Matndan PDF/Fayl",
            "🎁 Giftlar", "👤 Profilim", "💎 Premium", "🎁 Kunlik Bonus",
            "🧮 Kalkulyator", "💰 Balans To'ldirish", "🔙 Bosh Menyu",
            "⚙️ Admin Panel"
        }
        if text in menu_buttons_set or text.startswith("/"):
            clear_state(user_id)
            # Davom etib menyu tugmasini qayta ishlaydi
        else:
            text_clean = text.replace(",", ".")
            try:
                amount = float(text_clean)
                if amount <= 0:
                    raise ValueError
                card_idx = state.get("data", {}).get("card_idx", 0)
                k = KARTALAR[card_idx] if 0 <= card_idx < len(KARTALAR) else KARTALAR[0]
                set_state(user_id, "topup_screenshot", {"amount": amount, "card_idx": card_idx})
                bot.send_message(
                    user_id,
                    f"✅ Miqdor: <b>{amount:.2f} TJS</b>\n\n"
                    f"💳 Karta: <b>{k['nomi']}</b>\n"
                    f"🔢 Raqam: <code>{k['raqam']}</code>\n"
                    f"👤 Egasi: {k['egasi']}\n\n"
                    f"3️⃣ Endi to'lov chekining <b>rasmini</b> yuboring 📸"
                )
            except ValueError:
                bot.send_message(user_id, "❌ Noto'g'ri miqdor! Raqam kiriting, masalan: <code>10</code>")
            return

    # ── AI CHAT HOLAT ──────────────────────────────────────────────────
    if state.get("state") == "ai_chat":
        menu_buttons = {
            "🎬 Kinolar", "🎵 Musiqa", "💳 Donat", "📥 Video Yuklab Olish",
            "🤖 AI Rasm Yasash", "💬 AI Chat", "📄 Matndan PDF/Fayl",
            "🎁 Giftlar", "👤 Profilim", "💎 Premium", "🎁 Kunlik Bonus",
            "🧮 Kalkulyator", "💰 Balans To'ldirish", "🔙 Bosh Menyu",
            "⚙️ Admin Panel", "🔍 Kino Qidirish", "🔍 Musiqa Qidirish",
            "⭐ Mashhur Kinolar", "🆕 Yangi Kinolar", "📂 Kategoriyalar",
            "🔥 Mashhur Musiqalar"
        }
        if text in menu_buttons or text.lower() in ("chiqish", "exit", "/start"):
            clear_state(user_id)
            # Davom etib menyu tugmasini qayta ishlaydi
        else:
            prompt = text.strip()
            if len(prompt) < 2:
                bot.send_message(user_id, "❌ Xabar juda qisqa!")
                return
            wait_msg = bot.send_message(user_id, "🤖 AI javob yozmoqda...")

            def ai_chat_and_send():
                answer = ask_claude_ai(prompt)
                kb_back = InlineKeyboardMarkup()
                kb_back.add(InlineKeyboardButton("🔙 Bosh menyuga", callback_data="back_main"))
                try:
                    bot.edit_message_text(
                        f"🤖 <b>AI Javob:</b>\n\n{answer}\n\n"
                        f"💬 Yana savol bering yoki <b>🔙 Bosh Menyu</b> bosing",
                        user_id, wait_msg.message_id,
                        reply_markup=kb_back
                    )
                except Exception:
                    bot.send_message(
                        user_id,
                        f"🤖 <b>AI Javob:</b>\n\n{answer}",
                        reply_markup=kb_back
                    )

            t = threading.Thread(target=ai_chat_and_send, daemon=True)
            t.start()
            return

    # ── ADMIN PANEL TUGMALARI ──────────────────────────────────────────
    if is_admin(user_id):
        if text == "➕ Kino Qo'shish":
            set_state(user_id, "add_movie_code")
            bot.send_message(user_id, "➕ <b>Kino Qo'shish</b>\n\n1️⃣ Kino kodini kiriting (masalan: <code>101</code>):")
            return
        if text == "🗑 Kino O'chirish":
            set_state(user_id, "delete_movie_code")
            bot.send_message(user_id, "🗑 O'chirmoqchi bo'lgan kino kodini kiriting:")
            return
        if text == "🎵 Musiqa Qo'shish":
            set_state(user_id, "add_music_code")
            bot.send_message(user_id, "🎵 <b>Musiqa Qo'shish</b>\n\n1️⃣ Musiqa kodini kiriting (masalan: <code>m101</code>):")
            return
        if text == "🗑 Musiqa O'chirish":
            set_state(user_id, "delete_music_code")
            bot.send_message(user_id, "🗑 O'chirmoqchi bo'lgan musiqa kodini kiriting:")
            return
        if text == "📢 Broadcast":
            set_state(user_id, "broadcast_text")
            bot.send_message(user_id,
                "📢 <b>Broadcast</b>\n\nBarcha foydalanuvchilarga yuboriladigan xabarni yozing:\n\n"
                "⚠️ Bu xabar BARCHA foydalanuvchilarga yuboriladi!")
            return
        if text == "💎 Premium Berish":
            set_state(user_id, "give_premium_id")
            bot.send_message(user_id, "💎 Premium bermoqchi bo'lgan foydalanuvchi ID sini kiriting:")
            return
        if text == "👥 Status Berish":
            set_state(user_id, "setstatus_id")
            bot.send_message(user_id, "👥 Status bermoqchi bo'lgan foydalanuvchi ID sini kiriting:")
            return
        if text.startswith("⏳ Buyurtmalar"):
            orders = get_pending_orders()
            if not orders:
                bot.send_message(user_id, "⏳ Hozircha kutilayotgan buyurtmalar yo'q.")
                return
            msg = "⏳ <b>Kutilayotgan buyurtmalar:</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
            for o in orders[:10]:
                msg += (
                    f"🔢 #{o['order_id']} | 🎮 {o['oyun']}\n"
                    f"👤 {o['user_name']} | 🆔 {o['player_id']}\n"
                    f"💎 {o['donat_miqdor']} — {o['narx']} TJS\n"
                    f"📅 {o['sana']}\n"
                    f"{'─' * 25}\n"
                )
            bot.send_message(user_id, msg)
            return
        if text.startswith("💰 Balans So'rovlari"):
            conn = get_conn()
            rows = conn.execute("SELECT * FROM balance_requests WHERE status='kutilmoqda' ORDER BY sana DESC LIMIT 20").fetchall()
            conn.close()
            reqs = [dict(r) for r in rows]
            if not reqs:
                bot.send_message(user_id, "💰 Hozircha kutilayotgan balans so'rovlari yo'q.")
                return
            for r in reqs:
                kb_r = InlineKeyboardMarkup()
                kb_r.add(
                    InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"topup_confirm_{r['req_id']}"),
                    InlineKeyboardButton("❌ Rad etish",  callback_data=f"topup_cancel_{r['req_id']}")
                )
                try:
                    bot.send_photo(
                        user_id, r["photo_id"],
                        caption=(
                            f"💰 <b>Balans so'rovi #{r['req_id']}</b>\n\n"
                            f"👤 {r['user_name']} (@{r['username']})\n"
                            f"🆔 User ID: <code>{r['user_id']}</code>\n"
                            f"💵 Miqdor: <b>{r['amount']:.2f} TJS</b>\n"
                            f"📅 {r['sana']}"
                        ),
                        reply_markup=kb_r
                    )
                except Exception as e:
                    logger.error(f"Balans so'rov ko'rsatishda xato: {e}")
            return

    # ── HOLAT HANDLERLARI (movie_search, music_search, download_url ...) ──

    if state.get("state") == "movie_search":
        clear_state(user_id)
        results = search_movies(text)
        if not results:
            bot.send_message(user_id, f"🔍 '<b>{text}</b>' bo'yicha kino topilmadi.")
            return
        msg = f"🔍 <b>{text}</b> bo'yicha natijalar:\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        kb = InlineKeyboardMarkup(row_width=1)
        for m in results:
            badge = "💎" if m["is_premium"] else "🆓"
            msg += f"{badge} <b>{m['title']}</b> | 📂 {m['category']} | 🔢 <code>{m['code']}</code>\n"
            kb.add(InlineKeyboardButton(f"▶️ {m['title'][:35]}", callback_data=f"get_movie_{m['code']}"))
        bot.send_message(user_id, msg, reply_markup=kb)
        return

    if state.get("state") == "music_search":
        clear_state(user_id)
        results = search_musics(text)
        if not results:
            bot.send_message(user_id, f"🔍 '<b>{text}</b>' bo'yicha musiqa topilmadi.")
            return
        msg = f"🎵 <b>{text}</b> bo'yicha natijalar:\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        kb = InlineKeyboardMarkup(row_width=1)
        for m in results:
            badge = "💎" if m["is_premium"] else "🆓"
            artist_str = m.get("artist", "") or "Noma'lum"
            msg += f"{badge} <b>{m['title']}</b> — {artist_str} | 🔢 <code>{m['code']}</code>\n"
            kb.add(InlineKeyboardButton(f"🎵 {m['title'][:35]}", callback_data=f"get_music_{m['code']}"))
        bot.send_message(user_id, msg, reply_markup=kb)
        return

    if state.get("state") == "download_url":
        url = text.strip()
        # Instagram URL tozalash (tracking parametrlarini olib tashlash)
        url_clean = re.sub(r'(https?://(?:www\.)?instagram\.com/(?:reel|p|tv)/[\w-]+)/?.*', r'\1/', url)

        ig_pattern = r"https?://(www\.)?instagram\.com/(reel|p|tv)/[\w-]+"
        if not re.match(ig_pattern, url_clean, re.IGNORECASE):
            kb_err = InlineKeyboardMarkup()
            kb_err.add(InlineKeyboardButton("🔙 Bosh menyuga", callback_data="back_main"))
            bot.send_message(user_id,
                "❌ <b>Noto'g'ri havola!</b>\n\n"
                "Faqat <b>Instagram</b> havolasini yuboring:\n"
                "• <code>https://www.instagram.com/reel/...</code>\n"
                "• <code>https://www.instagram.com/p/...</code>\n"
                "• <code>https://www.instagram.com/tv/...</code>",
                reply_markup=kb_err
            )
            return
        if not YT_DLP_AVAILABLE:
            clear_state(user_id)
            bot.send_message(user_id, "❌ yt-dlp o'rnatilmagan!\n<code>pip install yt-dlp</code>")
            return

        clear_state(user_id)
        wait_msg = bot.send_message(user_id, "⏳ Video ma'lumotlari olinmoqda...")

        def fetch_and_show():
            info = get_video_info(url_clean)
            if info:
                set_state(user_id, "download_ready", {"url": url_clean})
                kb = InlineKeyboardMarkup(row_width=2)
                kb.add(
                    InlineKeyboardButton("🎬 Video (MP4)", callback_data="dl_video"),
                    InlineKeyboardButton("🎵 Audio (MP3)", callback_data="dl_audio")
                )
                kb.add(InlineKeyboardButton("❌ Bekor", callback_data="dl_cancel"))
                dur = info.get("duration", 0)
                dur_str = f"{dur // 60}:{dur % 60:02d}" if dur else "N/A"
                title = info.get("title", "Instagram Video")[:50]
                try:
                    bot.edit_message_text(
                        f"📱 <b>{title}</b>\n"
                        f"👤 {info.get('uploader','Instagram')}\n"
                        f"⏱ {dur_str}\n\n"
                        f"Qaysi formatda yuklab olmoqchisiz?",
                        user_id, wait_msg.message_id, reply_markup=kb
                    )
                except Exception:
                    pass
            else:
                set_state(user_id, "download_url")
                kb_retry = InlineKeyboardMarkup()
                kb_retry.add(InlineKeyboardButton("🔙 Bosh menyuga", callback_data="back_main"))
                try:
                    bot.edit_message_text(
                        "❌ <b>Video yuklab olinmadi!</b>\n\n"
                        "<b>Asosiy sabablar:</b>\n"
                        "• Reel/Post yopiq yoki o'chirilgan\n"
                        "• Instagram login talab qiladi\n"
                        "• Fayl 50MB dan katta\n\n"
                        "💡 <b>Yechim:</b>\n"
                        "1. Boshqa ochiq Instagram havolasini sinab ko'ring\n"
                        "2. <code>instagram_cookies.txt</code> faylini bot papkasiga qo'ying\n"
                        "   (Cookies export qilish: <i>EditThisCookie</i> yoki <i>Get cookies.txt</i> Chrome extension)\n\n"
                        "📎 Yangi havola yuboring:",
                        user_id, wait_msg.message_id, reply_markup=kb_retry
                    )
                except Exception:
                    pass

        t = threading.Thread(target=fetch_and_show, daemon=True)
        t.start()
        return

    if state.get("state") == "ai_prompt":
        prompt = text.strip()
        if len(prompt) < 3:
            bot.send_message(user_id, "❌ Prompt juda qisqa! Kamida 3 ta harf yozing.")
            return

        clear_state(user_id)
        can, reason = can_generate_ai_image(user_id)
        if not can:
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("💎 Premium Olish", callback_data="premium_info"))
            bot.send_message(
                user_id,
                f"⏰ <b>Cheklov!</b>\n\n"
                f"Free tarifda 2 soatda 1 ta rasm generatsiya qilishingiz mumkin.\n"
                f"⏳ Keyingi rasm: <b>{reason}</b> keyin\n\n"
                f"💎 <b>Premium</b> olib, cheksiz rasm generatsiya qiling!",
                reply_markup=kb
            )
            return

        wait_msg = bot.send_message(user_id, f"🤖 AI rasm yaratilmoqda...\n🎨 Prompt: <i>{prompt}</i>\n\n⏳ Iltimos kuting (10-30 sekund)...")

        def generate_and_send():
            img_bytes = generate_ai_image(prompt, user_id)
            if img_bytes:
                update_user(user_id, ai_image_used_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                conn = get_conn()
                conn.execute("INSERT INTO ai_logs (user_id,prompt,status) VALUES (?,?,?)", (user_id, prompt, "success"))
                conn.commit()
                conn.close()
                try:
                    bot.delete_message(user_id, wait_msg.message_id)
                except Exception:
                    pass
                bot.send_photo(
                    user_id,
                    photo=img_bytes,
                    caption=f"🤖 <b>AI Rasm Tayyor!</b>\n🎨 Prompt: <i>{prompt}</i>\n\n"
                            f"{'⏰ Keyingi rasm 2 soatdan keyin (Free tarif)' if not is_premium(user_id) else '💎 Premium — cheksiz rasm!'}"
                )
            else:
                conn = get_conn()
                conn.execute("INSERT INTO ai_logs (user_id,prompt,status) VALUES (?,?,?)", (user_id, prompt, "failed"))
                conn.commit()
                conn.close()
                try:
                    bot.edit_message_text(
                        "❌ <b>Rasm yaratishda xatolik!</b>\n\n"
                        "Rasm serverlari hozir band yoki promptni qayta ishlashda muammo.\n\n"
                        "💡 <b>Maslahatlar:</b>\n"
                        "• Promtni <b>ingliz tilida</b> yozing\n"
                        "• Qisqaroq, aniqroq prompt kiriting\n"
                        "• 1-2 daqiqadan keyin qayta urinib ko'ring\n\n"
                        "✅ <b>Yaxshi misol:</b>\n"
                        "<code>big burger with fries and kfc bucket, food photography, 4k</code>",
                        user_id, wait_msg.message_id
                    )
                except Exception:
                    pass

        t = threading.Thread(target=generate_and_send, daemon=True)
        t.start()
        return

    if state.get("state") == "pdf_style":
        # Foydalanuvchi matn yuborganda — stil tanlash yo'q, to'g'ridan yuborgan
        clear_state(user_id)
        content = text.strip()
        style = "standart"
        if len(content) < 5:
            bot.send_message(user_id, "❌ Matn juda qisqa!")
            return
        wait_msg = bot.send_message(user_id, "📄 Fayl yaratilmoqda...")
        filepath = create_pdf_from_text(content, style=style)
        if filepath:
            ext = "pdf" if filepath.endswith(".pdf") else "txt"
            fname = f"hujjat_{user_id}.{ext}"
            try:
                with open(filepath, "rb") as f:
                    if ext == "pdf":
                        bot.send_document(user_id, f, visible_file_name=fname,
                                          caption=f"📄 <b>Hujjatingiz tayyor!</b>\n🎨 Stil: {style}\n📝 {len(content)} ta belgi")
                    else:
                        bot.send_document(user_id, f, visible_file_name=fname,
                                          caption=f"📝 <b>Matn fayli tayyor!</b>")
                os.remove(filepath)
            except Exception as e:
                bot.send_message(user_id, f"❌ Fayl yuborishda xato: {e}")
            try:
                bot.delete_message(user_id, wait_msg.message_id)
            except Exception:
                pass
        else:
            bot.edit_message_text("❌ Fayl yaratishda xatolik!", user_id, wait_msg.message_id)
        return

    if state.get("state") == "pdf_text":
        clear_state(user_id)
        content = text.strip()
        style = state.get("data", {}).get("style", "standart")
        if len(content) < 5:
            bot.send_message(user_id, "❌ Matn juda qisqa!")
            return
        wait_msg = bot.send_message(user_id, "📄 Fayl yaratilmoqda...")
        filepath = create_pdf_from_text(content, style=style)
        if filepath:
            ext = "pdf" if filepath.endswith(".pdf") else "txt"
            fname = f"hujjat_{user_id}.{ext}"
            try:
                with open(filepath, "rb") as f:
                    if ext == "pdf":
                        bot.send_document(user_id, f, visible_file_name=fname,
                                          caption=f"📄 <b>Hujjatingiz tayyor!</b>\n🎨 Stil: {style}\n📝 {len(content)} ta belgi")
                    else:
                        bot.send_document(user_id, f, visible_file_name=fname,
                                          caption=f"📝 <b>Matn fayli tayyor!</b>\n(PDF uchun reportlab kutubxonasi kerak)")
                os.remove(filepath)
            except Exception as e:
                bot.send_message(user_id, f"❌ Fayl yuborishda xato: {e}")
            try:
                bot.delete_message(user_id, wait_msg.message_id)
            except Exception:
                pass
        else:
            bot.edit_message_text("❌ Fayl yaratishda xatolik!", user_id, wait_msg.message_id)
        return

    # Donat Player ID holati
    if state.get("state") == "donat_player_id":
        player_id = text.strip()
        d = state.get("data", {})
        d["player_id"] = player_id
        narx = d["narx"]
        balance = get_user_balance(user_id)

        # Balansda yetarli pul bormi?
        if balance >= narx:
            # Balansdan yechib, buyurtmani avtomatik yaratish
            ok = deduct_user_balance(user_id, narx)
            if ok:
                order_id = next_order_id()
                order = {
                    "order_id": order_id,
                    "user_id": user_id,
                    "user_name": message.from_user.full_name,
                    "username": message.from_user.username or "yoq",
                    "oyun": d["oyun"],
                    "donat_tur": d["donat_tur"],
                    "donat_miqdor": d["donat_miqdor"],
                    "narx": narx,
                    "player_id": player_id,
                    "photo_id": "balance_payment",
                    "status": "kutilmoqda",
                    "sana": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                save_order(order)
                clear_state(user_id)
                new_bal = get_user_balance(user_id)
                bot.send_message(
                    user_id,
                    f"✅ <b>Buyurtmangiz qabul qilindi!</b>\n\n"
                    f"🔢 Buyurtma: #{order_id}\n"
                    f"🎮 O'yin: <b>{d['oyun']}</b>\n"
                    f"💎 Donat: <b>{d['donat_miqdor']}</b>\n"
                    f"🆔 Player ID: <code>{player_id}</code>\n"
                    f"💰 To'landi: <b>{narx} TJS</b> (balansdan)\n"
                    f"💳 Qolgan balans: <b>{new_bal:.2f} TJS</b>\n\n"
                    f"⚡ 5-30 daqiqa ichida yetkaziladi!\n"
                    f"Savol: {ADMIN_USERNAME}"
                )
                # Adminga xabar
                uname = message.from_user.username
                tg_link = f"@{uname}" if uname else f"tg://user?id={user_id}"
                kb_admin = InlineKeyboardMarkup(row_width=2)
                kb_admin.add(
                    InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_{order_id}"),
                    InlineKeyboardButton("❌ Rad etish",  callback_data=f"cancel_{order_id}")
                )
                admin_caption = (
                    f"🆕 <b>YANGI DONAT BUYURTMA #{order_id}</b>\n"
                    f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"👤 <b>Foydalanuvchi:</b> {message.from_user.full_name}\n"
                    f"📱 <b>Telegram:</b> {tg_link}\n"
                    f"🆔 <b>TG User ID:</b> <code>{user_id}</code>\n\n"
                    f"🎮 <b>O'yin:</b> {d['oyun']}\n"
                    f"💎 <b>Paket:</b> {d['donat_miqdor']}\n"
                    f"🎯 <b>Player ID:</b> <code>{player_id}</code>\n"
                    f"💰 <b>Narx:</b> {narx} TJS (balansdan to'landi)\n"
                    f"📅 <b>Vaqt:</b> {order['sana']}"
                )
                for admin_id in ADMIN_IDS:
                    try:
                        bot.send_message(admin_id, admin_caption, reply_markup=kb_admin)
                    except Exception as e:
                        logger.error(f"Admin ga xabar: {e}")
            else:
                bot.send_message(user_id, "❌ Balansdan yechishda xatolik!")
        else:
            # Balans yetarli emas — karta orqali to'lash
            set_state(user_id, "donat_screenshot", d)
            kartalar_text = "\n".join(f"  {k['nomi']}: <code>{k['raqam']}</code> ({k['egasi']})" for k in KARTALAR)
            bot.send_message(
                user_id,
                f"✅ <b>Player ID qabul qilindi!</b>\n\n"
                f"🎮 O'yin: <b>{d['oyun']}</b>\n"
                f"💎 Donat: <b>{d['donat_miqdor']}</b>\n"
                f"💰 Narx: <b>{narx} TJS</b>\n\n"
                f"⚠️ Balans: <b>{balance:.2f} TJS</b> (yetarli emas)\n\n"
                f"💳 <b>To'lov kartalarimiz:</b>\n{kartalar_text}\n\n"
                f"📸 To'lov chekini yuboring:"
            )
        return

    # Admin holatlari
    if is_admin(user_id):
        if state.get("state") == "add_movie_code":
            if get_movie(text):
                bot.send_message(user_id, f"❌ <code>{text}</code> kodi allaqachon mavjud!")
                clear_state(user_id)
                return
            set_state(user_id, "add_movie_title", {"code": text})
            bot.send_message(user_id, f"✅ Kod: <code>{text}</code>\n\n2️⃣ Kino nomini kiriting:")
            return

        if state.get("state") == "add_movie_title":
            d = state["data"]; d["title"] = text
            set_state(user_id, "add_movie_desc", d)
            bot.send_message(user_id, f"✅ Nom: <b>{text}</b>\n\n3️⃣ Tavsifni kiriting (yoki 'skip' yozing):")
            return

        if state.get("state") == "add_movie_desc":
            d = state["data"]; d["description"] = "" if text.lower() == "skip" else text
            set_state(user_id, "add_movie_category", d)
            kb = InlineKeyboardMarkup(row_width=2)
            for cat in ["Uzbek Kino", "Xorij Kino", "Multfilm", "Serial", "Hujjatli", "Boshqa"]:
                kb.add(InlineKeyboardButton(cat, callback_data=f"acat_{cat}"))
            bot.send_message(user_id, "4️⃣ Kategoriyani tanlang:", reply_markup=kb)
            return

        if state.get("state") == "add_movie_premium":
            d = state["data"]
            d["is_premium"] = 1 if text.lower() in ("ha", "yes", "1") else 0
            set_state(user_id, "add_movie_file", d)
            bot.send_message(user_id, "6️⃣ Kino videosini yuboring:")
            return

        if state.get("state") == "add_music_code":
            if get_music(text):
                bot.send_message(user_id, f"❌ <code>{text}</code> kodi allaqachon mavjud!")
                clear_state(user_id)
                return
            set_state(user_id, "add_music_title", {"code": text})
            bot.send_message(user_id, f"✅ Kod: <code>{text}</code>\n\n2️⃣ Musiqa nomini kiriting:")
            return

        if state.get("state") == "add_music_title":
            d = state["data"]; d["title"] = text
            set_state(user_id, "add_music_artist", d)
            bot.send_message(user_id, f"✅ Nom: <b>{text}</b>\n\n3️⃣ Artistni kiriting (yoki 'skip'):")
            return

        if state.get("state") == "add_music_artist":
            d = state["data"]; d["artist"] = "" if text.lower() == "skip" else text
            set_state(user_id, "add_music_premium", d)
            kb = InlineKeyboardMarkup(row_width=2)
            kb.add(InlineKeyboardButton("💎 Ha, Premium", callback_data="musprem_1"),
                   InlineKeyboardButton("🆓 Yo'q, Bepul", callback_data="musprem_0"))
            bot.send_message(user_id, "4️⃣ Bu musiqa Premiummi?", reply_markup=kb)
            return

        if state.get("state") == "delete_movie_code":
            clear_state(user_id)
            if delete_movie(text):
                bot.send_message(user_id, f"✅ <code>{text}</code> kodli kino o'chirildi!")
            else:
                bot.send_message(user_id, f"❌ <code>{text}</code> kodli kino topilmadi!")
            return

        if state.get("state") == "delete_music_code":
            clear_state(user_id)
            if delete_music(text):
                bot.send_message(user_id, f"✅ <code>{text}</code> kodli musiqa o'chirildi!")
            else:
                bot.send_message(user_id, f"❌ <code>{text}</code> kodli musiqa topilmadi!")
            return

        if state.get("state") == "broadcast_text":
            clear_state(user_id)
            do_broadcast(user_id, text)
            return

        if state.get("state") == "setstatus_id":
            try:
                target = int(text)
                set_state(user_id, "setstatus_value", {"target": target})
                kb = InlineKeyboardMarkup(row_width=2)
                kb.add(
                    InlineKeyboardButton("👤 Free",    callback_data=f"setst_{target}_free"),
                    InlineKeyboardButton("💎 Premium", callback_data=f"setst_{target}_premium"),
                    InlineKeyboardButton("👑 Admin",   callback_data=f"setst_{target}_admin")
                )
                bot.send_message(user_id, "Status tanlang:", reply_markup=kb)
            except ValueError:
                bot.send_message(user_id, "❌ Noto'g'ri ID!")
                clear_state(user_id)
            return

        if state.get("state") == "give_premium_id":
            try:
                target = int(text)
                set_state(user_id, "give_premium_days", {"target": target})
                bot.send_message(user_id, f"ID: <code>{target}</code>\n\nNecha kunga premium? (sonini kiriting):")
            except ValueError:
                bot.send_message(user_id, "❌ Noto'g'ri ID!")
                clear_state(user_id)
            return

        if state.get("state") == "give_premium_days":
            try:
                days = int(text)
                target = state["data"]["target"]
                until = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
                update_user(target, status="premium", premium_until=until)
                clear_state(user_id)
                bot.send_message(user_id, f"✅ <code>{target}</code> foydalanuvchiga {days} kunlik Premium berildi!")
                try:
                    bot.send_message(target,
                                     f"🎉 <b>Tabriklaymiz!</b>\nSizga <b>{days} kunlik Premium</b> berildi!\n"
                                     f"📅 Muddati: {until}")
                except Exception:
                    pass
            except ValueError:
                bot.send_message(user_id, "❌ Noto'g'ri son!")
                clear_state(user_id)
            return

        if state.get("state") == "donat_player_id_admin":
            # Admin uchun donat holat (ehtimol kerak emas, lekin qoldirish uchun)
            pass

    # ── MENYU TUGMALARI ────────────────────────────────────────────────

    if text == "🎬 Kinolar":
        bot.send_message(
            user_id,
            "🎬 <b>KINOLAR BO'LIMI</b>\n\nKino kodini kiriting yoki quyidagi bo'limlardan birini tanlang:",
            reply_markup=movie_keyboard()
        )
        return

    if text == "🎵 Musiqa":
        bot.send_message(
            user_id,
            "🎵 <b>MUSIQA BO'LIMI</b>\n\nMusiqa kodini kiriting yoki quyidagi bo'limlardan birini tanlang:",
            reply_markup=music_keyboard()
        )
        return

    if text == "🔍 Kino Qidirish":
        set_state(user_id, "movie_search")
        bot.send_message(user_id, "🔍 Qidirmoqchi bo'lgan kino nomini yozing:")
        return

    if text == "🔍 Musiqa Qidirish":
        set_state(user_id, "music_search")
        bot.send_message(user_id, "🔍 Qidirmoqchi bo'lgan musiqa nomini yozing:")
        return

    if text == "⭐ Mashhur Kinolar":
        movies = get_popular_movies()
        if not movies:
            bot.send_message(user_id, "📭 Hali kinolar yo'q.")
            return
        msg = "⭐ <b>ENG MASHHUR KINOLAR</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        kb = InlineKeyboardMarkup(row_width=1)
        for i, m in enumerate(movies, 1):
            badge = "💎" if m["is_premium"] else "🆓"
            msg += f"{i}. {badge} <b>{m['title']}</b> | 👁 {m['views']} | <code>{m['code']}</code>\n"
            kb.add(InlineKeyboardButton(f"▶️ {m['title'][:35]}", callback_data=f"get_movie_{m['code']}"))
        bot.send_message(user_id, msg, reply_markup=kb)
        return

    if text == "🔥 Mashhur Musiqalar":
        musics = get_popular_musics()
        if not musics:
            bot.send_message(user_id, "📭 Hali musiqalar yo'q.")
            return
        msg = "🔥 <b>ENG MASHHUR MUSIQALAR</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        kb = InlineKeyboardMarkup(row_width=1)
        for i, m in enumerate(musics, 1):
            badge = "💎" if m["is_premium"] else "🆓"
            artist_str = m.get("artist", "") or "Noma'lum"
            msg += f"{i}. {badge} <b>{m['title']}</b> — {artist_str} | <code>{m['code']}</code>\n"
            kb.add(InlineKeyboardButton(f"🎵 {m['title'][:35]}", callback_data=f"get_music_{m['code']}"))
        bot.send_message(user_id, msg, reply_markup=kb)
        return

    if text == "🆕 Yangi Kinolar":
        movies = get_latest_movies()
        if not movies:
            bot.send_message(user_id, "📭 Hali kinolar yo'q.")
            return
        msg = "🆕 <b>YANGI KINOLAR</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
        kb = InlineKeyboardMarkup(row_width=1)
        for i, m in enumerate(movies, 1):
            date = m.get("added_at", "")[:10]
            badge = "💎" if m["is_premium"] else "🆓"
            msg += f"{i}. {badge} <b>{m['title']}</b> | 📅 {date} | <code>{m['code']}</code>\n"
            kb.add(InlineKeyboardButton(f"▶️ {m['title'][:35]}", callback_data=f"get_movie_{m['code']}"))
        bot.send_message(user_id, msg, reply_markup=kb)
        return

    if text == "📂 Kategoriyalar":
        cats = get_categories()
        if not cats:
            bot.send_message(user_id, "📭 Hali kategoriyalar yo'q.")
            return
        kb = InlineKeyboardMarkup(row_width=2)
        for cat, cnt in cats:
            kb.add(InlineKeyboardButton(f"📂 {cat} ({cnt})", callback_data=f"cat_{cat}"))
        bot.send_message(user_id, "📂 <b>KATEGORIYALAR</b>\n\nBirini tanlang:", reply_markup=kb)
        return

    if text == "💳 Donat":
        bot.send_message(
            user_id,
            "🎮 <b>DONAT BO'LIMI</b>\n\n"
            "✅ Tez va ishonchli donat xizmati\n"
            "⚡ 5-30 daqiqa ichida yetkaziladi\n"
            "🕐 24/7 xizmat\n\n"
            "O'yinni tanlang:",
            reply_markup=donat_oyun_keyboard()
        )
        return

    if text == "📥 Video Yuklab Olish":
        if not YT_DLP_AVAILABLE:
            bot.send_message(user_id, "❌ yt-dlp kutubxonasi o'rnatilmagan!\n\nTerminalda: <code>pip install yt-dlp</code>")
            return
        set_state(user_id, "download_url")
        kb_vid = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        kb_vid.add(KeyboardButton("🔙 Bosh Menyu"))
        bot.send_message(
            user_id,
            "📥 <b>INSTAGRAM VIDEO YUKLAB OLISH</b>\n\n"
            "Instagram havolasini yuboring:\n\n"
            "Misol:\n"
            "• https://www.instagram.com/reel/...\n"
            "• https://www.instagram.com/p/...\n"
            "• https://www.instagram.com/tv/...\n\n"
            "(Bekor qilish uchun 🔙 Bosh Menyu bosing)",
            reply_markup=kb_vid
        )
        return

    if text == "🤖 AI Rasm Yasash":
        can, reason = can_generate_ai_image(user_id)
        prem = is_premium(user_id)
        info = (
            "💎 Premium: <b>Cheksiz rasm!</b>" if prem
            else f"👤 Free: 2 soatda 1 ta rasm\n"
                 f"{'✅ Hozir ishlata olasiz!' if can else f'⏳ Keyingi rasm: {reason} keyin'}"
        )
        set_state(user_id, "ai_prompt")
        kb_rasm = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        kb_rasm.add(KeyboardButton("🔙 Bosh Menyu"))
        bot.send_message(
            user_id,
            f"🤖 <b>AI RASM GENERATSIYA</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{info}\n\n"
            f"🎨 Rasmni tasvirlang (prompt yozing):\n\n"
            f"💡 <i>Maslahat: Ingliz tilida yozish yaxshiroq natija beradi</i>\n"
            f"Misol: <code>beautiful sunset over mountains, photorealistic</code>\n\n"
            f"(Bekor qilish uchun 🔙 Bosh Menyu bosing)",
            reply_markup=kb_rasm
        )
        return

    if text == "💬 AI Chat":
        set_state(user_id, "ai_chat")
        kb_ai = ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
        kb_ai.add(KeyboardButton("🔙 Bosh Menyu"))
        bot.send_message(
            user_id,
            "💬 <b>AI CHAT</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🤖 Men Claude AI — har qanday savolga javob beraman!\n\n"
            "💡 Misollar:\n"
            "• Dunyoning eng baland tog'i qaysi?\n"
            "• Python da ro'yxat yaratish usullarini ayting\n"
            "• Menga qo'shiq matni yozing\n\n"
            "Savolingizni yozing:\n"
            "(Chiqish uchun: 🔙 Bosh Menyu)",
            reply_markup=kb_ai
        )
        return

    if text == "🎁 Giftlar":
        balance = get_user_balance(user_id)
        kb = InlineKeyboardMarkup(row_width=2)
        msg = (
            "🎁 <b>GIFTLAR BO'LIMI</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Telegram giftlarini balans orqali sotib oling!\n\n"
            f"💰 Sizning balans: <b>{balance:.2f} TJS</b>\n\n"
            "🎀 <b>Mavjud giftlar:</b>\n\n"
        )
        for i, g in enumerate(GIFTLAR):
            msg += f"{g['emoji']} {g['nomi']} — ⭐{g['stars']} ({g['narx_tjs']} TJS)\n"
            status = "✅" if balance >= g["narx_tjs"] else "❌"
            kb.add(InlineKeyboardButton(
                f"{status} {g['emoji']} {g['nomi']} — {g['narx_tjs']} TJS",
                callback_data=f"gift_{i}"
            ))
        kb.add(InlineKeyboardButton("🏠 Bosh menyuga", callback_data="back_main"))
        msg += (
            "\n📌 <b>Narx jadval:</b>\n"
            "⭐15 stars = 5 TJS\n"
            "⭐25 stars = 8 TJS\n"
            "⭐50 stars = 13 TJS\n"
            "⭐100 stars = 25 TJS\n\n"
            "💡 Balansni to'ldirish uchun '💰 Balans To'ldirish' tugmasini bosing"
        )
        bot.send_message(user_id, msg, reply_markup=kb)
        return

    if text == "📄 Matndan PDF/Fayl":
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(
            InlineKeyboardButton("📝 Standart", callback_data="pdf_style_standart"),
            InlineKeyboardButton("✏️ Qiyshiq (Italic)", callback_data="pdf_style_qiyshiq"),
            InlineKeyboardButton("🔤 Chunmaydigan (Bold)", callback_data="pdf_style_chunmaydigan"),
            InlineKeyboardButton("📖 Classic", callback_data="pdf_style_classic"),
            InlineKeyboardButton("💼 Pro", callback_data="pdf_style_pro"),
            InlineKeyboardButton("🏠 Bosh menyuga", callback_data="back_main"),
        )
        bot.send_message(
            user_id,
            "📄 <b>PDF / FAYL YARATISH</b>\n\n"
            "Avval yozish stilini tanlang:\n\n"
            "📝 <b>Standart</b> — oddiy, toza\n"
            "✏️ <b>Qiyshiq</b> — italic, chiroyli\n"
            "🔤 <b>Chunmaydigan</b> — qalin, katta shrift\n"
            "📖 <b>Classic</b> — klassik Times uslubi\n"
            "💼 <b>Pro</b> — professional, ramkali",
            reply_markup=kb
        )
        return

    if text == "👤 Profilim":
        user = get_user(user_id)
        prem = is_premium(user_id)
        status_emoji = "💎" if prem else "👑" if is_admin(user_id) else "👤"
        status_name = "Premium" if prem else "Admin" if is_admin(user_id) else "Free"
        until = user.get("premium_until") or "—"
        ref_link = f"https://t.me/{bot.get_me().username}?start=ref_{user_id}"
        balance = get_user_balance(user_id)
        kb = InlineKeyboardMarkup(row_width=1)
        kb.add(InlineKeyboardButton("💰 Balans To'ldirish", callback_data="topup_balance"))
        kb.add(InlineKeyboardButton("💎 Premium Olish (Avto)", callback_data="auto_premium"))
        kb.add(InlineKeyboardButton("🎁 Kunlik Bonus", callback_data="daily_bonus"))
        bot.send_message(
            user_id,
            f"👤 <b>PROFILIM</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"🆔 ID: <code>{user_id}</code>\n"
            f"👤 Ism: {user.get('full_name','')}\n"
            f"{status_emoji} Status: <b>{status_name}</b>\n"
            f"📅 Premium muddati: {until}\n"
            f"💰 Balans: <b>{balance:.2f} TJS</b>\n"
            f"👥 Referallar: <b>{user.get('referral_count',0)}</b> kishi\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n"
            f"🔗 Referal havola:\n<code>{ref_link}</code>",
            reply_markup=kb
        )
        return

    if text == "💎 Premium":
        balance = get_user_balance(user_id)
        kb = InlineKeyboardMarkup(row_width=1)
        for k, v in PREMIUM_NARXLAR.items():
            kb.add(InlineKeyboardButton(
                f"💎 {v['nomi']} — {v['narx']} TJS",
                callback_data=f"buy_premium_{k}"
            ))
        kb.add(InlineKeyboardButton("💰 Balans To'ldirish", callback_data="topup_balance"))
        kb.add(InlineKeyboardButton("📞 Admin bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME.lstrip('@')}"))
        kb.add(InlineKeyboardButton("🏠 Bosh menyuga", callback_data="back_main"))
        msg = (
            "💎 <b>PREMIUM TARIF</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━\n\n"
            "Premium afzalliklari:\n"
            "✅ Barcha kinolar va musiqalar\n"
            "✅ YouTube/Instagram video yuklash\n"
            "✅ AI Rasm — cheksiz generatsiya\n"
            "✅ Reklamasiz foydalanish\n"
            "✅ 2x kunlik bonus (0.20 TJS)\n\n"
            f"💰 Joriy balans: <b>{balance:.2f} TJS</b>\n\n"
            "💰 <b>Narxlar (TJS):</b>\n"
        )
        for k, v in PREMIUM_NARXLAR.items():
            msg += f"• {v['nomi']}: <b>{v['narx']} TJS</b>\n"
        msg += "\n💡 Balans orqali avto sotib oling yoki admin bilan bog'laning!"
        bot.send_message(user_id, msg, reply_markup=kb)
        return

    if text == "🎁 Kunlik Bonus":
        user = get_user(user_id)
        today = datetime.now().strftime("%Y-%m-%d")
        last = user.get("last_bonus_date")
        if last == today:
            bot.send_message(user_id, "⏰ Bugun bonus allaqachon olingdi!\n\nErtaga yana keling! 🎁")
        else:
            bonus_tjs = 0.20 if is_premium(user_id) else 0.10
            add_user_balance(user_id, bonus_tjs)
            new_balance = get_user_balance(user_id)
            update_user(user_id, last_bonus_date=today)
            bot.send_message(
                user_id,
                f"🎁 <b>Kunlik Bonus!</b>\n\n"
                f"✅ +{bonus_tjs:.2f} TJS balansga qo'shildi!\n"
                f"💰 Joriy balans: <b>{new_balance:.2f} TJS</b>\n\n"
                f"{'💎 Premium bonus 2x!' if is_premium(user_id) else '💡 Premium olib 2x bonus oling!'}"
            )
        return

    if text == "💰 Balans To'ldirish":
        balance = get_user_balance(user_id)
        kb = InlineKeyboardMarkup(row_width=1)
        for i, k in enumerate(KARTALAR):
            kb.add(InlineKeyboardButton(f"{k['nomi']}", callback_data=f"select_card_{i}"))
        kb.add(InlineKeyboardButton("🔙 Bosh menyuga", callback_data="back_main"))
        bot.send_message(
            user_id,
            f"💰 <b>BALANS TO'LDIRISH</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"Joriy balans: <b>{balance:.2f} TJS</b>\n\n"
            f"1️⃣ Avval kartani tanlang:",
            reply_markup=kb
        )
        return

    if text == "🧮 Kalkulyator":
        set_state(user_id, "calculator")
        bot.send_message(
            user_id,
            "🧮 <b>KALKULYATOR</b>\n\n"
            "Hisob-kitob yozing va javob olasiz!\n\n"
            "Misollar:\n"
            "• <code>2 + 2</code>\n"
            "• <code>100 * 5.5</code>\n"
            "• <code>1500 / 3</code>\n"
            "• <code>2 ** 10</code> (daraja)\n"
            "• <code>sqrt(144)</code>\n\n"
            "Chiqish uchun: /start"
        )
        return

    if text == "🔙 Bosh Menyu":
        bot.send_message(user_id, "🏠 Bosh menyu", reply_markup=main_keyboard(user_id))
        return

    # Admin tugmalari
    if is_admin(user_id):
        if text == "⚙️ Admin Panel":
            show_admin_panel(user_id)
            return

    # Raqam bo'lsa — avval kino, keyin musiqa qidirish
    if re.match(r"^[a-zA-Z0-9_\-]{2,20}$", text):
        movie = get_movie(text)
        if movie:
            send_movie_to_user(user_id, movie, user_id)
            return
        music = get_music(text)
        if music:
            send_music_to_user(user_id, music, user_id)
            return

    # Umumiy qidiruv
    if len(text) > 2:
        m_results = search_movies(text)
        s_results = search_musics(text)
        if m_results or s_results:
            kb = InlineKeyboardMarkup(row_width=1)
            msg = "🔍 <b>Qidiruv natijalari:</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
            if m_results:
                msg += "🎬 <b>Kinolar:</b>\n"
                for m in m_results[:5]:
                    badge = "💎" if m["is_premium"] else "🆓"
                    msg += f"{badge} <b>{m['title']}</b> | <code>{m['code']}</code>\n"
                    kb.add(InlineKeyboardButton(f"▶️ {m['title'][:35]}", callback_data=f"get_movie_{m['code']}"))
            if s_results:
                msg += "\n🎵 <b>Musiqalar:</b>\n"
                for m in s_results[:5]:
                    badge = "💎" if m["is_premium"] else "🆓"
                    msg += f"{badge} <b>{m['title']}</b> — {m.get('artist','') or ''} | <code>{m['code']}</code>\n"
                    kb.add(InlineKeyboardButton(f"🎵 {m['title'][:35]}", callback_data=f"get_music_{m['code']}"))
            bot.send_message(user_id, msg, reply_markup=kb)
            return

    bot.send_message(
        user_id,
        "❓ Kino/musiqa kodini kiriting yoki menyu tugmalaridan foydalaning!\n\n"
        "💡 <i>Misol: 101 (kino kodi) yoki kino nomini yozing</i>"
    )

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    📁 FAYL HANDLERLARI                                ║
# ╚══════════════════════════════════════════════════════════════════════╝

@bot.message_handler(content_types=["video", "audio", "document", "photo"])
def file_handler(message):
    user_id = message.from_user.id
    state = get_state(user_id)

    # Oddiy foydalanuvchilar uchun ruxsat berilgan state'lar
    allowed_states = {"donat_screenshot", "topup_screenshot"}
    if not is_admin(user_id):
        if state.get("state") in allowed_states:
            pass  # quyida ishlanadi
        else:
            bot.send_message(user_id, "❌ Faqat adminlar fayl yuborishi mumkin.")
            return

    # Balans to'ldirish screenshot (FOTO)
    if state.get("state") == "topup_screenshot":
        if message.content_type != "photo":
            bot.send_message(user_id, "❌ Iltimos, to'lov chekining rasmini yuboring!")
            return
        amount = state.get("data", {}).get("amount", 0)
        photo_id = message.photo[-1].file_id
        req_id = next_balance_req_id()
        req = {
            "req_id": req_id,
            "user_id": user_id,
            "user_name": message.from_user.full_name,
            "username": message.from_user.username or "yoq",
            "amount": amount,
            "photo_id": photo_id,
            "status": "kutilmoqda",
            "sana": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_balance_request(req)
        clear_state(user_id)
        bot.send_message(
            user_id,
            f"✅ <b>So'rovingiz yuborildi!</b>\n\n"
            f"🔢 So'rov: #{req_id}\n"
            f"💰 Miqdor: <b>{amount:.2f} TJS</b>\n\n"
            f"⏳ Admin tasdiqlashidan so'ng balans qo'shiladi.\n"
            f"Savol: {ADMIN_USERNAME}"
        )
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"topup_confirm_{req_id}"),
            InlineKeyboardButton("❌ Rad etish", callback_data=f"topup_cancel_{req_id}")
        )
        for admin_id in ADMIN_IDS:
            try:
                bot.send_photo(
                    admin_id, photo_id,
                    caption=(
                        f"💰 <b>Yangi balans so'rovi #{req_id}</b>\n\n"
                        f"👤 {message.from_user.full_name} (@{message.from_user.username or 'yoq'})\n"
                        f"🆔 User ID: <code>{user_id}</code>\n"
                        f"💵 Miqdor: <b>{amount:.2f} TJS</b>\n"
                        f"📅 {req['sana']}"
                    ),
                    reply_markup=kb
                )
            except Exception as e:
                logger.error(f"Admin ga balans xabari: {e}")
        return

    if state.get("state") == "add_movie_file":
        d = state["data"]
        if message.content_type == "video":
            file_id = message.video.file_id; ftype = "video"
        elif message.content_type == "document":
            file_id = message.document.file_id; ftype = "document"
        elif message.content_type == "photo":
            file_id = message.photo[-1].file_id; ftype = "photo"
        else:
            bot.send_message(user_id, "❌ Video yoki rasm yuboring!"); return

        ok = add_movie(d["code"], d["title"], d.get("description",""), file_id, ftype,
                       d.get("category","Umumiy"), d.get("is_premium",0), user_id)
        clear_state(user_id)
        if ok:
            bot.send_message(
                user_id,
                f"✅ <b>Kino qo'shildi!</b>\n\n"
                f"🔢 Kod: <code>{d['code']}</code>\n"
                f"🎬 Nom: <b>{d['title']}</b>\n"
                f"📂 Kategoriya: {d.get('category','Umumiy')}\n"
                f"💎 Premium: {'Ha' if d.get('is_premium') else 'Yoq'}"
            )
        else:
            bot.send_message(user_id, f"❌ <code>{d['code']}</code> kodi allaqachon mavjud!")
        return

    if state.get("state") == "add_music_file":
        d = state["data"]
        if message.content_type == "audio":
            file_id = message.audio.file_id
            duration = message.audio.duration or 0
        elif message.content_type == "document":
            file_id = message.document.file_id; duration = 0
        else:
            bot.send_message(user_id, "❌ Audio fayl yuboring!"); return

        ok = add_music(d["code"], d["title"], d.get("artist",""), file_id, duration,
                       d.get("is_premium",0), user_id)
        clear_state(user_id)
        if ok:
            artist_display = d.get("artist", "Noma'lum")
            bot.send_message(
                user_id,
                f"✅ <b>Musiqa qo'shildi!</b>\n\n"
                f"🔢 Kod: <code>{d['code']}</code>\n"
                f"🎵 Nom: <b>{d['title']}</b>\n"
                f"🎤 Artist: {artist_display}\n"
                f"💎 Premium: {'Ha' if d.get('is_premium') else 'Yoq'}"
            )
        else:
            bot.send_message(user_id, f"❌ <code>{d['code']}</code> kodi allaqachon mavjud!")
        return

    # Donat screenshot
    if state.get("state") == "donat_screenshot":
        d = state["data"]
        if message.content_type != "photo":
            bot.send_message(user_id, "❌ Iltimos, to'lov chekining rasmini yuboring!")
            return
        photo_id = message.photo[-1].file_id
        order_id = next_order_id()
        order = {
            "order_id": order_id,
            "user_id": user_id,
            "user_name": message.from_user.full_name,
            "username": message.from_user.username or "yoq",
            "oyun": d["oyun"],
            "donat_tur": d["donat_tur"],
            "donat_miqdor": d["donat_miqdor"],
            "narx": d["narx"],
            "player_id": d["player_id"],
            "photo_id": photo_id,
            "status": "kutilmoqda",
            "sana": datetime.now().strftime("%Y-%m-%d %H:%M")
        }
        save_order(order)
        clear_state(user_id)

        bot.send_message(
            user_id,
            f"✅ <b>Buyurtmangiz qabul qilindi!</b>\n\n"
            f"🔢 Buyurtma: #{order_id}\n"
            f"🎮 O'yin: {d['oyun']}\n"
            f"💎 Donat: {d['donat_miqdor']}\n"
            f"🆔 Player ID: {d['player_id']}\n"
            f"💰 Narx: {d['narx']} TJS\n\n"
            f"⚡ 5-30 daqiqa ichida yetkaziladi!\n"
            f"Savol: {ADMIN_USERNAME}"
        )

        # Adminlarga xabar (barcha kerakli ma'lumotlar bilan)
        uname = message.from_user.username
        tg_link = f"@{uname}" if uname else f"tg://user?id={user_id}"
        kb_admin = InlineKeyboardMarkup(row_width=2)
        kb_admin.add(
            InlineKeyboardButton("✅ Tasdiqlash", callback_data=f"confirm_{order_id}"),
            InlineKeyboardButton("❌ Rad etish",  callback_data=f"cancel_{order_id}")
        )
        admin_caption = (
            f"🆕 <b>YANGI DONAT BUYURTMA #{order_id}</b>\n"
            f"━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 <b>Foydalanuvchi:</b> {message.from_user.full_name}\n"
            f"📱 <b>Telegram:</b> {tg_link}\n"
            f"🆔 <b>TG User ID:</b> <code>{user_id}</code>\n\n"
            f"🎮 <b>O'yin:</b> {d['oyun']}\n"
            f"💎 <b>Paket:</b> {d['donat_miqdor']}\n"
            f"🎯 <b>O'yin (Player) ID:</b> <code>{d['player_id']}</code>\n"
            f"💰 <b>Narx:</b> {d['narx']} TJS\n"
            f"📅 <b>Vaqt:</b> {order['sana']}"
        )
        for admin_id in ADMIN_IDS:
            try:
                bot.send_photo(
                    admin_id, photo_id,
                    caption=admin_caption,
                    reply_markup=kb_admin
                )
            except Exception as e:
                logger.error(f"Admin ga xabar: {e}")
        return

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    🖱 CALLBACK HANDLERLARI                            ║
# ╚══════════════════════════════════════════════════════════════════════╝

@bot.callback_query_handler(func=lambda c: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data

    try:
        # PDF stil tanlash
        if data.startswith("pdf_style_"):
            style = data.replace("pdf_style_", "")
            style_names = {
                "standart": "📝 Standart",
                "qiyshiq": "✏️ Qiyshiq (Italic)",
                "chunmaydigan": "🔤 Chunmaydigan (Bold)",
                "classic": "📖 Classic",
                "pro": "💼 Pro",
            }
            style_label = style_names.get(style, style)
            set_state(user_id, "pdf_text", {"style": style})
            bot.answer_callback_query(call.id, f"✅ {style_label} tanlandi!")
            try:
                bot.edit_message_text(
                    f"📄 <b>PDF YARATISH</b>\n\n"
                    f"🎨 Tanlangan stil: <b>{style_label}</b>\n\n"
                    f"Endi hujjatga aylantirmoqchi bo'lgan matnni yozing:",
                    call.message.chat.id, call.message.message_id
                )
            except Exception:
                bot.send_message(user_id,
                    f"🎨 Stil: <b>{style_label}</b>\n\nMatnni yozing:")
            return

        # Obuna tekshirish
        if data == "check_sub":
            is_sub, not_sub = check_subscription(user_id)
            if is_sub:
                bot.answer_callback_query(call.id, "✅ Ajoyib! Obunalar tasdiqlandi!")
                try:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                except Exception:
                    pass
                # start xabarini to'g'ridan-to'g'ri yuborish
                user = get_user(user_id)
                full_name = call.from_user.full_name or "Mehmon"
                prem = is_premium(user_id)
                status_emoji = "💎" if prem else "👑" if is_admin(user_id) else "👤"
                status_name = "Premium" if prem else "Admin" if is_admin(user_id) else "Free"
                welcome = (
                    f"🚀 <b>SUPER BOT</b> — Hamma narsa bitta joyda!\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"👋 Xush kelibsiz, <b>{full_name}</b>!\n"
                    f"{status_emoji} Status: <b>{status_name}</b>\n\n"
                    f"🎬 <b>Kinolar</b> — kod orqali kino oling\n"
                    f"🎵 <b>Musiqa</b> — musiqa tinglang\n"
                    f"💳 <b>Donat</b> — o'yinlarga donat xizmati\n"
                    f"📥 <b>Video Yuklab Olish</b> — Instagram\n"
                    f"🤖 <b>AI Rasm</b> — prompt orqali rasm oling\n"
                    f"📄 <b>PDF/Fayl</b> — matndan hujjat yarating\n\n"
                    f"💎 Free: <i>ba'zi funksiyalar cheklangan</i>\n"
                    f"👑 Premium: <i>hamma narsa cheksiz!</i>"
                )
                bot.send_message(user_id, welcome, reply_markup=main_keyboard(user_id))
            else:
                bot.answer_callback_query(call.id, "❌ Hali obuna bo'lmadingiz!")
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                              reply_markup=get_sub_keyboard(not_sub))
            return

        # Kino olish
        if data.startswith("get_movie_"):
            code = data.replace("get_movie_", "")
            movie = get_movie(code)
            if movie:
                send_movie_to_user(user_id, movie, user_id)
                bot.answer_callback_query(call.id)
            else:
                bot.answer_callback_query(call.id, "❌ Kino topilmadi!")
            return

        # Musiqa olish
        if data.startswith("get_music_"):
            code = data.replace("get_music_", "")
            music = get_music(code)
            if music:
                send_music_to_user(user_id, music, user_id)
                bot.answer_callback_query(call.id)
            else:
                bot.answer_callback_query(call.id, "❌ Musiqa topilmadi!")
            return

        # Kategoriya
        if data.startswith("cat_"):
            category = data.replace("cat_", "")
            movies = get_movies_by_category(category)
            if not movies:
                bot.answer_callback_query(call.id, f"'{category}' da kino yo'q!")
                return
            kb = InlineKeyboardMarkup(row_width=1)
            msg = f"📂 <b>{category}</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
            for m in movies:
                badge = "💎" if m["is_premium"] else "🆓"
                msg += f"{badge} <b>{m['title']}</b> | 👁 {m['views']} | <code>{m['code']}</code>\n"
                kb.add(InlineKeyboardButton(f"▶️ {m['title'][:35]}", callback_data=f"get_movie_{m['code']}"))
            bot.answer_callback_query(call.id)
            bot.send_message(user_id, msg, reply_markup=kb)
            return

        # Reyting
        if data.startswith("rate_"):
            parts = data.split("_")
            itype, code, rat = parts[1], parts[2], int(parts[3])
            conn = get_conn()
            try:
                conn.execute(
                    "INSERT OR REPLACE INTO ratings (user_id,item_code,item_type,rating) VALUES (?,?,?,?)",
                    (user_id, code, itype, rat)
                )
                conn.commit()
            finally:
                conn.close()
            bot.answer_callback_query(call.id, f"✅ Bahoyingiz: {'⭐' * rat}")
            return

        # Donat o'yin tanlash
        if data.startswith("donat_") and data[6:] in DONATLAR:
            tur = data[6:]
            donat = DONATLAR[tur]
            kb = InlineKeyboardMarkup(row_width=1)
            for i, v in enumerate(donat["variantlar"]):
                kb.add(InlineKeyboardButton(f"{v['miqdor']} — {v['narx']} TJS", callback_data=f"dv_{tur}_{i}"))
            kb.add(InlineKeyboardButton("🔙 Orqaga", callback_data="back_donat"))
            bot.answer_callback_query(call.id)
            bot.edit_message_text(
                f"{donat['nomi']}\n\n🛒 Miqdorni tanlang:",
                call.message.chat.id, call.message.message_id, reply_markup=kb
            )
            return

        # Donat variant tanlash
        if data.startswith("dv_"):
            # format: dv_{tur}_{idx} — tur ichida _ bo'lishi mumkin, shuning uchun oxiridan ajratamiz
            last_underscore = data.rfind("_")
            tur = data[3:last_underscore]
            try:
                idx = int(data[last_underscore + 1:])
            except ValueError:
                bot.answer_callback_query(call.id, "❌ Xatolik!")
                return
            if tur not in DONATLAR:
                bot.answer_callback_query(call.id, "❌ Donat turi topilmadi!")
                return
            variant = DONATLAR[tur]["variantlar"][idx]
            set_state(user_id, "donat_player_id", {
                "donat_tur": DONATLAR[tur]["nomi"],
                "oyun": DONATLAR[tur]["oyun"],
                "donat_miqdor": variant["miqdor"],
                "narx": variant["narx"]
            })
            bot.answer_callback_query(call.id)
            bot.edit_message_text(
                f"✅ Tanlangan: <b>{variant['miqdor']}</b> — {variant['narx']} TJS\n\n"
                f"📲 <b>{DONATLAR[tur]['oyun']}</b> Player ID ni yuboring:",
                call.message.chat.id, call.message.message_id
            )
            return

        # Orqaga donat
        if data == "back_donat":
            bot.answer_callback_query(call.id)
            bot.edit_message_text(
                "🎮 <b>DONAT BO'LIMI</b>\n\nO'yinni tanlang:",
                call.message.chat.id, call.message.message_id,
                reply_markup=donat_oyun_keyboard()
            )
            return

        # Orqaga main
        if data == "back_main":
            bot.answer_callback_query(call.id)
            clear_state(user_id)
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass
            bot.send_message(user_id, "🏠 Bosh menyu", reply_markup=main_keyboard(user_id))
            return

        # Download bekor qilish
        if data == "dl_cancel":
            clear_state(user_id)
            bot.answer_callback_query(call.id, "❌ Bekor qilindi")
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass
            bot.send_message(user_id, "📥 <b>Video Yuklab Olish</b>\n\nYangi havola yuboring:", reply_markup=main_keyboard(user_id))
            return

        # Download video
        if data == "dl_video":
            state = get_state(user_id)
            url = state.get("data", {}).get("url")
            if not url:
                bot.answer_callback_query(call.id, "❌ URL topilmadi!")
                return
            clear_state(user_id)
            bot.answer_callback_query(call.id, "⬇️ Yuklab olinmoqda...")
            bot.edit_message_text("⏳ Video yuklab olinmoqda (1-3 daqiqa)...", call.message.chat.id, call.message.message_id)

            def dl_and_send():
                path = download_video(url, user_id, is_audio=False)
                if path and os.path.exists(path):
                    try:
                        with open(path, "rb") as f:
                            bot.send_video(user_id, f, caption="✅ Video tayyor!")
                        os.remove(path)
                    except Exception as e:
                        bot.send_message(user_id, f"❌ Yuborishda xato: {e}\n\n💡 Fayl 50MB dan katta bo'lishi mumkin.")
                else:
                    bot.send_message(user_id, "❌ Video yuklab olishda xatolik! Havolani tekshiring.")
                try:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                except Exception:
                    pass
            t = threading.Thread(target=dl_and_send, daemon=True)
            t.start()
            return

        if data == "dl_audio":
            state = get_state(user_id)
            url = state.get("data", {}).get("url")
            if not url:
                bot.answer_callback_query(call.id, "❌ URL topilmadi!")
                return
            clear_state(user_id)
            bot.answer_callback_query(call.id, "⬇️ Yuklab olinmoqda...")
            bot.edit_message_text("⏳ Audio yuklab olinmoqda...", call.message.chat.id, call.message.message_id)

            def dl_audio_and_send():
                path = download_video(url, user_id, is_audio=True)
                # yt-dlp ba'zan extension o'zgartiradi
                if not path or not os.path.exists(path):
                    # .mp3 bo'lmasligi mumkin
                    base = path.rsplit(".", 1)[0] if path else None
                    for ext in [".mp3", ".m4a", ".webm", ".opus"]:
                        if base and os.path.exists(base + ext):
                            path = base + ext
                            break
                if path and os.path.exists(path):
                    try:
                        with open(path, "rb") as f:
                            bot.send_audio(user_id, f, caption="✅ Audio tayyor!")
                        os.remove(path)
                    except Exception as e:
                        bot.send_message(user_id, f"❌ Yuborishda xato: {e}")
                else:
                    bot.send_message(user_id, "❌ Audio yuklab olishda xatolik!")
                try:
                    bot.delete_message(call.message.chat.id, call.message.message_id)
                except Exception:
                    pass
            t = threading.Thread(target=dl_audio_and_send, daemon=True)
            t.start()
            return

        # Premium info
        if data == "premium_info":
            kb = InlineKeyboardMarkup()
            kb.add(InlineKeyboardButton("📞 Admin", url=f"https://t.me/{ADMIN_USERNAME.lstrip('@')}"))
            msg = (
                "💎 <b>PREMIUM TARIF</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
                "✅ Barcha kinolar va musiqalar\n"
                "✅ YouTube/Instagram yuklash\n"
                "✅ AI Rasm — cheksiz\n"
                "✅ Reklamasiz\n\n"
                "💰 <b>Narxlar:</b>\n"
            )
            for k, v in PREMIUM_NARXLAR.items():
                msg += f"• {v['nomi']}: <b>{v['narx']} TJS</b>\n"
            msg += f"\n📞 To'lov: {ADMIN_USERNAME}"
            bot.answer_callback_query(call.id)
            bot.send_message(user_id, msg, reply_markup=kb)
            return

        # Kunlik bonus
        if data == "daily_bonus":
            user = get_user(user_id)
            today = datetime.now().strftime("%Y-%m-%d")
            last = user.get("last_bonus_date")
            if last == today:
                bot.answer_callback_query(call.id, "⏰ Bugun allaqachon oldingiz!")
            else:
                bonus_tjs = 0.20 if is_premium(user_id) else 0.10
                add_user_balance(user_id, bonus_tjs)
                update_user(user_id, last_bonus_date=today)
                bot.answer_callback_query(call.id, f"🎁 +{bonus_tjs:.2f} TJS balansga qo'shildi!")
            return

        # Admin kategoriya tanlash (kino qo'shish)
        if data.startswith("acat_") and is_admin(user_id):
            cat = data.replace("acat_", "")
            state = get_state(user_id)
            if state.get("state") == "add_movie_category":
                d = state["data"]; d["category"] = cat
                set_state(user_id, "add_movie_premium", d)
                kb = InlineKeyboardMarkup(row_width=2)
                kb.add(InlineKeyboardButton("💎 Ha, Premium", callback_data="movprem_1"),
                       InlineKeyboardButton("🆓 Yo'q, Bepul", callback_data="movprem_0"))
                bot.answer_callback_query(call.id, f"✅ Kategoriya: {cat}")
                bot.send_message(user_id, f"5️⃣ Bu kino Premiummi?", reply_markup=kb)
            return

        # Kino premium tanlash
        if data.startswith("movprem_") and is_admin(user_id):
            prem_val = int(data.replace("movprem_", ""))
            state = get_state(user_id)
            d = state.get("data", {})
            d["is_premium"] = prem_val
            set_state(user_id, "add_movie_file", d)
            bot.answer_callback_query(call.id)
            bot.send_message(user_id, "6️⃣ Kino videosini yuboring:")
            return

        # Musiqa premium tanlash
        if data.startswith("musprem_") and is_admin(user_id):
            prem_val = int(data.replace("musprem_", ""))
            state = get_state(user_id)
            d = state.get("data", {})
            d["is_premium"] = prem_val
            set_state(user_id, "add_music_file", d)
            bot.answer_callback_query(call.id)
            bot.send_message(user_id, "5️⃣ Musiqa (audio) faylini yuboring:")
            return

        # Donat tasdiqlash
        if data.startswith("confirm_") and is_admin(user_id):
            order_id = data.replace("confirm_", "")
            order = get_order(order_id)
            if not order:
                bot.answer_callback_query(call.id, "Buyurtma topilmadi!")
                return
            update_order_status(order_id, "tasdiqlangan")
            bot.answer_callback_query(call.id, "✅ Tasdiqlandi!")
            try:
                bot.send_message(
                    order["user_id"],
                    f"🎉 <b>Buyurtmangiz tasdiqlandi!</b>\n\n"
                    f"🔢 Buyurtma #{order_id}\n"
                    f"🎮 {order['oyun']} — {order['donat_miqdor']}\n"
                    f"🆔 Player ID: {order['player_id']}\n\n"
                    f"✅ Donat hisobingizga o'tkazildi!"
                )
            except Exception:
                pass
            try:
                bot.edit_message_caption(
                    (call.message.caption or "") + "\n\n✅ <b>TASDIQLANDI</b>",
                    call.message.chat.id, call.message.message_id
                )
            except Exception:
                pass
            return

        # Donat bekor qilish
        if data.startswith("cancel_") and is_admin(user_id):
            order_id = data.replace("cancel_", "")
            order = get_order(order_id)
            if not order:
                bot.answer_callback_query(call.id, "Buyurtma topilmadi!")
                return
            update_order_status(order_id, "bekor_qilingan")
            bot.answer_callback_query(call.id, "❌ Bekor qilindi!")
            try:
                bot.send_message(
                    order["user_id"],
                    f"❌ <b>Buyurtmangiz bekor qilindi.</b>\n\n"
                    f"🔢 Buyurtma #{order_id}\n"
                    f"Muammo uchun: {ADMIN_USERNAME}"
                )
            except Exception:
                pass
            try:
                bot.edit_message_caption(
                    (call.message.caption or "") + "\n\n❌ <b>BEKOR QILINDI</b>",
                    call.message.chat.id, call.message.message_id
                )
            except Exception:
                pass
            return

        # Balans so'rovini tasdiqlash
        if data.startswith("topup_confirm_") and is_admin(user_id):
            req_id = data.replace("topup_confirm_", "")
            req = get_balance_request(req_id)
            if not req:
                bot.answer_callback_query(call.id, "So'rov topilmadi!")
                return
            if req["status"] != "kutilmoqda":
                bot.answer_callback_query(call.id, "Bu so'rov allaqachon ko'rib chiqilgan!")
                return
            update_balance_request_status(req_id, "tasdiqlangan")
            add_user_balance(req["user_id"], req["amount"])
            new_bal = get_user_balance(req["user_id"])
            bot.answer_callback_query(call.id, "✅ Tasdiqlandi!")
            try:
                bot.send_message(
                    req["user_id"],
                    f"✅ <b>Balans to'ldirildi!</b>\n\n"
                    f"💰 +{req['amount']:.2f} TJS qo'shildi\n"
                    f"💳 Joriy balans: <b>{new_bal:.2f} TJS</b>"
                )
            except Exception:
                pass
            try:
                bot.edit_message_caption(
                    (call.message.caption or "") + f"\n\n✅ <b>TASDIQLANDI | +{req['amount']:.2f} TJS</b>",
                    call.message.chat.id, call.message.message_id
                )
            except Exception:
                pass
            return

        # Balans so'rovini rad etish
        if data.startswith("topup_cancel_") and is_admin(user_id):
            req_id = data.replace("topup_cancel_", "")
            req = get_balance_request(req_id)
            if not req:
                bot.answer_callback_query(call.id, "So'rov topilmadi!")
                return
            if req["status"] != "kutilmoqda":
                bot.answer_callback_query(call.id, "Bu so'rov allaqachon ko'rib chiqilgan!")
                return
            update_balance_request_status(req_id, "rad_etilgan")
            bot.answer_callback_query(call.id, "❌ Rad etildi!")
            try:
                bot.send_message(
                    req["user_id"],
                    f"❌ <b>Balans so'rovingiz rad etildi.</b>\n\n"
                    f"💵 Miqdor: {req['amount']:.2f} TJS\n"
                    f"Muammo uchun: {ADMIN_USERNAME}"
                )
            except Exception:
                pass
            try:
                bot.edit_message_caption(
                    (call.message.caption or "") + "\n\n❌ <b>RAD ETILDI</b>",
                    call.message.chat.id, call.message.message_id
                )
            except Exception:
                pass
            return

        # Balans orqali premium topup tugmasi (profil da)
        if data == "topup_balance":
            balance = get_user_balance(user_id)
            kb = InlineKeyboardMarkup(row_width=1)
            for i, k in enumerate(KARTALAR):
                kb.add(InlineKeyboardButton(f"{k['nomi']}", callback_data=f"select_card_{i}"))
            kb.add(InlineKeyboardButton("🔙 Bosh menyuga", callback_data="back_main"))
            bot.answer_callback_query(call.id)
            bot.send_message(
                user_id,
                f"💰 <b>BALANS TO'LDIRISH</b>\n"
                f"━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"Joriy balans: <b>{balance:.2f} TJS</b>\n\n"
                f"1️⃣ Avval kartani tanlang:",
                reply_markup=kb
            )
            return

        # Karta tanlash
        if data.startswith("select_card_"):
            try:
                idx = int(data.replace("select_card_", ""))
                k = KARTALAR[idx]
                set_state(user_id, "topup_amount", {"card_idx": idx})
                bot.answer_callback_query(call.id)
                bot.send_message(
                    user_id,
                    f"✅ Tanlangan karta: <b>{k['nomi']}</b>\n\n"
                    f"💳 Karta raqami: <code>{k['raqam']}</code>\n"
                    f"👤 Egasi: <b>{k['egasi']}</b>\n\n"
                    f"2️⃣ Ushbu kartaga pul o'tkazing\n\n"
                    f"💵 Qancha o'tkazayotganingizni yozing (TJS):\n"
                    f"Misol: <code>10</code>"
                )
            except (ValueError, IndexError):
                bot.answer_callback_query(call.id, "❌ Xatolik!")
            return

        # Avto premium sotib olish
        if data == "auto_premium":
            balance = get_user_balance(user_id)
            kb = InlineKeyboardMarkup(row_width=1)
            for k, v in PREMIUM_NARXLAR.items():
                status = "✅" if balance >= v["narx"] else "❌"
                kb.add(InlineKeyboardButton(
                    f"{status} {v['nomi']} — {v['narx']} TJS",
                    callback_data=f"buy_premium_{k}"
                ))
            bot.answer_callback_query(call.id)
            bot.send_message(
                user_id,
                f"💎 <b>PREMIUM SOTIB OLISH</b>\n\n"
                f"💰 Balans: <b>{balance:.2f} TJS</b>\n\n"
                f"✅ — yetarli | ❌ — yetarli emas\n\n"
                f"Tarifni tanlang:",
                reply_markup=kb
            )
            return

        # Premium sotib olish (avto)
        if data.startswith("buy_premium_"):
            key = data.replace("buy_premium_", "")
            if key not in PREMIUM_NARXLAR:
                bot.answer_callback_query(call.id, "❌ Tarif topilmadi!")
                return
            v = PREMIUM_NARXLAR[key]
            balance = get_user_balance(user_id)
            if balance < v["narx"]:
                bot.answer_callback_query(call.id, f"❌ Balans yetarli emas! Kerak: {v['narx']} TJS, sizda: {balance:.2f} TJS")
                return
            # Balansdan ayir
            ok = deduct_user_balance(user_id, v["narx"])
            if not ok:
                bot.answer_callback_query(call.id, "❌ Balans yetarli emas!")
                return
            # Premium ber
            until = (datetime.now() + timedelta(days=v["kun"])).strftime("%Y-%m-%d")
            update_user(user_id, status="premium", premium_until=until)
            new_bal = get_user_balance(user_id)
            bot.answer_callback_query(call.id, f"✅ {v['nomi']} faollashtirildi!")
            bot.send_message(
                user_id,
                f"🎉 <b>Premium faollashtirildi!</b>\n\n"
                f"💎 Tarif: {v['nomi']}\n"
                f"📅 Muddat: {until} gacha\n"
                f"💰 Qolgan balans: <b>{new_bal:.2f} TJS</b>\n\n"
                f"✅ Barcha premium imkoniyatlar ochiq!"
            )
            return

        # Gift sotib olish
        if data.startswith("gift_confirm_"):
            try:
                idx = int(data.replace("gift_confirm_", ""))
                g = GIFTLAR[idx]
                balance = get_user_balance(user_id)
                if balance < g["narx_tjs"]:
                    bot.answer_callback_query(call.id, "❌ Balans yetarli emas!")
                    return
                ok = deduct_user_balance(user_id, g["narx_tjs"])
                if not ok:
                    bot.answer_callback_query(call.id, "❌ Balans yetarli emas!")
                    return
                new_bal = get_user_balance(user_id)
                bot.answer_callback_query(call.id, f"✅ {g['nomi']} sotib olindi!")
                try:
                    bot.edit_message_text(
                        f"🎉 <b>Gift muvaffaqiyatli sotib olindi!</b>\n\n"
                        f"{g['emoji']} {g['nomi']}\n"
                        f"⭐ {g['stars']} Telegram Stars\n"
                        f"💰 To'landi: {g['narx_tjs']} TJS\n"
                        f"💳 Qolgan balans: <b>{new_bal:.2f} TJS</b>\n\n"
                        f"📌 Gift so'rovingiz adminga yuborildi!",
                        call.message.chat.id, call.message.message_id
                    )
                except Exception:
                    pass
                for admin_id in ADMIN_IDS:
                    try:
                        u = get_user(user_id)
                        bot.send_message(
                            admin_id,
                            f"🎁 <b>Yangi Gift so'rovi</b>\n\n"
                            f"👤 {u.get('full_name','')} (@{u.get('username','yoq')})\n"
                            f"🆔 User ID: <code>{user_id}</code>\n"
                            f"{g['emoji']} {g['nomi']} — ⭐{g['stars']}\n"
                            f"💰 To'landi: {g['narx_tjs']} TJS\n\n"
                            f"⚡ Ushbu foydalanuvchiga {g['stars']} Stars yuboring!"
                        )
                    except Exception:
                        pass
            except (ValueError, IndexError):
                bot.answer_callback_query(call.id, "❌ Xatolik!")
            return

        if data.startswith("gift_"):
            try:
                idx = int(data.replace("gift_", ""))
                if idx < 0 or idx >= len(GIFTLAR):
                    bot.answer_callback_query(call.id, "❌ Gift topilmadi!")
                    return
                g = GIFTLAR[idx]
                balance = get_user_balance(user_id)
                if balance < g["narx_tjs"]:
                    bot.answer_callback_query(call.id, f"❌ Balans yetarli emas! Kerak: {g['narx_tjs']} TJS, sizda: {balance:.2f} TJS")
                    return
                kb = InlineKeyboardMarkup(row_width=2)
                kb.add(
                    InlineKeyboardButton("✅ Ha, sotib olaman", callback_data=f"gift_confirm_{idx}"),
                    InlineKeyboardButton("❌ Bekor", callback_data="gift_cancel")
                )
                bot.answer_callback_query(call.id)
                bot.send_message(
                    user_id,
                    f"🎁 <b>Gift sotib olish</b>\n\n"
                    f"{g['emoji']} {g['nomi']}\n"
                    f"⭐ {g['stars']} Telegram Stars\n"
                    f"💰 Narx: <b>{g['narx_tjs']} TJS</b>\n"
                    f"💳 Sizning balans: <b>{balance:.2f} TJS</b>\n\n"
                    f"❓ Tasdiqlaysizmi?",
                    reply_markup=kb
                )
            except (ValueError, IndexError):
                bot.answer_callback_query(call.id, "❌ Xatolik!")
            return

        if data == "gift_cancel":
            bot.answer_callback_query(call.id, "❌ Bekor qilindi")
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass
            return

        # Status berish
        if data.startswith("setst_") and is_admin(user_id):
            parts = data.split("_")
            target, new_status = int(parts[1]), parts[2]
            update_user(target, status=new_status)
            bot.answer_callback_query(call.id, f"✅ Status: {new_status}")
            bot.edit_message_text(
                f"✅ <code>{target}</code> foydalanuvchiga <b>{new_status}</b> statusli berildi!",
                call.message.chat.id, call.message.message_id
            )
            clear_state(user_id)
            try:
                bot.send_message(target, f"🎉 Statusingiz <b>{new_status}</b> ga o'zgartirildi!")
            except Exception:
                pass
            return

    except Exception as e:
        logger.error(f"Callback xatosi [{data}]: {e}")
        try:
            bot.answer_callback_query(call.id, "❌ Xatolik!")
        except Exception:
            pass

# (calculator_handler endi text_handler ichida)

# (topup_amount_handler endi text_handler ichida)

# (topup_screenshot_handler endi file_handler ichida)


# (donat_player_id_handler endi text_handler ichida)

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    👑 ADMIN PANEL                                     ║
# ╚══════════════════════════════════════════════════════════════════════╝

def show_admin_panel(user_id):
    stats = get_stats()
    pending = len(get_pending_orders())
    conn = get_conn()
    pending_topups = conn.execute("SELECT COUNT(*) FROM balance_requests WHERE status='kutilmoqda'").fetchone()[0]
    conn.close()
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        KeyboardButton("➕ Kino Qo'shish"),
        KeyboardButton("🗑 Kino O'chirish")
    )
    kb.add(
        KeyboardButton("🎵 Musiqa Qo'shish"),
        KeyboardButton("🗑 Musiqa O'chirish")
    )
    kb.add(
        KeyboardButton("📢 Broadcast"),
        KeyboardButton("💎 Premium Berish")
    )
    kb.add(
        KeyboardButton("👥 Status Berish"),
        KeyboardButton(f"⏳ Buyurtmalar ({pending})")
    )
    kb.add(KeyboardButton(f"💰 Balans So'rovlari ({pending_topups})"))
    kb.add(KeyboardButton("🔙 Bosh Menyu"))
    bot.send_message(
        user_id,
        f"👑 <b>ADMIN PANEL</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👥 Foydalanuvchilar: <b>{stats['total']}</b>\n"
        f"💎 Premium: <b>{stats['premium']}</b>\n"
        f"🎬 Kinolar: <b>{stats['movies']}</b>\n"
        f"🎵 Musiqalar: <b>{stats['musics']}</b>\n"
        f"✅ Tasdiqlangan buyurtmalar: <b>{stats['confirmed_orders']}</b>\n"
        f"⏳ Kutilayotgan buyurtmalar: <b>{pending}</b>\n"
        f"💰 Kutilayotgan balans: <b>{pending_topups}</b>",
        reply_markup=kb
    )

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    📢 BROADCAST                                       ║
# ╚══════════════════════════════════════════════════════════════════════╝

def do_broadcast(admin_id, text):
    def _run():
        users = get_all_users()
        total = len(users)
        success = failed = 0
        bot.send_message(admin_id, f"📢 Broadcast boshlandi...\n👥 Jami: <b>{total}</b>")
        for uid in users:
            try:
                bot.send_message(uid, f"📢 <b>E'lon</b>\n\n{text}")
                success += 1
                time.sleep(0.05)
            except Exception:
                failed += 1
        bot.send_message(
            admin_id,
            f"✅ <b>Broadcast yakunlandi!</b>\n\n"
            f"✅ Muvaffaqiyatli: <b>{success}</b>\n"
            f"❌ Xatolik: <b>{failed}</b>\n"
            f"📊 Jami: <b>{total}</b>"
        )
    threading.Thread(target=_run, daemon=True).start()

# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    🚀 ASOSIY FUNKSIYA                                 ║
# ╚══════════════════════════════════════════════════════════════════════╝

def main():
    logger.info("🚀 SUPER BOT ishga tushmoqda...")
    create_database()
    logger.info(f"👑 Adminlar: {ADMIN_IDS}")
    logger.info(f"📦 yt-dlp: {'✅' if YT_DLP_AVAILABLE else '❌'}")
    logger.info(f"📄 ReportLab: {'✅' if REPORTLAB_AVAILABLE else '❌'}")
    logger.info(f"🌐 Requests: {'✅' if REQUESTS_AVAILABLE else '❌'}")

    logger.info("✅ Bot muvaffaqiyatli ishga tushdi!")
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=30, skip_pending=True)
    except Exception as e:
        logger.critical(f"❌ Bot to'xtadi: {e}")
        raise

if __name__ == "__main__":
    main()

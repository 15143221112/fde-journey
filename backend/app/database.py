"""FDE 学习卡片工具 —— SQLite 数据库层

单文件 SQLite，零配置。数据存于 backend/data/fde.db。
"""

import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# 数据库文件位置，可通过环境变量 DB_PATH 覆盖（Docker 下指向数据卷）
DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "fde.db"
DB_PATH = os.environ.get("DB_PATH", str(DEFAULT_DB))


def get_conn() -> sqlite3.Connection:
    """建立数据库连接（每请求新建，保证线程安全）。"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """建表 + 种子数据（幂等）。"""
    Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = get_conn()
    try:
        conn.executescript(
            """
            -- 学习卡片表
            CREATE TABLE IF NOT EXISTS cards (
              id INTEGER PRIMARY KEY,
              day_number INTEGER UNIQUE,
              week_number INTEGER,
              title TEXT,
              category TEXT,
              content_json TEXT,
              is_weekend INTEGER DEFAULT 0,
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- 打卡记录表（含笔记）
            CREATE TABLE IF NOT EXISTS checkins (
              id INTEGER PRIMARY KEY,
              card_id INTEGER REFERENCES cards(id),
              checked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              notes TEXT
            );

            -- 收藏表
            CREATE TABLE IF NOT EXISTS favorites (
              id INTEGER PRIMARY KEY,
              card_id INTEGER REFERENCES cards(id),
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- 资料表
            CREATE TABLE IF NOT EXISTS resources (
              id INTEGER PRIMARY KEY,
              title TEXT NOT NULL,
              type TEXT NOT NULL,            -- link / file / code / video / note
              url TEXT,
              file_path TEXT,
              file_name TEXT,
              code_content TEXT,
              note_content TEXT,
              category TEXT NOT NULL,
              tags TEXT,
              summary TEXT,
              related_week INTEGER,
              related_card_id INTEGER REFERENCES cards(id),
              read_status TEXT DEFAULT 'unread',
              created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
              updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            -- 索引
            CREATE INDEX IF NOT EXISTS idx_cards_day ON cards(day_number);
            CREATE INDEX IF NOT EXISTS idx_resources_cat ON resources(category);
            CREATE INDEX IF NOT EXISTS idx_resources_status ON resources(read_status);
            """
        )
        conn.commit()

        # 种子卡片（仅当表为空时写入）
        count = conn.execute("SELECT COUNT(*) AS c FROM cards").fetchone()["c"]
        if count == 0:
            _seed_cards(conn)
            conn.commit()
    finally:
        conn.close()


def _seed_cards(conn: sqlite3.Connection) -> None:
    """从 cards_seed.json 写入 84 张卡片。"""
    seed_file = Path(__file__).resolve().parent.parent / "cards_seed.json"
    if not seed_file.exists():
        raise FileNotFoundError(f"缺少种子文件: {seed_file}")
    import json

    cards = json.loads(seed_file.read_text(encoding="utf-8"))
    for c in cards:
        conn.execute(
            """
            INSERT INTO cards (day_number, week_number, title, category, content_json, is_weekend, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                c["day"],
                c["week"],
                c["title"],
                c.get("category", "其他"),
                json.dumps(
                    {
                        "title": c.get("title", ""),
                        "points": c.get("points", []),
                        "exercise": c.get("exercise", ""),
                        "rice_project": c.get("rice_project", ""),
                        "weekend_note": c.get("weekend_note", ""),
                    },
                    ensure_ascii=False,
                ),
                1 if c.get("is_weekend") else 0,
                datetime.now().isoformat(),
            ),
        )


def today_card_day() -> int:
    """返回今天对应的卡片天数。

    学习周期 2026-10-27 起，共 84 天。超过 84 天则固定返回最后一天（第84天）。
    """
    start = datetime(2026, 10, 27)
    today = datetime.now()
    day = (today.date() - start.date()).days + 1
    if day < 1:
        day = 1
    if day > 84:
        day = 84
    return day

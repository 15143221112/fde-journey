"""卡片相关接口。"""
import json

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from ..database import get_conn, today_card_day

router = APIRouter(prefix="/api/cards", tags=["cards"])


def _card_row(row):
    c = dict(row)
    try:
        c["content"] = json.loads(c.pop("content_json"))
    except Exception:
        c["content"] = {}
    return c


@router.get("/today")
def get_today():
    """返回今日应学的卡片 + 周次 + 总进度 + 今日是否已打卡 + 是否收藏。"""
    day = today_card_day()
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM cards WHERE day_number = ?", (day,)
        ).fetchone()
        if not row:
            raise HTTPException(404, "今日卡片不存在")

        total = conn.execute("SELECT COUNT(*) AS c FROM cards").fetchone()["c"]
        done = conn.execute("SELECT COUNT(*) AS c FROM checkins").fetchone()["c"]
        # 今日打卡：当天有记录（按自然日）
        today_str = __import__("datetime").datetime.now().strftime("%Y-%m-%d")
        today_checked = conn.execute(
            "SELECT COUNT(*) AS c FROM checkins WHERE date(checked_at)=? AND card_id=?",
            (today_str, row["id"]),
        ).fetchone()["c"]
        fav = conn.execute(
            "SELECT COUNT(*) AS c FROM favorites WHERE card_id=?", (row["id"],)
        ).fetchone()["c"]

        card = _card_row(row)

        # 连续打卡天数
        from datetime import date, timedelta
        checked_days = {r["d"] for r in conn.execute("SELECT date(checked_at) AS d FROM checkins").fetchall()}
        streak = 0
        cur = date.today()
        if cur.isoformat() not in checked_days:
            cur = cur - timedelta(days=1)
        while cur.isoformat() in checked_days:
            streak += 1
            cur -= timedelta(days=1)

        return {
            "card": card,
            "week_number": row["week_number"],
            "week_topic": _week_topic(row["week_number"]),
            "total_weeks": 12,
            "progress": {"done": done, "total": total},
            "today_checked": today_checked > 0,
            "is_favorite": fav > 0,
            "streak": streak,
            "day": day,
        }
    finally:
        conn.close()


@router.get("")
def list_cards(
    search: str = "",
    category: str = "",
    q_day: int = Query(None, alias="day"),
):
    """全部卡片浏览：支持搜索、分类筛选、按天数定位。"""
    conn = get_conn()
    try:
        sql = "SELECT * FROM cards WHERE 1=1"
        params = []
        if search:
            sql += " AND (title LIKE ? OR content_json LIKE ?)"
            params += [f"%{search}%", f"%{search}%"]
        if category:
            sql += " AND category = ?"
            params.append(category)
        if q_day:
            sql += " AND day_number = ?"
            params.append(q_day)
        sql += " ORDER BY day_number"
        rows = conn.execute(sql, params).fetchall()
        return [_card_row(r) for r in rows]
    finally:
        conn.close()


@router.get("/timeline")
def timeline():
    """12周时间线，按周聚合。"""
    conn = get_conn()
    try:
        rows = conn.execute("SELECT * FROM cards ORDER BY day_number").fetchall()
        # 完成状态：按 card_id 是否在 checkins
        checked = {r["card_id"] for r in conn.execute("SELECT card_id FROM checkins").fetchall()}
        weeks = []
        for w in range(1, 13):
            week_cards = [r for r in rows if r["week_number"] == w]
            weeks.append(
                {
                    "week": w,
                    "week_topic": _week_topic(w),
                    "cards": [
                        {
                            "id": r["id"],
                            "day": r["day_number"],
                            "title": r["title"],
                            "is_weekend": bool(r["is_weekend"]),
                            "done": r["id"] in checked,
                        }
                        for r in week_cards
                    ],
                }
            )
        return weeks
    finally:
        conn.close()


@router.get("/categories")
def categories():
    conn = get_conn()
    try:
        rows = conn.execute("SELECT DISTINCT category FROM cards").fetchall()
        return [r["category"] for r in rows]
    finally:
        conn.close()


@router.get("/{card_id}")
def get_card(card_id: int):
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM cards WHERE id=?", (card_id,)).fetchone()
        if not row:
            raise HTTPException(404, "卡片不存在")
        # 关联资料
        res = conn.execute(
            "SELECT id,title,type,category,read_status FROM resources WHERE related_card_id=?",
            (card_id,),
        ).fetchall()
        card = _card_row(row)
        card["related_resources"] = [dict(r) for r in res]
        return card
    finally:
        conn.close()


def _week_topic(week: int) -> str:
    topics = {
        1: "Python 基础热身",
        2: "Python 进阶与 HTTP/API",
        3: "LangChain 1.0 · 起步",
        4: "LangChain 1.0 · 组件实战",
        5: "LangGraph · 图与状态",
        6: "LangGraph · 路由与实战",
        7: "RAG · 检索增强",
        8: "RAG · 评测与优化",
        9: "安全合规",
        10: "部署运维 · 基础",
        11: "部署运维 · 生产实践",
        12: "FDE 认证冲刺",
    }
    return topics.get(week, "")

"""统计仪表盘接口。"""
from datetime import date, datetime, timedelta

from fastapi import APIRouter

from ..database import get_conn

router = APIRouter(prefix="/api/stats", tags=["stats"])


def _streak(conn, checked_days) -> int:
    """连续打卡天数：从今天（或昨天，若今天还没打）向前连续计数。"""
    # checked_days: 已打卡的自然日集合
    if not checked_days:
        return 0
    today = date.today().isoformat()
    streak = 0
    cur = date.today()
    if today not in checked_days:
        cur = cur - timedelta(days=1)  # 今天未打，从昨天数
    while cur.isoformat() in checked_days:
        streak += 1
        cur -= timedelta(days=1)
    return streak


@router.get("")
def get_stats():
    conn = get_conn()
    try:
        total = conn.execute("SELECT COUNT(*) AS c FROM cards").fetchone()["c"]
        done = conn.execute("SELECT COUNT(*) AS c FROM checkins").fetchone()["c"]

        # 本周完成率：按当前周
        today_card_day = _today_day(conn)
        week = conn.execute(
            "SELECT week_number FROM cards WHERE day_number=?", (today_card_day,)
        ).fetchone()
        week_num = week["week_number"] if week else 1
        week_total = conn.execute(
            "SELECT COUNT(*) AS c FROM cards WHERE week_number=?", (week_num,)
        ).fetchone()["c"]
        week_done = conn.execute(
            "SELECT COUNT(*) AS c FROM checkins ck JOIN cards c ON ck.card_id=c.id "
            "WHERE c.week_number=?",
            (week_num,),
        ).fetchone()["c"]

        # 最近 7 天打卡日历（自然日）
        heatmap = []
        checked_days = set()
        for r in conn.execute("SELECT date(checked_at) AS d FROM checkins").fetchall():
            checked_days.add(r["d"])
        for i in range(6, -1, -1):
            d = (date.today() - timedelta(days=i)).isoformat()
            heatmap.append({"date": d, "checked": d in checked_days})

        favorites = conn.execute("SELECT COUNT(*) AS c FROM favorites").fetchone()["c"]
        notes = conn.execute(
            "SELECT COUNT(*) AS c FROM checkins WHERE notes IS NOT NULL AND notes!=''"
        ).fetchone()["c"]
        resources = conn.execute("SELECT COUNT(*) AS c FROM resources").fetchone()["c"]

        return {
            "streak": _streak(conn, checked_days),
            "total_completion": {"done": done, "total": total},
            "week": {
                "week_number": week_num,
                "done": week_done,
                "total": week_total,
            },
            "heatmap": heatmap,
            "favorites_count": favorites,
            "notes_count": notes,
            "resources_count": resources,
        }
    finally:
        conn.close()


def _today_day(conn) -> int:
    start = datetime(2026, 10, 27).date()
    day = (date.today() - start).days + 1
    if day < 1:
        day = 1
    total = conn.execute("SELECT COUNT(*) AS c FROM cards").fetchone()["c"]
    if day > total:
        day = total
    return day

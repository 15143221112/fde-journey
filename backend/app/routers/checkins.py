"""打卡接口。"""
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..database import get_conn

router = APIRouter(prefix="/api/checkins", tags=["checkins"])


class CheckinIn(BaseModel):
    card_id: int
    notes: str = ""


@router.post("")
def check_in(data: CheckinIn):
    """今日已学：打卡，附带可选笔记。"""
    conn = get_conn()
    try:
        card = conn.execute("SELECT id FROM cards WHERE id=?", (data.card_id,)).fetchone()
        if not card:
            raise HTTPException(404, "卡片不存在")
        today = datetime.now().strftime("%Y-%m-%d")
        dup = conn.execute(
            "SELECT id FROM checkins WHERE card_id=? AND date(checked_at)=?",
            (data.card_id, today),
        ).fetchone()
        if dup:
            # 已打过，只更新笔记
            conn.execute(
                "UPDATE checkins SET notes=? WHERE id=?",
                (data.notes, dup["id"]),
            )
            conn.commit()
            return {"ok": True, "id": dup["id"], "updated": True}
        cur = conn.execute(
            "INSERT INTO checkins (card_id, checked_at, notes) VALUES (?, ?, ?)",
            (data.card_id, datetime.now().isoformat(), data.notes),
        )
        conn.commit()
        return {"ok": True, "id": cur.lastrowid, "updated": False}
    finally:
        conn.close()


@router.get("")
def list_checkins():
    conn = get_conn()
    try:
        rows = conn.execute(
            """SELECT ck.*, c.day_number, c.title
               FROM checkins ck JOIN cards c ON ck.card_id=c.id
               ORDER BY ck.checked_at DESC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.delete("/{id}")
def undo_checkin(id: int):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM checkins WHERE id=?", (id,))
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()

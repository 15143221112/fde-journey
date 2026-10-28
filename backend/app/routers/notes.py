"""笔记接口：打卡笔记 + 卡片独立笔记。"""
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..database import get_conn

router = APIRouter(prefix="/api", tags=["notes"])


class NoteIn(BaseModel):
    notes: str = ""
    card_id: int


@router.post("/cards/{card_id}/note")
def save_note(card_id: int, data: NoteIn):
    """保存某张卡片的笔记。若该卡片今日已打卡则并入打卡笔记，否则新增打卡记录。"""
    conn = get_conn()
    try:
        card = conn.execute("SELECT id FROM cards WHERE id=?", (card_id,)).fetchone()
        if not card:
            raise HTTPException(404, "卡片不存在")
        today = datetime.now().strftime("%Y-%m-%d")
        cur = conn.execute(
            "SELECT id FROM checkins WHERE card_id=? AND date(checked_at)=?",
            (card_id, today),
        ).fetchone()
        if cur:
            conn.execute("UPDATE checkins SET notes=? WHERE id=?", (data.notes, cur["id"]))
        else:
            conn.execute(
                "INSERT INTO checkins (card_id, checked_at, notes) VALUES (?, ?, ?)",
                (card_id, datetime.now().isoformat(), data.notes),
            )
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()


@router.get("/notes")
def list_notes():
    """所有含笔记的打卡记录（有笔记才显示）。"""
    conn = get_conn()
    try:
        rows = conn.execute(
            """SELECT ck.id, ck.card_id, ck.checked_at, ck.notes, c.day_number, c.title
               FROM checkins ck JOIN cards c ON ck.card_id=c.id
               WHERE ck.notes IS NOT NULL AND ck.notes != ''
               ORDER BY ck.checked_at DESC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

"""收藏接口。"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..database import get_conn

router = APIRouter(prefix="/api/favorites", tags=["favorites"])


class FavIn(BaseModel):
    card_id: int


@router.post("")
def add_favorite(data: FavIn):
    conn = get_conn()
    try:
        card = conn.execute("SELECT id FROM cards WHERE id=?", (data.card_id,)).fetchone()
        if not card:
            raise HTTPException(404, "卡片不存在")
        dup = conn.execute("SELECT id FROM favorites WHERE card_id=?", (data.card_id,)).fetchone()
        if not dup:
            conn.execute("INSERT INTO favorites (card_id) VALUES (?)", (data.card_id,))
            conn.commit()
        return {"ok": True}
    finally:
        conn.close()


@router.delete("/{card_id}")
def remove_favorite(card_id: int):
    conn = get_conn()
    try:
        conn.execute("DELETE FROM favorites WHERE card_id=?", (card_id,))
        conn.commit()
        return {"ok": True}
    finally:
        conn.close()


@router.get("")
def list_favorites():
    conn = get_conn()
    try:
        rows = conn.execute(
            """SELECT f.id, f.card_id, f.created_at, c.day_number, c.title
               FROM favorites f JOIN cards c ON f.card_id=c.id
               ORDER BY f.created_at DESC"""
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()

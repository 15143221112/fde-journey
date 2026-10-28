"""资料管理接口：增删改查 / 分类标签 / 全文搜索 / 文件上传 / 导出。"""
import json
import os
import uuid
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, UploadFile, File
from fastapi.responses import FileResponse, PlainTextResponse
from pydantic import BaseModel

from ..database import get_conn

router = APIRouter(prefix="/api/resources", tags=["resources"])

UPLOAD_DIR = os.environ.get("UPLOAD_DIR", os.path.join(os.path.dirname(__file__), "..", "..", "uploads"))


class ResourceIn(BaseModel):
    title: str
    type: str = "note"  # link / file / code / video / note
    url: str = ""
    code_content: str = ""
    note_content: str = ""
    category: str = "其他"
    tags: str = ""
    summary: str = ""
    related_week: int | None = None
    related_card_id: int | None = None
    read_status: str = "unread"


@router.post("")
def create_resource(data: ResourceIn):
    if data.type not in ("link", "file", "code", "video", "note"):
        raise HTTPException(400, "type 非法")
    if data.read_status not in ("unread", "reading", "read"):
        data.read_status = "unread"
    conn = get_conn()
    try:
        cur = conn.execute(
            """INSERT INTO resources
               (title, type, url, code_content, note_content, category, tags, summary,
                related_week, related_card_id, read_status, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (
                data.title, data.type, data.url or None, data.code_content or None,
                data.note_content or None, data.category, data.tags, data.summary,
                data.related_week, data.related_card_id, data.read_status,
                datetime.now().isoformat(), datetime.now().isoformat(),
            ),
        )
        conn.commit()
        return _row(conn, cur.lastrowid)
    finally:
        conn.close()


@router.post("/upload")
async def upload_file(file: UploadFile = File(...), category: str = "其他",
                      summary: str = "", tags: str = "", title: str = ""):
    """上传本地文件（PDF/MD/TXT），落盘并登记。"""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    fname = file.filename or "file"
    safe = os.path.basename(fname)
    stored = f"{uuid.uuid4().hex}_{safe}"
    dest = os.path.join(UPLOAD_DIR, stored)
    content = await file.read()
    with open(dest, "wb") as f:
        f.write(content)

    final_title = title or safe
    conn = get_conn()
    try:
        cur = conn.execute(
            """INSERT INTO resources
               (title, type, file_path, file_name, category, tags, summary,
                read_status, created_at, updated_at)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                final_title, "file", dest, safe, category, tags, summary,
                "unread", datetime.now().isoformat(), datetime.now().isoformat(),
            ),
        )
        conn.commit()
        return _row(conn, cur.lastrowid)
    finally:
        conn.close()


@router.get("")
def list_resources(
    category: str = "",
    tags: str = "",
    search: str = "",
    status: str = "",
    type: str = "",
    related_card_id: int | None = None,
):
    """资料列表：分类/标签/状态/类型筛选 + 全文搜索（标题/摘要/标签/代码/笔记）。"""
    conn = get_conn()
    try:
        sql = "SELECT * FROM resources WHERE 1=1"
        params = []
        if category:
            sql += " AND category = ?"
            params.append(category)
        if tags:
            # 交叉筛选：某资料 tags 字段需包含全部所选标签
            for t in tags.split(","):
                t = t.strip()
                if t:
                    sql += " AND (',' || tags || ',') LIKE ?"
                    params.append(f"%,{t},%")
        if search:
            sql += (
                " AND (title LIKE ? OR summary LIKE ? OR tags LIKE ? "
                "OR code_content LIKE ? OR note_content LIKE ?)"
            )
            params += [f"%{search}%"] * 5
        if status:
            sql += " AND read_status = ?"
            params.append(status)
        if type:
            sql += " AND type = ?"
            params.append(type)
        if related_card_id is not None:
            sql += " AND related_card_id = ?"
            params.append(related_card_id)
        sql += " ORDER BY id DESC"
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


@router.get("/categories")
def resource_categories():
    return ["FDE", "LangGraph", "LangChain", "RAG", "Python", "安全合规", "其他"]


@router.get("/export")
def export(fmt: str = "markdown"):
    """导出全部资料为 Markdown 或 JSON。"""
    conn = get_conn()
    try:
        rows = conn.execute("SELECT * FROM resources ORDER BY id DESC").fetchall()
        data = [dict(r) for r in rows]
    finally:
        conn.close()

    if fmt == "json":
        return PlainTextResponse(
            json.dumps(data, ensure_ascii=False, indent=2),
            media_type="application/json",
        )
    lines = ["# FDE 资料库导出", ""]
    for r in data:
        lines.append(f"## {r['title']}")
        lines.append(f"- 类型：{r['type']} | 分类：{r['category']} | 状态：{r['read_status']}")
        if r["tags"]:
            lines.append(f"- 标签：{r['tags']}")
        if r["summary"]:
            lines.append(f"- 摘要：{r['summary']}")
        if r["url"]:
            lines.append(f"- 链接：{r['url']}")
        if r["file_name"]:
            lines.append(f"- 文件：{r['file_name']}")
        if r["related_week"]:
            lines.append(f"- 关联周次：第{r['related_week']}周")
        if r["code_content"]:
            lines.append("- 代码：\n```\n" + r["code_content"] + "\n```")
        if r["note_content"]:
            lines.append(f"- 随手记：{r['note_content']}")
        lines.append("")
    return PlainTextResponse("\n".join(lines), media_type="text/markdown; charset=utf-8")


@router.get("/{id}")
def get_resource(id: int):
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM resources WHERE id=?", (id,)).fetchone()
        if not row:
            raise HTTPException(404, "资料不存在")
        return dict(row)
    finally:
        conn.close()


@router.patch("/{id}")
def update_resource(id: int, data: dict):
    """部分更新：read_status / title / tags / summary / related_card_id 等。"""
    allowed = {"title", "summary", "tags", "read_status", "category",
               "related_week", "related_card_id", "type", "url"}
    conn = get_conn()
    try:
        row = conn.execute("SELECT id FROM resources WHERE id=?", (id,)).fetchone()
        if not row:
            raise HTTPException(404, "资料不存在")
        fields, params = [], []
        for k, v in data.items():
            if k in allowed and v is not None:
                fields.append(f"{k}=?")
                params.append(v)
        if fields:
            params.append(datetime.now().isoformat())
            conn.execute(
                f"UPDATE resources SET {', '.join(fields)}, updated_at=? WHERE id=?",
                params + [id],
            )
            conn.commit()
        return _row(conn, id)
    finally:
        conn.close()


@router.delete("/{id}")
def delete_resource(id: int):
    conn = get_conn()
    try:
        row = conn.execute("SELECT file_path FROM resources WHERE id=?", (id,)).fetchone()
        if not row:
            raise HTTPException(404, "资料不存在")
        conn.execute("DELETE FROM resources WHERE id=?", (id,))
        conn.commit()
        # 删除关联的本地文件
        if row["file_path"] and os.path.exists(row["file_path"]):
            try:
                os.remove(row["file_path"])
            except OSError:
                pass
        return {"ok": True}
    finally:
        conn.close()


@router.get("/{id}/download")
def download_resource(id: int):
    conn = get_conn()
    try:
        row = conn.execute("SELECT * FROM resources WHERE id=?", (id,)).fetchone()
    finally:
        conn.close()
    if not row or not row["file_path"] or not os.path.exists(row["file_path"]):
        raise HTTPException(404, "文件不存在")
    return FileResponse(row["file_path"], filename=row["file_name"] or "file")


def _row(conn, id):
    r = conn.execute("SELECT * FROM resources WHERE id=?", (id,)).fetchone()
    return dict(r)

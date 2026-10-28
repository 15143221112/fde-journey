"""FDE 每日学习卡片工具 —— FastAPI 入口。

- /api/* : REST 接口
- /*     : 前端静态资源（若 frontend/dist 存在则托管，便于 docker 单容器部署）
"""

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database import init_db
from .routers import cards, checkins, favorites, notes, stats, resources

app = FastAPI(title="FDE 每日学习卡片工具", version="1.0.0")

# CORS：允许本地前端开发服务器（vite dev on 5173）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库（含 84 张卡片种子）
@app.on_event("startup")
def _startup():
    init_db()

app.include_router(cards.router)
app.include_router(checkins.router)
app.include_router(favorites.router)
app.include_router(notes.router)
app.include_router(stats.router)
app.include_router(resources.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "fde-learning-tool"}


# ---- 托管前端静态文件（docker 单容器模式） ----
_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
if _DIST.exists():
    assets = _DIST / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        f = _DIST / full_path
        if f.is_file():
            return FileResponse(f)
        return FileResponse(_DIST / "index.html")

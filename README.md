# FDE 每日学习卡片工具

一个每天推送技术卡片、追踪学习进度、关联水稻 AI 实战项目、统一管理资料的轻量 Web 应用。

- 目标：FDE（前沿部署工程师）12 周学习路线（2026-10-27 ~ 2027-01-18，84 天）
- 技术栈：React + Vite + TailwindCSS（前端）、Python FastAPI（后端）、SQLite（本地数据）
- 部署：Docker Compose 一条命令启动，手机浏览器可用

---

## 一、快速启动（Docker）

```bash
docker compose up -d --build
```

启动后浏览器打开：**http://localhost:8000**

- 局域网手机访问：用电脑 IP 打开 `http://<电脑IP>:8000`
- 停止：`docker compose down`
- 查看日志：`docker logs -f fde-learning`

数据持久化在宿主机 `backend/data/`（SQLite）与 `backend/uploads/`（上传文件），
删容器不丢数据。

> 首次构建需联网拉取基础镜像（node / python）。若拉取超时，可先 `docker pull node:20-alpine` 和 `docker pull python:3.12-slim` 缓存后再构建。

---

## 二、本地开发（不用 Docker）

```bash
# 后端（端口 8000）
cd backend
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python -m uvicorn app.main:app --port 8000 --reload

# 前端（端口 5173，自动代理 /api 到 8000）
cd frontend
npm install
npm run dev
# 打开 http://localhost:5173
```

---

## 三、功能

| 页面 | 功能 |
|---|---|
| 🎯 今日 | 每日卡片（知识点/练习/水稻项目关联）、今日已学打卡、收藏、记笔记 |
| 📅 路线 | 12 周时间线，周次展开查看每日，完成绿色、今天高亮、周末轻量 |
| 📚 卡片 | 全部 84 张卡片，关键词搜索 + 7 大分类筛选 |
| 📁 资料 | 添加网页/文件/代码/视频/随手记，分类与标签筛选、全文搜索、阅读状态、文件上传、导出 MD/JSON |
| 📊 统计 | 连续打卡、总/本周完成率、最近 7 天打卡热力图、收藏/笔记/资料数量 |
| 📝 笔记 | 每张卡片的 Markdown 笔记列表 |

---

## 四、目录结构

```
fde/
├── docker-compose.yml      # 一键启动
├── Dockerfile              # 多阶段：前端构建 + Python 运行
├── backend/
│   ├── requirements.txt
│   ├── cards_seed.json     # 84 张卡片种子数据（可直接改）
│   ├── data/               # SQLite 数据库（运行时生成，勿手动删）
│   ├── uploads/            # 上传的本地文件
│   └── app/
│       ├── main.py         # FastAPI 入口，托管前端
│       ├── database.py     # SQLite 建表 + 种子 + 今日卡片
│       └── routers/        # cards/checkins/favorites/notes/stats/resources
├── frontend/
│   ├── src/
│   │   ├── App.jsx         # 布局 + 底部导航
│   │   ├── api.js          # API 客户端
│   │   ├── utils/md.jsx    # 轻量 Markdown 渲染
│   │   └── pages/          # Home/Timeline/Cards/Resources/Stats/Notes
└── scripts/
    ├── generate_cards.py   # 重新生成 84 张卡片
    └── api_test.py         # 端到端 API 回归测试
```

---

## 五、修改卡片内容

直接编辑 `backend/cards_seed.json`，或改 `scripts/generate_cards.py` 里每周的内容后重新生成：

```bash
python scripts/generate_cards.py
```

改动后重建数据库（容器会重新播种）：

```bash
docker compose down
# 删除旧库让容器重新播种（会清空打卡/收藏/笔记，请先备份）
del backend\data\fde.db
docker compose up -d --build
```

每张卡片结构：

```json
{
  "day": 1, "week": 1,
  "title": "Python 基础：环境与虚拟环境",
  "category": "Python基础",
  "points": ["用 venv 创建隔离环境：`python -m venv .venv`", "..."],
  "exercise": "为水稻项目建一个独立 venv…",
  "rice_project": "水稻知识库后端…",
  "is_weekend": false
}
```

---

## 六、数据模型

- `cards`：84 张学习卡片（day/week/title/category/content_json/is_weekend）
- `checkins`：打卡记录（含笔记），同一卡片同一天只记一次
- `favorites`：收藏
- `resources`：资料（类型/URL/文件/代码/随手记/分类/标签/摘要/关联周次/阅读状态）

---

## 七、API 速查

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | /api/cards/today | 今日卡片 + 进度 + 打卡状态 + streak |
| GET | /api/cards | 卡片列表（search/category） |
| GET | /api/cards/timeline | 12 周时间线 |
| POST | /api/checkins | 打卡 `{card_id, notes}` |
| POST | /api/favorites | 收藏 |
| POST | /api/cards/{id}/note | 存笔记 |
| GET | /api/stats | 统计仪表盘 |
| POST | /api/resources | 新增资料 |
| GET | /api/resources | 资料列表（category/tags/search/status） |
| PATCH | /api/resources/{id} | 改阅读状态等 |
| POST | /api/resources/upload | 上传本地文件 |
| GET | /api/resources/export | 导出 MD/JSON |

交互式接口文档：启动后访问 `http://localhost:8000/docs`

---

## 八、测试

```bash
# API 回归测试（需后端已启动）
python scripts/api_test.py http://127.0.0.1:8000
```

覆盖：今日卡片、84 张完整性、12 周时间线、7 分类、打卡联动、收藏、中文笔记、
资料增删改查 / 分类标签筛选 / 全文搜索 / 标记已读 / 关联卡片 / 导出。

---

## 九、后续可扩展（v2.0）

- [ ] 对接 AI API，卡片一键"问豆包"
- [ ] 导入 Anki 间隔重复复习
- [ ] 每周自动生成学习周报
- [ ] 番茄钟
- [ ] 微信/钉钉推送提醒

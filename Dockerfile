# ============================================================
# FDE 每日学习卡片工具 —— 多阶段镜像
# stage 1: 构建前端 (React + Vite + Tailwind)
# stage 2: Python 运行 FastAPI 后端，并托管前端 dist
# ============================================================

# ---- stage 1: build frontend ----
FROM node:20-alpine AS frontend-build
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

# ---- stage 2: python runtime ----
FROM python:3.12-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 先装依赖（利用层缓存）
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# 拷贝后端代码 + 前端构建产物
COPY backend/ ./backend/
COPY --from=frontend-build /build/frontend/dist ./frontend/dist

WORKDIR /app/backend
EXPOSE 8000
# 0.0.0.0 便于局域网手机访问
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

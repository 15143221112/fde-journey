"""FDE 学习工具 —— 端到端 API 回归测试（纯 Python，规避终端编码干扰）。

用法：python scripts/api_test.py [base_url]
默认 base_url = http://127.0.0.1:8000
"""
import json
import sys
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8000"

PASS = []
FAIL = []


def call(method, path, body=None):
    url = BASE + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    if body is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=15) as resp:
        raw = resp.read()
        if not raw:
            return None
        return json.loads(raw.decode("utf-8"))


def check(name, cond, detail=""):
    if cond:
        PASS.append(name)
        print(f"  [PASS] {name}")
    else:
        FAIL.append(name)
        print(f"  [FAIL] {name}  {detail}")


print("=== 读接口 ===")
h = call("GET", "/api/health")
check("health ok", h and h.get("status") == "ok")

today = call("GET", "/api/cards/today")
check("today 返回今日卡片", today and today.get("card") and today["card"]["title"])

cards = call("GET", "/api/cards")
check("卡片总数=84", len(cards) == 84, f"实际 {len(cards)}")
check("卡片内容非空", all(c["content"].get("points") for c in cards if not c["is_weekend"]),
      "存在空主题卡片")

tl = call("GET", "/api/cards/timeline")
check("时间线 12 周", len(tl) == 12, f"实际 {len(tl)}")
check("每周 7 天", all(len(w["cards"]) == 7 for w in tl))

cats = call("GET", "/api/cards/categories")
check("分类含7类", len(cats) == 7, f"实际 {cats}")

print("=== 打卡 / 收藏 / 笔记 ===")
call("POST", "/api/checkins", {"card_id": 1, "notes": "今日学了 venv 隔离"})
today2 = call("GET", "/api/cards/today")
check("打卡后 today_checked=True", today2["today_checked"] is True)
st = call("GET", "/api/stats")
check("打卡后进度 done=1", st["total_completion"]["done"] == 1, f"{st['total_completion']}")
check("打卡后 streak>=1", st["streak"] >= 1, f"streak={st['streak']}")

call("POST", "/api/favorites", {"card_id": 5})
favs = call("GET", "/api/favorites")
check("收藏成功", len(favs) >= 1)

call("POST", "/api/cards/2/note", {"card_id": 2, "notes": "HTTP 请求实战笔记"})
notes = call("GET", "/api/notes")
check("笔记含中文且正常", any("实战笔记" in (n["notes"] or "") for n in notes))

print("=== 资料管理（中文回环测试）===")
# 先清空测试资料
conn = None
import sqlite3
conn = sqlite3.connect(r"D:\个人学习\fde\backend\data\fde.db")
conn.execute("DELETE FROM resources")
conn.commit()
conn.close()

r1 = call("POST", "/api/resources", {
    "title": "LangGraph 官方文档-概念篇", "type": "link",
    "url": "https://langchain-ai.github.io/langgraph/concepts/",
    "category": "LangGraph", "tags": "状态机,节点,边",
    "summary": "讲清楚 LangGraph 的核心概念", "related_card_id": 36,
})
check("新增网页链接", r1 and r1["id"], f"{r1}")
r1_id = r1["id"]

r2 = call("POST", "/api/resources", {
    "title": "DeepSeek function calling 要加 tool_choice", "type": "note",
    "note_content": "踩坑记录：记得传 tools 参数", "category": "LangChain",
    "tags": "工具调用,踩坑", "read_status": "reading",
})
r2_id = r2["id"]

# 中文是否被正确存储（从接口读回）
detail = call("GET", f"/api/resources/{r1_id}")
check("资料中文标题正确存储", detail["title"] == "LangGraph 官方文档-概念篇", repr(detail["title"]))

lg = call("GET", "/api/resources?category=LangGraph")
check("分类筛选 LangGraph=1", len(lg) == 1, f"实际 {len(lg)}")

tag = call("GET", "/api/resources?tags=" + urllib.parse.quote("状态机"))
check("标签筛选 状态机=1", len(tag) == 1, f"实际 {len(tag)}")

search = call("GET", "/api/resources?search=" + urllib.parse.quote("function calling"))
check("全文搜索 function calling=1", len(search) == 1, f"实际 {len(search)}")

search_zh = call("GET", "/api/resources?search=" + urllib.parse.quote("踩坑记录"))
check("全文搜索中文=1", len(search_zh) == 1, f"实际 {len(search_zh)}")

call("PATCH", f"/api/resources/{r1_id}", {"read_status": "read"})
rd = call("GET", "/api/resources?status=read")
check("标记已读后 status=read 筛选=1", len(rd) == 1, f"实际 {len(rd)}")

c36 = call("GET", "/api/cards/36")
check("关联卡片查询含补充资料", len(c36["related_resources"]) == 1)

export = call("GET", "/api/resources/export?fmt=json")
check("导出 JSON 正常", isinstance(export, list) and len(export) == 2)

print()
print(f"结果: PASS={len(PASS)}  FAIL={len(FAIL)}")
if FAIL:
    print("失败项:", FAIL)
    sys.exit(1)
print("全部通过")

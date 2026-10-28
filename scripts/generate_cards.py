"""生成 84 张学习卡片的种子数据 -> backend/cards_seed.json

12 周路线（2026-10-27 起，每周7天，周一到周五主题学习，周六日轻量内容）。
内容关联「东北水稻农业 AI 知识库」实战项目。
运行：python scripts/generate_cards.py
"""

import json
import os

WEEK_TOPIC = {
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

CAT = {
    1: "Python基础", 2: "Python基础", 3: "LangChain 1.0", 4: "LangChain 1.0",
    5: "LangGraph", 6: "LangGraph", 7: "RAG与评测", 8: "RAG与评测",
    9: "安全合规", 10: "部署运维", 11: "部署运维", 12: "FDE认证",
}


def weekday_cards(week, titles_points_ex, cat=None):
    """返回某周一至周五的主题卡片。
    titles_points_ex: list of (title, [points], exercise, rice_project)
    """
    out = []
    for i, (title, points, exercise, rice) in enumerate(titles_points_ex):
        day = (week - 1) * 7 + i + 1
        out.append({
            "day": day,
            "week": week,
            "title": title,
            "category": cat or CAT[week],
            "points": points,
            "exercise": exercise,
            "rice_project": rice,
            "is_weekend": False,
        })
    return out


def weekend_cards(week, note_title, note_text, points, exercise):
    """周六、周日轻量卡片。"""
    base = (week - 1) * 7
    out = []
    for idx, extra in enumerate(["(周六)", "(周日)"]):
        day = base + 6 + idx
        out.append({
            "day": day,
            "week": week,
            "title": f"{note_title} {extra}",
            "category": CAT[week],
            "points": points,
            "exercise": exercise,
            "rice_project": "",
            "weekend_note": note_text,
            "is_weekend": True,
        })
    return out


# ==================== 内容定义 ====================
CARDS = []

# ---------- 第1周 Python 基础热身 ----------
CARDS += weekday_cards(1, [
    ("Python 基础：环境与虚拟环境", [
        "用 venv 创建隔离环境：`python -m venv .venv`，激活后 `pip install` 不污染全局",
        "requirements.txt 锁定依赖版本：`pip freeze > requirements.txt`",
        "习惯用 uv 或 conda 管理多套 Python 环境，AI 项目依赖多、版本敏感",
    ], "为水稻项目建一个独立 venv，安装 requests 并 `pip freeze` 导出 requirements.txt",
     "水稻知识库后端会依赖多个库，先学会用 venv 隔离，避免环境冲突"),
    ("Python 基础：第一个 HTTP 请求", [
        "requests 库三件套：`resp = requests.get(url)`、`resp.status_code`、`resp.json()`",
        "调用 OpenAI 兼容接口的写法：`requests.post(url, headers={\"Authorization\": \"Bearer key\"}, json={\"model\": \"...\", \"messages\": [...]})`",
        "把 API key 放环境变量，不写死在代码里：`os.getenv(\"DEEPSEEK_API_KEY\")`",
    ], "用 requests 调 DeepSeek API，发一句“你好”，打印返回的 content",
     "水稻问答 Agent 的入口就是 HTTP 调用模型接口，这一步是地基"),
    ("Python 基础：数据容器 list/dict/set/tuple", [
        "list 有序可变，适合存问题列表；dict 键值映射，适合存结构化结果",
        "set 去重：农户问题里有大量重复关键词，用 set 一次清掉",
        "列表推导式：`[q for q in questions if q]` 快速过滤空值",
    ], "把“水稻、稻瘟病、施肥、灌溉”等关键词去重并排序，练习 set/list/dict",
     "农技知识分类、去重、索引，处处用得到这些容器"),
    ("Python 基础：函数与作用域", [
        "函数是一等公民：`def greet(name): return f\"你好,{name}\"`",
        "参数默认值、*args/**kwargs 让函数更灵活",
        "全局变量与局部变量作用域，尽量少用 global",
    ], "写一个 `classify(question)` 函数，根据关键词返回分类标签",
     "把“按问题判断类别”的逻辑抽成函数，后续可单独测试"),
    ("Python 基础：面向对象入门", [
        "类 = 属性 + 方法：`class RAG: def __init__(self): ...`",
        "封装数据与行为，水稻知识库的文档加载器、检索器都可做成类",
        "简单优先：能用函数不用类，避免过度设计",
    ], "定义一个 DocumentLoader 类，封装加载+清洗两件事",
     "检索器、向量库、重排序都做成类，便于复用与替换实现"),
])

# ---------- 第2周 Python 进阶与 HTTP/API ----------
CARDS += weekday_cards(2, [
    ("Python 进阶：异步 asyncio", [
        "async/await：`async def f(): await asyncio.sleep(1)`",
        "并发调模型接口：`asyncio.gather(*tasks)` 大幅提升吞吐",
        "注意：requests 是同步的，异步场景用 httpx",
    ], "用 httpx + asyncio.gather 并发发 3 个模型请求，统计耗时",
     "水稻问答要并发处理多个农户提问，异步是必须"),
    ("Python 进阶：FastAPI 快速上手", [
        "最简服务：`app = FastAPI(); @app.get(\"/ping\")` + `uvicorn app:app --reload`",
        "路径参数与查询参数：`/query/{kw}?limit=10`",
        "自动生成 /docs 交互式文档，调试神器",
    ], "起一个 FastAPI 服务，提供 /ping 与 /ask 两个接口",
     "水稻问答后端就用 FastAPI，这就是它的雏形"),
    ("Python 进阶：Pydantic 数据校验", [
        "用模型类定义请求/响应结构：`class AskReq(BaseModel): question: str`",
        "自动校验类型，非法输入直接 422",
        "嵌套模型组织复杂数据结构，知识库条目就是典型",
    ], "定义 AskReq（question/question_type）并校验必填字段",
     "农户提问格式千奇百怪，用 Pydantic 兜住边界"),
    ("Python 进阶：装饰器与闭包", [
        "装饰器：`@app.get(...)` 本质就是装饰器，给函数加行为",
        "自己写个 @timer 统计函数耗时，排查慢查询",
        "闭包记住外层变量，做简单状态缓存",
    ], "写 @timer 装饰器包住一个检索函数，打印执行耗时",
     "定位水稻知识库哪一步最慢，先从装饰器计时开始"),
    ("Python 进阶：异常处理与日志", [
        "try/except 兜住网络超时、模型报错，不让服务崩",
        "logging 分级：debug/info/error，生产只留 info+",
        "给每次问答生成 request_id，方便追踪",
    ], "给模型调用加超时与重试，出错时记录 error 日志",
     "线上问答必须健壮，异常与日志是运维的第一步"),
])

# ---------- 第3周 LangChain 1.0 · 起步 ----------
CARDS += weekday_cards(3, [
    ("LangChain 1.0：框架是什么", [
        "LangChain 统一封装模型、提示、检索、Agent 的调用链",
        "核心是 LCEL（LangChain Expression Language）：用 `|` 串起组件",
        "1.0 更聚焦：langchain-core 提供抽象，具体能力靠 langchain-openai 等包",
    ], "安装 langchain + langchain-openai，跑通最简单的链",
     "水稻问答的所有组件都在这套框架里组装"),
    ("LangChain 1.0：Chat Models 调用", [
        "用 `ChatOpenAI(model=\"deepseek-chat\")` 兼容各家模型（需 base_url）",
        "messages 结构：system + user + assistant 多轮",
        "`model.invoke([...])` 返回 AIMessage，`.content` 取文本",
    ], "用 langchain-openai 调一次 DeepSeek，走完整条链",
     "水稻 Agent 的对话能力从一次 invoke 开始"),
    ("LangChain 1.0：Prompt 模板", [
        "PromptTemplate 占位符：`\"你是水稻专家，回答：{question}\"`",
        "用 SystemMessage 固定角色，用 user 消息传变量",
        "模板里放示例（few-shot）提升回答质量",
    ], "写一个带角色和示例的农技回答模板",
     "水稻问答的回答质量，一半在提示词模板"),
    ("LangChain 1.0：输出解析器", [
        "输出解析器把模型文本转成结构化：JsonOutputParser、StrOutputParser",
        "配合 `.with_structured_output()` 直接拿对象",
        "解析失败要有兜底，别让 JSON 报错弄崩流程",
    ], "让模型输出 JSON（分类+置信度），用解析器取出",
     "把回答结构化，后续才能存库、统计、做评测"),
    ("LangChain 1.0：LCEL 链式调用", [
        "一条链：`prompt | model | parser`",
        "链可复用、可并行、可流式，天然适配",
        "`chain.invoke({\"question\": \"...\"})` 一次跑完",
    ], "把模板+模型+解析器串成一条链并 invoke",
     "水稻问答主流程就是一条 LCEL 链"),
])

# ---------- 第4周 LangChain 1.0 · 组件实战 ----------
CARDS += weekday_cards(4, [
    ("LangChain 1.0：记忆 Memory", [
        "多轮对话要记住上下文：用 LangGraph 的持久化，或手动拼 messages",
        "简单做法：把历史消息拼进 prompt",
        "注意 token 上限，历史太长要裁剪/摘要",
    ], "实现一个有 3 轮记忆的简单对话",
     "农户连续追问时，Agent 要记得前面说过什么"),
    ("LangChain 1.0：工具调用 Tool Calling", [
        "定义工具（函数+描述），让模型决定调哪个",
        "`tool.bind_tools([...])` 触发模型输出 tool_calls",
        "DeepSeek 的 function calling 需在请求里带 tools 参数",
    ], "定义一个 get_rice_price 工具，让模型调用它",
     "查虫害、查价格、查天气，都做成工具让 Agent 调用"),
    ("LangChain 1.0：文档加载器", [
        "DocumentLoader 读取本地文件：PDF/MD/TXT",
        "每个 Document 有 page_content 和 metadata（来源、页号）",
        "metadata 是检索溯源的关键",
    ], "加载一个水稻知识 MD 文件，打印文档数与元数据",
     "把农技资料、论文、手册全部加载进知识库"),
    ("LangChain 1.0：文本分割 Text Splitter", [
        "长文档要切成小块再向量化，控制检索粒度",
        "RecursiveCharacterTextSplitter 按层级切分，保留语义",
        "chunk_size / chunk_overlap 两个关键参数要调",
    ], "用 splitter 把一篇文章切成带重叠的块，观察数量",
     "水稻文档动辄上万字，分块好坏直接决定检索效果"),
    ("LangChain 1.0：向量存储起步", [
        "向量库存 embedding，支持相似度检索",
        "本地轻量可选 Chroma；生产用 PGVector（水稻项目在用）",
        "`vectorstore.add_documents(docs)` + `similarity_search(query)`",
    ], "用 Chroma 建库、写入几块文本、做一次相似检索",
     "水稻知识库就是“文档→分块→向量→检索”这一套"),
])

# ---------- 第5周 LangGraph · 图与状态 ----------
CARDS += weekday_cards(5, [
    ("LangGraph：核心概念", [
        "LangGraph 用「图」描述 Agent：节点=函数，边=路由，状态=共享数据",
        "节点是普通 Python 函数，输入输出都是状态",
        "状态用 TypedDict 定义，全程唯一数据源",
    ], "画出“加载→检索→回答”三步的节点图",
     "水稻 Agent 从线性链升级成可控制的图"),
    ("LangGraph：StateGraph 入门", [
        "`StateGraph(State)` 建图，`add_node` 加节点",
        "`add_edge` 定顺序，`compile()` 成可调用对象",
        "`graph.invoke(initial_state)` 跑一遍，返回最终状态",
    ], "搭一个 2 节点的 StateGraph 并跑通",
     "先搭最简单的图，理解数据怎么在节点间流动"),
    ("LangGraph：节点 Node", [
        "节点函数签名：`def node(state: dict) -> dict: ...`",
        "返回值会更新状态；返回 None 则不更新",
        "一个节点可做大任务，也可拆多个小节点便于控制",
    ], "写一个 retrieve 节点，接收 question 返回相关文档",
     "把水稻检索逻辑做成独立节点"),
    ("LangGraph：边 Edge", [
        "add_edge 是固定顺序，add_conditional_edges 是动态路由",
        "边决定图下一步执行谁",
        "起始点 START、终点 END 是内置特殊节点",
    ], "给图加上 START→A→B→END 的完整链路",
     "理解图的执行顺序，是路由的基础"),
    ("LangGraph：状态 State 深入", [
        "TypedDict 定义字段类型；列表字段可用 reducer 合并（Annotated）",
        "状态是图的核心，所有节点读写同一份",
        "善用注释字段（messages）累积对话历史",
    ], "定义含 question/context/answer 的状态并贯穿全图",
     "水稻问答的“问题-资料-回答”都装进状态里"),
])

# ---------- 第6周 LangGraph · 路由与实战 ----------
CARDS += weekday_cards(6, [
    ("LangGraph：条件路由 Conditional Edges", [
        "`add_conditional_edges(node, router_fn, path_map)`",
        "路由函数返回下一个节点的名字（字符串）",
        "典型场景：判断是否需要检索、是否需要工具、去哪个分支",
    ], "写一个按意图返回“检索/闲聊/求助”的路由函数",
     "农户的问题分类型，用路由分流到不同处理链"),
    ("LangGraph：循环与图的控制", [
        "图可以成环（A→B→A），实现多轮工具调用/自我纠错",
        "用“最大轮数”防止死循环：状态里计数",
        "条件路由+环 = Agent 循环执行直到结束",
    ], "实现一个最多调用工具 3 次的循环图",
     "Agent 查完虫害还要查防治，就需要循环"),
    ("LangGraph：子图与多 Agent", [
        "把子图当作节点嵌入主图，模块化复用",
        "子图有自己的内部状态，主图只看到出入口",
        "多 Agent 协作：一个主管路由，多个专家子图",
    ], "把一个“检索子图”嵌入主问答图",
     "水稻不同主题（病虫害/水肥/气象）各自成子图"),
    ("LangGraph：检查点与持久化", [
        "Checkpointer 保存每一步状态，支持断点续跑/回放",
        "也用来保存多轮对话记忆（thread_id）",
        "SqliteSaver 把状态存 SQLite，符合本工具数据本地原则",
    ], "用 SqliteSaver 保存对话状态，跨请求恢复",
     "农户多轮对话上下文，靠检查点持久化"),
    ("LangGraph：水稻问答 Agent 实战", [
        "串起：路由→检索→工具→生成→校验 的完整图",
        "把前几天的组件（模板/向量库/工具）都接入图",
        "端到端跑通一条真实农技问答",
    ], "把水稻问答 Agent 端到端跑通，回答一个真实问题",
     "这就是水稻知识库 MVP 的核心可运行版本"),
])

# ---------- 第7周 RAG · 检索增强 ----------
CARDS += weekday_cards(7, [
    ("RAG：整体架构", [
        "RAG = 检索(Retrieval) + 生成(Generation)，先查资料再回答",
        "索引流程：文档→分块→向量化→入库",
        "查询流程：问题→向量化→检索→拼上下文→生成",
    ], "画出水稻知识库的 RAG 索引与查询两条流程",
     "水稻问答的核心就是一套 RAG 系统"),
    ("RAG：文本嵌入 Embedding", [
        "embedding 把文本变向量，语义相近向量距离近",
        "选模型：bge、text-embedding 等；中文农技用中文模型效果更好",
        "维度与模型强相关，检索与入库必须用同一模型",
    ], "把“稻瘟病”和“水稻病害”两个词向量化，看相似度",
     "Embedding 选型直接决定水稻检索质量"),
    ("RAG：向量检索", [
        "余弦相似度/内积 找最近邻",
        "PGVector 扩展在 PostgreSQL 里做向量检索",
        "top_k 控制返回条数，别一次拉太多",
    ], "用 PGVector 或 Chroma 检索“水稻叶面发黄”最相近的文档",
     "水稻知识库已规划 PGVector，这正是落地点"),
    ("RAG：混合检索", [
        "关键词检索(BM25) + 向量检索 结合，兼顾精确与语义",
        "农业术语精确（如“赤枯病”）适合关键词",
        "用加权合并两个结果集",
    ], "把 BM25 与向量检索结果各取前5合并去重",
     "水稻专业名词多，混合检索比纯向量更稳"),
    ("RAG：重排序 Rerank", [
        "先粗召回再精排：rerank 模型对候选重新打分",
        "显著提升 top_k 命中质量，成本高但值得",
        "常见：bge-reranker、Cohere rerank",
    ], "对检索到的 10 条用 rerank 重排取前 3",
     "水稻回答引用哪几条资料，靠重排序把关"),
])

# ---------- 第8周 RAG · 评测与优化 ----------
CARDS += weekday_cards(8, [
    ("RAG 评测：指标", [
        "忠实度（是否基于资料）、相关性、上下文精度/召回",
        "回答质量 vs 检索质量 分开评估",
        "用真实农户问题建评测集，才测得准",
    ], "列出水稻问答要评估的 3 个核心指标",
     "评测集就是 100 条真实农技问题+参考答案"),
    ("RAG 评测：RAGAS 框架", [
        "RAGAS 自动化评估 RAG 的忠实度/相关性",
        "构造 synthetic 测试集，或用自己的标注集",
        "跑完出分数，便于版本对比",
    ], "用 RAGAS 跑一遍小评测集，输出分数",
     "每次改知识库都跑评测，用分数证明有没有变好"),
    ("RAG 优化：幻觉与溯源", [
        "幻觉=模型编造没依据的内容，农业场景后果严重",
        "回答必须带资料引用，无资料就说“资料库没有”",
        "用溯源（返回来源文档+页码）倒逼检索质量",
    ], "给回答加“参考来源”字段，无依据时明确拒绝",
     "水稻用药/防治建议绝不能编，溯源是底线"),
    ("RAG 优化：分块与元数据", [
        "分块大小影响检索粒度：小块精确、大块完整",
        "给块打元数据（品种/病害/年份），支持过滤检索",
        "元数据过滤=用条件缩小检索范围",
    ], "给水稻文档分块时加“作物+病害类型”元数据并过滤",
     "按品种/病害过滤，水稻问答才能精准定位"),
    ("RAG 实战：水稻知识库评测", [
        "端到端：加载水稻资料→建索引→问答→评测出分",
        "找出 3 个失败案例，分析是检索还是生成问题",
        "调整分块/重排/提示词后重新评测对比",
    ], "对水稻知识库做一次完整评测并给出优化清单",
     "把评测做成日常流程，越用越准"),
])

# ---------- 第9周 安全合规 ----------
CARDS += weekday_cards(9, [
    ("安全：提示注入防护", [
        "用户可能试图让模型越权/泄露系统提示",
        "把“系统指令”与“用户内容”严格隔离，别把用户话拼进 system",
        "对输出做敏感内容过滤与关键词拦截",
    ], "构造一个注入攻击样本，验证系统不被带偏",
     "水稻系统面对的是真实用户，注入防护必须做"),
    ("安全：数据隐私与脱敏", [
        "农户数据、地理位置、手机号等敏感信息要脱敏",
        "API key、数据库口令走环境变量/密钥服务",
        "日志里不打敏感字段",
    ], "写一个脱敏函数，把手机号/姓名打码后再入库",
     "农业数据涉及农户隐私，合规先行"),
    ("安全：内容安全合规", [
        "生成内容要过内容安全审核（涉及政策/医疗/安全红线）",
        "农业建议要有免责声明：仅供参考，不构成专业诊断",
        "接入内容安全 API 或自建拦截词表",
    ], "给农药/化肥回答加“请咨询当地农技站”免责声明",
     "农技回答涉及用药安全，合规是硬门槛"),
    ("安全：鉴权与权限", [
        "接口要鉴权，别裸奔在公网",
        "简单方案：API key / JWT；内网可加访问控制",
        "管理端与普通端权限分离",
    ], "给问答接口加一个简单的 Bearer Token 校验",
     "知识库对外开放前，先把鉴权做上"),
    ("安全：幻觉治理与免责", [
        "模型不确认的资料要标注“待核实”",
        "重大决策（用药剂量）必须引用权威来源",
        "交互文案写明“AI 仅供参考”",
    ], "为高风险农技回答设计“引用+免责”的双保险文案",
     "水稻用药建议出错可能误农时，必须严谨"),
])

# ---------- 第10周 部署运维 · 基础 ----------
CARDS += weekday_cards(10, [
    ("部署：Docker 基础", [
        "镜像=只读模板，容器=运行实例：`docker run -p 8000:8000 img`",
        "Dockerfile：FROM + COPY + CMD，多阶段构建减小体积",
        "`docker build -t name .` + `docker run` 跑起来",
    ], "把本工具的 FastAPI 后端打包成一个镜像并运行",
     "水稻系统上服务器，先学会用 Docker 打包"),
    ("部署：Docker Compose", [
        "compose 用 YAML 编排多服务：后端/前端/数据库/模型",
        "`docker compose up -d` 一键启动，数据用 volume 持久化",
        "env_file 管理环境变量",
    ], "为“后端+数据库”写一个 compose 文件并一键启动",
     "水稻知识库就是一套多服务 compose 编排"),
    ("部署：Ollama/vLLM 本地模型", [
        "Ollama：一键跑本地开源模型：`ollama run qwen2.5`",
        "vLLM：高性能推理，支持并发与 KV cache",
        "本地模型接口兼容 OpenAI 格式，代码无缝切换",
    ], "用 Ollama 拉一个轻量模型并调通接口",
     "水稻数据敏感时，模型放本地私有化部署"),
    ("部署：配置管理", [
        "环境变量区分 dev/prod：DATABASE_URL、MODEL_NAME",
        "`.env` 本地 + 服务器环境变量，不提交密钥",
        "配置集中、可覆盖、可审计",
    ], "把模型名和数据库地址改成环境变量驱动",
     "多环境部署，配置不写死在代码里"),
    ("部署：日志与监控", [
        "结构化日志（JSON 行）方便收集与检索",
        "监控关键指标：请求量、延迟、错误率、token 消耗",
        "Prometheus + Grafana 是标准组合",
    ], "给后端加访问日志，记录每个请求的耗时与错误",
     "水稻系统上线后，靠日志和监控发现异常"),
])

# ---------- 第11周 部署运维 · 生产实践 ----------
CARDS += weekday_cards(11, [
    ("运维：性能优化与并发", [
        "慢查询是头号问题：索引、缓存、异步并发",
        "模型调用是瓶颈：合并请求、控制并发数、超时重试",
        "用连接池复用数据库连接",
    ], "压测 /ask 接口，找出吞吐瓶颈并优化",
     "水稻问答要扛住农忙季的高峰并发"),
    ("运维：缓存与限流", [
        "高频问题结果缓存，命中直接返回",
        "限流保护模型与数据库：令牌桶/漏桶",
        "缓存要设过期，别让陈旧数据误导农户",
    ], "给热门问题加内存缓存，并给接口加简单限流",
     "重复问题别每次重算，缓存省成本也更快"),
    ("运维：CI/CD 自动化", [
        "CI：代码提交自动跑测试与构建",
        "CD：构建镜像→推仓库→部署到服务器",
        "常用：GitHub Actions / GitLab CI",
    ], "写一个 GitHub Actions 自动构建并测试后端",
     "水稻系统迭代频繁，靠 CI/CD 省人工"),
    ("运维：灰度与回滚", [
        "新版本先灰度一小部分流量，验证再全量",
        "镜像打版本标签（v1.0.0），随时回滚上一版",
        "数据库迁移要向后兼容",
    ], "给后端镜像加版本标签，演示回滚到上一版",
     "改坏知识库配置能一键回滚，才有安全感"),
    ("运维：生产故障排查", [
        "故障处理四步：看日志→看监控→复现→修复",
        "先止血（回滚/重启），再根因分析",
        "记录事故复盘，形成预案",
    ], "模拟一次模型超时故障，按步骤排查并记录",
     "系统上线后最值钱的就是排障能力"),
])

# ---------- 第12周 FDE 认证冲刺 ----------
CARDS += weekday_cards(12, [
    ("FDE 认证：概览与考点", [
        "FDE（前沿部署工程师）：聚焦大模型/生成式 AI 的部署落地",
        "考点覆盖：模型部署、推理优化、RAG、提示工程、私有化、安全",
        "理论+实操，动手是关键",
    ], "梳理 FDE 考纲，列出自己薄弱项做成冲刺清单",
     "把 12 周所学对照考纲逐条自查"),
    ("FDE 认证：腾讯云 ADP 核心产品", [
        "ADP（AI 开发平台）：模型部署、数据集、工作流一体",
        "支持私有化部署，契合农业数据不上云诉求",
        "熟悉控制台：模型仓库、在线推理、监控",
    ], "在 ADP 控制台走一遍模型部署流程",
     "认证考点常考产品实操，动手过一遍"),
    ("FDE 认证：大模型部署最佳实践", [
        "部署链路：模型→推理框架→API→网关→应用",
        "推理优化：量化、vLLM、KV cache、动态批处理",
        "容错：健康检查、超时、优雅降级",
    ], "写一篇“水稻问答模型部署方案”提纲",
     "把水稻系统当成 FDE 认证的实战项目"),
    ("FDE 认证：私有化与推理优化", [
        "私有化部署的取舍：成本、性能、数据安全",
        "量化（INT8/INT4）省显存，精度损失可接受",
        "显存=并发上限，评估 RTX 工作站够不够",
    ], "估算自己 RTX 5090 能跑多大的模型、多少并发",
     "水稻数据私有化部署，推理优化是重点"),
    ("FDE 认证：模拟题与应试策略", [
        "刷官方样题，熟悉题型（概念+场景+实操）",
        "不会的先标记，最后再补；案例题先答框架再填细节",
        "实操题平时多敲，考试少犯错",
    ], "做一套模拟题并复盘错题，整理错题本",
     "把 12 周知识系统化，带着水稻项目去应试"),
])

# ---------- 各周周末轻量内容 ----------
def _light(title, note, points, exercise):
    return {"title": title, "note": note, "points": points, "exercise": exercise}

LIGHT = {
    1: _light("Python 轻量：行业动态与工具", "本周热身完成。关注 Python 3.13、AI 工程化动态；回顾 venv/requests 用法。",
              ["本周关键：venv 隔离 + requests 调模型接口是后续所有开发的地基", "面试题：解释 Python 中 list 与 tuple 的区别"],
              "把本周 5 天内容用一句话各写一遍，加深记忆"),
    2: _light("Python 轻量：面试题与开源工具", "本周掌握异步/FastAPI/Pydantic。推荐 FastAPI 官方文档精读。",
              ["面试题：async/await 如何提升并发，适用什么场景", "推荐工具：httpx、uvicorn、ruff（代码检查）"],
              "用一个 asyncio 例子，说说它比同步快在哪"),
    3: _light("LangChain 轻量：官方动态", "本周入门 LCEL。看 LangChain 1.0 官方博客了解 1.0 与 0.x 差异。",
              ["LangChain 1.0 强调轻量与统一：langchain-core 是核心", "面试题：LCEL 的 `|` 运算符把组件串成什么"],
              "用一句话说明 prompt|model|parser 这条链做了什么"),
    4: _light("LangChain 轻量：开源工具推荐", "本周完成组件实战。推荐 langchain 官方 cookbook 与 LangSmith 观察链。",
              ["工具调用是 Agent 的基础能力，务必掌握 bind_tools", "推荐：LangSmith（可观测）、langchain hub（提示词模板）"],
              "把本周用过的 5 个组件写进自己的速查卡"),
    5: _light("LangGraph 轻量：面试题", "本周建立图思维。重点理解节点/边/状态三要素。",
              ["面试题：LangGraph 的节点和边分别是什么", "状态是图唯一数据源，所有节点读写同一份"],
              "用自己的话解释：为什么说 LangGraph 比线性链更可控"),
    6: _light("LangGraph 轻量：实战复盘", "本周完成水稻 Agent MVP。回顾条件路由与检查点用法。",
              ["条件路由 = add_conditional_edges + 路由函数", "检查点=持久化状态，跨请求恢复对话"],
              "画一遍水稻问答 Agent 的图：节点、边、分支"),
    7: _light("RAG 轻量：行业动态", "本周学完检索链路。关注开源 RAG 框架（如 RAGFlow、Dify）进展。",
              ["RAG = 检索+生成，先查资料再回答", "面试题：为什么农业场景要强调引用溯源"],
              "给“水稻叶面发黄”走一遍 RAG 四步流程"),
    8: _light("RAG 轻量：开源工具", "本周学评测。推荐 RAGAS 文档、LangSmith 评测面板。",
              ["忠实度/相关性是 RAG 最核心两个指标", "评测集用真实问题，结果才可信"],
              "列举你会用哪 3 个指标验收水稻问答"),
    9: _light("安全轻量：合规案例", "本周学安全合规。关注生成式 AI 服务管理办法动态。",
              ["提示注入与数据脱敏是上线必答题", "农技回答要有免责声明与来源引用"],
              "给你的水稻 Agent 列出 3 条上线前的安全清单"),
    10: _light("运维轻量：面试题", "本周学 Docker/compose/本地模型。回顾 compose 编排。",
              ["面试题：镜像与容器的区别", "volume 用来持久化数据，容器本身无状态"],
              "用 3 句话讲清 docker compose 能解决什么"),
    11: _light("运维轻量：生产经验", "本周学生产实践。推荐读 12-Factor App 与 SRE 入门。",
              ["监控三件套：日志、指标、告警", "灰度+回滚让变更可逆，是上线安全感的来源"],
              "列出你的水稻系统需要监控的 3 个指标"),
    12: _light("FDE 冲刺：考前复盘与工具", "认证冲刺收官。整理错题本，带水稻项目案例去考试。",
              ["把 12 周内容对照考纲自查，补齐薄弱项", "考前 2 天：过一遍实操命令，别只看理论"],
              "写一句：我的水稻知识库项目，如何证明我有 FDE 实战能力"),
}

for week in range(1, 13):
    l = LIGHT[week]
    CARDS += weekend_cards(week, l["title"], l["note"], l["points"], l["exercise"])


def main():
    CARDS.sort(key=lambda c: c["day"])
    assert len(CARDS) == 84, f"期望 84 张，实际 {len(CARDS)} 张"
    assert [c["day"] for c in CARDS] == list(range(1, 85)), "天数必须 1..84 连续"

    out_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
    path = os.path.join(out_dir, "cards_seed.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(CARDS, f, ensure_ascii=False, indent=2)
    # 校验：周一到周五主题、周六日轻量
    weekend = [c for c in CARDS if c["is_weekend"]]
    print(f"已生成 {len(CARDS)} 张卡片 -> {path}")
    print(f"  其中主题卡片 {len(CARDS)-len(weekend)} 张，轻量卡片 {len(weekend)} 张")
    for w in range(1, 13):
        cnt = len([c for c in CARDS if c["week"] == w])
        print(f"  第{w}周（{WEEK_TOPIC[w]}）: {cnt} 张")


if __name__ == "__main__":
    main()

# Library — 个人知识库 AI 应用

## 技术栈

| 层 | 技术 |
|-----|------|
| 前端 | Vue 3 + Vite + TypeScript + Tailwind CSS + vue-i18n |
| 后端 | Python FastAPI + Pydantic v2 |
| 向量存储 | numpy + JSON (`backend/data/vectors.json`) |
| AI 聊天 | 用户可配置 (DashScope / DeepSeek / OpenAI 兼容) |
| AI Embedding | 用户可配置，自动适配 DashScope 或 OpenAI 格式 |

## 项目结构

```
library/
├── .claude/
│   ├── agents/              # subagent 配置文件
│   └── reports/             # 开发+审查报告
├── backend/
│   ├── main.py              # FastAPI 入口，启动扫描
│   ├── config.py            # 配置管理，settings.json 读写
│   ├── data/                # vectors.json + settings.json
│   ├── models/schemas.py    # Pydantic 请求/响应模型
│   ├── routers/             # API 路由
│   │   ├── chat.py          # SSE 流式聊天
│   │   ├── documents.py     # 文档上传/列表/删除
│   │   ├── rag.py           # RAG 问答
│   │   └── settings.py      # 配置读写
│   ├── services/            # 业务逻辑层
│   │   ├── chat_service.py       # 多模型 SSE 聊天
│   │   ├── document_service.py   # 文档解析→分块→embedding→入库
│   │   ├── embedding_service.py  # 多格式 embedding (DashScope/OpenAI)
│   │   ├── rag_service.py        # RAG 检索+生成
│   │   └── vector_store.py       # numpy 余弦相似度 + JSON 持久化
│   └── utils/               # 工具
│       ├── document_parser.py    # PDF/DOCX 解析
│       └── text_chunker.py       # 文本分块
├── frontend/                # Vue3 前端
│   └── src/
│       ├── pages/HomePage.vue    # 主页面
│       ├── components/
│       │   ├── chat/             # 聊天面板、消息、输入框
│       │   ├── document/         # 文档上传、列表
│       │   ├── layout/           # 顶栏、侧栏
│       │   ├── settings/         # 设置面板、模型选择器
│       │   └── shared/           # Toast、Loading
│       ├── composables/          # 状态逻辑 (useChat/useDocuments/useSettings/useRagContext)
│       ├── locales/              # i18n (zh.json / en.json)
│       └── types/                # TypeScript 类型定义
└── CLAUDE.md                # 本文件
```

## 开发流程 (Subagent 工作流)

```
主 agent (分发任务、审查调度)
    │
    ├─→ frontend-dev  → 写前端代码 → 报告到 .claude/reports/
    ├─→ backend-dev   → 写后端代码 → 报告到 .claude/reports/
    └─→ code-review   → 只读审查 → 报告到 .claude/reports/
                              │
                        PASS → 完成
                        FAIL → 返给开发 agent 修改
```

## AI 配置 (用户可配置)

用户在设置面板配置，存储到 `backend/data/settings.json`：

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `api_key` | API 密钥 | 空（fallback 到 .env DASHSCOPE_API_KEY） |
| `api_base_url` | Chat API 地址 | DashScope 兼容端点 |
| `api_embedding_url` | Embedding API 地址 | DashScope embedding |
| `embedding_model` | Embedding 模型名 | text-embedding-v3 |
| `selected_model` | 聊天模型名 | qwen-plus |

支持的模型和推荐地址在前端设置面板有 datalist 建议（DashScope / DeepSeek / OpenAI），用户也可自由输入。

## 功能

- 上传 PDF/DOCX 文档 → 自动分块 → embedding → 入库
- 文档列表（来源: vectors.json，非文件夹直读）
- 启动时自动扫描上传文件夹，索引未入库文件
- 文档删除同时清理物理文件和向量数据
- 普通 AI 聊天（SSE 流式，多模型可切换）
- RAG 文档问答（选中文档 + 提问 → 带来源引用）
- 中英文切换 (vue-i18n)
- 用户自定义 API 配置、模型名

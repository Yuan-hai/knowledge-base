# Library — 个人知识库 AI 应用

## 技术栈

| 层 | 技术 |
|-----|------|
| 前端 | Vue 3 + Vite + TypeScript + Tailwind CSS |
| 后端 | Python FastAPI |
| 向量存储 | ChromaDB |
| AI | 通义千问 (Dashscope, 已配置 Anthropic 兼容代理) |

## 项目结构

```
library/
├── .claude/
│   ├── agents/           # subagent 配置文件
│   │   ├── frontend-dev.md
│   │   ├── backend-dev.md
│   │   └── code-review.md
│   └── reports/          # 开发+审查报告
├── frontend/             # Vue3 前端应用
├── backend/              # FastAPI 后端应用
└── CLAUDE.md             # 本文件
```

## 开发流程 (Subagent 工作流)

```
主 agent (分发任务)
    │
    ├─→ frontend-dev  → 写代码 → 报告到 .claude/reports/
    ├─→ backend-dev   → 写代码 → 报告到 .claude/reports/
    └─→ code-review   → 只读审查 → 报告到 .claude/reports/
                              │
                        PASS → 完成
                        FAIL → 返给开发 agent 修改
```

## AI 配置

- Chat: 走已配置的 Dashscope Anthropic 代理
- Embedding: Dashscope text-embedding-v3 (直接 HTTP 调用)

## 功能

- 上传 PDF/Word 文档
- 文档管理（列表、删除）
- 普通 AI 聊天
- RAG 文档问答（选择文档 + 提问 → 带来源引用的回答）

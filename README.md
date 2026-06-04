# Code Repository Q&A Agent

一个支持自然语言驱动、带代码引用溯源的智能代码问答系统。通过 AST 解析、混合检索和 LangGraph 智能体编排，帮助开发者快速查阅和理解大型代码仓库。

[English](./README.en.md) | **中文**

## 🎯 核心特性

- **多语言支持**：支持 Python、Java、C++、JavaScript、TypeScript、TSX 等 6 种编程语言的 AST 解析
- **混合检索**：Dense 语义检索 + BM25 词法检索 + RRF 融合，准确率提升 35%
- **智能问答**：基于 LangGraph 的多轮工具协调，支持符号查找、Git 历史、代码依赖分析
- **可溯源答案**：所有答案都附带 `文件:行号` 代码引用，用户可直接跳转到源代码验证
- **流式传输**：SSE 流式 API，首字节延迟 < 200ms，实时展示答案
- **全栈实现**：Python 后端 + React 前端，Docker 一键部署

## 🚀 快速开始

### 前置要求
- Docker & docker-compose
- Node.js 18+ (本地开发前端时)
- Python 3.12 (本地开发后端时)

### 使用 Docker 启动

```bash
# 1. 克隆仓库
git clone https://github.com/yourusername/repoqa.git
cd repoqa

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 API keys：
# DEEPSEEK_API_KEY=your_key_here

# 3. 启动所有服务
docker compose up --build

# 4. 访问应用
# 前端：http://localhost:5173
# 后端 API：http://localhost:8000/docs
# 健康检查：http://localhost:8000/health
```

### 本地开发

#### 后端
```bash
# 安装依赖
uv sync --all-groups

# 运行测试
make test

# 代码质量检查
make check

# 启动开发服务器
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端
```bash
cd ui
pnpm install
pnpm dev
```

## 📊 系统架构

```
浏览器 (React + TypeScript)
    ↓ SSE /api/*
FastAPI 后端
    ├─ LangGraph Agent (query_analyzer → planner → executor ↔ tool_node → synthesizer)
    ├─ MCP Tools (11 个工具：文件系统、Git、符号查找、依赖分析)
    └─ RAG System (Dense + BM25 + RRF + CrossEncoder)
    ↓
数据层 (Qdrant + PostgreSQL + Redis)
```

## 📈 性能指标

| 指标 | 目标 | 状态 |
|-----|------|------|
| 索引速度 | 50K 行代码 < 5 分钟 | ✅ |
| 检索准确率 | MRR@5 > 0.7 | ✅ (0.75+) |
| 代码覆盖 | 80%+ | ✅ (104 测试通过) |
| 类型检查 | mypy strict | ✅ (0 错误) |
| SSE 延迟 | < 200ms | ✅ |

## 📚 使用示例

### 1. 注册仓库
```bash
curl -X POST http://localhost:8000/repo/register \
  -H "Content-Type: application/json" \
  -d '{"repo_path": "/path/to/repo"}'
```

### 2. 提问（流式接收答案）
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "用户登录流程是什么？", "repo_root": "/path/to/repo"}' \
  -N
```

## 🏗️ 项目结构

```
src/
  ├── agent/          # LangGraph 智能体
  ├── ingestion/      # 代码索引（tree-sitter）
  ├── retrieval/      # 混合检索系统
  ├── mcp/            # 11 个 MCP 工具
  ├── api/            # FastAPI 路由
  └── db/             # 会话存储

ui/                   # React 前端

tests/                # 104+ 单元测试

docs/                 # 开发阶段文档 (Phase 0-6)
```

## 🔧 技术栈

**后端**
- Python 3.12 + FastAPI + LangGraph
- Qdrant (向量数据库) + PostgreSQL + Redis
- tree-sitter (多语言解析)
- pytest + mypy strict + ruff

**前端**
- React 18 + TypeScript + Vite
- Vanilla CSS

**DevOps**
- Docker + docker-compose
- Nginx 反向代理

## 📖 完整文档

详见 `docs/phases/` 目录下的 6 个开发阶段日志，包含详细的技术设计和实现细节。

## 🔐 安全性

- API key 通过 `.env` 管理，不提交到版本控制
- 会话隔离，支持 TTL 自动过期
- 所有输入通过 Pydantic 校验
- 配额系统支持速率限制

## 🤝 贡献

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/xyz`)
3. 提交更改 (`git commit -m 'Add xyz'`)
4. 确保测试通过 (`make check`)
5. 推送到分支并开启 Pull Request

## 📄 许可证

MIT License - 详见 [LICENSE](./LICENSE)

## 📞 支持

- 🐛 Bug 报告: [GitHub Issues](https://github.com/yourusername/repoqa/issues)
- 💬 讨论: [GitHub Discussions](https://github.com/yourusername/repoqa/discussions)


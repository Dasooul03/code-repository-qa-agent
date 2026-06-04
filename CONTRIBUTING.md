# 贡献指南

感谢你有兴趣为 Code Repository Q&A Agent 做出贡献！本文档描述了如何贡献代码、报告 bug 和改进文档。

## 行为准则

请对所有贡献者保持尊重和友好。我们致力于创建一个包容的社区。

## 报告 Bug

### 报告前
- 检查 [Issues](https://github.com/yourusername/repoqa/issues) 中是否已有相同的 bug 报告
- 检查文档和常见问题是否已有解决方案

### 报告步骤
1. 使用清晰的标题描述 bug
2. 提供详细的重现步骤
3. 提供具体的示例来展示步骤
4. 描述观察到的行为和预期的行为
5. 包含环境信息（OS、Python 版本、Docker 版本等）

### Bug 报告示例
```
标题: 索引大型仓库时内存溢出

重现步骤:
1. 使用 docker compose up 启动服务
2. POST /repo/register 注册一个 200K 行的代码仓库
3. 等待索引完成

预期行为: 索引在 10 分钟内完成
实际行为: 进程在 5 分钟后被杀死（内存耗尽）

环境:
- 操作系统: Ubuntu 22.04
- Python: 3.12
- 内存: 4GB
- Docker: 24.0
```

## 建议功能

- 在 [GitHub Discussions](https://github.com/yourusername/repoqa/discussions) 中讨论新功能
- 或开启一个标记为 `enhancement` 的 Issue

## 提交代码

### 1. Fork 和克隆
```bash
git clone https://github.com/your-username/repoqa.git
cd repoqa
```

### 2. 创建特性分支
```bash
git checkout -b feature/your-feature-name
```

分支命名约定:
- `feature/` - 新功能
- `fix/` - Bug 修复
- `docs/` - 文档改进
- `refactor/` - 代码重构
- `test/` - 测试相关

### 3. 做出更改

#### 后端开发
```bash
# 安装依赖
uv sync --all-groups

# 做出更改...

# 运行测试
uv run pytest

# 格式化代码
uv run black src tests

# 检查 lint 错误
uv run ruff check src tests --fix

# 类型检查
uv run mypy src tests
```

#### 前端开发
```bash
cd ui

# 安装依赖
pnpm install

# 做出更改...

# 类型检查
pnpm lint

# 构建检查
pnpm build
```

### 4. 提交更改

遵循提交消息约定:
```
feat(phase-x): add new feature
fix(component-name): resolve issue
docs: update README
test(module): add test cases
refactor(agent): improve code structure
```

### 5. 推送并开启 Pull Request

```bash
git push origin feature/your-feature-name
```

在 GitHub 上开启 PR，描述：
- 解决的问题或实现的功能
- 如何进行测试
- 涉及的文件列表

### PR 检查清单

提交前请确保：
- [ ] 所有测试通过 (`make check`)
- [ ] 代码遵循项目风格 (mypy strict, ruff, black)
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] commit 消息清晰明了
- [ ] 没有硬编码的 API key 或敏感信息

## 代码风格

### Python
- 使用 black 进行格式化（88 字符行宽）
- 使用 ruff 进行 linting
- 使用 mypy strict 进行类型检查
- 添加类型注解到所有函数
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/)

### TypeScript
- 使用 TypeScript strict 模式
- 所有变量和函数必须有类型注解
- 使用 Prettier 进行格式化（via Vite）

### 提交消息
```
<type>(<scope>): <subject>

<body>

<footer>
```

示例:
```
feat(agent): implement multi-round tool execution

Add support for conditional routing between executor and tool_node,
enabling up to 3 rounds of tool calls based on planning feedback.

Closes #123
```

## 测试要求

### 后端测试
- 新功能必须添加单元测试
- 目标覆盖率：80%+
- 使用 pytest 和 pytest-asyncio

### 前端测试
- 主要组件应有集成测试
- 使用 Vitest (可选)

```bash
# 运行所有测试
make test

# 运行特定测试
uv run pytest tests/agent/test_planner.py -v

# 生成覆盖率报告
uv run pytest --cov=src tests/
```

## 文档

### 代码文档
- 所有公共函数必须有 docstring
- 复杂逻辑应添加注释
- 保持 docstring 简洁（通常一句话）

### 项目文档
- 更新 README.md 中的相关部分
- 对于新功能，在 docs/ 中添加说明文档
- 更新 API 文档（FastAPI 自动生成，无需手动）

## 审查流程

1. **自动检查**：GitHub Actions 运行 lint、type-check 和测试
2. **代码审查**：至少一个维护者审查代码
3. **反馈**：维护者可能要求更改
4. **合并**：通过审查后，PR 被合并到 main 分支

## 发布流程

仓库维护者负责版本发布和 tag 管理，遵循 [Semantic Versioning](https://semver.org/)：
- MAJOR: 不兼容的 API 变化
- MINOR: 向后兼容的新功能
- PATCH: Bug 修复

## 获得帮助

- 📖 查看 docs/ 中的开发阶段文档
- 💬 在 GitHub Discussions 中讨论
- 🐛 查看现有的 Issues 了解常见问题

感谢你的贡献！

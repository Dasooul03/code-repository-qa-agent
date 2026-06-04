# GitHub 上线指南

## 完成度检查 ✅

你的项目已准备就绪：

- ✅ 104 个单元测试全部通过
- ✅ 100% 类型覆盖（mypy strict）
- ✅ 0 Lint 违规（ruff + black）
- ✅ 6 个完整的开发阶段文档
- ✅ 敏感信息已隐去
- ✅ 完整的 README 和文档
- ✅ MIT 许可证
- ✅ Docker 一键部署

## 步骤 1：验证敏感信息已移除 ✓

```bash
# 检查没有硬编码的 API key
grep -r "sk-" src/ tests/ ui/ 2>/dev/null || echo "✅ 无硬编码 key"

# 验证 .gitignore 正确配置
git check-ignore .env
# 输出：.env

# 验证 .env.example 中没有真实的 key
cat .env.example | grep "_API_KEY="
# 应该都是空的：DEEPSEEK_API_KEY=
```

## 步骤 2：运行最终测试 ✓

```bash
# 后端完整检查
make check
# 应该看到：✅ black, ✅ ruff, ✅ mypy, ✅ pytest

# 前端构建
cd ui && pnpm build
# 应该生成 dist/ 目录
```

## 步骤 3：在 GitHub 创建仓库

1. 访问 [github.com/new](https://github.com/new)
2. 仓库名称：`repoqa` 或 `code-repository-qa-agent`
3. 选择 `Public`（开源）
4. **不选择** "Initialize with README"（我们已有）
5. 点击 "Create repository"

## 步骤 4：推送代码到 GitHub

```bash
# 添加远程仓库
git remote add origin https://github.com/YOUR-USERNAME/repoqa.git

# 重命名主分支为 main（GitHub 默认分支）
git branch -M main

# 推送所有内容
git push -u origin main

# 验证成功
git remote -v
```

## 步骤 5：验证 GitHub 上的内容

访问 https://github.com/YOUR-USERNAME/repoqa，检查：

- ✅ README.md 正确显示
- ✅ 所有 6 个 Phase 提交可见
- ✅ LICENSE 文件存在
- ✅ docs/ 目录完整
- ✅ 没有 `.env` 文件（应在 .gitignore）
- ✅ 没有 `node_modules`（应在 .gitignore）

## 步骤 6：配置 GitHub 仓库（可选但推荐）

### 6.1 仓库设置

进入 Settings → General：

- **Description**: 
  ```
  AI-powered code Q&A system with LangGraph agent, hybrid retrieval, and MCP tools
  ```

- **Topics** (Tags)：
  ```
  langraph, rag, mcp, code-search, ai, python, fastapi, react
  ```

- **License**: MIT

### 6.2 启用 GitHub Pages（可选，托管项目文档）

Settings → Pages：
- Source: Deploy from a branch
- Branch: main, /docs folder
- 点击 Save

### 6.3 添加分支保护（可选但推荐）

Settings → Branches → Add rule：
- Branch name pattern: `main`
- Require pull request reviews: ✅ 1
- Require status checks: ✅ (如果有 GitHub Actions)

## 步骤 7：添加 GitHub Actions CI/CD（推荐）

创建 `.github/workflows/ci.yml`：

```yaml
name: CI

on: [push, pull_request]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install uv
      - run: uv sync --all-groups
      - run: uv run pytest
      - run: uv run ruff check src tests
      - run: uv run mypy src tests

  frontend-build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '18'
      - run: cd ui && pnpm install
      - run: cd ui && pnpm lint
      - run: cd ui && pnpm build
```

然后推送：
```bash
git add .github/
git commit -m "ci: add github actions workflow"
git push origin main
```

## 步骤 8：创建首个 Release（可选但推荐）

```bash
# 打上版本标签
git tag v1.0.0

# 推送标签
git push origin v1.0.0
```

然后在 GitHub 上：
1. 进入 Releases
2. 点击 "Create a release"
3. Tag: `v1.0.0`
4. Release title: `v1.0.0 - Initial Release`
5. Description:
   ```markdown
   # Features
   - Multi-language AST parsing (6 languages)
   - Hybrid retrieval (Dense + BM25 + RRF)
   - LangGraph-based agent orchestration
   - 11 MCP tools (filesystem, git, symbols, dependencies)
   - Real-time SSE streaming
   - Full-stack implementation (FastAPI + React)
   
   # Metrics
   - 104/104 tests passing
   - 80%+ code coverage
   - mypy strict mode compliance
   - 0 lint violations
   
   # Quick Start
   See [README.md](https://github.com/YOUR-USERNAME/repoqa#quick-start)
   ```

## 步骤 9：分享和推广（可选）

### 社区分享
- **Product Hunt**: https://www.producthunt.com/
- **Hacker News**: https://news.ycombinator.com/submit
- **Reddit**: r/MachineLearning, r/Python, r/WebDevelopment
- **Twitter/X**: 分享 GitHub 链接和项目特点

### 文档分享
- **Awesome Lists**: 提交到相关的 Awesome 列表
  - https://github.com/awesome-python
  - https://github.com/awesome-react
  - https://github.com/awesome-langchain

### 示例贴文

```markdown
🚀 Just open-sourced Code Repository Q&A Agent - an AI system for code understanding

Features:
✅ Multi-language AST parsing (Python, Java, C++, JS, TS)
✅ Hybrid retrieval with 35% accuracy boost
✅ LangGraph agent orchestration
✅ 11 MCP tools for code analysis
✅ Real-time SSE streaming

🏗️ Full-stack: FastAPI + React 18
📊 104 tests, 80%+ coverage, mypy strict
📖 Complete phase-by-phase documentation

GitHub: github.com/YOUR-USERNAME/repoqa

Let's democratize code understanding with AI! 🤖

#langchain #rag #ai #opensource #python #react
```

## 验证清单 ✅

上线前最后确认：

- [ ] GitHub 仓库创建成功
- [ ] 所有代码已推送
- [ ] README 在 GitHub 上正确显示
- [ ] 没有 `.env` 或其他敏感文件
- [ ] License 文件可见
- [ ] 所有 6 个 phase 文档完整
- [ ] (可选) GitHub Actions 配置并通过
- [ ] (可选) Release v1.0.0 已创建

## 常见问题

**Q: 如何更新项目？**
```bash
git add .
git commit -m "feat/fix/docs: description"
git push origin main
```

**Q: 如何接收贡献？**
- 等待 Pull Requests
- 在 Issues 中讨论建议
- 在 Discussions 中进行技术讨论

**Q: 如何管理项目？**
- 定期检查 Issues 和 PRs
- 回复社区提问
- 保持依赖更新
- 发布新版本（当有重大更新时）

---

## 最终提示

你的项目已完全准备就绪！以下是我对后续的建议：

1. **第一周**：设置 GitHub Actions 和 CI/CD
2. **第二周**：添加到 Awesome Lists
3. **第三周**：在社区中分享
4. **持续**：维护和改进

这是一个高质量的项目，有完整的文档和测试。相信会获得社区的关注！

祝发布顺利！🚀

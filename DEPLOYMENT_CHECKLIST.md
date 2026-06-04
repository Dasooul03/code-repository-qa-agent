# GitHub 上线前检查清单

## ✅ 代码和安全

- [ ] 移除所有硬编码的 API key 和敏感信息
  ```bash
  # 检查代码中是否有 API key
  grep -r "sk-\|pk-\|api_key=\|secret=" src/ tests/ ui/ --include="*.py" --include="*.ts" --include="*.tsx"
  ```

- [ ] 验证 `.gitignore` 正确配置
  ```bash
  git check-ignore -v .env
  git check-ignore -v src/api/quota.py  # 应该被忽略
  ```

- [ ] 所有敏感环境变量在 `.env.example` 中显示为空
  ```bash
  cat .env.example | grep "API_KEY\|PASSWORD"
  ```

- [ ] 没有提交过的隐私文件
  ```bash
  git log --diff-filter=D --summary | grep "delete mode"
  ```

## ✅ 代码质量

- [ ] 后端测试通过
  ```bash
  uv run pytest
  ```

- [ ] 代码格式化
  ```bash
  uv run black src tests --check
  ```

- [ ] Lint 检查通过
  ```bash
  uv run ruff check src tests
  ```

- [ ] 类型检查通过
  ```bash
  uv run mypy src tests
  ```

- [ ] 前端类型检查通过
  ```bash
  cd ui && pnpm lint
  ```

- [ ] 前端构建成功
  ```bash
  cd ui && pnpm build
  ```

## ✅ 文档完整性

- [ ] README.md 包含：
  - 项目描述和核心特性
  - 快速开始指南
  - 系统架构图
  - 项目结构说明
  - API 文档示例
  - 技术栈列表
  - 贡献指南链接
  - 许可证信息

- [ ] CONTRIBUTING.md 包含：
  - Bug 报告模板
  - 开发环境设置
  - 代码风格要求
  - 提交流程
  - 测试要求

- [ ] LICENSE 文件存在

- [ ] .env.example 包含所有必需的环境变量

- [ ] docs/phases/ 中所有阶段文档完整

## ✅ 项目配置

- [ ] pyproject.toml 包含正确的项目元数据
  ```toml
  [project]
  name = "repoqa"
  version = "1.0.0"
  description = "..."
  ```

- [ ] package.json 包含正确的项目信息

- [ ] Docker 配置可用：
  - [ ] Dockerfile 存在
  - [ ] docker-compose.yml 包含所有服务
  - [ ] .dockerignore 配置正确

- [ ] Makefile 包含所有必要命令

## ✅ Git 提交历史

- [ ] 提交消息遵循约定
  - [ ] Phase 提交使用 `feat(phase-x): description` 格式
  - [ ] 没有临时提交或 WIP 提交

- [ ] 主要功能的提交清晰可见
  ```bash
  git log --oneline | head -20
  # 应该看到 6 个主要 Phase 提交
  ```

## ✅ GitHub 仓库设置

**在 GitHub 创建仓库后：**

- [ ] 仓库名称：`repoqa` 或 `code-repository-qa-agent`
- [ ] 描述：简短且清晰的项目说明
- [ ] 主页 URL：(可选)
- [ ] 话题标签：`langraph`, `rag`, `mcp`, `code-search`, `ai`
- [ ] 许可证：MIT
- [ ] 默认分支：`main`（可选从 `master` 重命名）

## ✅ GitHub Actions (可选但推荐)

创建 `.github/workflows/ci.yml`：
```yaml
name: CI

on: [push, pull_request]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install uv
      - run: uv sync --all-groups
      - run: uv run pytest
      - run: uv run ruff check src tests
      - run: uv run mypy src tests

  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: cd ui && pnpm install
      - run: cd ui && pnpm lint
      - run: cd ui && pnpm build
```

## ✅ 发布前最后检查

- [ ] 本地构建 Docker 镜像成功
  ```bash
  docker compose build
  ```

- [ ] 本地 `docker compose up` 可以启动所有服务

- [ ] 能访问 `http://localhost:5173` 前端

- [ ] 能访问 `http://localhost:8000/docs` API 文档

- [ ] 能访问 `http://localhost:8000/health` 健康检查

- [ ] 测试一个完整的工作流：
  1. 注册仓库
  2. 等待索引完成
  3. 提问并获取答案
  4. 验证代码引用

## 📋 上传到 GitHub

```bash
# 1. 创建新的 GitHub 仓库（通过 GitHub Web 界面）

# 2. 添加远程仓库
git remote add origin https://github.com/yourusername/repoqa.git
# 或使用 SSH
git remote add origin git@github.com:yourusername/repoqa.git

# 3. 重命名主分支（可选，GitHub 默认为 main）
git branch -M main

# 4. 推送代码
git push -u origin main

# 5. 验证推送成功
git remote -v
```

## 📝 发布清单

发布后可选步骤：

- [ ] 在 GitHub Releases 创建 v1.0.0 发布
- [ ] 在 Awesome Lists 上列出项目
- [ ] 发布到 PyPI（如果设置了包）
- [ ] 在社区中分享（Hacker News, Reddit 等）

## 🎯 发布后维护

- [ ] 设置 GitHub Issues 模板
- [ ] 设置 Pull Request 模板
- [ ] 启用分支保护规则
- [ ] 定期检查和回复 Issues
- [ ] 保持依赖更新

---

**检查清单完成后，你的项目就可以安全地发布到 GitHub！** 🚀

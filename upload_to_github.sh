#!/bin/bash
# Code Repository Q&A Agent - GitHub 上传脚本
# 使用方法：bash upload_to_github.sh <GITHUB_USERNAME> <REPO_NAME>

set -e  # 任何错误就退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Code Repository Q&A Agent - GitHub 上传向导${NC}"
echo ""

# 检查参数
if [ $# -lt 2 ]; then
    echo -e "${RED}❌ 错误：需要提供 GitHub 用户名和仓库名${NC}"
    echo "使用方法："
    echo "  bash upload_to_github.sh <GITHUB_USERNAME> <REPO_NAME>"
    echo ""
    echo "示例："
    echo "  bash upload_to_github.sh daijiuyi repoqa"
    exit 1
fi

USERNAME=$1
REPO_NAME=$2
REPO_URL="https://github.com/${USERNAME}/${REPO_NAME}.git"

echo -e "${YELLOW}📋 上传信息${NC}"
echo "  用户名: $USERNAME"
echo "  仓库名: $REPO_NAME"
echo "  仓库地址: $REPO_URL"
echo ""

# 第1步：验证 Git 状态
echo -e "${YELLOW}1️⃣  检查 Git 状态...${NC}"
if [ -n "$(git status --porcelain)" ]; then
    echo -e "${RED}❌ 有未提交的更改。请先提交：${NC}"
    git status --short
    exit 1
fi
echo -e "${GREEN}✅ Git 工作目录清洁${NC}"
echo ""

# 第2步：检查远程仓库
echo -e "${YELLOW}2️⃣  检查远程仓库...${NC}"
if git remote get-url origin &>/dev/null; then
    echo -e "${YELLOW}⚠️  已存在远程仓库：$(git remote get-url origin)${NC}"
    read -p "   是否覆盖？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git remote remove origin
        echo -e "${GREEN}✅ 已移除旧远程仓库${NC}"
    else
        echo -e "${RED}❌ 已取消上传${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✅ 无存在的远程仓库${NC}"
fi
echo ""

# 第3步：添加远程仓库
echo -e "${YELLOW}3️⃣  添加远程仓库...${NC}"
git remote add origin "$REPO_URL"
echo -e "${GREEN}✅ 远程仓库已添加${NC}"
echo ""

# 第4步：重命名分支为 main（GitHub 默认分支）
echo -e "${YELLOW}4️⃣  重命名分支为 main...${NC}"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ]; then
    git branch -M main
    echo -e "${GREEN}✅ 已从 $CURRENT_BRANCH 重命名为 main${NC}"
else
    echo -e "${GREEN}✅ 已在 main 分支${NC}"
fi
echo ""

# 第5步：推送代码
echo -e "${YELLOW}5️⃣  推送代码到 GitHub...${NC}"
echo "   (这可能需要几分钟，请耐心等待)"
if git push -u origin main; then
    echo -e "${GREEN}✅ 代码推送成功！${NC}"
else
    echo -e "${RED}❌ 推送失败。请检查：${NC}"
    echo "   1. GitHub 仓库是否已创建"
    echo "   2. 是否有写入权限"
    echo "   3. GitHub 认证是否成功"
    exit 1
fi
echo ""

# 第6步：验证推送成功
echo -e "${YELLOW}6️⃣  验证推送...${NC}"
if git ls-remote origin main &>/dev/null; then
    echo -e "${GREEN}✅ 推送验证成功${NC}"
else
    echo -e "${YELLOW}⚠️  无法验证推送（可能是网络延迟）${NC}"
fi
echo ""

# 完成
echo -e "${GREEN}🎉 上传完成！${NC}"
echo ""
echo -e "${YELLOW}📌 后续步骤：${NC}"
echo "   1. 访问仓库: $REPO_URL"
echo "   2. 添加描述和话题标签"
echo "   3. (可选) 创建 Release: git tag v1.0.0 && git push origin v1.0.0"
echo "   4. (可选) 设置 GitHub Actions CI/CD"
echo ""
echo -e "${GREEN}✨ 项目已成功发布到 GitHub！${NC}"

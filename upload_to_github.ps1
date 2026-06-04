# Code Repository Q&A Agent - GitHub 上传脚本 (PowerShell)
# 使用方法：.\upload_to_github.ps1 -Username <GITHUB_USERNAME> -RepoName <REPO_NAME>

param(
    [Parameter(Mandatory=$true)]
    [string]$Username,

    [Parameter(Mandatory=$true)]
    [string]$RepoName
)

$ErrorActionPreference = "Stop"

# 颜色输出函数
function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Error-Custom {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "🚀 $Message" -ForegroundColor Yellow
}

# 开始
Write-Info "Code Repository Q&A Agent - GitHub 上传向导"
Write-Host ""

$RepoUrl = "https://github.com/${Username}/${RepoName}.git"

Write-Info "📋 上传信息"
Write-Host "  用户名: $Username"
Write-Host "  仓库名: $RepoName"
Write-Host "  仓库地址: $RepoUrl"
Write-Host ""

# 第1步：验证 Git 状态
Write-Info "1️⃣  检查 Git 状态..."
$status = git status --porcelain
if ($status) {
    Write-Error-Custom "有未提交的更改。请先提交："
    git status --short
    exit 1
}
Write-Success "Git 工作目录清洁"
Write-Host ""

# 第2步：检查远程仓库
Write-Info "2️⃣  检查远程仓库..."
try {
    $existingRemote = git remote get-url origin 2>$null
    if ($existingRemote) {
        Write-Host "⚠️  已存在远程仓库：$existingRemote" -ForegroundColor Yellow
        $response = Read-Host "   是否覆盖？(y/n)"
        if ($response -eq 'y' -or $response -eq 'Y') {
            git remote remove origin
            Write-Success "已移除旧远程仓库"
        } else {
            Write-Error-Custom "已取消上传"
            exit 1
        }
    } else {
        Write-Success "无存在的远程仓库"
    }
} catch {
    Write-Success "无存在的远程仓库"
}
Write-Host ""

# 第3步：添加远程仓库
Write-Info "3️⃣  添加远程仓库..."
git remote add origin $RepoUrl
Write-Success "远程仓库已添加"
Write-Host ""

# 第4步：重命名分支为 main
Write-Info "4️⃣  重命名分支为 main..."
$currentBranch = git rev-parse --abbrev-ref HEAD
if ($currentBranch -ne "main") {
    git branch -M main
    Write-Success "已从 $currentBranch 重命名为 main"
} else {
    Write-Success "已在 main 分支"
}
Write-Host ""

# 第5步：推送代码
Write-Info "5️⃣  推送代码到 GitHub..."
Write-Host "   (这可能需要几分钟，请耐心等待)"
try {
    git push -u origin main
    Write-Success "代码推送成功！"
} catch {
    Write-Error-Custom "推送失败。请检查："
    Write-Host "   1. GitHub 仓库是否已创建"
    Write-Host "   2. 是否有写入权限"
    Write-Host "   3. GitHub 认证是否成功"
    exit 1
}
Write-Host ""

# 第6步：验证推送成功
Write-Info "6️⃣  验证推送..."
try {
    git ls-remote origin main | Out-Null
    Write-Success "推送验证成功"
} catch {
    Write-Host "⚠️  无法验证推送（可能是网络延迟）" -ForegroundColor Yellow
}
Write-Host ""

# 完成
Write-Host "🎉 上传完成！" -ForegroundColor Green
Write-Host ""
Write-Info "📌 后续步骤："
Write-Host "   1. 访问仓库: $RepoUrl"
Write-Host "   2. 添加描述和话题标签"
Write-Host "   3. (可选) 创建 Release:"
Write-Host "      git tag v1.0.0"
Write-Host "      git push origin v1.0.0"
Write-Host "   4. (可选) 设置 GitHub Actions CI/CD"
Write-Host ""
Write-Host "✨ 项目已成功发布到 GitHub！" -ForegroundColor Green

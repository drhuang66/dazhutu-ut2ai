#!/bin/bash
# 🚀 ut2ai.com Railway 部署脚本
# 
# 使用方法：
# 1. 将 YOUR_GITHUB_USERNAME 替换为您的 GitHub 用户名
# 2. 运行: bash deploy.sh

echo "======================================"
echo "🐰 云上大耳兔 · Railway 部署准备"
echo "======================================"
echo ""

# ⚠️ 请修改这一行，替换为您的 GitHub 用户名
GITHUB_USERNAME="YOUR_GITHUB_USERNAME"

REPO_NAME="dazhutu-ut2ai"

echo "📋 步骤 1: 检查 Git 状态..."
if [ -z "$(git status --porcelain)" ]; then
    echo "✅ 工作区干净，无待提交文件"
else
    echo "⚠️ 有未提交的文件，请先处理或取消脚本"
    read -p "是否继续？(y/N): " confirm
    if [ "$confirm" != "y" ]; then
        exit 1
    fi
fi

echo ""
echo "📋 步骤 2: 设置远程仓库..."
echo "   GitHub 用户名: $GITHUB_USERNAME"
echo "   仓库名称: $REPO_NAME"
echo "   远程地址: https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
echo ""

# 添加/更新远程仓库
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git

echo ""
echo "📋 步骤 3: 设置主分支为 main..."
git branch -M main

echo ""
echo "📋 步骤 4: 推送到 GitHub..."
echo ""
echo "======================================"
echo "执行命令："
echo "   git push -u origin main"
echo ""
echo "如果遇到身份验证问题："
echo "   1. 确保已登录 GitHub (github.com)"
echo "   2. 如果使用个人访问令牌，输入令牌作为密码"
echo "======================================"
echo ""

# 执行推送（如果用户确认）
read -p "是否立即推送？(y/N): " push_confirm
if [ "$push_confirm" = "y" ]; then
    git push -u origin main
    if [ $? -eq 0 ]; then
        echo ""
        echo "======================================"
        echo "✅ 代码推送成功！"
        echo ""
        echo "下一步：在 Railway 上部署"
        echo "   1. 访问 https://railway.app"
        echo "   2. New Project → Deploy from GitHub repo"
        echo "   3. 选择 $GITHUB_USERNAME/$REPO_NAME"
        echo "   4. 设置环境变量 PORT=5000"
        echo "   5. 等待 1-3 分钟完成部署"
        echo ""
        echo "======================================"
    else
        echo ""
        echo "❌ 推送失败，请检查："
        echo "   - GitHub 用户名是否正确？"
        echo "   - 仓库是否已创建？"
        echo "   - 是否有推送权限？"
    fi
else
    echo ""
    echo "💡 手动执行以下命令完成部署："
    echo ""
    echo "   git remote add origin https://github.com/$GITHUB_USERNAME/$REPO_NAME.git"
    echo "   git branch -M main"
    echo "   git push -u origin main"
fi

echo ""
echo "📖 完整部署指南：DEPLOY_GUIDE.md"
echo "======================================"

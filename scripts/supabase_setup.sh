#!/bin/bash

# Supabase 项目设置脚本
# 用于初始化和配置 Supabase CLI

set -e

echo "🚀 开始设置 Supabase 项目..."

# 检查 Supabase CLI 是否已安装
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI 未安装"
    echo "请先安装 Supabase CLI:"
    echo "  macOS: brew install supabase/tap/supabase"
    echo "  Windows: choco install supabase"
    echo "  Linux: curl -fsSL https://supabase.com/install.sh | sh"
    exit 1
fi

echo "✅ Supabase CLI 已安装"

# 检查是否已初始化
if [ ! -f "supabase/config.toml" ]; then
    echo "📝 初始化 Supabase 项目..."
    supabase init
    echo "✅ 项目初始化完成"
else
    echo "✅ 项目已初始化"
fi

# 检查是否已链接到远程项目
if [ -f ".supabase/config.toml" ]; then
    echo "🔗 项目已链接到远程数据库"
    echo "当前项目信息:"
    supabase status
else
    echo "⚠️  项目未链接到远程数据库"
    echo "请运行以下命令链接到你的 Supabase 项目:"
    echo "  supabase login"
    echo "  supabase link --project-ref your-project-ref"
fi

echo ""
echo "📋 可用的命令:"
echo "  supabase start          # 启动本地服务"
echo "  supabase stop           # 停止本地服务"
echo "  supabase db push        # 推送迁移到远程数据库"
echo "  supabase db reset       # 重置本地数据库"
echo "  supabase config pull    # 拉取远程配置"
echo "  supabase config push    # 推送本地配置"
echo ""

echo "🎉 设置完成！" 
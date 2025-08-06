# Supabase CLI 使用指南

## 目录结构

现在项目使用标准的 Supabase CLI 目录结构：

```
supabase/
├── config.toml          # Supabase 配置文件
├── migrations/          # 数据库迁移文件
│   └── 20241201000000_create_ragspace_schema.sql
├── seed/               # 种子数据文件
│   └── seed.sql
└── functions/          # Edge Functions (未来使用)
```

## 安装 Supabase CLI

### macOS
```bash
# 使用 Homebrew
brew install supabase/tap/supabase

# 或使用 npm
npm install -g supabase
```

### Windows
```bash
# 使用 Chocolatey
choco install supabase

# 或使用 npm
npm install -g supabase
```

### Linux
```bash
# 下载二进制文件
curl -fsSL https://supabase.com/install.sh | sh
```

## 初始化项目

1. **登录 Supabase**
   ```bash
   supabase login
   ```

2. **链接到远程项目**
   ```bash
   supabase link --project-ref your-project-ref
   ```

3. **初始化本地开发环境**
   ```bash
   supabase init
   ```

## 数据库管理

### 应用迁移
```bash
# 应用所有迁移到远程数据库
supabase db push

# 应用迁移到本地数据库
supabase db reset
```

### 创建新迁移
```bash
# 创建新的迁移文件
supabase migration new add_vector_support

# 这会创建类似 supabase/migrations/20241201120000_add_vector_support.sql 的文件
```

### 生成迁移
```bash
# 基于本地数据库的更改生成迁移
supabase db diff -f migration_name
```

### 应用种子数据
```bash
# 应用种子数据到远程数据库
supabase db push --include-seed

# 应用种子数据到本地数据库
supabase db reset --seed
```

## 本地开发

### 启动本地服务
```bash
# 启动所有本地服务
supabase start

# 这会启动：
# - PostgreSQL 数据库 (端口 54322)
# - Supabase API (端口 54321)
# - Supabase Studio (端口 54323)
# - Inbucket (邮件测试服务器，端口 54324)
```

### 停止本地服务
```bash
supabase stop
```

### 重启本地服务
```bash
supabase restart
```

## 项目配置

### config.toml 管理

Supabase CLI 可以自动生成和更新 `config.toml` 文件：

```bash
# 初始化项目时自动生成 config.toml
supabase init

# 将本地配置推送到远程项目
supabase config push

### 手动编辑 config.toml

你可以直接编辑 `supabase/config.toml` 文件来修改配置：

```toml
# 修改项目 ID
project_id = "ragspace"

# 修改 API 端口
[api]
port = 54321

# 修改数据库端口
[db]
port = 54322

# 修改 Studio 端口
[studio]
port = 54323
```

### 环境变量
更新 `.env` 文件以使用本地开发环境：

```bash
# 本地开发环境
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZS1kZW1vIiwicm9sZSI6ImFub24iLCJleHAiOjE5ODM4MTI5OTZ9.CRXP1A7WOeoJeXxjNni43kdQwgnWNReilDMblYTn_I0

# 生产环境
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_KEY=your-anon-key
```

### 数据库连接
本地开发时，数据库连接信息：

- **主机**: `127.0.0.1`
- **端口**: `54322`
- **数据库**: `postgres`
- **用户**: `postgres`
- **密码**: `postgres`

## 常用命令

### 数据库操作
```bash
# 查看数据库状态
supabase status

# 备份数据库
supabase db dump -f backup.sql

# 恢复数据库
supabase db restore backup.sql
```

### 迁移管理
```bash
# 查看迁移历史
supabase migration list

# 回滚到特定迁移
supabase db reset --db-url postgresql://postgres:postgres@127.0.0.1:54322/postgres
```

### 项目链接
```bash
# 查看当前链接的项目
supabase projects list

# 切换项目
supabase link --project-ref new-project-ref
```

### 配置管理
```bash
# 将本地配置推送到远程项目
supabase config push
```

## 开发工作流

### 1. 本地开发
```bash
# 启动本地服务
supabase start

# 运行应用
poetry run python app.py

# 在另一个终端中运行测试
poetry run python test_supabase_integration.py
```

### 2. 创建数据库更改
```bash
# 创建新迁移
supabase migration new add_new_feature

# 编辑迁移文件
# 编辑 supabase/migrations/YYYYMMDDHHMMSS_add_new_feature.sql

# 应用迁移到本地
supabase db reset

# 测试更改
poetry run python test_supabase_integration.py
```

### 3. 部署到生产环境
```bash
# 应用迁移到远程数据库
supabase db push

# 应用种子数据
supabase db push --include-seed
```

## 故障排除

### 常见问题

1. **端口冲突**
   ```bash
   # 检查端口使用情况
   lsof -i :54321
   lsof -i :54322
   lsof -i :54323
   
   # 停止冲突的服务
   sudo kill -9 <PID>
   ```

2. **数据库连接失败**
   ```bash
   # 重启本地服务
   supabase stop
   supabase start
   ```

3. **迁移失败**
   ```bash
   # 重置本地数据库
   supabase db reset
   
   # 重新应用迁移
   supabase db push
   ```

### 调试技巧

1. **查看服务日志**
   ```bash
   supabase logs
   ```

2. **检查数据库状态**
   ```bash
   supabase status
   ```

3. **验证连接**
   ```bash
   # 测试数据库连接
   psql postgresql://postgres:postgres@127.0.0.1:54322/postgres
   ```

## 最佳实践

1. **迁移命名**: 使用描述性的迁移名称，如 `add_user_authentication`
2. **种子数据**: 只在 `seed.sql` 中放置测试数据，不要在生产迁移中包含测试数据
3. **版本控制**: 将 `supabase/` 目录提交到版本控制
4. **环境分离**: 使用不同的项目引用进行开发、测试和生产环境

## 下一步

1. **向量搜索**: 添加 pgvector 扩展支持
2. **用户认证**: 集成 Supabase Auth
3. **实时功能**: 使用 Supabase Realtime
4. **Edge Functions**: 创建自定义 API 端点 
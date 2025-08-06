# Supabase 配置管理

## 回答你的问题：Supabase CLI 可以更新 config.toml 吗？

**是的，Supabase CLI 可以自动生成、更新和管理 `config.toml` 文件。**

## 目录结构

现在项目使用标准的 Supabase CLI 目录结构：

```
supabase/
├── config.toml          # Supabase 配置文件 (CLI 可以自动生成和更新)
├── migrations/          # 数据库迁移文件
│   └── 20241201000000_create_ragspace_schema.sql
├── seed/               # 种子数据文件
│   └── seed.sql
└── functions/          # Edge Functions (未来使用)
```

## CLI 配置管理命令

### 1. 自动生成 config.toml

```bash
# 初始化项目时自动生成 config.toml
supabase init

# 这会创建包含所有默认配置的 config.toml 文件
```

### 2. 从远程项目拉取配置

```bash
# 从远程 Supabase 项目拉取最新配置
supabase config pull

# 这会更新本地的 config.toml 文件以匹配远程项目设置
```

### 3. 推送本地配置到远程

```bash
# 将本地配置推送到远程项目
supabase config push

# 这会将本地的 config.toml 设置应用到远程项目
```

### 4. 验证配置文件

```bash
# 验证 config.toml 语法和设置
supabase config verify

# 检查配置是否有错误或冲突
```

### 5. 查看当前配置

```bash
# 显示当前配置信息
supabase config show

# 查看所有配置选项和当前值
```

### 6. 重置配置

```bash
# 重置 config.toml 为默认值
supabase config reset

# 这会覆盖当前的配置文件
```

## 手动编辑 config.toml

你也可以直接编辑 `supabase/config.toml` 文件：

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

## 配置同步工作流

### 开发环境设置

1. **初始化项目**
   ```bash
   supabase init
   ```

2. **链接到远程项目**
   ```bash
   supabase login
   supabase link --project-ref your-project-ref
   ```

3. **拉取远程配置**
   ```bash
   supabase config pull
   ```

4. **本地开发**
   ```bash
   supabase start
   ```

### 配置更新流程

1. **修改本地配置**
   ```bash
   # 编辑 supabase/config.toml
   vim supabase/config.toml
   ```

2. **验证配置**
   ```bash
   supabase config verify
   ```

3. **推送配置**
   ```bash
   supabase config push
   ```

4. **应用更改**
   ```bash
   supabase restart
   ```

## 配置示例

### 基本配置
```toml
project_id = "ragspace"

[api]
enabled = true
port = 54321

[db]
port = 54322
major_version = 15

[studio]
enabled = true
port = 54323
```

### 高级配置
```toml
project_id = "ragspace"

[api]
enabled = true
port = 54321
schemas = ["public", "storage", "graphql_public"]
max_rows = 1000

[db]
port = 54322
shadow_port = 54320
major_version = 15

[db.pooler]
enabled = false
port = 54329
pool_mode = "transaction"

[realtime]
enabled = true
ip_version = "ipv4"

[studio]
enabled = true
port = 54323
api_url = "http://127.0.0.1:54321"

[storage]
enabled = true
file_size_limit = "50MiB"

[auth]
enabled = true
site_url = "http://127.0.0.1:3000"
jwt_expiry = 3600
enable_signup = true
```

## 最佳实践

### 1. 版本控制
- 将 `supabase/config.toml` 提交到版本控制
- 团队成员可以共享相同的配置

### 2. 环境分离
- 使用不同的项目引用进行开发、测试和生产
- 每个环境可以有独立的配置

### 3. 配置验证
- 在推送配置前总是运行 `supabase config verify`
- 确保配置语法正确且没有冲突

### 4. 备份配置
```bash
# 备份当前配置
cp supabase/config.toml supabase/config.toml.backup

# 恢复配置
cp supabase/config.toml.backup supabase/config.toml
```

## 故障排除

### 常见问题

1. **配置冲突**
   ```bash
   # 拉取远程配置覆盖本地更改
   supabase config pull
   ```

2. **端口冲突**
   ```bash
   # 修改 config.toml 中的端口设置
   [api]
   port = 54325  # 使用不同的端口
   ```

3. **配置验证失败**
   ```bash
   # 重置为默认配置
   supabase config reset
   ```

## 总结

Supabase CLI 提供了完整的配置管理功能：

- ✅ **自动生成**: `supabase init` 自动创建 config.toml
- ✅ **远程同步**: `supabase config pull/push` 同步远程配置
- ✅ **验证检查**: `supabase config verify` 确保配置正确
- ✅ **手动编辑**: 可以直接编辑 config.toml 文件
- ✅ **版本控制**: 支持 Git 版本控制

这使得配置管理变得简单和可靠，特别适合团队协作开发。 
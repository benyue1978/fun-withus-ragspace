# Poetry 使用指南

## 什么是 Poetry？

Poetry 是一个 Python 依赖管理和打包工具，它简化了 Python 项目的依赖管理、虚拟环境管理和打包发布。

## 安装 Poetry

### macOS/Linux
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

### Windows
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

### 添加到 PATH
```bash
export PATH="/Users/$USER/.local/bin:$PATH"
```

## 项目配置

### pyproject.toml
这是 Poetry 的核心配置文件，包含：

```toml
[tool.poetry]
name = "ragspace"
version = "0.1.0"
description = "AI Knowledge Hub"
authors = ["RAGSpace Team"]

[tool.poetry.dependencies]
python = "^3.10"
gradio = "^5.40.0"
python-dotenv = "^1.1.0"
requests = "^2.31.0"
numpy = "^1.24.0"

[tool.poetry.group.dev.dependencies]
watchdog = "^6.0.0"
pytest = "^8.0.0"
pytest-cov = "^6.2.1"

[tool.poetry.scripts]
ragspace = "app:main"
```

## 常用命令

### 环境管理

```bash
# 安装插件
poetry self add poetry-plugin-export

# 安装依赖
poetry install

# 激活虚拟环境
poetry shell

# 在虚拟环境中运行命令
poetry run python app.py

# 退出虚拟环境
exit
```

### 依赖管理

```bash
# 添加生产依赖
poetry add package-name

# 添加开发依赖
poetry add --group dev package-name

# 移除依赖
poetry remove package-name

# 更新依赖
poetry update

# 查看依赖树
poetry show --tree
```

### 项目运行

```bash
# 运行应用
poetry run python app.py

# 运行测试
poetry run python -m pytest tests/ -v

# 运行覆盖率测试
poetry run python -m pytest --cov=src/ragspace --cov-report=html

# 使用脚本别名
poetry run ragspace
```

### 打包发布

```bash
# 构建包
poetry build

# 发布到 PyPI
poetry publish

# 检查包信息
poetry check
```

## 与 pip 的对比

| 功能 | Poetry | pip + venv |
|------|--------|------------|
| 依赖管理 | ✅ 自动解析 | ⚠️ 手动管理 |
| 虚拟环境 | ✅ 自动创建 | ⚠️ 手动创建 |
| 锁定文件 | ✅ poetry.lock | ❌ 无 |
| 脚本别名 | ✅ pyproject.toml | ❌ 需要 setup.py |
| 开发依赖 | ✅ 分组管理 | ⚠️ 手动管理 |

## 项目结构

```
ragspace/
├── pyproject.toml      # Poetry 配置
├── poetry.lock         # 锁定文件（自动生成）
├── src/
│   └── ragspace/       # 源代码
├── tests/              # 测试文件
└── README.md
```

## 优势

1. **依赖解析**: 自动解决依赖冲突
2. **虚拟环境**: 自动管理项目虚拟环境
3. **锁定文件**: 确保依赖版本一致性
4. **脚本别名**: 简化命令执行
5. **分组依赖**: 区分生产和开发依赖
6. **现代标准**: 使用 pyproject.toml 标准

## 迁移指南

### 从 pip 迁移到 Poetry

1. **备份当前环境**
   ```bash
   pip freeze > requirements.txt
   ```

2. **创建 pyproject.toml**
   ```bash
   poetry init
   ```

3. **安装依赖**
   ```bash
   poetry add $(cat requirements.txt)
   ```

4. **测试项目**
   ```bash
   poetry run python -m pytest
   ```

## 最佳实践

1. **始终使用 poetry.lock**: 确保环境一致性
2. **分组依赖**: 使用 `--group dev` 区分开发依赖
3. **版本约束**: 使用 `^` 允许补丁更新
4. **脚本别名**: 为常用命令创建别名
5. **CI/CD**: 在 CI 中使用 `poetry install --no-dev`

## 故障排除

### 常见问题

1. **Poetry 命令未找到**
   ```bash
   export PATH="/Users/$USER/.local/bin:$PATH"
   ```

2. **依赖冲突**
   ```bash
   poetry update
   poetry show --tree
   ```

3. **虚拟环境问题**
   ```bash
   poetry env remove python
   poetry install
   ```

4. **缓存问题**
   ```bash
   poetry cache clear --all .
   ``` 
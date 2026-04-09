# Shared Configs

个人项目配置模板库，避免每个新项目重复配置开发工具链。

## 目录结构

```
shared-configs/
├── python/
│   ├── pyproject-tools.toml      # ruff/black/isort/pytest 配置
│   ├── .pre-commit-config.yaml   # pre-commit hooks
│   └── ci.yml                    # GitHub Actions CI
├── typescript/
│   └── ci.yml                    # Next.js CI workflow
└── README.md
```

---

## Python 项目使用方法

### 新项目

1. 复制配置文件：
   ```bash
   # 复制 pyproject.toml 工具配置
   cat python/pyproject-tools.toml >> your-project/pyproject.toml
   
   # 复制 pre-commit hooks
   cp python/.pre-commit-config.yaml your-project/
   
   # 创建 CI workflow
   mkdir -p your-project/.github/workflows
   cp python/ci.yml your-project/.github/workflows/
   ```

2. 安装 pre-commit hooks：
   ```bash
   cd your-project
   pip install pre-commit
   pre-commit install
   ```

3. 安装开发依赖：
   ```bash
   pip install ruff black isort pytest pytest-cov
   ```

### 现有项目

将 `pyproject-tools.toml` 中的配置段追加到现有的 `pyproject.toml` 末尾。

---

## TypeScript/Next.js 项目使用方法

1. 创建 CI workflow：
   ```bash
   mkdir -p your-project/.github/workflows
   cp typescript/ci.yml your-project/.github/workflows/
   ```

2. 确保 `package.json` 中有 `lint` 和 `build` 脚本。

---

## 配置说明

### Python 工具链

| 工具 | 配置 |
|------|------|
| ruff | line-length=100, 仅关键错误 |
| black | line-length=100, py311+ |
| isort | profile=black |
| pytest | asyncio_mode=auto, coverage |
| pre-commit | 安全检查 + 格式化 |

### CI/CD

- **Python**: lint → test (3个版本) → coverage
- **TypeScript**: lint → build → test

---

## 维护

更新模板后：
```bash
git add .
git commit -m "Update config templates"
git push
```

各项目需要手动同步最新配置。

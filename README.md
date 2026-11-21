# Project Templates

个人项目脚手架模板库 —— 避免每个新项目重复搭工具链。

> 原名 `shared-configs`，2026-11-21 改名为 `project-templates`（GitHub 已改，
> 本地目录因本会话持有 `.git` 句柄暂未改名，重启后补，见文末）。

## 作为 Claude Code skill 使用

本仓库同时是一个技能：根目录的 `SKILL.md` 定义了 `project-scaffold`，
通过 junction 挂到 `~/.claude/skills/project-scaffold`。

新建项目时只要说「新建项目 / 初始化仓库 / 配一下 CI」，Claude 就会：
读本仓库的模板 → 按项目类型选 profile → 复制并校验，而不是临场发挥。

**改模板 = 改 skill**，两者是同一份文件，不会漂移。

**2026-11 改版**：按实际技术栈（FastAPI + Next.js + uv + Cloudflare）重写，
移除 black / isort / bandit（ruff 已完全取代），修掉弃用配置，版本号全部对齐当前。

## 目录结构

```
shared-configs/
├── python/
│   ├── pyproject-tools.toml        # ruff + mypy + pytest + coverage（分块，按需追加）
│   ├── .pre-commit-config.yaml     # Python 项目的完整钩子集
│   ├── ci.yml                      # 纯 Python 项目 CI（uv + matrix）
│   └── ci-fullstack.yml            # Python + web/ 前端 + Playwright E2E
├── typescript/
│   ├── .pre-commit-config.yaml     # 前端项目：只做语言无关检查
│   └── ci.yml                      # React / Next.js / Vite CI
├── scripts/
│   └── guard_staged.py             # 跨平台守卫：.env/密钥文件 + Markdown 断链
└── README.md
```

---

## 取舍原则：不是每个项目都用得全

**核心思路：按「是否语言无关」分层，而不是把最先进的东西全塞进去。**

体检实际数据：22 个 Python 项目里，用 ruff 的 12 个、mypy 5 个、coverage 3 个；
43 个前端项目中大部分没有 pre-commit。所以模板必须可裁剪。

### 按项目类型选

| 项目类型 | pyproject 追加 | pre-commit 用 | CI 用 |
|---|---|---|---|
| Python 服务 / 库（uv） | `ruff` + `pytest` + `coverage`（`mypy` 按需） | `python/` 完整版 | `python/ci.yml` |
| Python + web/ 前端同仓 | 同上 | 完整版 | `python/ci-fullstack.yml` |
| Python 但用 pip / requirements.txt | `ruff` + `pytest` | 完整版（去掉 uv 相关说明） | `ci.yml` 换成 pip 步骤 |
| 纯前端 / TypeScript | 不加 | `typescript/` 版 | `typescript/ci.yml` |
| 一次性脚本 / 实验 | 只追加 `[tool.ruff]` | 只留「文件卫生 + 密钥」两块 | 不加 |
| 文档仓库 / vault | 不加 | 只留 Markdown 两钩子 | 不加 |

### 三个判断标准

1. **语言无关 → 必选**。文件卫生、密钥扫描、`.env` 拦截，任何项目都受益，
   而且零配置、零额外依赖，不会因为项目变大而变慢。
2. **语言特定 → 放 CI**。ESLint、`tsc`、`vitest` 不进 pre-commit：跑得慢，
   每次 commit 都等一遍，实际会被人 `--no-verify` 绕过。CI 里跑一次足够。
3. **工具链有替代 → 只留一个**。ruff 覆盖 black + isort + bandit；保留多套
   只会让三个工具互相改写同一份文件。

### 每个块都能整块删除

`python/.pre-commit-config.yaml` 里每个 `repo:` 块都标了 【必选】/【可选】，
注释里写了什么情况下删。删任意块后 YAML 仍成立，不需要改别的地方。

---

## Python 项目怎么用

### 1. 依赖与版本

```toml
[project]
requires-python = ">=3.11"

[dependency-groups]
dev = ["pytest", "pytest-asyncio", "pytest-cov", "ruff", "mypy", "pre-commit"]
```

uv 管理依赖，`uv.lock` 入库。

### 2. 追加工具配置（按需，可只取其中几段）

```bash
# 全部
cat ../shared-configs/python/pyproject-tools.toml >> pyproject.toml

# 只要 ruff 段（脚本类项目）
sed -n '/^\[tool.ruff\]/,/^\[tool.mypy\]/p' ../shared-configs/python/pyproject-tools.toml >> pyproject.toml
```

> ⚠️ **`[tool.ruff] target-version` 必须等于 `requires-python` 的下限**。
> 写高了，`pyupgrade` 会改出旧版本跑不了的代码。

### 3. pre-commit

```bash
mkdir -p scripts
cp ../shared-configs/scripts/guard_staged.py scripts/
cp ../shared-configs/python/.pre-commit-config.yaml .
uv run pre-commit install
uv run pre-commit run --all-files
```

`gitleaks` 需要二进制：

```powershell
winget install --id Gitleaks.Gitleaks   # Windows
```

没装就注释掉 gitleaks 块，`detect-private-key` 仍会兜底。

### 4. CI

```bash
mkdir -p .github/workflows
cp ../shared-configs/python/ci.yml .github/workflows/ci.yml
# 全栈项目改用 ci-fullstack.yml，按需改 WEB_DIR / PY_VER
```

不用 uv 的项目，把 `uv sync` 换成 `pip install -e ".[dev]"`。

---

## TypeScript 项目怎么用

```bash
cp ../shared-configs/typescript/.pre-commit-config.yaml .
mkdir -p scripts && cp ../shared-configs/scripts/guard_staged.py scripts/
mkdir -p .github/workflows && cp ../shared-configs/typescript/ci.yml .github/workflows/
```

`package.json` 需要有 `build`，以及可选的 `lint` / `typecheck` / `test`
（模板全用 `--if-present`，缺了不报错）。

pnpm 项目把三处 `npm` 换成 `pnpm`，`cache: npm` 换成 `cache: pnpm`。

---

## 版本与坑（2026-11 实测）

| 组件 | 版本 | 说明 |
|---|---|---|
| pre-commit-hooks | v6.0.0 | |
| ruff-pre-commit | v0.17.6 | 钩子自带 ruff，与本机 CLI 版本互不影响 |
| gitleaks | v8.30.1 | 用 `gitleaks-system`；官方的 `gitleaks` 钩子需要 Go |
| mdformat | **0.7.22** | ⚠️ 不能升 1.0.0：`mdformat-tables` 仍要求 `mdformat<0.8.0` |
| pymarkdown | v0.9.42 | 纯 Python，不依赖 Node。全局参数必须写在 `scan` 之前 |
| actions/checkout | v7 | |
| actions/setup-node | v7 | |
| astral-sh/setup-uv | **v10.4.0** | 该仓库没有 `v10` 浮动标签，必须写完整版本号 |
| codecov/codecov-action | v7 | 参数是 `files:`，不是旧版的 `file:` |

### 已踩过并修掉的坑

- **不要用 `markdownlint-cli`**：它 `language: node`，pre-commit 会用 nodeenv
  去拉 `node 27.0.0-alpha` 并崩在版本号解析上；`node: system` 在 Windows 上
  也不支持。改用纯 Python 的 pymarkdown。
- **pymarkdown 参数顺序**：`-d md013,... scan`，选项在前，子命令在后。
- **mdformat 与 markdownlint 同时带 `--fix` 会互相改写**，只让 mdformat 改。

---

## 相比旧版的改动

| 旧 | 新 | 原因 |
|---|---|---|
| ruff + black + isort + bandit 四件套 | 只用 ruff | `ruff format` 取代 black，`I`/`S` 规则取代 isort/bandit |
| `[tool.ruff] select/ignore` 顶层写法 | `[tool.ruff.lint]` | 顶层写法已弃用，ruff 会警告 |
| 版本停在 2024 初（hooks v4.5.0 / black 24.3） | 全部对齐 2026-11 | |
| `bash -c` 本地钩子 | `scripts/guard_staged.py` | 跨平台，Windows 不依赖 Git Bash |
| `.env` 只拦精确名 | 拦 `.env` 与 `.env.*`，放行 `.env.example` 等 | 实际泄漏多是 `.env.local` |
| 没有类型检查 | 增加 `mypy` 段（可选） | 五个项目已在用 mypy |
| 无 Markdown 规范 | mdformat + pymarkdown（可选） | 本机大量 Markdown 文档 |
| `actions/*@v4` | `@v7` | 旧版本已停止维护 |
| 只有 Python 模板 | 增加 TypeScript 版 | 43 个 `package.json`，之前完全没有钩子 |

---

## 维护

```bash
git add .
git commit -m "chore: update config templates"
git push
```

各项目需手动同步 —— 这是模板库不是包，没有自动分发。

---

## 待办：本地目录改名

GitHub 仓库已改名 `project-templates`，但本地目录仍是 `shared-configs`
（改名那一刻本会话正持有 `.git` 句柄）。重启 Claude Code 后执行：

```powershell
Move-Item C:\Users\Q\Code\shared-configs C:\Users\Q\Code\project-templates
Remove-Item "$env:USERPROFILE\.claude\skills\project-scaffold" -Force
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\project-scaffold" `
  -Target C:\Users\Q\Code\project-templates
```

junction 存的是绝对路径，所以**改名后必须重建**，否则技能会失效。

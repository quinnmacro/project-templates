---
name: project-scaffold
description: Use when starting a new project or adding a toolchain to a fresh repository — 用户说「新建项目」「初始化仓库」「搭个骨架」「配一下 lint / pre-commit / CI」时
---

# Project Scaffold

用已经验证过的模板搭新项目，而不是每次临场发挥。模板就在本技能目录里。

## 何时使用

- 新建空仓库或空目录，需要 lint、格式化、pre-commit、CI
- 给已有仓库补工具链（只补缺的部分，不重写已有的）

不适用：改业务代码；只在已有项目里修一个 lint 报错。

## 先定 profile

| 项目类型 | 用哪些文件 |
|---|---|
| Python 服务 / 库（uv 管理） | `python/pyproject-tools.toml`、`python/.pre-commit-config.yaml`、`python/ci.yml` |
| Python + `web/` 前端同仓 | 同上，CI 换成 `python/ci-fullstack.yml` |
| 纯前端 / TypeScript | `typescript/.pre-commit-config.yaml`、`typescript/ci.yml` |
| 一次性脚本、实验 | 只取 `pyproject-tools.toml` 里的 `[tool.ruff]` 段 |
| 文档仓库 / vault | 只取 Markdown 两个钩子（mdformat + pymarkdown） |

判断不了就问用户一句，不要猜。**不要全量套用**——用不到的块删掉，模板里每块都标了必选/可选。

## 执行

1. 复制对应模板到项目；把 `scripts/guard_staged.py` 放到项目根 `scripts/`
2. 确认 `requires-python`，把 `[tool.ruff] target-version` 改成与它**下限一致**
3. 在项目 README 写清：怎么装钩子、怎么跑检查
4. **验证（必做）**：
   ```bash
   pre-commit validate-config .pre-commit-config.yaml
   SKIP=gitleaks-system pre-commit run --all-files   # 首次会把自动修复项改一遍，再跑一次应全通过
   ```
   有 CI 就本地跑一次 `ruff check .` / `npm run build`

## 硬规则

- **不覆盖已存在的文件**：先读，再问用户要不要合并
- `target-version` 必须等于 `requires-python` 下限，写高了 pyupgrade 会改出跑不了的代码
- `mdformat` 钉 **0.7.x**：`mdformat-tables` 1.0.0 仍要求 `mdformat<0.8.0`，升上去就装不上
- `astral-sh/setup-uv` 写 **v10.4.0**：该仓库没有 `v10` 浮动标签
- ESLint / `tsc` / vitest **不要**挂进 pre-commit，放 CI；pre-commit 只做语言无关的检查
- 本地钩子用 Python 脚本，不要用 `bash -c`（Windows 上依赖 Git Bash，还不跨平台）

## 常见错误

| 症状 | 原因 | 修法 |
|---|---|---|
| pre-commit 装 node 环境时崩在 `27.0.0-alpha` | 用了 `language: node` 的 markdownlint-cli | 换 `pymarkdown`（纯 Python） |
| `unrecognized arguments: --disable-rules` | pymarkdown 全局参数写在了 `scan` 后面 | 改成 `-d md013,... scan` |
| `target-version` 报错 | 与 `requires-python` 不一致 | 改前者的下限 |
| CI 找不到 `astral-sh/setup-uv@v10` | 浮动标签不存在 | 写完整 `v10.4.0` |
| 守卫提示拦不到 `.env.local` | 用了旧模板的精确匹配 | 用本模板的 `guard_staged.py files` |

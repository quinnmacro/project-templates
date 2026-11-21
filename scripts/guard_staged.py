#!/usr/bin/env python3
"""跨平台 pre-commit 守卫 —— 替代原来依赖 Git Bash 的 bash -c 钩子。

用法（pre-commit 会自己把暂存文件名传进来）：

    python scripts/guard_staged.py files  FILE [FILE ...]
        阻止提交 .env / 私钥 / 凭据文件

    python scripts/guard_staged.py links  FILE [FILE ...]
        检查 Markdown 里的相对链接是否指向真实存在的文件

退出码：0 通过，1 发现违规。
"""

from __future__ import annotations

import ntpath
import re
import sys
from fnmatch import fnmatchcase
from pathlib import Path
from urllib.parse import unquote, urlsplit

# .env 类的白名单：这些是要提交的模板文件
ALLOWED_ENV = {".env.example", ".env.sample", ".env.template", ".env.dist", ".env.test"}

BLOCKED_NAME_PATTERNS = (
    "*.pem",
    "*.key",
    "*.pfx",
    "*.p12",
    "*.jks",
    "id_rsa*",
    "id_ed25519*",
    "credentials.json",
    "service-account*.json",
    "*.keystore",
    ".netrc",
    ".npmrc",
    ".pypirc",
)

# 这些目录下的匹配不算（构建产物、第三方依赖）
IGNORED_DIRS = {
    "node_modules",
    ".venv",
    "venv",
    "dist",
    "build",
    ".next",
    "site-packages",
}

MD_LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def _skip(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def check_files(paths: list[str]) -> list[str]:
    problems: list[str] = []
    for raw in paths:
        path = Path(raw.replace("\\", "/"))
        if _skip(path):
            continue
        name = path.name
        if name == ".env" or (name.startswith(".env.") and name not in ALLOWED_ENV):
            problems.append(f"{raw}  (.env 文件)")
            continue
        for pattern in BLOCKED_NAME_PATTERNS:
            if fnmatchcase(name, pattern):
                problems.append(f"{raw}  (密钥/凭据文件 {pattern})")
                break
    return problems


def _repo_root(start: Path) -> Path:
    """向上找 .git 作为检查边界；找不到就退回文件所在目录。"""
    for parent in (start, *start.parents):
        if (parent / ".git").exists():
            return parent
    return start


def _safe_relative_target(target: str) -> str | None:
    """只返回可安全检查的本仓库相对路径，否则返回 None。

    必须拒绝带 scheme 的链接和 UNC / 绝对路径：对 ``\\\\server\\share`` 调用
    ``exists()`` 会让 Windows 发起 SMB 连接并泄漏 NTLM 凭据。
    """
    cleaned = unquote(target).split("#", 1)[0].split("?", 1)[0].strip()
    if not cleaned:
        return None
    if urlsplit(cleaned).scheme:  # http: / https: / file: / javascript: ...
        return None
    if cleaned.startswith(("/", "\\")):  # 绝对路径、UNC（\\\\server\\share）
        return None
    if ntpath.splitdrive(cleaned)[0]:  # C: / D: 等盘符
        return None
    if cleaned.startswith("<"):  # <mailto:...> 之类
        return None
    return cleaned


def check_links(paths: list[str]) -> list[str]:
    problems: list[str] = []
    for raw in paths:
        path = Path(raw)
        if path.suffix.lower() != ".md" or not path.is_file() or _skip(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        base = path.parent
        root = _repo_root(base).resolve()
        for target in MD_LINK.findall(text):
            cleaned = _safe_relative_target(target)
            if cleaned is None:
                continue
            try:
                resolved = (base / cleaned).resolve()
            except (OSError, RuntimeError):
                continue
            # 解析后必须仍在仓库内：拦掉 ../ 逃逸和符号链接指向仓库外
            if not resolved.is_relative_to(root):
                continue
            if not resolved.exists():
                problems.append(f"{raw}  → 断链: {target}")
    return problems


def main(argv: list[str]) -> int:
    if len(argv) < 2 or argv[0] not in {"files", "links"}:
        print(__doc__, file=sys.stderr)
        return 2

    mode, targets = argv[0], argv[1:]
    if not targets:
        return 0

    problems = check_files(targets) if mode == "files" else check_links(targets)
    if not problems:
        return 0

    header = ".env / 密钥文件不允许提交：" if mode == "files" else "Markdown 存在断链："
    print(header, file=sys.stderr)
    for item in problems:
        print(f"  - {item}", file=sys.stderr)
    if mode == "files":
        print(
            "\n确实需要提交请改用 .env.example 之类模板，或询问仓库所有者。",
            file=sys.stderr,
        )
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

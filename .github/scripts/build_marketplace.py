#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 TgtoDrive 插件市场目录 ``plugins.json``。

用法::

    python scripts/build_marketplace.py --repo <账号>/<仓库名>
    python scripts/build_marketplace.py            # 在 GitHub Actions 中自动读取 GITHUB_REPOSITORY

脚本扫描 ``plugins/*/plugin.json``，为每个插件从 ``dist/`` 中找到打包产物，
计算真实的 SHA-256 与字节数，并按固定 tag 拼出 Release 下载地址。

输出顶层结构固定为 ``{"schema_version": 1, "plugins": [...]}`` ——
TgtoDrive 读取市场目录时会校验 ``schema_version`` 必须为整数 ``1``，
且 ``plugins`` 数组最多 500 项。

默认读取每个插件目录下可选的 ``marketplace.json`` 覆盖市场元数据
（``category`` / ``homepage`` / ``python_requires`` / ``requirements`` /
``status`` / ``notice``），未提供时使用下方默认值。

只依赖 Python 标准库。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

# 本脚本位于 <repo>/.github/scripts/ 下，仓库根目录需往上三级
# （parents[0]=scripts, parents[1]=.github, parents[2]=仓库根）。
REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGINS_DIR = REPO_ROOT / "plugins"
DIST_DIR = REPO_ROOT / "dist"
DEFAULT_OUTPUT = REPO_ROOT / "plugins.json"

ANSI_ESCAPE = re.compile(r"\x1b\[[0-9;]*m")

# TgtoDrive 插件市场目录的协议约束：顶层必须是
# {"schema_version": 1, "plugins": [...]}，且 plugins 最多 500 项。
SCHEMA_VERSION = 1
MAX_PLUGINS = 500

VALID_STATUS = {"active", "withdrawn"}

DEFAULT_METADATA = {
    "category": "tool",
    "python_requires": ">=3.9",
    "requirements": [],
    "status": "active",
    "notice": "",
}


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def detect_repository() -> str:
    """按 GitHub Actions 环境变量推断仓库名。"""
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    if repo and "/" in repo:
        return repo
    return ""


def load_marketplace_metadata(plugin_dir: Path) -> dict:
    path = plugin_dir / "marketplace.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[错误] {path} 不是合法 JSON：{exc}")
    if not isinstance(data, dict):
        raise SystemExit(f"[错误] {path} 顶层必须是 JSON 对象")
    unknown = set(data) - set(DEFAULT_METADATA) - {"homepage"}
    if unknown:
        raise SystemExit(f"[错误] {path} 含未知字段：{', '.join(sorted(unknown))}")
    return data


def build_entry(
    plugin_dir: Path,
    repo: str,
    branch: str,
    artifact_ext: str,
    tag_template: str,
) -> dict:
    manifest = json.loads((plugin_dir / "plugin.json").read_text(encoding="utf-8"))

    plugin_id = manifest["id"]
    version = manifest["version"]
    artifact = DIST_DIR / f"{plugin_id}{artifact_ext}"

    if not artifact.is_file():
        raise SystemExit(
            f"[错误] 未找到产物 {artifact.relative_to(REPO_ROOT).as_posix()}。\n"
            "  market 目录是按 plugins/ 下的**每一个**插件生成的，因此所有插件都必须先打包，\n"
            f"  只打包 {plugin_id} 是不够的。请运行：\n"
            "    python scripts/package_plugin.py --all"
        )

    overrides = load_marketplace_metadata(plugin_dir)
    metadata = {**DEFAULT_METADATA, **{k: v for k, v in overrides.items() if k != "homepage"}}

    status = metadata.get("status", "active")
    if status not in VALID_STATUS:
        raise SystemExit(
            f"[错误] {plugin_dir.name}/marketplace.json 的 status 必须是 "
            f"{' 或 '.join(sorted(VALID_STATUS))}，实际为 {status!r}"
        )

    tag = tag_template.format(id=plugin_id, version=version)
    homepage = overrides.get("homepage") or (
        f"https://github.com/{repo}/tree/{branch}/plugins/{plugin_id}"
    )

    return {
        "id": plugin_id,
        "name": manifest.get("name", plugin_id),
        "version": version,
        "description": manifest.get("description", ""),
        "author": manifest.get("author", ""),
        "category": metadata.get("category", "tool"),
        "homepage": homepage,
        "download_url": (
            f"https://github.com/{repo}/releases/download/{tag}/{artifact.name}"
        ),
        "sha256": sha256_of(artifact),
        "size": artifact.stat().st_size,
        "python_requires": metadata.get("python_requires", ">=3.9"),
        "requirements": metadata.get("requirements", []),
        "status": status,
        "notice": metadata.get("notice", ""),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="生成 TgtoDrive 插件市场目录 plugins.json")
    parser.add_argument(
        "--repo",
        default="",
        help="GitHub 仓库，格式 账号/仓库名；缺省时读取 GITHUB_REPOSITORY 环境变量",
    )
    parser.add_argument("--branch", default="main", help="仓库分支，用于拼 homepage（默认 main）")
    parser.add_argument(
        "--artifact",
        choices=("zip", "py"),
        default="zip",
        help="plugins.json 指向的产物类型（默认 zip）",
    )
    parser.add_argument(
        "--tag-template",
        default="{id}-v{version}",
        help="Release tag 模板，可用 {id} 与 {version}（默认 {id}-v{version}）",
    )
    parser.add_argument("--out", default=str(DEFAULT_OUTPUT), help="输出文件（默认仓库根 plugins.json）")
    args = parser.parse_args(argv)

    repo = (args.repo or detect_repository()).strip()
    if not repo or "/" not in repo:
        raise SystemExit(
            "[错误] 未能确定 GitHub 仓库。请传入 --repo <账号>/<仓库名>，"
            "或在 GitHub Actions 中运行（自动读取 GITHUB_REPOSITORY）"
        )

    if not PLUGINS_DIR.is_dir():
        raise SystemExit(f"[错误] 未找到插件目录：{PLUGINS_DIR}")

    plugin_dirs = sorted(
        p for p in PLUGINS_DIR.iterdir() if p.is_dir() and (p / "plugin.json").is_file()
    )
    if not plugin_dirs:
        raise SystemExit(f"[错误] {PLUGINS_DIR} 下没有包含 plugin.json 的插件目录")

    entries = [
        build_entry(plugin_dir, repo, args.branch, f".{args.artifact}", args.tag_template)
        for plugin_dir in plugin_dirs
    ]
    entries.sort(key=lambda item: item["id"])

    if len(entries) > MAX_PLUGINS:
        raise SystemExit(
            f"[错误] 市场目录最多 {MAX_PLUGINS} 项插件，当前 {len(entries)} 项"
        )

    document = {"schema_version": SCHEMA_VERSION, "plugins": entries}

    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = REPO_ROOT / out_path
    out_path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    print(f"[完成] 已生成 {out_path.relative_to(REPO_ROOT).as_posix()}，共 {len(entries)} 个插件：")
    for entry in entries:
        print(
            f"  - {entry['id']} v{entry['version']} [{entry['status']}]  "
            f"{entry['size']} 字节  sha256={entry['sha256'][:16]}…"
        )
        print(f"    {entry['download_url']}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

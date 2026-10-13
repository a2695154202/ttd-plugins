#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""打包 TgtoDrive 插件产物。

用法::

    python scripts/package_plugin.py --plugin invites-signin
    python scripts/package_plugin.py --all

对每个插件完成四件事：

1. 校验 ``plugins/<id>/plugin.json`` 的清单字段是否符合 TgtoDrive 协议；
2. 生成单文件版 ``dist/<id>.py``（顶层 ``PLUGIN_MANIFEST`` 字面量 + 入口源码）；
3. 生成压缩包 ``dist/<id>.zip``（``plugin.json`` + 入口 + ``README.md`` + 附带资源）；
4. 打印产物的 SHA-256 与字节数，供 ``build_marketplace.py`` 与发布流程使用。

关于「单文件必须在顶层定义唯一的 PLUGIN_MANIFEST 常量字典」这条协议约束，
本脚本做了三重保证：

* ``PLUGIN_MANIFEST`` 是文件里的**第一条语句**，且全文件**只出现一次**赋值；
* 右侧是**纯字面量**（``ast.literal_eval`` 可解析），不使用变量、函数或表达式；
* 渲染器**不产生隐式字符串拼接**（``'a' 'b'``）——``pprint`` 会为超长字符串
  折行成相邻字面量，虽然仍是合法 Python，但会让一部分静态解析实现读不到完整
  值，因此这里改为自写的单行字符串渲染。

压缩包使用 ``ZIP_STORED`` 而非 ``ZIP_DEFLATED``：deflate 的字节输出依赖 zlib
版本（开发机与 CI 可能不同），会导致同源产物哈希不一致、``plugins.json`` 反复
被判为「不同步」。此外还固定了三处会影响字节的元数据：

* 条目时间戳 ``ZIP_DATE_TIME``；
* 条目顺序（按 POSIX 相对路径排序，避免 Windows 不区分大小写、Linux 区分大小写
  带来的顺序差异）；
* ``create_system``（默认随平台为 0 或 3，会写进中央目录）。

以上保证相同源码在任何平台、任何 Python 版本下都得到相同的字节与 SHA-256。

只依赖 Python 标准库，可直接在开发机与 GitHub Actions 上运行。
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import io
import json
import re
import sys
import tokenize
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"
DIST_DIR = REPO_ROOT / "dist"

ID_RE = re.compile(r"^[a-z][a-z0-9_-]{1,63}$")
INPUT_NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]{0,63}$")

INPUT_TYPES = {
    "text", "textarea", "password", "email", "url", "tel", "search",
    "date", "datetime-local", "time", "color", "number", "range",
    "boolean", "switch", "select", "radio", "multiselect",
}

EXCLUDE_DIR_NAMES = {"__pycache__", ".git", ".github", ".idea", ".vscode"}
EXCLUDE_FILE_NAMES = {"settings.json", "marketplace.json"}
EXCLUDE_FILE_SUFFIXES = {".pyc", ".pyo", ".log"}

# 固定 zip 内时间戳，使相同输入得到相同的 SHA-256，便于校验与复现
ZIP_DATE_TIME = (2020, 1, 1, 0, 0, 0)

# 不压缩：deflate 的输出字节依赖 zlib 版本，开发机与 GitHub Actions 可能不同，
# 会让同源产物哈希不一致；ZIP_STORED 下产物字节完全确定。
ZIP_COMPRESS_TYPE = zipfile.ZIP_STORED


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest(plugin_dir: Path) -> dict:
    manifest_path = plugin_dir / "plugin.json"
    if not manifest_path.is_file():
        raise SystemExit(f"[错误] 缺少清单文件：{manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"[错误] {manifest_path} 不是合法 JSON：{exc}")
    if not isinstance(manifest, dict):
        raise SystemExit(f"[错误] {manifest_path} 顶层必须是 JSON 对象")
    return manifest


def validate_manifest(plugin_dir: Path, manifest: dict) -> list[str]:
    """按 TgtoDrive 插件协议校验清单，返回问题列表。"""
    problems: list[str] = []

    if manifest.get("schema_version") != 1:
        problems.append("schema_version 必须为整数 1")

    plugin_id = manifest.get("id")
    if not isinstance(plugin_id, str) or not ID_RE.match(plugin_id):
        problems.append("id 必须匹配 ^[a-z][a-z0-9_-]{1,63}$")
    elif plugin_id != plugin_dir.name:
        problems.append(f"id ({plugin_id}) 与目录名 ({plugin_dir.name}) 不一致")

    name = manifest.get("name")
    if not isinstance(name, str) or not name.strip():
        problems.append("name 必须是非空字符串")
    elif len(name) > 100:
        problems.append("name 长度不能超过 100 字符")

    version = manifest.get("version")
    if not isinstance(version, str) or not version.strip():
        problems.append("version 必须是非空字符串")
    elif len(version) > 50:
        problems.append("version 长度不能超过 50 字符")

    entry = manifest.get("entry", "plugin.py")
    if not isinstance(entry, str) or not entry.endswith(".py"):
        problems.append("entry 必须是包内 .py 文件的相对路径")
    elif not (plugin_dir / entry).is_file():
        problems.append(f"entry 指向的文件不存在：{entry}")

    timeout = manifest.get("timeout", 60)
    if not isinstance(timeout, int) or isinstance(timeout, bool):
        problems.append("timeout 必须是整数")
    elif not 1 <= timeout <= 86400:
        problems.append("timeout 必须在 1–86400 之间")

    inputs = manifest.get("inputs", [])
    if not isinstance(inputs, list):
        problems.append("inputs 必须是数组")
    elif len(inputs) > 50:
        problems.append("inputs 最多 50 项")
    else:
        seen: set[str] = set()
        for index, item in enumerate(inputs):
            where = f"inputs[{index}]"
            if not isinstance(item, dict):
                problems.append(f"{where} 必须是对象")
                continue
            key = item.get("name")
            if not isinstance(key, str) or not INPUT_NAME_RE.match(key):
                problems.append(f"{where}.name 必须匹配 ^[A-Za-z_][A-Za-z0-9_]{{0,63}}$")
            elif key in seen:
                problems.append(f"{where}.name 重复：{key}")
            else:
                seen.add(key)

            label = item.get("label")
            if not isinstance(label, str) or not label.strip():
                problems.append(f"{where}.label 必须是非空字符串")

            field_type = item.get("type")
            if field_type not in INPUT_TYPES:
                problems.append(f"{where}.type 不受支持：{field_type!r}")

            options = item.get("options")
            if field_type in {"select", "radio", "multiselect"}:
                if not isinstance(options, list) or not options:
                    problems.append(f"{where} 为 {field_type} 时必须提供非空 options")
                elif len(options) > 100:
                    problems.append(f"{where}.options 最多 100 项")
                else:
                    values = [opt.get("value") for opt in options if isinstance(opt, dict)]
                    if len(values) != len(options):
                        problems.append(f"{where}.options 每项必须是对象")
                    elif len(set(values)) != len(values):
                        problems.append(f"{where}.options 的 value 必须唯一")

    return problems


def iter_package_files(plugin_dir: Path) -> list[Path]:
    files: list[Path] = []
    # 显式按 POSIX 相对路径排序：Path 之间的比较在 Windows 上会小写化，
    # 在 Linux 上区分大小写，同一批文件会得到不同顺序，进而产生不同字节的 zip。
    for path in sorted(
        plugin_dir.rglob("*"), key=lambda item: item.relative_to(plugin_dir).as_posix()
    ):
        if not path.is_file():
            continue
        if any(part in EXCLUDE_DIR_NAMES for part in path.relative_to(plugin_dir).parts[:-1]):
            continue
        if path.name in EXCLUDE_FILE_NAMES or path.suffix in EXCLUDE_FILE_SUFFIXES:
            continue
        files.append(path)
    return files


def py_literal(value: object, indent: int = 0) -> str:
    """把 JSON 风格的数据渲染成 Python 字面量源码。

    与 :func:`pprint.pformat` 的关键差异：字符串**永远输出成单行**，不会折行成
    ``'aaa' 'bbb'`` 这样的隐式拼接，从而保证任何静态解析实现都能读到完整值。
    """
    pad = "  " * indent
    inner = "  " * (indent + 1)

    if isinstance(value, dict):
        if not value:
            return "{}"
        lines = [
            f"{inner}{py_literal(key)}: {py_literal(item, indent + 1)}"
            for key, item in value.items()
        ]
        return "{\n" + ",\n".join(lines) + f",\n{pad}}}"

    if isinstance(value, list):
        if not value:
            return "[]"
        lines = [f"{inner}{py_literal(item, indent + 1)}" for item in value]
        return "[\n" + ",\n".join(lines) + f",\n{pad}]"

    if isinstance(value, str):
        # repr() 总是给出合法的 Python 字符串字面量，且 Python 3 不转义非 ASCII 字符
        return repr(value)

    if value is True:
        return "True"
    if value is False:
        return "False"
    if value is None:
        return "None"
    if isinstance(value, int):
        return repr(value)
    if isinstance(value, float):
        return repr(value)

    raise SystemExit(f"[错误] 清单中出现无法渲染为字面量的类型：{type(value).__name__}")


def render_single_file(manifest: dict, entry_path: Path) -> str:
    """把清单与入口合并为一个可导入的单文件插件。"""
    literal = py_literal(manifest)
    body = entry_path.read_text(encoding="utf-8")
    plugin_id = manifest.get("id", "")
    return (
        "# -*- coding: utf-8 -*-\n"
        f"# 由 scripts/package_plugin.py 依据 plugins/{plugin_id}/ 自动生成，请勿直接编辑。\n"
        f"# 单文件插件：顶层唯一的 PLUGIN_MANIFEST 常量字典 + 入口源码。\n"
        "\n"
        f"PLUGIN_MANIFEST = {literal}\n"
        "\n"
        "\n"
        f"{body.rstrip()}\n"
    )


def has_implicit_concat(source: str, start_line: int, end_line: int) -> bool:
    """检查指定行区间内是否存在相邻字符串字面量（``'a' 'b'`` 形式的隐式拼接）。"""
    reader = io.StringIO(source).readline
    previous_string = False
    try:
        for token in tokenize.generate_tokens(reader):
            if token.type in {tokenize.NL, tokenize.NEWLINE, tokenize.COMMENT,
                              tokenize.INDENT, tokenize.DEDENT}:
                continue
            if not (start_line <= token.start[0] and (token.end[0] or token.start[0]) <= end_line):
                previous_string = False
                continue
            if token.type == tokenize.STRING:
                if previous_string:
                    return True
                previous_string = True
            else:
                previous_string = False
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return False
    return False


def assert_manifest_is_literal(source: str) -> None:
    """确认生成的单文件里 PLUGIN_MANIFEST 是可直接静态读取的字面量赋值。"""
    tree = ast.parse(source)
    assignments = [
        index
        for index, node in enumerate(tree.body)
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "PLUGIN_MANIFEST" for t in node.targets)
    ]

    if len(assignments) != 1:
        raise SystemExit(
            f"[错误] 单文件必须且只能有一次顶层 PLUGIN_MANIFEST 赋值，实际 {len(assignments)} 次"
        )
    if assignments[0] != 0:
        raise SystemExit(
            f"[错误] PLUGIN_MANIFEST 必须是文件的第一条语句，实际位于第 {assignments[0] + 1} 条"
        )

    node = tree.body[assignments[0]]
    if not isinstance(node.value, ast.Dict):
        raise SystemExit("[错误] PLUGIN_MANIFEST 右侧必须是字典字面量")

    try:
        parsed = ast.literal_eval(node.value)
    except (ValueError, SyntaxError) as exc:
        raise SystemExit(f"[错误] PLUGIN_MANIFEST 必须是字面量：{exc}")

    if not isinstance(parsed, dict) or not parsed:
        raise SystemExit("[错误] PLUGIN_MANIFEST 解析结果必须是非空字典")

    # 相邻字符串字面量在 CPython 中会被合并成单个 ast.Constant，语法上合法，
    # 但可能被逐 token 读取的实现误判，这里显式禁止。
    if has_implicit_concat(source, node.lineno, node.end_lineno):
        raise SystemExit("[错误] PLUGIN_MANIFEST 中出现了隐式字符串拼接")

    # 反向校验：源码里不允许再以其它形式出现同名标识符（例如第二次赋值）
    if len(re.findall(r"^\s*PLUGIN_MANIFEST\s*=", source, flags=re.MULTILINE)) != 1:
        raise SystemExit("[错误] 源码中 PLUGIN_MANIFEST 赋值语句不唯一")


def build_zip(plugin_dir: Path, out_path: Path) -> int:
    files = iter_package_files(plugin_dir)
    if not files:
        raise SystemExit(f"[错误] {plugin_dir} 内没有可打包的文件")
    with zipfile.ZipFile(out_path, "w", ZIP_COMPRESS_TYPE) as archive:
        for path in files:
            rel = path.relative_to(plugin_dir).as_posix()
            info = zipfile.ZipInfo(rel, date_time=ZIP_DATE_TIME)
            info.compress_type = ZIP_COMPRESS_TYPE
            # create_system 默认随 sys.platform 变化（Windows=0 FAT / Linux=3 Unix），
            # 会写进 zip 中央目录并改变整体字节，这里固定为 Unix。
            info.create_system = 3
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())
    return len(files)


def package_one(plugin_dir: Path) -> dict:
    manifest = load_manifest(plugin_dir)

    problems = validate_manifest(plugin_dir, manifest)
    if problems:
        raise SystemExit(
            f"[错误] {plugin_dir.name} 清单校验未通过：\n  - " + "\n  - ".join(problems)
        )

    plugin_id = manifest["id"]
    version = manifest["version"]
    entry = manifest.get("entry", "plugin.py")

    DIST_DIR.mkdir(parents=True, exist_ok=True)

    single_path = DIST_DIR / f"{plugin_id}.py"
    source = render_single_file(manifest, plugin_dir / entry)
    assert_manifest_is_literal(source)
    single_path.write_text(source, encoding="utf-8", newline="\n")

    zip_path = DIST_DIR / f"{plugin_id}.zip"
    file_count = build_zip(plugin_dir, zip_path)

    return {
        "id": plugin_id,
        "version": version,
        "single": single_path,
        "zip": zip_path,
        "zip_file_count": file_count,
    }


def discover_plugins() -> list[Path]:
    if not PLUGINS_DIR.is_dir():
        raise SystemExit(f"[错误] 未找到插件目录：{PLUGINS_DIR}")
    found = sorted(p for p in PLUGINS_DIR.iterdir() if p.is_dir() and (p / "plugin.json").is_file())
    if not found:
        raise SystemExit(f"[错误] {PLUGINS_DIR} 下没有包含 plugin.json 的插件目录")
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="打包 TgtoDrive 插件并计算产物哈希")
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--plugin", help="要打包的插件 id（即 plugins/ 下的目录名）")
    target.add_argument("--all", action="store_true", help="打包 plugins/ 下的全部插件")
    args = parser.parse_args(argv)

    plugin_dirs = discover_plugins()
    if args.plugin:
        selected = [p for p in plugin_dirs if p.name == args.plugin]
        if not selected:
            available = ", ".join(p.name for p in plugin_dirs)
            raise SystemExit(f"[错误] 未找到插件 {args.plugin}，可用：{available}")
    else:
        selected = plugin_dirs

    summaries = []
    for plugin_dir in selected:
        result = package_one(plugin_dir)
        summaries.append(result)
        print(f"[完成] {result['id']} v{result['version']}")
        print(
            f"  单文件  {result['single'].relative_to(REPO_ROOT).as_posix()}"
            f"  {result['single'].stat().st_size} 字节"
            f"  sha256={sha256_of(result['single'])}"
        )
        print(
            f"  压缩包  {result['zip'].relative_to(REPO_ROOT).as_posix()}"
            f"  {result['zip'].stat().st_size} 字节"
            f"  {result['zip_file_count']} 个文件"
            f"  sha256={sha256_of(result['zip'])}"
        )

    print(f"\n共打包 {len(summaries)} 个插件，输出目录：{DIST_DIR.relative_to(REPO_ROOT).as_posix()}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())

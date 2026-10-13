#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一键发布：打包全部插件 → 刷新 plugins.json → 提交并推送到 GitHub。

一般通过仓库根目录的 ``publish.bat`` 调用，也可以直接运行::

    python scripts/publish_all.py                  # 自动生成提交说明后推送
    python scripts/publish_all.py -m "提交说明"     # 自定义提交说明
    python scripts/publish_all.py --no-push        # 只打包并提交，不推送
    python scripts/publish_all.py --dry-run        # 只打印将要执行的命令

流程
    1. 确认当前目录是 git 仓库
    2. ``package_plugin.py --all``  —— 打包全部插件到 ``dist/``
    3. ``build_marketplace.py``     —— 刷新 ``plugins.json``（sha256 / size / download_url）
    4. ``git add -A`` → ``git commit`` → ``git push``

说明
    * 打包是**确定性输出**，重复运行不会改变已发布插件的哈希，
      因此这里对全部插件打包不会影响其它插件的 Release。
    * 若工作区没有需要提交的改动，脚本会跳过提交与推送。
    * 推送完成后，插件市场仍需要对应的 **Release 附件**才能被安装；
      请在 GitHub 仓库的 Actions 页面手动触发 **Publish plugin**，
      为改过版本的插件各跑一次（``plugin_id`` 填插件 id）。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"


def banner(text):
    print("", flush=True)
    print("=" * 60, flush=True)
    print("  " + text, flush=True)
    print("=" * 60, flush=True)


def run_command(args, dry_run=False, capture=False, check=True):
    """执行命令。返回 CompletedProcess；capture=True 时捕获输出。"""
    display = " ".join(str(a) for a in args)
    print("> " + display, flush=True)
    if dry_run:
        return subprocess.CompletedProcess(args, 0, b"", b"")
    result = subprocess.run(
        [str(a) for a in args],
        cwd=str(ROOT),
        capture_output=capture,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if check and result.returncode != 0:
        if capture:
            print(result.stdout or "", flush=True)
            print(result.stderr or "", file=sys.stderr, flush=True)
        raise SystemExit("[错误] 命令执行失败（退出码 %d）：%s" % (result.returncode, display))
    return result


def git(args, **kwargs):
    return run_command(["git", *args], **kwargs)


def ensure_git_repo(dry_run=False):
    if dry_run:
        return
    result = subprocess.run(["git", "rev-parse", "--is-inside-work-tree"],
                            cwd=str(ROOT), capture_output=True, text=True)
    if result.returncode != 0 or result.stdout.strip() != "true":
        raise SystemExit("[错误] 当前目录不是 git 仓库：%s" % ROOT)


def build_commit_message():
    """依据 plugins.json 生成提交说明，列出本次涉及的插件与版本。"""
    catalog = ROOT / "plugins.json"
    lines = ["chore(release): 打包插件并刷新插件市场目录", ""]
    if catalog.is_file():
        try:
            data = json.loads(catalog.read_text(encoding="utf-8"))
            entries = data.get("plugins") or []
        except (OSError, ValueError):
            entries = []
        if entries:
            lines.append("插件：")
            for entry in entries:
                lines.append("  - %s v%s" % (entry.get("id", "?"), entry.get("version", "?")))
            lines.append("")
    lines.append("由 scripts/publish_all.py 自动生成：重新打包全部插件、")
    lines.append("刷新 plugins.json 的 sha256 / size / download_url 后提交。")
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description="打包全部插件并推送到 GitHub")
    parser.add_argument("-m", "--message", default="", help="提交说明（默认自动生成）")
    parser.add_argument("--branch", default="main", help="推送目标分支（默认 main）")
    parser.add_argument("--remote", default="origin", help="远端名（默认 origin）")
    parser.add_argument("--no-push", action="store_true", help="只打包并提交，不推送")
    parser.add_argument("--dry-run", action="store_true", help="只打印将要执行的命令")
    parser.add_argument("--skip-package", action="store_true",
                        help="跳过打包（只刷新 plugins.json 并提交）")
    args = parser.parse_args(argv)

    python = sys.executable
    dry = args.dry_run

    print("仓库目录：%s" % ROOT)
    print("使用 Python：%s" % python)

    ensure_git_repo(dry)

    banner("1/4  打包全部插件")
    if args.skip_package:
        print("（已跳过）", flush=True)
    else:
        run_command([python, SCRIPTS / "package_plugin.py", "--all"], dry_run=dry)

    banner("2/4  刷新插件市场目录 plugins.json")
    run_command([python, SCRIPTS / "build_marketplace.py",
                 "--repo", "a2695154202/ttd-plugins"], dry_run=dry)

    banner("3/4  提交改动")
    git(["add", "-A"], dry_run=dry)
    status = git(["diff", "--cached", "--quiet"], dry_run=dry, check=False)
    if not dry and status.returncode == 0:
        print("没有需要提交的改动，跳过提交与推送。", flush=True)
        banner("完成")
        return 0

    message = args.message or build_commit_message()
    print("提交说明：", flush=True)
    print(message, flush=True)
    if dry:
        print("> git commit -F <临时文件>", flush=True)
        print("> git push %s %s" % (args.remote, args.branch), flush=True)
        banner("dry-run 完成（未做任何改动）")
        return 0

    commit = subprocess.run(["git", "commit", "-F", "-"], cwd=str(ROOT),
                            input=message, capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    if commit.returncode != 0:
        print(commit.stdout or "", flush=True)
        print(commit.stderr or "", file=sys.stderr, flush=True)
        raise SystemExit("[错误] git commit 失败")
    print((commit.stdout or "").strip(), flush=True)

    if args.no_push:
        banner("完成（按 --no-push 跳过推送）")
        print("已提交到本地，未推送。需要时执行：git push %s %s"
              % (args.remote, args.branch), flush=True)
        return 0

    banner("4/4  推送到 %s/%s" % (args.remote, args.branch))
    push = git(["push", args.remote, args.branch], dry_run=dry, check=False)
    if not dry and push.returncode != 0:
        print("", flush=True)
        print("[提示] 推送失败。常见原因：", flush=True)
        print("  - 到 github.com 的网络不通（报 CONNECT tunnel failed / schannel）：检查代理后重试", flush=True)
        print("  - 远端有新提交：先执行 git pull --rebase 再重跑本脚本", flush=True)
        print("  - 需要登录：git 凭据失效时执行一次 git push 手动登录", flush=True)
        raise SystemExit("[错误] git push 失败（本地提交已完成，可直接重试推送）")

    banner("完成")
    print("代码与 plugins.json 已推送。", flush=True)
    print("", flush=True)
    print("别忘了：插件市场安装依赖 Release 附件。若本次有插件改了版本，", flush=True)
    print("请到 GitHub 的 Actions 页面触发 Publish plugin，plugin_id 填对应插件 id。", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

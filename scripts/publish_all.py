#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一键发布：打包全部插件 → 刷新 plugins.json → 提交推送 → 触发 Release 发布并校验。

一般通过仓库根目录的 ``publish.bat`` 调用，也可以直接运行::

    python scripts/publish_all.py                  # 打包 → 提交 → 推送 → 发布 → 校验
    python scripts/publish_all.py -m "提交说明"     # 自定义提交说明
    python scripts/publish_all.py --no-publish     # 只到推送为止，不触发 Release
    python scripts/publish_all.py --publish-only   # 只做发布与校验（补发上次漏掉的 Release）
    python scripts/publish_all.py --no-push        # 只打包并提交到本地
    python scripts/publish_all.py --dry-run        # 只打印将要执行的命令

流程
    1. ``package_plugin.py --all``  —— 打包全部插件到 ``dist/``
    2. ``build_marketplace.py``     —— 刷新 ``plugins.json``（sha256 / size / download_url）
    3. ``git add -A`` → ``git commit``
    4. ``git push``
    5. ``gh_publish.py``            —— 触发 Publish plugin 工作流并逐字节复核附件

关于第 5 步为什么必须有
    插件市场是拿 ``plugins.json`` 里的 ``download_url`` 去 Release 下载附件的。
    只推送代码**不会**创建 Release：

    * Release 不存在 → 市场报「GitHub 下载失败（HTTP 404）」
    * 附件与目录声明的 sha256 / size 不符 → 市场报
      「GitHub 文件超过允许大小或长度无效」

    所以推送之后必须再触发一次 ``Publish plugin`` 工作流。本脚本自动完成，
    并在工作流结束后重新下载附件逐字节复核；校验不通过会以非零退出码结束。

说明
    * 打包是**确定性输出**（zip 用 STORED、固定时间戳、POSIX 顺序排序），
      重复运行不会改变已发布插件的哈希，也不会让工作流产生多余提交。
    * 若工作区没有需要提交的改动，脚本会跳过提交与推送，但仍会继续做
      发布与校验 —— 这样"上次推了代码忘了发布"可以再跑一次本脚本补上。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"
MARKET_REPO = "a2695154202/ttd-plugins"


def _force_utf8():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8", errors="replace")
            except (ValueError, OSError):
                pass


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


def do_commit(dry, message):
    """提交已暂存的改动；返回 True 表示确实提交了。"""
    git(["add", "-A"], dry_run=dry)
    staged = git(["diff", "--cached", "--quiet"], dry_run=dry, check=False)
    if not dry and staged.returncode == 0:
        print("没有需要提交的改动。", flush=True)
        return False

    print("提交说明：", flush=True)
    print(message, flush=True)
    if dry:
        print("> git commit -F <临时文件>", flush=True)
        return True

    commit = subprocess.run(["git", "commit", "-F", "-"], cwd=str(ROOT),
                            input=message, capture_output=True, text=True,
                            encoding="utf-8", errors="replace")
    if commit.returncode != 0:
        print(commit.stdout or "", flush=True)
        print(commit.stderr or "", file=sys.stderr, flush=True)
        raise SystemExit("[错误] git commit 失败")
    print((commit.stdout or "").strip(), flush=True)
    return True


def do_push(args, dry):
    push = git(["push", args.remote, args.branch], dry_run=dry, check=False)
    if not dry and push.returncode != 0:
        print("", flush=True)
        print("[提示] 推送失败。常见原因：", flush=True)
        print("  - 到 github.com 的网络不通（CONNECT tunnel failed / schannel）：检查代理后重试", flush=True)
        print("  - 远端有新提交：先 git pull --rebase 再重跑本脚本", flush=True)
        print("  - 需要登录：git 凭据失效时手动执行一次 git push 登录", flush=True)
        raise SystemExit("[错误] git push 失败（本地提交已完成，可直接重试推送）")


def main(argv=None):
    _force_utf8()
    parser = argparse.ArgumentParser(description="打包全部插件、推送并发布 Release")
    parser.add_argument("-m", "--message", default="", help="提交说明（默认自动生成）")
    parser.add_argument("--branch", default="main", help="推送目标分支（默认 main）")
    parser.add_argument("--remote", default="origin", help="远端名（默认 origin）")
    parser.add_argument("--repo", default=MARKET_REPO,
                        help="插件市场仓库 owner/name（默认 %s）" % MARKET_REPO)
    parser.add_argument("--no-push", action="store_true",
                        help="只打包并提交到本地（推送与发布都会跳过）")
    parser.add_argument("--no-publish", action="store_true",
                        help="推送后不触发 Release 发布")
    parser.add_argument("--publish-only", action="store_true",
                        help="跳过打包与提交，只触发发布并校验")
    parser.add_argument("--dry-run", action="store_true", help="只打印将要执行的命令")
    parser.add_argument("--skip-package", action="store_true",
                        help="跳过打包（只刷新 plugins.json 并提交）")
    args = parser.parse_args(argv)

    python = sys.executable
    dry = args.dry_run

    print("仓库目录：%s" % ROOT)
    print("使用 Python：%s" % python)
    print("市场仓库：%s" % args.repo)

    ensure_git_repo(dry)

    pushed = False
    if args.publish_only:
        banner("0/5  按 --publish-only 跳过打包、提交与推送")
    else:
        banner("1/5  打包全部插件")
        if args.skip_package:
            print("（已跳过）", flush=True)
        else:
            run_command([python, SCRIPTS / "package_plugin.py", "--all"], dry_run=dry)

        banner("2/5  刷新插件市场目录 plugins.json")
        run_command([python, SCRIPTS / "build_marketplace.py", "--repo", args.repo], dry_run=dry)

        banner("3/5  提交改动")
        do_commit(dry, args.message or build_commit_message())

        if args.no_push:
            banner("4/5  按 --no-push 跳过推送")
            print("已提交到本地。需要时执行：git push %s %s" % (args.remote, args.branch),
                  flush=True)
        else:
            banner("4/5  推送到 %s/%s" % (args.remote, args.branch))
            do_push(args, dry)
            pushed = True

    # -- 发布与校验 ------------------------------------------------------
    if args.no_publish:
        banner("5/5  按 --no-publish 跳过 Release 发布")
        print("提示：只有推送而没有发布时，插件市场会报", flush=True)
        print("      「GitHub 下载失败（HTTP 404）」或「文件超过允许大小或长度无效」。", flush=True)
        print("      需要时执行：python scripts/gh_publish.py", flush=True)
        return 0

    if args.no_push and not args.publish_only:
        banner("5/5  跳过 Release 发布")
        print("未推送时发布没有意义（发布的是远端代码）。推送后再跑一次本脚本即可。", flush=True)
        return 0

    if dry:
        banner("5/5  发布 Release 并校验（dry-run 跳过）")
        print("> python scripts/gh_publish.py --repo %s --require-sync" % args.repo, flush=True)
        banner("dry-run 完成（未做任何改动）")
        return 0

    banner("5/5  发布 Release 并校验")
    if not pushed:
        print("本次没有新的提交需要推送，仍会校验并补发缺失的 Release。", flush=True)

    result = run_command(
        [python, SCRIPTS / "gh_publish.py",
         "--repo", args.repo, "--branch", args.branch, "--require-sync"],
        dry_run=False, check=False,
    )
    if result.returncode != 0:
        print("", flush=True)
        print("[错误] 发布或校验未通过（gh_publish.py 退出码 %d）。" % result.returncode, flush=True)
        print("       代码已推送成功，可修好问题后单独重试：", flush=True)
        print("       python scripts/gh_publish.py", flush=True)
        return result.returncode

    banner("完成")
    print("代码、plugins.json 与 Release 附件现已全部一致。", flush=True)
    print("在 TgtoDrive「插件市场 → 来源设置」刷新目录即可看到新版本。", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

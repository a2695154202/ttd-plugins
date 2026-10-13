#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""触发 Publish plugin 工作流，并逐字节校验 Release 附件与 ``plugins.json`` 是否一致。

为什么需要这个脚本
------------------
插件市场安装插件时，是拿 ``plugins.json`` 里声明的 ``download_url`` 去下载对应
Release 附件的。目录里声明的 ``sha256`` / ``size`` 必须与附件**逐字节一致**，
否则市场会拒绝安装，而且报错信息并不直观：

* tag 对应的 Release 还不存在
  → 「GitHub 下载失败（HTTP 404）；Release API 回退失败：GitHub 下载失败（HTTP 404）」
* Release 存在，但附件与目录声明的大小/摘要不符（例如只改了源码没重新发布）
  → 「GitHub 文件超过允许大小或长度无效」

而 ``publish_all.py`` 只负责把源码与 ``plugins.json`` 推到仓库 ——
**推送本身不会创建 Release**，必须再触发一次 ``Publish plugin`` 工作流。
本脚本把这一步自动化，并在工作流结束后重新下载附件逐字节复核，
避免"推了代码忘了发布"这种问题。

用法::

    python scripts/gh_publish.py                     # 校验全部插件，按需发布
    python scripts/gh_publish.py --verify-only       # 只校验，不触发发布
    python scripts/gh_publish.py --plugin wecom-notify
    python scripts/gh_publish.py --no-wait           # 触发后不等待工作流

退出码
    0  全部插件的 Release 附件都与目录声明一致
    1  有插件需要发布、但发布失败或发布后仍不一致
    2  无法访问 GitHub / 找不到可用凭据 / 其它致命错误
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = "publish-plugin.yml"
API = "https://api.github.com"
DEFAULT_REPO = "a2695154202/ttd-plugins"


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


def resolve_repo(root=ROOT):
    """从 origin 远端地址解析 ``owner/name``，失败时回退到默认仓库。"""
    try:
        proc = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=str(root), capture_output=True, text=True,
            encoding="utf-8", errors="replace",
        )
        url = (proc.stdout or "").strip()
    except OSError:
        url = ""
    match = re.search(r"github\.com[:/]+([^/]+)/([^/]+?)(?:\.git)?/?$", url)
    if match:
        return "%s/%s" % (match.group(1), match.group(2))
    return DEFAULT_REPO


def resolve_token(root=ROOT):
    """取 GitHub 凭据：环境变量优先，其次复用 git 已保存的凭据。"""
    for name in ("GH_TOKEN", "GITHUB_TOKEN"):
        value = (os.environ.get(name) or "").strip()
        if value:
            return value, "环境变量 " + name
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            cwd=str(root),
            input="protocol=https\nhost=github.com\n\n",
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired):
        return "", ""
    for line in (proc.stdout or "").splitlines():
        if line.startswith("password="):
            value = line[len("password="):].strip()
            if value:
                return value, "git 已保存的 github.com 凭据"
    return "", ""


class GitHubError(RuntimeError):
    """与 GitHub 交互时的致命错误。"""


class GitHub:
    def __init__(self, repo, token, timeout=60):
        self.repo = repo
        self.token = token
        self.timeout = timeout

    def request(self, path, method="GET", payload=None, accept=None, raw=False):
        url = path if path.startswith("http") else API + path
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = urllib.request.Request(
            url, data=data, method=method,
            headers={
                "Authorization": "Bearer " + self.token,
                "User-Agent": "ttd-plugins-publish-tool",
                "Accept": accept or "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read()
                if raw:
                    return response.status, body
                return response.status, json.loads(body.decode("utf-8") or "null")
        except urllib.error.HTTPError as exc:
            return exc.code, exc.read().decode("utf-8", "replace")[:300]
        except urllib.error.URLError as exc:
            raise GitHubError("无法访问 GitHub（%s）：%s" % (url, exc.reason))
        except TimeoutError:
            raise GitHubError("访问 GitHub 超时：%s" % url)

    # -- Release ---------------------------------------------------------

    def get_release(self, tag):
        status, data = self.request("/repos/%s/releases/tags/%s" % (self.repo, tag))
        if status == 200:
            return data
        if status == 404:
            return None
        raise GitHubError("读取 Release %s 失败：HTTP %s %s" % (tag, status, data))

    def download_asset(self, asset_id):
        status, blob = self.request(
            "/repos/%s/releases/assets/%s" % (self.repo, asset_id),
            accept="application/octet-stream", raw=True,
        )
        if status != 200 or not isinstance(blob, bytes):
            raise GitHubError("下载附件失败：HTTP %s" % status)
        return blob

    # -- Actions ---------------------------------------------------------

    def dispatch(self, workflow, ref, inputs):
        status, data = self.request(
            "/repos/%s/actions/workflows/%s/dispatches" % (self.repo, workflow),
            method="POST", payload={"ref": ref, "inputs": inputs},
        )
        if status not in (201, 204):
            raise GitHubError("触发工作流失败：HTTP %s %s" % (status, data))

    def workflow_runs(self, workflow, per_page=10):
        status, data = self.request(
            "/repos/%s/actions/workflows/%s/runs?per_page=%d"
            % (self.repo, workflow, per_page)
        )
        if status != 200:
            raise GitHubError("读取工作流运行记录失败：HTTP %s %s" % (status, data))
        return data.get("workflow_runs", []) or []

    def run_jobs(self, run_id):
        status, data = self.request("/repos/%s/actions/runs/%s/jobs" % (self.repo, run_id))
        return (data.get("jobs", []) if status == 200 else []) or []

    def branch_sha(self, branch="main"):
        status, data = self.request("/repos/%s/git/ref/heads/%s" % (self.repo, branch))
        if status != 200:
            return ""
        return (data.get("object") or {}).get("sha", "")


# ---------------------------------------------------------------------------
# 目录条目 → Release
# ---------------------------------------------------------------------------

def tag_from_entry(entry):
    match = re.search(r"/releases/download/([^/]+)/", entry.get("download_url", "") or "")
    return match.group(1) if match else ""


def asset_name_from_entry(entry):
    return (entry.get("download_url", "") or "").rstrip("/").split("/")[-1]


def verify_entry(github, entry):
    """校验单个插件的 Release 附件是否与目录声明一致。返回 (ok, message)。"""
    tag = tag_from_entry(entry)
    if not tag:
        return False, "download_url 不是 .../releases/download/<tag>/<文件名> 结构"

    release = github.get_release(tag)
    if release is None:
        return False, "Release %s 不存在 —— 需要发布（否则市场报 HTTP 404）" % tag

    name = asset_name_from_entry(entry)
    asset = next((a for a in release.get("assets", []) if a.get("name") == name), None)
    if asset is None:
        return False, "Release %s 中没有附件 %s —— 需要发布" % (tag, name)

    blob = github.download_asset(asset["id"])
    digest = hashlib.sha256(blob).hexdigest()
    declared_size = entry.get("size")
    declared_hash = str(entry.get("sha256") or "")

    if declared_size is not None and len(blob) != declared_size:
        return False, ("附件大小不符：实际 %d B，目录声明 %s B —— 需要重新发布"
                       % (len(blob), declared_size))
    if declared_hash and digest != declared_hash:
        return False, ("附件 sha256 不符：实际 %s…，目录声明 %s… —— 需要重新发布"
                       % (digest[:16], declared_hash[:16]))
    return True, "%s 与目录声明一致（%d B / %s…）" % (name, len(blob), digest[:16])


def publish_plugin(github, plugin_id, branch="main", wait=True, limit=420):
    """触发 Publish plugin 工作流；wait=True 时等待并返回结论。"""
    known = {run["id"] for run in github.workflow_runs(WORKFLOW, per_page=10)}
    github.dispatch(WORKFLOW, branch, {"plugin_id": plugin_id, "prerelease": False})
    print("    已触发 Publish plugin（plugin_id=%s）" % plugin_id, flush=True)
    if not wait:
        return {"plugin": plugin_id, "conclusion": "triggered"}

    target = None
    deadline = time.time() + limit
    while time.time() < deadline:
        try:
            for run in github.workflow_runs(WORKFLOW, per_page=10):
                if run["id"] not in known:
                    target = run
                    break
        except GitHubError:
            pass
        if target and target.get("status") == "completed":
            break
        time.sleep(8)

    if target is None:
        return {"plugin": plugin_id, "conclusion": "unknown",
                "note": "未取到本次运行记录（可能仍在排队）"}

    info = {"plugin": plugin_id, "conclusion": target.get("conclusion"),
            "url": target.get("html_url", "")}
    if target.get("conclusion") != "success":
        try:
            jobs = github.run_jobs(target["id"])
            info["failed_steps"] = [
                (step.get("name"), step.get("conclusion"))
                for job in jobs
                for step in (job.get("steps") or [])
                if step.get("conclusion") not in ("success", "skipped", None)
            ]
        except GitHubError:
            pass
    return info


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def load_entries(only=None):
    catalog = ROOT / "plugins.json"
    if not catalog.is_file():
        raise SystemExit("[错误] 找不到 %s" % catalog)
    document = json.loads(catalog.read_text(encoding="utf-8"))
    entries = document.get("plugins") or []
    if only:
        wanted = set(only)
        entries = [e for e in entries if e.get("id") in wanted]
        missing = wanted - {e.get("id") for e in entries}
        if missing:
            raise SystemExit("[错误] plugins.json 中没有这些插件：%s" % ", ".join(sorted(missing)))
    if not entries:
        raise SystemExit("[错误] plugins.json 里没有可处理的插件")
    return entries


def main(argv=None):
    _force_utf8()
    parser = argparse.ArgumentParser(
        description="触发 Publish plugin 工作流并校验 Release 附件与 plugins.json 一致")
    parser.add_argument("--repo", default="", help="owner/name（默认从 origin 解析）")
    parser.add_argument("--branch", default="main", help="分支（默认 main）")
    parser.add_argument("--plugin", action="append", default=[],
                        help="只处理指定插件 id，可重复")
    parser.add_argument("--verify-only", action="store_true", help="只校验，不触发发布")
    parser.add_argument("--no-wait", action="store_true", help="触发后不等待工作流结束")
    parser.add_argument("--require-sync", action="store_true",
                        help="本地 HEAD 必须与远端分支一致，否则中止（避免发布旧代码）")
    parser.add_argument("--quiet", action="store_true", help="精简输出")
    args = parser.parse_args(argv)

    entries = load_entries(args.plugin)

    repo = args.repo or resolve_repo()
    token, source = resolve_token()
    if not token:
        print("[错误] 找不到 GitHub 凭据。", file=sys.stderr, flush=True)
        print("       可设置环境变量 GH_TOKEN，或先用 git 登录一次 github.com。",
              file=sys.stderr, flush=True)
        return 2

    if not args.quiet:
        print("仓库：%s" % repo, flush=True)
        print("凭据：%s" % source, flush=True)

    github = GitHub(repo, token)

    if args.require_sync:
        remote_sha = github.branch_sha(args.branch)
        local_sha = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=str(ROOT),
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        ).stdout.strip()
        if remote_sha and local_sha and remote_sha != local_sha:
            print("", flush=True)
            print("[错误] 远端 %s 是 %s，本地 HEAD 是 %s —— 两者不一致。"
                  % (args.branch, remote_sha[:7], local_sha[:7]), flush=True)
            print("       请先 git pull --ff-only（或推送本地提交）后再发布，"
                  "否则发布会指向旧代码。", flush=True)
            return 2

    banner("1/2  校验 Release 附件与 plugins.json")

    pending = []
    for entry in entries:
        plugin_id = entry.get("id", "?")
        try:
            ok, message = verify_entry(github, entry)
        except GitHubError as exc:
            ok, message = False, "校验失败：%s" % exc
        print("  %-18s v%-8s %s %s"
              % (plugin_id, entry.get("version", "?"), "OK  " if ok else "待发布", message),
              flush=True)
        if not ok:
            pending.append(plugin_id)

    if not pending:
        print("", flush=True)
        print("全部插件的 Release 附件都与目录声明一致，无需发布。", flush=True)
        return 0

    if args.verify_only:
        print("", flush=True)
        print("以上 %d 个插件需要发布，但按 --verify-only 未触发。" % len(pending), flush=True)
        return 1

    banner("2/2  发布并复核")

    results = []
    for plugin_id in pending:
        print("  → %s" % plugin_id, flush=True)
        try:
            info = publish_plugin(github, plugin_id, args.branch, wait=not args.no_wait)
        except GitHubError as exc:
            print("    触发失败：%s" % exc, flush=True)
            results.append((plugin_id, False, str(exc)))
            continue
        conclusion = info.get("conclusion")
        print("    工作流结论：%s %s" % (conclusion, info.get("url", "")), flush=True)
        for step, state in info.get("failed_steps", []):
            print("      失败步骤：%s（%s）" % (step, state), flush=True)
        if info.get("note"):
            print("    备注：%s" % info["note"], flush=True)

        if args.no_wait:
            results.append((plugin_id, True, "已触发（未等待）"))
            continue

        entry = next(e for e in entries if e.get("id") == plugin_id)
        try:
            ok, message = verify_entry(github, entry)
        except GitHubError as exc:
            ok, message = False, "复核失败：%s" % exc
        print("    复核：%s %s" % ("通过" if ok else "未通过", message), flush=True)
        results.append((plugin_id, ok, message))

    failed = [r for r in results if not r[1]]
    banner("结果")
    for plugin_id, ok, message in results:
        print("  %-18s %s  %s" % (plugin_id, "OK  " if ok else "失败", message), flush=True)

    if failed:
        print("", flush=True)
        print("有 %d 个插件未能完成发布，请到 Actions 页面查看日志。" % len(failed), flush=True)
        return 1
    print("", flush=True)
    print("全部发布完成，市场刷新目录后即可正常安装/更新。", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())

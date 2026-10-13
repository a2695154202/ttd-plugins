"""TgtoDrive Python 插件：只使用 Python 标准库。"""
import json
from pathlib import Path


def run(params, context):
    lines = params["text"].splitlines()
    if params.get("strip", True):
        lines = [line.strip() for line in lines]
    original_count = len(lines)
    if params.get("action", "unique") == "unique":
        lines = list(dict.fromkeys(lines))
    else:
        lines = sorted(lines)

    # 写到 data_dir 的数据会在更新插件后保留；卸载时删除。
    stats_file = Path(context["data_dir"]) / "stats.json"
    try:
        count = int(json.loads(stats_file.read_text(encoding="utf-8"))["runs"])
    except (OSError, ValueError, KeyError, TypeError):
        count = 0
    stats_file.write_text(json.dumps({"runs": count + 1}), encoding="utf-8")
    print(f"已处理 {original_count} 行，输出 {len(lines)} 行")
    return {
        "output": "\n".join(lines),
        "input_lines": original_count,
        "output_lines": len(lines),
        "runs": count + 1,
    }

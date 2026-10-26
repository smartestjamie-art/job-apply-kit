"""To-dos with deadlines, kept in the 「待办 / To-do」 section at the top of data/progress.md
(the log below it only ever gets lines appended, so read to-dos with this script, not with tail).

  python scripts/todo.py list                          # 未完成的待办
  python scripts/todo.py add "10-31 前完成 Acme 在线测评"   # 已有同样的待办就跳过
  python scripts/todo.py done "Acme"                   # 把包含这段文字的那一条标为完成
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import PROGRESS  # noqa: E402

HEADER = "## 待办 / To-do"
EXAMPLE = "（例）"


def section(lines):
    """(start, end) line indexes of the to-do items; start is the header line, or None."""
    start = next((i for i, l in enumerate(lines) if l.startswith("## 待办")), None)
    if start is None:
        return None, None
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return start, end


def items(lines, start, end, state):
    return [i for i in range(start + 1, end) if lines[i].startswith(f"- [{state}] ") and EXAMPLE not in lines[i]]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    sub.add_parser("add").add_argument("text")
    sub.add_parser("done").add_argument("text")
    a = ap.parse_args()
    if not PROGRESS.exists():
        sys.exit(f"找不到 / not found: {PROGRESS}\n运行 / run: python scripts/setup_workspace.py")
    lines = PROGRESS.read_text(encoding="utf-8").splitlines()
    start, end = section(lines)

    if a.cmd == "list":
        open_ = items(lines, start, end, " ") if start is not None else []
        print("\n".join(lines[i] for i in open_) or "（没有未完成的待办 / no open to-dos）")
        return

    text = " ".join(a.text.split())
    if a.cmd == "add":
        if start is None:
            log = next((i for i, l in enumerate(lines) if l.startswith("## ")), len(lines))
            lines[log:log] = [HEADER, "", ""] if log < len(lines) else ["", HEADER]
            start, end = section(lines)
        if any(lines[i][6:].strip() == text for i in range(start + 1, end) if lines[i].startswith("- [")):
            print(f"= 已有这条待办，跳过 / already there: {text}")
            return
        last = max([i for i in range(start + 1, end) if lines[i].startswith("- [")] or [start])
        lines.insert(last + 1, f"- [ ] {text}")
        print(f"✓ 已加待办 / added: {text}")
    else:
        hits = [i for i in items(lines, start, end, " ") if text in lines[i]] if start is not None else []
        if len(hits) != 1:
            print("\n".join(lines[i] for i in hits) or f"没有找到 / not found: {text}")
            sys.exit("对上的不是正好一条，请写得更具体 / be more specific" if hits else 1)
        lines[hits[0]] = lines[hits[0]].replace("- [ ] ", "- [x] ", 1)
        print(f"✓ 已完成 / done: {lines[hits[0]][6:]}")
    PROGRESS.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

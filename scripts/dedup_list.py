"""Print the de-duplication list for a search run: everything already applied to,
deliberately skipped, blacklisted, or statically excluded. Scheduled runs read this
first and pass it to every sub-agent.

  python scripts/dedup_list.py            # markdown
  python scripts/dedup_list.py --json
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import PROGRESS, SEARCH, TRACKER, data_rows, load_search, open_tracker  # noqa: E402

SKIP_WORDS = re.compile(r"(跳过|不投|决定不|skip(ped)?|not applying|declined to apply)", re.I)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    applied, skipped, black, static = [], [], [], []
    if TRACKER.exists():
        _, ws = open_tracker()
        for _, d in data_rows(ws):
            applied.append(f"{d['Company']} — {d['Job Title']} (#{d['#']}, {d['Status']})")
    if PROGRESS.exists():
        for line in PROGRESS.read_text(encoding="utf-8").splitlines():
            if SKIP_WORDS.search(line):
                skipped.append(line.lstrip("- ").strip())
    if SEARCH.exists():
        f = load_search().get("filters") or {}
        black = [f"{b.get('name')} ({b.get('reason', '')})" if isinstance(b, dict) else str(b)
                 for b in f.get("blacklist_companies") or []]
        static = [str(x) for x in f.get("static_excludes") or []]
    if a.json:
        print(json.dumps({"applied": applied, "skipped": skipped, "blacklist": black, "static": static},
                         ensure_ascii=False, indent=2))
        return
    for title, items in (("已投（不再推荐，除非状态变化）", applied), ("已决定跳过", skipped),
                         ("黑名单（直接跳过）", black), ("额外排除", static)):
        print(f"## {title} ({len(items)})")
        print("\n".join(f"- {x}" for x in items) or "- （无）")
        print()


if __name__ == "__main__":
    main()

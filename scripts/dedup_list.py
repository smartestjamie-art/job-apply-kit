"""Print the de-duplication list for a search run: everything already applied to,
already reported, deliberately skipped, blacklisted, or statically excluded. Scheduled
runs read this first and pass it to every sub-agent.

  python scripts/dedup_list.py            # markdown
  python scripts/dedup_list.py --json
"""
import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (CANDIDATES, PROFILE, PROGRESS, SEARCH, TRACKER, data_rows, load_profile,  # noqa: E402
                     load_search, open_tracker, read_json)

SKIP_WORDS = re.compile(r"(跳过|不投|决定不|skip(ped)?|not applying|declined to apply)", re.I)
REPORTED_DAYS = 45


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    applied, reported, skipped, black, static = [], [], [], [], []
    if TRACKER.exists():
        _, ws = open_tracker()
        for _, d in data_rows(ws):
            applied.append(f"{d['Company']} — {d['Job Title']} (#{d['#']}, {d['Status']})")
    since = (date.today() - timedelta(days=REPORTED_DAYS)).isoformat()
    for v in read_json(CANDIDATES, {"jobs": {}})["jobs"].values():
        if v.get("status") == "skipped":
            skipped.append(f"{v['company']} — {v['title']} ({v.get('skip_reason') or '用户决定不投'})")
        elif v.get("last_seen", "") >= since:
            reported.append(f"{v['company']} — {v['title']} (首次汇报 {v.get('first_reported', '')})")
    if PROGRESS.exists():
        for line in PROGRESS.read_text(encoding="utf-8").splitlines():
            if SKIP_WORDS.search(line):
                skipped.append(line.lstrip("- ").strip())
    if SEARCH.exists():
        f = load_search().get("filters") or {}
        black = [f"{b.get('name')} ({b.get('reason', '')})" if isinstance(b, dict) else str(b)
                 for b in f.get("blacklist_companies") or []]
        static = [str(x) for x in f.get("static_excludes") or []]
    if PROFILE.exists():
        black += [f"{c} (profile.exclude_companies)"
                  for c in (load_profile().get("job_search") or {}).get("exclude_companies") or []]
    if a.json:
        print(json.dumps({"applied": applied, "reported": reported, "skipped": skipped, "blacklist": black,
                          "static": static}, ensure_ascii=False, indent=2))
        return
    for title, items in (("已投（不再推荐，除非状态变化）", applied), (f"已汇报过（近 {REPORTED_DAYS} 天，不再当作新增）", reported),
                         ("已决定跳过", skipped), ("黑名单（直接跳过）", black), ("额外排除", static)):
        print(f"## {title} ({len(items)})")
        print("\n".join(f"- {x}" for x in items) or "- （无）")
        print()


if __name__ == "__main__":
    main()

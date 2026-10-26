"""State file for the graduate-scheme watch: data/state/scheme_watch.json

  python scripts/scheme_state.py list
  python scripts/scheme_state.py update "Company — Scheme" --status open --opens 2026-10-01 \
        --closes 2026-11-30 --url https://...
  python scripts/scheme_state.py due --days 14      # open schemes closing within N days

`update` prints CHANGED / NEW / same, so the run can report only changes.
Status values: open | closed | opens-soon | unknown
  - --status unknown (official page unreachable) keeps the last known status and prints
    `unknown`, never CHANGED, so one bad day does not show up as "newly opened" the next.
  - an empty --closes keeps the last known closing date and is not a change.
"""
import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import STATE, read_json, today, write_json  # noqa: E402

FILE = STATE / "scheme_watch.json"
STATUSES = {"open", "closed", "opens-soon", "unknown"}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    u = sub.add_parser("update")
    u.add_argument("name")
    u.add_argument("--status", required=True, choices=sorted(STATUSES))
    for k in ("opens", "closes", "url", "note"):
        u.add_argument("--" + k, default="")
    d = sub.add_parser("due")
    d.add_argument("--days", type=int, default=14)
    a = ap.parse_args()
    db = read_json(FILE, {"schemes": {}})
    s = db["schemes"]

    if a.cmd == "list":
        for name, v in sorted(s.items()):
            print(f"{v['status']:<10} {name} | opens {v.get('opens', '')} | closes {v.get('closes', '')} | "
                  f"checked {v.get('last_checked', '')} | {v.get('url', '')}")
        print(f"({len(s)} schemes)")
    elif a.cmd == "update":
        old = s.get(a.name)
        if a.status == "unknown":
            if old:
                old["last_unreachable"] = today()
            else:
                s[a.name] = {"status": "unknown", "last_checked": today()}
            write_json(FILE, db)
            kept = f"保留上次状态 / kept: {old.get('status')}" if old else "还没有记录 / no record yet"
            print(f"unknown  {a.name}: 未能核实，{kept}")
            return
        new = {"status": a.status, "opens": a.opens, "closes": a.closes, "url": a.url, "note": a.note,
               "last_checked": today()}
        old_close = (old or {}).get("closes", "")
        closes_changed = bool(a.closes) and a.closes != old_close
        if old is None:
            print(f"NEW      {a.name}: {a.status}")
        elif old.get("status") != a.status or closes_changed:
            extra = f" (closes {old_close or '?'} → {a.closes})" if closes_changed else ""
            print(f"CHANGED  {a.name}: {old.get('status')} → {a.status}{extra}")
        else:
            print(f"same     {a.name}")
        s[a.name] = {**(old or {}), **{k: v for k, v in new.items() if v or k == "status"}}
        write_json(FILE, db)
    elif a.cmd == "due":
        limit = date.today() + timedelta(days=a.days)
        for name, v in s.items():
            try:
                c = date.fromisoformat(v.get("closes", "")[:10])
            except ValueError:
                continue
            if v.get("status") == "open" and date.today() <= c <= limit:
                print(f"{c}  {name}  {v.get('url', '')}")


if __name__ == "__main__":
    main()

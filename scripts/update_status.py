"""Update status / flow / notes of an existing application.

  python scripts/update_status.py 12 --status "Interview 面试中" --flow "HR 面 11-10"
  python scripts/update_status.py 12 --status "Rejected 被拒" --note "rejected after OT"

--flow is appended with an arrow (→) to the existing flow; --note is appended to Notes.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import COL, STATUSES, TRACKER, append_progress, data_rows, open_tracker  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("number", type=int)
    ap.add_argument("--status")
    ap.add_argument("--flow")
    ap.add_argument("--note")
    a = ap.parse_args()
    if a.status and a.status not in STATUSES:
        match = [s for s in STATUSES if s.lower().startswith(a.status.lower())]
        if len(match) != 1:
            sys.exit(f"状态请用 / status must be one of: {STATUSES}")
        a.status = match[0]
    wb, ws = open_tracker()
    for r, d in data_rows(ws):
        if str(d["#"]) == str(a.number):
            if a.status:
                ws.cell(r, COL["Status"]).value = a.status
            if a.flow:
                old = d["Flow"] or ""
                ws.cell(r, COL["Flow"]).value = f"{old}→{a.flow}" if old else a.flow
            if a.note:
                old = d["Notes"] or ""
                ws.cell(r, COL["Notes"]).value = f"{old} | {a.note}" if old else a.note
            wb.save(TRACKER)
            append_progress(f"#{a.number} {d['Company']} — {d['Job Title']}: "
                            f"{a.status or d['Status']}{(' · ' + a.flow) if a.flow else ''}{(' · ' + a.note) if a.note else ''}")
            print(f"✓ #{a.number} 已更新 / updated")
            return
    sys.exit(f"找不到 #{a.number} / not found")


if __name__ == "__main__":
    main()

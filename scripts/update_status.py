"""Update status / flow / notes of an existing application.

  python scripts/update_status.py 12 --status "Interview 面试中" --flow "HR 面 11-10"
  python scripts/update_status.py 12 --status "Rejected 被拒" --note "rejected after OT"

--flow is appended with an arrow (→) to the existing flow; --note is appended to Notes.
Running the same update twice (e.g. the same email seen by two overlapping email checks)
changes nothing the second time and writes no progress line.
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
            status = a.status if a.status and a.status != d["Status"] else None
            flow = a.flow if a.flow and a.flow not in str(d["Flow"] or "").split("→") else None
            note = a.note if a.note and a.note not in str(d["Notes"] or "").split(" | ") else None
            if not (status or flow or note):
                print(f"= #{a.number} 已是最新，未改动 / already recorded, nothing changed")
                return
            if status:
                ws.cell(r, COL["Status"]).value = status
            if flow:
                old = d["Flow"] or ""
                ws.cell(r, COL["Flow"]).value = f"{old}→{flow}" if old else flow
            if note:
                old = d["Notes"] or ""
                ws.cell(r, COL["Notes"]).value = f"{old} | {note}" if old else note
            wb.save(TRACKER)
            append_progress(f"#{a.number} {d['Company']} — {d['Job Title']}: "
                            f"{status or d['Status']}{(' · ' + flow) if flow else ''}{(' · ' + note) if note else ''}")
            print(f"✓ #{a.number} 已更新 / updated")
            return
    sys.exit(f"找不到 #{a.number} / not found")


if __name__ == "__main__":
    main()

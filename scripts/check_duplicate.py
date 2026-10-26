"""Check whether a company/role is already in the tracker.

  python scripts/check_duplicate.py "Company" ["Job title"]
"""
import sys
from difflib import SequenceMatcher
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import data_rows, norm, open_tracker  # noqa: E402


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    company, title = norm(sys.argv[1]), norm(sys.argv[2] if len(sys.argv) > 2 else "")
    _, ws = open_tracker()
    same_role, same_company = [], []
    for _, d in data_rows(ws):
        c = norm(d["Company"])
        if not c or not (c == company or SequenceMatcher(None, c, company).ratio() > 0.85
                         or (len(company) > 3 and (company in c or c in company))):
            continue
        t = norm(d["Job Title"])
        sim = SequenceMatcher(None, t, title).ratio() if title else 0
        (same_role if title and sim > 0.8 else same_company).append((sim, d))
    if not same_role and not same_company:
        print("✓ 没有投过这家公司 / no previous applications to this company")
        return
    for label, items in (("⚠ 同一岗位已投过 / SAME ROLE already applied", same_role),
                         ("ℹ 同公司其他记录 / other applications at this company", same_company)):
        if items:
            print(label)
            for _, d in items:
                print(f"  #{d['#']} {d['Job Title']} | {d['Date Applied']} | {d['Status']} | {d['Flow'] or ''}")
    if same_role:
        sys.exit(2)


if __name__ == "__main__":
    main()

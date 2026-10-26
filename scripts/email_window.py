"""Remember when the mailbox was last checked, so each run covers the gap with overlap.

  python scripts/email_window.py           # prints the Gmail query fragment, e.g. after:2026/10/24
  python scripts/email_window.py --done    # call at the end of a successful run
"""
import argparse
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import SEARCH, STATE, load_search, read_json, today, write_json  # noqa: E402

FILE = STATE / "email_check.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--done", action="store_true")
    a = ap.parse_args()
    st = read_json(FILE, {})
    if a.done:
        st["last_success"] = today()
        write_json(FILE, st)
        print(f"✓ recorded last_success = {st['last_success']}")
        return
    look = 2
    if SEARCH.exists():
        look = int((load_search().get("email_check") or {}).get("lookback_days", 2))
    start = date.today() - timedelta(days=look)
    if st.get("last_success"):
        start = min(start, date.fromisoformat(st["last_success"]) - timedelta(days=1))
    print(f"after:{start:%Y/%m/%d}")


if __name__ == "__main__":
    main()

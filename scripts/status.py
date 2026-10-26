"""Show where things stand.

  python scripts/status.py               # application statistics
  python scripts/status.py --setup-check # is the kit set up? what is missing?
"""
import argparse
import subprocess
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import CHEATSHEET, PROFILE, ROOT, TRACKER, data_rows, open_tracker  # noqa: E402


def setup_check():
    ok = True
    print("环境检查 / setup check")
    for mod, pipn in (("yaml", "pyyaml"), ("openpyxl", "openpyxl"), ("pdfplumber", "pdfplumber"), ("reportlab", "reportlab")):
        try:
            __import__(mod)
            print(f"  ✓ {pipn}")
        except ImportError:
            print(f"  ✗ {pipn} 未安装 → pip install -r requirements.txt")
            ok = ok and mod not in ("yaml", "openpyxl")
    if not PROFILE.exists():
        print("  ✗ profile/profile.yaml 不存在 → 执行 playbooks/00-onboarding.md（对 Claude 说「开始设置」）")
        return False
    print("  ✓ profile/profile.yaml 存在")
    res = subprocess.run([sys.executable, str(ROOT / "scripts" / "validate_profile.py")], capture_output=True, text=True)
    errs = [l for l in res.stdout.splitlines() if l.startswith("ERROR")]
    if errs:
        print(f"  ✗ 资料有 {len(errs)} 个错误 → python scripts/validate_profile.py 查看")
        ok = False
    else:
        print("  ✓ 资料校验通过")
    if TRACKER.exists():
        print("  ✓ data/applications.xlsx 存在")
    else:
        print("  ✗ data/ 未初始化 → python scripts/setup_workspace.py")
        ok = False
    print("  ✓ 填表速查卡存在" if CHEATSHEET.exists() else "  ✗ 缺少填表速查卡 → python scripts/make_cheatsheet.py")
    ok = ok and CHEATSHEET.exists()
    print("\n✓ 已就绪 / ready" if ok else "\n→ 按上面的提示补齐 / fix the items above")
    return ok


def parse_date(v):
    if hasattr(v, "date"):
        return v.date()
    try:
        return date.fromisoformat(str(v)[:10])
    except ValueError:
        return None


def stats():
    _, ws = open_tracker()
    rows = [d for _, d in data_rows(ws)]
    print(f"总投递 / total: {len(rows)}")
    for s, n in Counter(d["Status"] or "(空)" for d in rows).most_common():
        print(f"  {s}: {n}")
    today = date.today()
    recent = [d for d in rows if (dt := parse_date(d["Date Applied"])) and dt >= today - timedelta(days=7)]
    print(f"\n近 7 天 / last 7 days: {len(recent)}")
    for d in recent:
        print(f"  #{d['#']} {d['Company']} — {d['Job Title']} ({d['Status']})")
    print("\n近 4 周每周 / per week:")
    for w in range(3, -1, -1):
        start = today - timedelta(days=today.weekday() + 7 * w)
        n = sum(1 for d in rows if (dt := parse_date(d["Date Applied"])) and start <= dt < start + timedelta(days=7))
        print(f"  {start}: {n}")
    active = [d for d in rows if str(d["Status"]).startswith(("Assessment", "Interview", "Offer"))]
    if active:
        print("\n进行中 / in progress:")
        for d in active:
            print(f"  #{d['#']} {d['Company']} — {d['Job Title']} | {d['Status']} | {d['Flow'] or ''}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--setup-check", action="store_true")
    a = ap.parse_args()
    if a.setup_check:
        sys.exit(0 if setup_check() else 1)
    stats()


if __name__ == "__main__":
    main()

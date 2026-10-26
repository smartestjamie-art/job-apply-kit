"""Shared helpers for job-apply-kit scripts.

Paths can be overridden with environment variables (handy for testing):
  JOBKIT_PROFILE  -> profile file (default: profile/profile.yaml)
  JOBKIT_DATA     -> data directory (default: data/)
"""
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROFILE = Path(os.environ.get("JOBKIT_PROFILE", ROOT / "profile" / "profile.yaml"))
DATA = Path(os.environ.get("JOBKIT_DATA", ROOT / "data"))
TRACKER = DATA / "applications.xlsx"
JD_ARCHIVE = DATA / "JD_archive.md"
PROGRESS = DATA / "progress.md"
NOTES = DATA / "notes.md"
CHEATSHEET = DATA / "form_cheatsheet.md"
SEARCH = Path(os.environ.get("JOBKIT_SEARCH", ROOT / "config" / "search.yaml"))
STATE = DATA / "state"
SCHEDULES = DATA / "schedules"

COLUMNS = ["#", "Job Title", "Company", "Location", "Date Applied", "Salary", "Fit Score",
           "Cover Letter", "CV Version", "Job Source", "URL", "Flow", "Notes", "Status"]
COL = {name: i + 1 for i, name in enumerate(COLUMNS)}
STATUSES = ["Applied 已投/等待", "Assessment 测评中", "Interview 面试中", "Offer",
            "Rejected 被拒", "Withdrawn 撤回", "Closed 岗位关闭"]
HEADER_ROW = 2
FIRST_DATA_ROW = 3

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def today() -> str:
    return date.today().isoformat()


def need(module: str, pip_name: str = None):
    try:
        return __import__(module)
    except ImportError:
        sys.exit(f"缺少依赖 / missing dependency: {pip_name or module}\n"
                 f"运行 / run: pip install -r requirements.txt")


def load_profile(path: Path = None) -> dict:
    yaml = need("yaml", "pyyaml")
    p = Path(path or PROFILE)
    if not p.exists():
        sys.exit(f"找不到资料文件 / profile not found: {p}\n"
                 f"对 Claude 说「开始设置」，或 cp profile/profile.template.yaml profile/profile.yaml")
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def open_tracker():
    openpyxl = need("openpyxl")
    if not TRACKER.exists():
        sys.exit(f"找不到投递表 / tracker not found: {TRACKER}\n运行 / run: python scripts/setup_workspace.py")
    wb = openpyxl.load_workbook(TRACKER)
    return wb, wb["Applications"]


def data_rows(ws):
    """Yield (row_index, dict) for every filled data row."""
    for r in range(FIRST_DATA_ROW, ws.max_row + 1):
        if ws.cell(r, 1).value in (None, ""):
            continue
        yield r, {name: ws.cell(r, i).value for name, i in COL.items()}


def norm(s) -> str:
    import re
    s = str(s or "").lower()
    s = re.sub(r"\b(ltd|limited|plc|inc|llc|group|uk|the)\b", " ", s)
    return re.sub(r"[^a-z0-9一-鿿]+", " ", s).strip()


def append_progress(line: str):
    DATA.mkdir(parents=True, exist_ok=True)
    with open(PROGRESS, "a", encoding="utf-8") as f:
        f.write(f"- {today()} {line}\n")


def load_search(path: Path = None) -> dict:
    yaml = need("yaml", "pyyaml")
    p = Path(path or SEARCH)
    if not p.exists():
        sys.exit(f"找不到搜索配置 / search config not found: {p}\n"
                 f"对 Claude 说「帮我配置搜索」，或 cp presets/uk-london-tech.yaml config/search.yaml")
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def read_json(path: Path, default):
    import json
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return default


def write_json(path: Path, obj):
    import json
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def applied_keys(ws=None):
    """Set of (normalised company, normalised title) already in the tracker."""
    if ws is None:
        if not TRACKER.exists():
            return set()
        _, ws = open_tracker()
    return {(norm(d["Company"]), norm(d["Job Title"])) for _, d in data_rows(ws)}

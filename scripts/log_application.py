"""Log a submitted application: tracker row + JD archive entry + progress line.

  python scripts/log_application.py --title "Graduate Engineer" --company "Acme" \
      --location London --url https://... --source "Company site" --fit 4 --cover Y \
      --cv "software/Your Name.pdf" --notes "..." [--jd-file "data/tmp_jd/Acme_Graduate Engineer.md"] \
      [--date YYYY-MM-DD]

A --jd-file inside data/tmp_jd/ is deleted once its text is in the JD archive.
"""
import argparse
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import (COL, FIRST_DATA_ROW, JD_ARCHIVE, ROOT, STATUSES, TMP_JD, TRACKER,  # noqa: E402
                     append_progress, data_rows, need, open_tracker, today)

MARK = "<!-- NEW ENTRIES BELOW / 新条目插在这一行下面 -->"


def add_jd(num, company, title, date_, url, jd_text):
    head = f"## #{num} {company} — {title} | {date_}\n"
    body = head + (f"链接 / URL: {url}\n\n" if url else "\n") + (jd_text.strip() or "(JD 未保存 / not saved)") + "\n\n---\n\n"
    text = JD_ARCHIVE.read_text(encoding="utf-8") if JD_ARCHIVE.exists() else f"# JD archive\n\n{MARK}\n\n"
    if MARK not in text:
        text = text.rstrip() + f"\n\n{MARK}\n\n"
    text = text.replace(MARK + "\n\n", MARK + "\n\n" + body, 1) if MARK + "\n\n" in text else text.replace(MARK, MARK + "\n\n" + body, 1)
    JD_ARCHIVE.write_text(text, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", required=True)
    ap.add_argument("--company", required=True)
    for k in ["location", "url", "source", "fit", "cover", "cv", "salary", "flow", "notes"]:
        ap.add_argument("--" + k, default="")
    ap.add_argument("--status", default=STATUSES[0])
    ap.add_argument("--date", default=today())
    ap.add_argument("--jd-file")
    ap.add_argument("--jd-text", default="")
    a = ap.parse_args()

    wb, ws = open_tracker()
    rows = list(data_rows(ws))
    last_row = rows[-1][0] if rows else FIRST_DATA_ROW - 1
    num = max([int(d["#"]) for _, d in rows if str(d["#"]).isdigit()] or [0]) + 1
    r = last_row + 1
    if rows:
        for c in range(1, len(COL) + 1):
            ws.cell(r, c)._style = copy.copy(ws.cell(last_row, c)._style)
    fit = int(a.fit) if str(a.fit).isdigit() else a.fit
    values = {"#": num, "Job Title": a.title, "Company": a.company, "Location": a.location,
              "Date Applied": a.date, "Salary": a.salary or "Not listed", "Fit Score": fit,
              "Cover Letter": a.cover, "CV Version": a.cv, "Job Source": a.source, "URL": a.url,
              "Flow": a.flow or "Applied", "Notes": a.notes, "Status": a.status}
    for k, v in values.items():
        ws.cell(r, COL[k]).value = v
    wb.save(TRACKER)

    openpyxl = need("openpyxl")
    chk = openpyxl.load_workbook(TRACKER)["Applications"]
    if chk.cell(r, COL["Company"]).value != a.company:
        sys.exit("✗ 保存校验失败，请重试 / save verification failed")

    jd, jd_path = a.jd_text, None
    if a.jd_file:
        jd_path = next((p for p in (Path(a.jd_file), ROOT / a.jd_file) if p.exists()), None)
        if jd_path:
            jd = jd_path.read_text(encoding="utf-8")
        else:
            print(f"⚠ 找不到 JD 文件 / JD file not found: {a.jd_file}（存档里会写“JD 未保存”）")
    add_jd(num, a.company, a.title, a.date, a.url, jd)
    if jd_path and TMP_JD.resolve() in jd_path.resolve().parents:
        jd_path.unlink()
    append_progress(f"投递 #{num} {a.company} — {a.title}（{a.status}）{(' · ' + a.notes) if a.notes else ''}")
    print(f"✓ 已记录 #{num}（第 {r} 行）/ logged as #{num}; JD 已存档; progress 已更新")


if __name__ == "__main__":
    main()

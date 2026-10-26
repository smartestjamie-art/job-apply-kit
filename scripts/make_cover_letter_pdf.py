"""Turn a plain-text / markdown cover letter into a clean one-page PDF.

  python scripts/make_cover_letter_pdf.py data/cover_letters/Acme_Engineer.md [--out file.pdf]

Header (name, contact line) is taken from profile.yaml. Blank lines separate paragraphs.
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _common import load_profile, need  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source")
    ap.add_argument("--out")
    a = ap.parse_args()
    need("reportlab")
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import mm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
    from xml.sax.saxutils import escape

    p = load_profile()
    idt = p.get("identity", {}) or {}
    name = " ".join(x for x in [idt.get("preferred_name") or idt.get("legal_first_name"), idt.get("last_name")] if x)
    links = idt.get("links") or {}
    contact = " | ".join(x for x in [(idt.get("address") or {}).get("city"), idt.get("email"),
                                     (idt.get("phone") or {}).get("number_e164"),
                                     (links.get("linkedin") or "").replace("https://www.", "")] if x)
    text = Path(a.source).read_text(encoding="utf-8")
    text = re.sub(r"^#.*\n", "", text)                      # drop markdown title lines
    paras = [re.sub(r"\s*\n\s*", " ", x.strip()) for x in re.split(r"\n\s*\n", text) if x.strip()]

    body = ParagraphStyle("b", fontName="Helvetica", fontSize=10.5, leading=14.5, spaceAfter=8)
    head = ParagraphStyle("h", parent=body, fontName="Helvetica-Bold", fontSize=14, spaceAfter=2)
    out = a.out or str(Path(a.source).with_suffix(".pdf"))
    doc = SimpleDocTemplate(out, pagesize=A4, leftMargin=22 * mm, rightMargin=22 * mm, topMargin=20 * mm, bottomMargin=18 * mm)
    story = [Paragraph(escape(name), head), Paragraph(escape(contact), body), Spacer(1, 6)]
    story += [Paragraph(escape(x), body) for x in paras]
    doc.build(story)
    print(f"✓ 已生成 / written: {out}")


if __name__ == "__main__":
    main()

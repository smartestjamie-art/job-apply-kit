"""Print the text of a CV PDF so Claude can pre-fill the profile.

  python scripts/extract_cv.py "cv/software/Your Name.pdf"
"""
import shutil
import subprocess
import sys

if len(sys.argv) < 2:
    sys.exit(__doc__)
path = sys.argv[1]
try:
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        print("\n\n".join((pg.extract_text() or "") for pg in pdf.pages))
except ImportError:
    if shutil.which("pdftotext"):
        print(subprocess.run(["pdftotext", "-layout", path, "-"], capture_output=True, text=True).stdout)
    else:
        sys.exit("需要 pdfplumber（pip install -r requirements.txt）或 pdftotext；也可以让 Claude 直接读取 PDF。")

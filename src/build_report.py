"""Fill the README and report templates with computed numbers and print the PDF.

Templates in templates/ contain placeholders such as
{{median_burden/All countries/2024:.1f}}: a path into
outputs/key_numbers.json followed by an optional Python format spec. A
missing path is an error, so the text cannot quote a number the analysis did
not produce. The PDF is printed from HTML by a local Chrome or Edge in
headless mode; if neither is installed the Markdown report is still written.
"""

import os
import re
import shutil
import subprocess
import json

import markdown

import config

TEMPLATES = config.ROOT / "templates"
PLACEHOLDER = re.compile(r"\{\{\s*([^}:]+?)\s*(?::([^}]+))?\}\}")

BROWSERS = [
    os.environ.get("CHROME_PATH", ""),
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "google-chrome", "chromium", "chromium-browser", "microsoft-edge",
]


def lookup(data, path):
    node = data
    for part in path.split("/"):
        if isinstance(node, list):
            node = node[int(part)]
        elif part in node:
            node = node[part]
        else:
            raise KeyError(f"Template refers to missing value: {path}")
    return node


def render(text, data):
    def sub(m):
        value = lookup(data, m.group(1))
        spec = m.group(2)
        if value is None:
            raise ValueError(f"Template value is empty: {m.group(1)}")
        return format(value, spec) if spec else str(value)
    return PLACEHOLDER.sub(sub, text)


def find_browser():
    for b in BROWSERS:
        if not b:
            continue
        path = b if os.path.isabs(b) else shutil.which(b)
        if path and os.path.exists(path):
            return path
    return None


def to_pdf(html_path, pdf_path):
    browser = find_browser()
    if browser is None:
        print("No Chrome/Edge found: skipped the PDF (set CHROME_PATH to enable it).")
        return None
    cmd = [browser, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
           "--print-to-pdf-no-header", "--virtual-time-budget=10000",
           f"--print-to-pdf={pdf_path}", html_path.absolute().as_uri()]
    subprocess.run(cmd, check=True, capture_output=True, timeout=180)
    return pdf_path


def run(pdf=True):
    data = json.loads((config.ROOT / "outputs" / "key_numbers.json").read_text(encoding="utf-8"))

    readme = render((TEMPLATES / "README.md").read_text(encoding="utf-8"), data)
    (config.ROOT / "README.md").write_text(readme, encoding="utf-8")

    report_md = render((TEMPLATES / "economic_analysis.md").read_text(encoding="utf-8"), data)
    config.REPORT.mkdir(parents=True, exist_ok=True)
    md_path = config.REPORT / "economic_analysis.md"
    md_path.write_text(report_md, encoding="utf-8")

    body = markdown.markdown(report_md, extensions=["tables", "attr_list", "md_in_html", "toc"])
    css = (TEMPLATES / "report.css").read_text(encoding="utf-8")
    html = ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<title>The Cost of Public Debt</title>"
            f"<style>{css}</style></head><body>{body}</body></html>")
    html_path = config.REPORT / "economic_analysis.html"
    html_path.write_text(html, encoding="utf-8")
    if pdf:
        return to_pdf(html_path, config.REPORT / "economic_analysis.pdf")
    return md_path

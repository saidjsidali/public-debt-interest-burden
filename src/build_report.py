"""Fill the README and report templates with computed numbers and print the PDF.

Templates in templates/ contain placeholders such as
{{median_burden/All countries/2024:.1f}}: a path into
outputs/key_numbers.json followed by an optional Python format spec. A
missing path is an error, so the text cannot quote a number the analysis did
not produce.

The PDF is printed from HTML by a local Chrome or Edge in headless mode; if
neither is installed the Markdown report is still written. In the HTML used
for the PDF, links to other files in the repository are rewritten to public
GitHub URLs, so the PDF never points to a folder on the computer that built
it. Images and fonts are still loaded from the local files.
"""

import json
import os
import posixpath
import re
import shutil
import subprocess

import markdown

import config

TEMPLATES = config.ROOT / "templates"
PLACEHOLDER = re.compile(r"\{\{\s*([^}:]+?)\s*(?::([^}]+))?\}\}")
HREF = re.compile(r'href="([^"]+)"')

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


def public_links(html, base="report"):
    """Rewrite relative links (not images) to the public repository on GitHub."""
    def sub(m):
        target = m.group(1)
        if target.startswith("#") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
            return m.group(0)
        path, _, anchor = target.partition("#")
        path = posixpath.normpath(posixpath.join(base, path))
        url = f"{config.REPO_URL}/blob/{config.REPO_LINK_REF}/{path}"
        return f'href="{url}{"#" + anchor if anchor else ""}"'
    return HREF.sub(sub, html)


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


DRAFT_BANNER = (
    "> **DRAFT built from an unreviewed data snapshot** (`{snapshot}`). The numbers come from that "
    "snapshot, but the text, the reviewed cases and the conclusions were written for the October 2026 "
    "IMF data and have not been checked again. Do not publish this file as it is.\n\n"
)


DRAFT_PATHS = [  # published path -> draft path, for links, images and file names in the text
    (re.compile(r"(?<![\w-])outputs/"), "outputs_draft/"),
    (re.compile(r"(?<![\w-])audit/validation_report\.md"), "audit/draft/validation_report.md"),
    (re.compile(r"(?<![\w-])audit/flags/"), "audit/draft/flags/"),
]


def as_draft(text):
    """Mark a rendered document as a draft and point it to the draft figures, tables and checks."""
    snapshot = config.DATA_RAW.relative_to(config.ROOT).as_posix() if config.DATA_RAW.is_relative_to(config.ROOT) \
        else config.DATA_RAW.as_posix()
    for pattern, draft_path in DRAFT_PATHS:
        text = pattern.sub(draft_path, text)
    return DRAFT_BANNER.format(snapshot=snapshot) + text


def run(pdf=True):
    """Write README.md and the report; in draft mode write *_draft files and leave the published ones alone."""
    data = json.loads(config.KEY_NUMBERS.read_text(encoding="utf-8"))
    suffix = "_draft" if config.DRAFT else ""

    readme = render((TEMPLATES / "README.md").read_text(encoding="utf-8"), data)
    report_md = render((TEMPLATES / "economic_analysis.md").read_text(encoding="utf-8"), data)
    if config.DRAFT:
        readme, report_md = as_draft(readme), as_draft(report_md)
    (config.ROOT / f"README{suffix}.md").write_text(readme, encoding="utf-8")
    config.REPORT.mkdir(parents=True, exist_ok=True)
    md_path = config.REPORT / f"economic_analysis{suffix}.md"
    md_path.write_text(report_md, encoding="utf-8")

    body = markdown.markdown(report_md, extensions=["tables", "attr_list", "md_in_html", "toc"])
    css = (TEMPLATES / "report.css").read_text(encoding="utf-8")
    html = ("<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<title>Public debt and interest burdens, 2015-2024</title>"
            f"<style>{css}</style></head><body>{public_links(body)}</body></html>")
    html_path = config.REPORT / f"economic_analysis{suffix}.html"
    html_path.write_text(html, encoding="utf-8")
    if pdf:
        return to_pdf(html_path, config.REPORT / f"economic_analysis{suffix}.pdf")
    return md_path

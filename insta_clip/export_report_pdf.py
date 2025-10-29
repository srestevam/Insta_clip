# export_report_pdf.py
from playwright.sync_api import sync_playwright
from pathlib import Path
import time

BASE_URL = "http://127.0.0.1:5000/report"  # a rota do relatório
OUT_DIR = Path("exports"); OUT_DIR.mkdir(exist_ok=True)
OUT_FILE = OUT_DIR / "Clipping_AZUVER_Relatorio.pdf"

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(BASE_URL, wait_until="networkidle")
        time.sleep(0.8)  # fonts/CDN extra
        page.pdf(
            path=str(OUT_FILE),
            print_background=True,
            format="A4",
            margin={"top": "12mm", "bottom": "12mm", "left": "12mm", "right": "12mm"},
            prefer_css_page_size=True,
            display_header_footer=True,
            header_template="""
              <div style="width:100%; font-size:9px; color:#666; padding:0 10mm;">
                <span>Clipping AZUVER — Relatório</span>
              </div>""",
            footer_template="""
              <div style="width:100%; font-size:9px; color:#666; padding:0 10mm; display:flex; justify-content:flex-end;">
                <span class="pageNumber"></span>/<span class="totalPages"></span>
              </div>"""
        )
        browser.close()
    print("PDF gerado em:", OUT_FILE.resolve())

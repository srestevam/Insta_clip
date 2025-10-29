# export_pdf.py
from playwright.sync_api import sync_playwright
from pypdf import PdfWriter, PdfReader
from pathlib import Path
import time

BASE_URL = "http://127.0.0.1:5000"
OUT_DIR = Path("exports")
OUT_DIR.mkdir(exist_ok=True)

def render_pdf(url: str, out_file: Path, wait_ms: int = 800):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        # Carrega e espera rede ociosa (imagens, fontes, etc.)
        page.goto(url, wait_until="networkidle")
        # Pequeno “extra wait” p/ fontes web ou CDN
        time.sleep(wait_ms/1000)
        # PDF com fundos, margens e número de página
        page.pdf(
            path=str(out_file),
            print_background=True,
            margin={"top": "18mm", "bottom": "16mm", "left": "14mm", "right": "14mm"},
            format="A4",
            display_header_footer=True,
            header_template="""
                <div style="font-size:10px;color:#666;padding-left:8mm;padding-right:8mm;width:100%;"></div>
            """,
            footer_template="""
                <div style="font-size:10px;color:#666;padding-left:8mm;padding-right:8mm;width:100%;display:flex;justify-content:space-between;">
                  <span></span>
                  <span class="pageNumber"></span>/<span class="totalPages"></span>
                </div>
            """,
            prefer_css_page_size=True,
        )
        browser.close()

def merge_pdfs(files, out_file: Path):
    writer = PdfWriter()
    for f in files:
        reader = PdfReader(str(f))
        for page in reader.pages:
            writer.add_page(page)
    with out_file.open("wb") as fp:
        writer.write(fp)

if __name__ == "__main__":
    feed_pdf = OUT_DIR / "01_feed.pdf"
    profiles_pdf = OUT_DIR / "02_perfis.pdf"
    final_pdf = OUT_DIR / "Clipping_AZUVER.pdf"

    # 1) Feed (homepage)
    render_pdf(f"{BASE_URL}/", feed_pdf)

    # 2) Perfis
    render_pdf(f"{BASE_URL}/profiles", profiles_pdf)

    # 3) Mesclar (feed -> perfis)
    merge_pdfs([feed_pdf, profiles_pdf], final_pdf)
    print("PDF gerado em:", final_pdf.resolve())

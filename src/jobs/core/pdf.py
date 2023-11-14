import pypdfium2 as pdfium
from pathlib import Path
from PIL import Image
import logging


def to_pil(pdf_path: Path) -> Image.Image:
    assert pdf_path.exists()
    pdf = pdfium.PdfDocument(pdf_path.as_posix())
    n_pages = len(pdf)
    width, height = pdf.get_page_size(0)
    result = Image.new("RGBA", (int(width), int(height * n_pages)))
    logging.debug(f"{pdf_path.name} {pdf.get_version()}, {n_pages} pages")
    for idx, page in enumerate(pdf):
        bitmap = page.render()
        result.paste(bitmap.to_pil(), (0, int(height * idx),
                     int(width), int(height * (idx+1))))
    return result

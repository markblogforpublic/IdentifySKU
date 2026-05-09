"""
US engine — TransferSKU: match "Single SKU" text, crop by grid, regroup by SKU name and export.

Uses a completely different processing logic from the UK/AU version (FBA label-number matching).
Built on PyMuPDF (fitz), consistent with other modules in the project.
"""
import fitz  # pymupdf
import re
import os
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


def _validate_margins(ml, mt, mr, mb, pw, ph):
    """Validate margin values against page dimensions. Raises ValueError."""
    for name, val in [("left", ml), ("top", mt), ("right", mr), ("bottom", mb)]:
        if val < 0:
            raise ValueError(f"Margin '{name}' cannot be negative (got {val})")
    if ml + mr >= pw:
        raise ValueError(f"Horizontal margins ({ml + mr}) exceed page width ({pw})")
    if mt + mb >= ph:
        raise ValueError(f"Vertical margins ({mt + mb}) exceed page height ({ph})")


def process_sku_pdf(input_pdf, output_dir, rows=3, cols=2,
                    margin_l=0, margin_t=40, margin_r=0, margin_b=40,
                    on_progress=None):
    """
    Process US PDF: crop by grid, extract SKU, regroup and export by SKU.

    Args:
      input_pdf:   source PDF path
      output_dir:  output directory
      rows, cols:  grid rows and columns per page (default 3x2)
      margin_l/t/r/b: margins (pt) to exclude non-label page edge areas
      on_progress:  callback (stage, current, total, message)

    Returns:
      {"files": ["SKU_A.pdf", "SKU_B.pdf", ...], "skus": [...], "errors": []}
    """
    errors = []
    sku_blocks = defaultdict(list)

    def emit(stage, cur, total, msg):
        if on_progress:
            on_progress(stage, cur, total, msg)
        logger.debug(msg)

    src_doc = fitz.open(input_pdf)
    total_pages = len(src_doc)

    # Validate margins against first page dimensions
    first_page = src_doc[0]
    _validate_margins(margin_l, margin_t, margin_r, margin_b,
                      first_page.rect.width, first_page.rect.height)

    emit("scan", 0, total_pages, f"US mode: scanning {total_pages} pages...")

    for page_idx in range(total_pages):
        page = src_doc[page_idx]
        pw, ph = page.rect.width, page.rect.height
        usable_w = pw - margin_l - margin_r
        usable_h = ph - margin_t - margin_b
        cell_w = usable_w / cols
        cell_h = usable_h / rows

        for r in range(rows):
            for c in range(cols):
                x0 = margin_l + c * cell_w
                y0 = margin_t + r * cell_h
                x1 = x0 + cell_w
                y1 = y0 + cell_h
                rect = fitz.Rect(x0, y0, x1, y1)

                text = page.get_text("text", clip=rect)
                if not text:
                    continue

                lines = text.strip().split('\n')
                for k, line in enumerate(lines):
                    if 'Single SKU' in line and k + 1 < len(lines):
                        sku = lines[k + 1].strip()
                        if sku:
                            sku_blocks[sku].append((page_idx, rect))
                            break

        emit("scan", page_idx + 1, total_pages,
             f"Scanning... {page_idx + 1}/{total_pages} pages")

    if not sku_blocks:
        errors.append("No SKU labels found. Please check the PDF format or grid parameters.")
        src_doc.close()
        return {"files": [], "skus": [], "errors": errors}

    sku_list = sorted(sku_blocks.keys())
    total_skus = len(sku_list)
    output_files = []

    emit("export", 0, total_skus, f"Identified {total_skus} SKU(s), exporting...")

    for j, sku in enumerate(sku_list):
        blocks = sku_blocks[sku]
        new_doc = fitz.open()

        for p_idx, crop_rect in blocks:
            new_doc.insert_pdf(src_doc, from_page=p_idx, to_page=p_idx)
            new_doc[-1].set_cropbox(crop_rect)
            new_doc[-1].set_mediabox(crop_rect)

        safe_name = re.sub(r'[\\/:*?"<>|]', '_', sku).strip()
        if not safe_name:
            safe_name = f"SKU_{j+1}"
        file_name = f"{safe_name}.pdf"
        save_path = os.path.join(output_dir, file_name)
        new_doc.save(save_path)
        new_doc.close()
        output_files.append(file_name)

        emit("export", j + 1, total_skus,
             f"[{j+1}/{total_skus}] {sku} → {len(blocks)} label(s)")

    src_doc.close()
    emit("export", total_skus, total_skus,
         f"Done! Exported {len(output_files)} SKU file(s)")
    return {"files": output_files, "skus": sku_list, "errors": errors}

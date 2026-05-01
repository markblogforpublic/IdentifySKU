"""
Core processing engine — UK/AU (FBA label-number matching) and US (Single SKU text matching).
Lite version — pure logic, no GUI dependencies.
"""
import fitz  # pymupdf
import re
import os
import csv


# ═══════════════════════════════════════════════════════════════
#  CSV Parsing (UK/AU)
# ═══════════════════════════════════════════════════════════════

def parse_ranges_from_csv(csv_path):
    """
    Extract ranges from an Amazon packing list CSV.
    Pattern: FBA[A-Z0-9]+U(\d+)-(\d+)
    Returns: [{"title": "GPETNPET1000", "start": 0, "end": 58}, ...]
    """
    range_pattern = re.compile(r"FBA[A-Z0-9]+U(\d+)-(\d+)")
    raw = []

    with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            sku = row[1].strip()
            found = False
            for cell in row:
                m = range_pattern.search(cell.strip())
                if m and not found:
                    raw.append((int(m.group(1)), int(m.group(2)), sku))
                    found = True

    if not raw:
        return []

    seen = set()
    unique = []
    for s, e, t in raw:
        key = (s, e)
        if key not in seen:
            seen.add(key)
            unique.append({"title": t or f"{s:03d}-{e}", "start": s, "end": e})

    unique.sort(key=lambda x: x["start"])
    if unique and unique[0]["start"] == 1:
        unique[0]["start"] = 0

    return unique


# ═══════════════════════════════════════════════════════════════
#  UK/AU Engine — FBA label-number matching
# ═══════════════════════════════════════════════════════════════

class FBABlockSorter:
    """UK/AU: split PDF by FBA label-number ranges."""

    def __init__(self, input_pdf, output_dir, range_configs, on_progress=None):
        self.input_pdf = input_pdf
        self.output_dir = output_dir
        self.range_configs = range_configs
        self.on_progress = on_progress
        self.output_files = []

    def _emit(self, stage, current, total, message):
        if self.on_progress:
            self.on_progress(stage, current, total, message)

    def process(self):
        src_doc = fitz.open(self.input_pdf)
        all_label_blocks = []
        total_pages = len(src_doc)

        self._emit("scan", 0, total_pages, "scan_start")

        # Scan phase: divide each page into 4 quadrants, extract labels
        for page_index in range(total_pages):
            page = src_doc[page_index]
            rect = page.rect
            w2, h2 = rect.width / 2, rect.height / 2

            quadrants = [
                fitz.Rect(0, 0, w2, h2),
                fitz.Rect(w2, 0, rect.width, h2),
                fitz.Rect(0, h2, w2, rect.height),
                fitz.Rect(w2, h2, rect.width, rect.height),
            ]

            for quad in quadrants:
                text = page.get_text("text", clip=quad)
                match = re.search(r"FBA[A-Z0-9]+U(\d+)", text)
                if match:
                    all_label_blocks.append({
                        "suffix": int(match.group(1)),
                        "page_idx": page_index,
                        "crop_rect": quad,
                    })

            self._emit("scan", page_index + 1, total_pages,
                       f"scan_page|{page_index + 1}|{total_pages}")

        all_label_blocks.sort(key=lambda x: x["suffix"])

        # Split phase: group by ranges and export
        total_ranges = len(self.range_configs)
        self._emit("split", 0, total_ranges, "split_start")

        for ri, cfg in enumerate(self.range_configs):
            start, end = cfg["start"], cfg["end"]
            title = cfg.get("title", f"{start}-{end}")
            matched = [b for b in all_label_blocks if start <= b["suffix"] <= end]

            if not matched:
                self._emit("split", ri + 1, total_ranges,
                           f"skip_range|{start}|{end}|{title}")
                continue

            export_order = [b["suffix"] for b in matched]
            if export_order != sorted(export_order):
                matched.sort(key=lambda x: x["suffix"])

            new_doc = fitz.open()
            for block in matched:
                new_doc.insert_pdf(src_doc, from_page=block["page_idx"],
                                   to_page=block["page_idx"])
                new_doc[-1].set_cropbox(block["crop_rect"])
                new_doc[-1].set_mediabox(block["crop_rect"])

            file_name = f"FBA_Labels_{start}_{end}.pdf"
            save_path = os.path.join(self.output_dir, file_name)
            new_doc.save(save_path)
            new_doc.close()

            # Verification
            verify_doc = fitz.open(save_path)
            verify_order = []
            for vp in verify_doc:
                vt = vp.get_text("text")
                vm = re.search(r"FBA[A-Z0-9]+U(\d+)", vt)
                if vm:
                    verify_order.append(int(vm.group(1)))
            verify_doc.close()

            ok = verify_order == sorted(verify_order)
            sample = ", ".join(str(x) for x in export_order[:5])
            if len(export_order) > 5:
                sample += f" ... {export_order[-1]}"

            self.output_files.append(file_name)
            status = "OK" if ok else "FAIL"
            self._emit("split", ri + 1, total_ranges,
                       f"export_label|{ri + 1}|{total_ranges}|{title}|{len(matched)}|{sample}|{status}")
            if not ok:
                self._emit("split", ri + 1, total_ranges,
                           f"verify_fail|{verify_order}")

        src_doc.close()
        self._emit("split", total_ranges, total_ranges, "split_done")
        return self.output_files


def process_uk_au(input_pdf, output_dir, csv_path=None, manual_ranges=None,
                  on_progress=None):
    """Run UK/AU processing: parse ranges from CSV or use manual ranges, then split."""
    errors = []
    ranges = None

    if manual_ranges:
        ranges = manual_ranges
    elif csv_path and os.path.exists(csv_path):
        ranges = parse_ranges_from_csv(csv_path)
        if not ranges:
            errors.append("No valid label ranges found in CSV")

    if not ranges:
        return {"files": [], "ranges": [], "errors": errors + ["No ranges configured"]}

    sorter = FBABlockSorter(input_pdf, output_dir, ranges, on_progress=on_progress)
    files = sorter.process()

    return {
        "files": files,
        "ranges": [{"title": r.get("title", ""), "start": r["start"], "end": r["end"]}
                   for r in ranges],
        "errors": errors,
    }


# ═══════════════════════════════════════════════════════════════
#  US Engine — Single SKU text matching
# ═══════════════════════════════════════════════════════════════

def process_us(input_pdf, output_dir, rows=3, cols=2,
               margin_l=0, margin_t=40, margin_r=0, margin_b=40,
               on_progress=None):
    """
    US mode: crop PDF by grid, detect "Single SKU" text, group by SKU and export.
    """
    errors = []
    from collections import defaultdict
    sku_blocks = defaultdict(list)

    def emit(stage, cur, total, msg):
        if on_progress:
            on_progress(stage, cur, total, msg)

    src_doc = fitz.open(input_pdf)
    total_pages = len(src_doc)
    emit("scan", 0, total_pages, "us_scan_start")

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

                lines = text.strip().split("\n")
                for k, line in enumerate(lines):
                    if "Single SKU" in line and k + 1 < len(lines):
                        sku = lines[k + 1].strip()
                        if sku:
                            sku_blocks[sku].append((page_idx, rect))
                            break

        emit("scan", page_idx + 1, total_pages,
             f"us_scan_page|{page_idx + 1}|{total_pages}")

    if not sku_blocks:
        errors.append("No SKU labels found")
        src_doc.close()
        return {"files": [], "skus": [], "errors": errors}

    sku_list = sorted(sku_blocks.keys())
    total_skus = len(sku_list)
    output_files = []
    emit("export", 0, total_skus, "us_export_start")

    for j, sku in enumerate(sku_list):
        blocks = sku_blocks[sku]
        new_doc = fitz.open()
        for p_idx, crop_rect in blocks:
            new_doc.insert_pdf(src_doc, from_page=p_idx, to_page=p_idx)
            new_doc[-1].set_cropbox(crop_rect)
            new_doc[-1].set_mediabox(crop_rect)

        safe_name = re.sub(r'[\\/:*?"<>|]', "_", sku).strip()
        if not safe_name:
            safe_name = f"SKU_{j+1}"
        file_name = f"{safe_name}.pdf"
        save_path = os.path.join(output_dir, file_name)
        new_doc.save(save_path)
        new_doc.close()
        output_files.append(file_name)
        emit("export", j + 1, total_skus,
             f"us_export_sku|{j + 1}|{total_skus}|{sku}|{len(blocks)}")

    src_doc.close()
    emit("export", total_skus, total_skus, "us_export_done")
    return {"files": output_files, "skus": sku_list, "errors": errors}

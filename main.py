import fitz  # pip install pymupdf
import re
import os
import csv
import logging

logger = logging.getLogger(__name__)


# ============================================================
#  GUI utility functions (CLI mode only)
# ============================================================

def select_paths():
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.attributes('-topmost', True)

    input_pdf = filedialog.askopenfilename(
        title="Select FBA label source file (PDF)",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not input_pdf:
        return None, None, None

    output_dir = filedialog.askdirectory(title="Select output folder for results")
    if not output_dir:
        return None, None, None

    pdf_dir = os.path.dirname(input_pdf)
    csv_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.csv')]

    csv_path = None
    if len(csv_files) == 1:
        csv_path = os.path.join(pdf_dir, csv_files[0])
        logger.info("Auto-matched packing list: %s", csv_files[0])
    elif len(csv_files) > 1:
        csv_path = filedialog.askopenfilename(
            title="Select packing list CSV (multiple found in same directory)",
            initialdir=pdf_dir,
            filetypes=[("CSV files", "*.csv")]
        )

    return input_pdf, output_dir, csv_path


# ============================================================
#  Core parsing: CSV → list of ranges with titles
# ============================================================

def parse_ranges_from_csv(csv_path):
    """
    Extract ranges from an Amazon packing list CSV, matching SKU names as titles.
    Compatible with UK / AU / and other marketplaces (column layout may vary, no fixed column index assumed).

    Returns:
      [{"title": "GPETNPET1000", "start": 0, "end": 58}, ...]
    """
    range_pattern = re.compile(r'FBA[A-Z0-9]+U(\d+)-(\d+)')
    raw = []  # (start, end, title)

    with open(csv_path, 'r', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 2:
                continue
            sku = row[1].strip()  # SKU column is the 2nd column for UK/AU
            row_title = sku
            found_in_row = False
            for cell in row:
                m = range_pattern.search(cell.strip())
                if m and not found_in_row:
                    raw.append((int(m.group(1)), int(m.group(2)), row_title))
                    found_in_row = True

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
        if not unique[0]["title"]:
            unique[0]["title"] = f"000-{unique[0]['end']}"

    return unique


# ============================================================
#  FBA label splitter (core engine)
# ============================================================

class FBABlockSorter:
    def __init__(self, input_pdf, output_dir, range_configs, on_progress=None):
        self.input_pdf = input_pdf
        self.output_dir = output_dir
        self.range_configs = range_configs
        self.on_progress = on_progress
        self.output_files = []

    def _emit(self, stage, current, total, message):
        if self.on_progress:
            self.on_progress(stage, current, total, message)
        logger.debug(message)

    def process(self):
        src_doc = fitz.open(self.input_pdf)
        all_label_blocks = []
        total_pages = len(src_doc)

        self._emit("scan", 0, total_pages, "Step 1: Slicing and identifying label block content...")

        for page_index in range(total_pages):
            page = src_doc[page_index]
            rect = page.rect
            w2, h2 = rect.width / 2, rect.height / 2

            # Use positioned text blocks instead of clipped text scans.
            # get_text("blocks") returns (x0,y0,x1,y1,text,...) per block;
            # assign each block to exactly one quadrant by its center coordinate,
            # eliminating boundary-overlap duplicates or misses.
            blocks = page.get_text("blocks")
            for block in blocks:
                x0, y0, x1, y1, text = block[:5]
                cx, cy = (x0 + x1) / 2, (y0 + y1) / 2

                match = re.search(r'FBA[A-Z0-9]+U(\d+)', text)
                if not match:
                    continue

                suffix = int(match.group(1))
                col = 1 if cx >= w2 else 0
                row = 1 if cy >= h2 else 0
                quad = fitz.Rect(col * w2, row * h2,
                                 (col + 1) * w2, (row + 1) * h2)

                all_label_blocks.append({
                    "suffix": suffix,
                    "page_idx": page_index,
                    "crop_rect": quad
                })

            self._emit("scan", page_index + 1, total_pages,
                       f"Scanning... {page_index + 1}/{total_pages} pages")

        all_label_blocks.sort(key=lambda x: x['suffix'])

        # Deduplication safety net: remove any duplicate (page_idx, suffix) pairs
        seen_blocks = set()
        deduped = []
        for b in all_label_blocks:
            key = (b["page_idx"], b["suffix"])
            if key not in seen_blocks:
                seen_blocks.add(key)
                deduped.append(b)
        all_label_blocks = deduped

        total_ranges = len(self.range_configs)
        self._emit("split", 0, total_ranges,
                   f"Step 2: Classifying slices by {total_ranges} range(s)...")

        for ri, cfg in enumerate(self.range_configs):
            start, end, title = cfg["start"], cfg["end"], cfg.get("title", "")
            matched_blocks = [b for b in all_label_blocks
                              if start <= b['suffix'] <= end]

            if not matched_blocks:
                self._emit("split", ri + 1, total_ranges,
                           f"Skipping [{start}-{end}] {title}: no matching labels")
                continue

            export_order = [b['suffix'] for b in matched_blocks]
            if export_order != sorted(export_order):
                matched_blocks.sort(key=lambda x: x['suffix'])

            new_doc = fitz.open()
            for block in matched_blocks:
                new_doc.insert_pdf(src_doc, from_page=block['page_idx'],
                                   to_page=block['page_idx'])
                new_doc[-1].set_cropbox(block['crop_rect'])
                new_doc[-1].set_mediabox(block['crop_rect'])

            file_name = f"FBA_Labels_{start}_{end}.pdf"
            save_path = os.path.join(self.output_dir, file_name)
            new_doc.save(save_path)
            new_doc.close()

            verify_doc = fitz.open(save_path)
            verify_order = []
            verify_wrong = []
            for vp in verify_doc:
                vt = vp.get_text("text")
                vm = re.search(r'FBA[A-Z0-9]+U(\d+)', vt)
                if vm:
                    val = int(vm.group(1))
                    verify_order.append(val)
                    if val < start or val > end:
                        verify_wrong.append(val)
            verify_doc.close()

            ok = verify_order == sorted(verify_order) and not verify_wrong
            status = "OK" if ok else "OUT_OF_ORDER!"
            sample = ", ".join(str(x) for x in export_order[:5])
            if len(export_order) > 5:
                sample += f" ... {export_order[-1]}"

            self.output_files.append(file_name)
            self._emit("split", ri + 1, total_ranges,
                       f"[{start}-{end}] {title} | {len(matched_blocks)} label(s) ({sample}) {status}")
            if verify_wrong:
                self._emit("split", ri + 1, total_ranges,
                           f"  Labels outside range [{start}-{end}]: {sorted(verify_wrong)}")
            if not ok:
                self._emit("split", ri + 1, total_ranges,
                           f"  Verification FAILED! Actual order: {verify_order}")

        src_doc.close()
        self._emit("split", total_ranges, total_ranges,
                   f"Done! Generated {len(self.output_files)} file(s)")
        return self.output_files


def process_pdf(input_pdf, output_dir, csv_path=None, manual_ranges=None,
                on_progress=None):
    errors = []
    ranges = None
    source = None

    if manual_ranges:
        ranges = manual_ranges
        source = "manual input"
    elif csv_path and os.path.exists(csv_path):
        ranges = parse_ranges_from_csv(csv_path)
        if ranges:
            source = "CSV packing list"
        else:
            errors.append("No valid label ranges found in CSV")

    if not ranges:
        return {
            "files": [],
            "ranges": [],
            "source": None,
            "errors": errors + ["No range configuration provided, cannot process."]
        }

    sorter = FBABlockSorter(input_pdf, output_dir, ranges,
                            on_progress=on_progress)
    files = sorter.process()

    return {
        "files": files,
        "ranges": [{"title": r.get("title", ""), "start": r["start"], "end": r["end"]}
                   for r in ranges],
        "source": source,
        "errors": errors
    }


if __name__ == "__main__":
    file_path, save_path, csv_path = select_paths()
    if not (file_path and save_path):
        print("Operation cancelled by user")
        exit()

    ranges = None
    if csv_path:
        ranges = parse_ranges_from_csv(csv_path)
        if ranges:
            print(f"Auto-identified {len(ranges)} range(s) from CSV:")
            for r in ranges:
                print(f"  [{r['start']}-{r['end']}] {r['title']}")
        else:
            print("No valid label ranges found in CSV.")

    if not ranges:
        from tkinter import messagebox
        messagebox.showerror("Missing Range Configuration",
            "No valid label ranges found.\n\nMake sure a packing list CSV file exists in the same directory as the PDF.")
        exit()

    try:
        sorter = FBABlockSorter(file_path, save_path, ranges)
        sorter.process()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred during processing:\n{str(e)}")

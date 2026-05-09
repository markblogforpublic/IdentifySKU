"""
CLI command engine — provides command vocabulary used on the web terminal.
Each session independently maintains state (region / file paths / ranges etc.).
"""
import os, json, shutil, uuid, zipfile, io, re
from datetime import datetime
import lang

import main as fba_engine
import us_engine


# ═══════════════════════════════════════════════════
#  Session state management
# ═══════════════════════════════════════════════════

sessions = {}  # session_id → CLIState


class CLIState:
    def __init__(self, session_id, temp_dir, lang_code='zh'):
        self.session_id = session_id
        self.temp_dir = temp_dir
        self.lang_code = lang_code
        self.region = 'uk'
        self.pdf_path = None
        self.csv_path = None
        self.ranges = []       # [{title, start, end}]
        self.us_grid = (3, 2)
        self.us_margin = (0, 40, 0, 40)
        self.job_id = None
        self.job_result = None
        self.history = []

    def reset_job(self):
        self.job_id = None
        self.job_result = None


def get_or_create_state(session_id, temp_dir, lang_code='zh'):
    if session_id not in sessions:
        os.makedirs(temp_dir, exist_ok=True)
        sessions[session_id] = CLIState(session_id, temp_dir, lang_code)
    else:
        sessions[session_id].lang_code = lang_code
    return sessions[session_id]


# ═══════════════════════════════════════════════════
#  Command parser
# ═══════════════════════════════════════════════════

def parse_command(text):
    """Split input text into command name and argument list. Supports quotes."""
    tokens = []
    current = ''
    in_quote = False
    for ch in text:
        if ch == '"':
            in_quote = not in_quote
        elif ch == ' ' and not in_quote:
            if current:
                tokens.append(current)
                current = ''
        else:
            current += ch
    if current:
        tokens.append(current)
    return tokens[0].lower() if tokens else '', tokens[1:]


# ═══════════════════════════════════════════════════
#  Command execution
# ═══════════════════════════════════════════════════

HELP_TEXT = """
FBA Label Splitter — CLI Command Reference
══════════════════════════════════════════════════════════════

UK / AU MODE  (FBA label-number matching)
  Use this when your PDF contains labels with FBA numbers
  like FBA15XXXU0 through FBA15XXXU58.

  region uk | au           Switch to UK or AU processing mode
  pdf <path>               Select the FBA label PDF file
                           Example: pdf C:\\labels\\FBA_labels.pdf
  csv <path>               Select the packing list CSV or Excel file
                           Example: csv C:\\labels\\packing.csv
                           XLSX files are auto-converted to CSV.
                           Ranges are parsed automatically from the file.
  range add <start> <end> [title]
                           Manually add a label number range
                           Example: range add 0 58 GPETNPET1000
  range list               Show all configured label ranges
  range remove <index>     Delete a range (1 = first range)
  range clear              Remove all ranges
  process                  Execute label splitting.
                           Output PDFs are saved and ready to download.

  Typical workflow:
    region uk → pdf C:\\labels.pdf → csv C:\\packing.csv → process

US MODE  (Single SKU text matching)
  Use this when your PDF contains "Single SKU" text markers
  followed by the SKU name on the next line.

  region us                Switch to US processing mode
  us-pdf <path>            Select the US SKU label PDF
                           Example: us-pdf C:\\labels\\US_sku.pdf
  us-grid <rows> <cols>    Set how many labels per page (grid layout)
                           Example: us-grid 3 2  (3 rows, 2 columns)
  us-margin <L> <T> <R> <B>
                           Set page margins in points (pt).
                           These exclude non-label areas at page edges.
                           Example: us-margin 0 40 0 40
  us-process               Execute SKU splitting.
                           Each unique SKU gets its own PDF file.

  Typical workflow:
    region us → us-pdf C:\\labels.pdf → us-grid 3 2 → us-process

DOWNLOAD
  After processing, use these to get your result files:

  download                 List all generated files
  download <filename>      Download a specific file
                           Example: download FBA_Labels_0_58.pdf
  download-all             Download everything as a ZIP archive

GENERAL COMMANDS
  help                     Show this detailed command reference
  info | status            Display current session state (region, files, ranges)
  history                  Show your command history (last 20 entries)
  clear                    Clear the terminal screen

TIPS
  - Use TAB in the future for auto-completion (coming soon)
  - Press up / down arrow keys to browse command history
  - All file paths must be absolute (e.g., C:\\folder\\file.pdf)
  - Commands are case-insensitive
  - Type a command without arguments to see its current value
"""


def execute(text, session_id, temp_root, lang_code='zh'):
    """Execute a command, returns (output_text, is_error)."""
    state = get_or_create_state(session_id, os.path.join(temp_root, session_id), lang_code)
    state.history.append(text)

    cmd, args = parse_command(text)
    if not cmd:
        return '', False

    try:
        handler = COMMANDS.get(cmd)
        if handler:
            return handler(state, args, temp_root)
        else:
            return lang.get('cli_unknown_cmd', state.lang_code).format(cmd=cmd) + '\n' + lang.get('cli_help_hint', state.lang_code), True
    except Exception as e:
        return f"Error: {e}", True


# ═══════════════════════════════════════════════════
#  Command implementations
# ═══════════════════════════════════════════════════

def _validate_file(path, ext_filter=None):
    """Validate file exists and extension matches, returns (ok, error_msg)."""
    if not os.path.exists(path):
        return False, f"File not found: {path}"
    if ext_filter:
        if not path.lower().endswith(ext_filter):
            return False, f"Invalid file type. Expected {ext_filter}"
    return True, None


def _cmd_help(state, args, _root):
    return HELP_TEXT, False


def _cmd_region(state, args, _root):
    if not args:
        return f"Current region: {state.region.upper()}\nUsage: region <uk|au|us>", False
    r = args[0].lower()
    if r not in ('uk', 'au', 'us'):
        return lang.get('cli_invalid_region', state.lang_code), True
    state.region = r
    state.reset_job()
    return lang.get('cli_region_set', state.lang_code).format(r=r.upper()), False


def _cmd_pdf(state, args, _root):
    if not args:
        return f"Current PDF: {state.pdf_path or '(none)'}\nUsage: pdf <absolute_path>", False
    path = args[0]
    ok, err = _validate_file(path, '.pdf')
    if not ok:
        return err, True
    state.pdf_path = path
    state.reset_job()
    return lang.get('cli_pdf_loaded', state.lang_code).format(path=path), False


def _cmd_csv(state, args, _root):
    if not args:
        return f"Current CSV: {state.csv_path or '(none)'}\nUsage: csv <absolute_path>", False
    path = args[0]
    ext = os.path.splitext(path)[1].lower()
    if ext not in ('.csv', '.xlsx', '.xls'):
        return "File must be .csv, .xlsx, or .xls", True
    ok, err = _validate_file(path)
    if not ok:
        return err, True
    state.csv_path = path

    # Try to parse ranges
    try:
        ranges = fba_engine.parse_ranges_from_csv(path)
        state.ranges = ranges
        lines = [lang.get('cli_csv_loaded', state.lang_code).format(path=path)]
        lines.append(lang.get('cli_ranges_parsed', state.lang_code).format(count=len(ranges)))
        for r in ranges:
            lines.append(f"  [{r['start']}-{r['end']}] {r.get('title', '')}")
        return '\n'.join(lines), False
    except Exception as e:
        state.ranges = []
        return f"{lang.get('cli_csv_loaded', state.lang_code).format(path=path)}\nWarning: Could not parse ranges - {e}", True


def _cmd_range(state, args, _root):
    sub = args[0].lower() if args else 'list'
    if sub == 'add':
        if len(args) < 3:
            return "Usage: range add <start> <end> [title]", True
        try:
            s, e = int(args[1]), int(args[2])
        except ValueError:
            return "Start and end must be integers", True
        title = args[3] if len(args) > 3 else f"{s}-{e}"
        state.ranges.append({"title": title, "start": s, "end": e})
        state.ranges.sort(key=lambda x: x['start'])
        state.reset_job()
        return lang.get('cli_range_added', state.lang_code).format(s=s, e=e, title=title, total=len(state.ranges)), False

    elif sub == 'remove':
        if len(args) < 2:
            return "Usage: range remove <index>", True
        try:
            idx = int(args[1]) - 1
        except ValueError:
            return "Index must be an integer (1-based)", True
        if idx < 0 or idx >= len(state.ranges):
            return f"Index out of range (1-{len(state.ranges)})", True
        removed = state.ranges.pop(idx)
        state.reset_job()
        return lang.get('cli_range_removed', state.lang_code).format(start=removed['start'], end=removed['end'], title=removed['title']), False

    elif sub == 'clear':
        state.ranges = []
        state.reset_job()
        return lang.get('cli_ranges_cleared', state.lang_code), False

    elif sub == 'list':
        if not state.ranges:
            return lang.get('cli_no_ranges', state.lang_code), False
        lines = [f"Ranges ({len(state.ranges)}):"]
        for i, r in enumerate(state.ranges):
            lines.append(f"  {i+1}. [{r['start']}-{r['end']}] {r.get('title', '')}")
        return '\n'.join(lines), False

    else:
        return f"Unknown sub-command: {sub}\nUsage: range <add|remove|list|clear>", True


def _cmd_process(state, args, _root):
    if state.region == 'us':
        return lang.get('cli_use_us_process', state.lang_code), True

    if not state.pdf_path:
        return lang.get('cli_no_pdf', state.lang_code), True
    if not state.ranges:
        return lang.get('cli_no_ranges_proc', state.lang_code), True

    output_dir = os.path.join(state.temp_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)

    try:
        result = fba_engine.process_pdf(
            input_pdf=state.pdf_path,
            output_dir=output_dir,
            csv_path=state.csv_path,
            manual_ranges=state.ranges
        )
        state.job_result = result
        lines = [lang.get('cli_processing_done', state.lang_code).format(count=len(result['files']))]
        for i, fname in enumerate(result['files']):
            r = result['ranges'][i] if i < len(result['ranges']) else {}
            lines.append(f"  {fname}  [{r.get('start', '?')}-{r.get('end', '?')}] {r.get('title', '')}")
        if result.get('errors'):
            lines.append(f"Warnings: {'; '.join(result['errors'])}")
        return '\n'.join(lines), False
    except Exception as e:
        return f"Processing failed: {e}", True


def _cmd_us_pdf(state, args, _root):
    if not args:
        return f"Current US PDF: {state.pdf_path or '(none)'}\nUsage: us-pdf <absolute_path>", False
    path = args[0]
    ok, err = _validate_file(path, '.pdf')
    if not ok:
        return err, True
    state.pdf_path = path
    state.reset_job()
    return f"US PDF loaded: {path}", False


def _cmd_us_grid(state, args, _root):
    if not args:
        r, c = state.us_grid
        return f"Current grid: {r} rows x {c} cols\nUsage: us-grid <rows> <cols>", False
    if len(args) < 2:
        return "Usage: us-grid <rows> <cols>", True
    try:
        rows, cols = int(args[0]), int(args[1])
    except ValueError:
        return "Rows and cols must be integers", True
    state.us_grid = (rows, cols)
    state.reset_job()
    return f"Grid set to {rows} rows x {cols} cols", False


def _cmd_us_margin(state, args, _root):
    if not args:
        l, t, r, b = state.us_margin
        return f"Current margins: L={l} T={t} R={r} B={b} pt\nUsage: us-margin <left> <top> <right> <bottom>", False
    if len(args) < 4:
        return "Usage: us-margin <left> <top> <right> <bottom>", True
    try:
        margins = tuple(float(x) for x in args[:4])
    except ValueError:
        return "Margins must be numbers (pt)", True
    state.us_margin = margins
    state.reset_job()
    return f"Margins set to L={margins[0]} T={margins[1]} R={margins[2]} B={margins[3]} pt", False


def _cmd_us_process(state, args, _root):
    if state.region != 'us':
        return lang.get('cli_switch_us', state.lang_code), True
    if not state.pdf_path:
        return lang.get('cli_no_pdf', state.lang_code), True

    output_dir = os.path.join(state.temp_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    rows, cols = state.us_grid
    ml, mt, mr, mb = state.us_margin

    try:
        result = us_engine.process_sku_pdf(
            input_pdf=state.pdf_path,
            output_dir=output_dir,
            rows=rows, cols=cols,
            margin_l=ml, margin_t=mt, margin_r=mr, margin_b=mb
        )
        state.job_result = result
        lines = [lang.get('cli_us_done', state.lang_code).format(count=len(result['files']))]
        for i, fname in enumerate(result['files']):
            sku = result['skus'][i] if i < len(result.get('skus', [])) else '?'
            lines.append(f"  {fname}  (SKU: {sku})")
        if result.get('errors'):
            lines.append(f"Warnings: {'; '.join(result['errors'])}")
        return '\n'.join(lines), False
    except Exception as e:
        return f"US processing failed: {e}", True


def _cmd_status(state, args, _root):
    lines = [f"Session: {state.session_id}"]
    lines.append(f"Region:  {state.region.upper()}")
    lines.append(f"PDF:     {state.pdf_path or '(none)'}")
    if state.region != 'us':
        lines.append(f"CSV:     {state.csv_path or '(none)'}")
        lines.append(f"Ranges:  {len(state.ranges)} configured")
    else:
        r, c = state.us_grid
        l, t, right, b = state.us_margin
        lines.append(f"Grid:    {r} x {c}")
        lines.append(f"Margin:  L={l} T={t} R={right} B={b} pt")
    if state.job_result:
        lines.append(f"Result:  {len(state.job_result.get('files', []))} file(s) ready")
    return '\n'.join(lines), False


def _cmd_download(state, args, _root):
    if not state.job_result:
        return lang.get('cli_no_results', state.lang_code), True
    if not args:
        files = state.job_result.get('files', [])
        if not files:
            return "No files to download.", True
        lines = ["Available files:"]
        for i, f in enumerate(files):
            lines.append(f"  {i+1}. {f}")
        lines.append("Usage: download <filename>  or  download-all")
        return '\n'.join(lines), False
    # Download single file - just report the path
    fname = args[0]
    output_dir = os.path.join(state.temp_dir, 'output')
    fpath = os.path.join(output_dir, fname)
    if not os.path.exists(fpath):
        return f"File not found: {fname}\nUse 'download' without args to list files.", True
    # Copy to a stable location for download
    downloads_dir = os.path.join(state.temp_dir, 'downloads')
    os.makedirs(downloads_dir, exist_ok=True)
    dest = os.path.join(downloads_dir, fname)
    shutil.copy2(fpath, dest)
    return lang.get('cli_file_ready', state.lang_code).format(session_id=state.session_id, fname=fname), False


def _cmd_download_all(state, args, _root):
    if not state.job_result:
        return lang.get('cli_no_results', state.lang_code), True
    downloads_dir = os.path.join(state.temp_dir, 'downloads')
    os.makedirs(downloads_dir, exist_ok=True)
    zip_name = f"FBA_Labels_{state.session_id}.zip"
    zip_path = os.path.join(downloads_dir, zip_name)
    output_dir = os.path.join(state.temp_dir, 'output')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fname in state.job_result.get('files', []):
            fpath = os.path.join(output_dir, fname)
            if os.path.exists(fpath):
                zf.write(fpath, fname)
    return lang.get('cli_zip_ready', state.lang_code).format(session_id=state.session_id, zip_name=zip_name), False


def _cmd_history(state, args, _root):
    if not state.history:
        return lang.get('cli_no_history', state.lang_code), False
    lines = ["Command history:"]
    for i, h in enumerate(state.history[-20:]):
        lines.append(f"  {i+1}. {h}")
    return '\n'.join(lines), False


def _cmd_clear(state, args, _root):
    return "__CLEAR__", False


def _cmd_info(state, args, _root):
    return _cmd_status(state, args, _root)


# Command routing table
COMMANDS = {
    'help':         _cmd_help,
    'region':       _cmd_region,
    'pdf':          _cmd_pdf,
    'csv':          _cmd_csv,
    'range':        _cmd_range,
    'process':      _cmd_process,
    'us-pdf':       _cmd_us_pdf,
    'us-grid':      _cmd_us_grid,
    'us-margin':    _cmd_us_margin,
    'us-process':   _cmd_us_process,
    'status':       _cmd_status,
    'download':     _cmd_download,
    'download-all': _cmd_download_all,
    'history':      _cmd_history,
    'clear':        _cmd_clear,
    'info':         _cmd_info,
}

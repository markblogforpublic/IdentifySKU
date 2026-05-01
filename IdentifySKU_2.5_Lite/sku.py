#!/usr/bin/env python3
"""
SKU Label Splitter (Lite) — Claude Code-style CLI
=================================================
Regions: UK / AU / US • Bilingual: zh / en
"""

import os
import sys
import shutil
import atexit
from pathlib import Path

# readline is Unix-only; provide a stub on Windows
try:
    import readline
    _HAS_READLINE = True
except ImportError:
    _HAS_READLINE = False

import lang
import engine as proc_engine


# ═══════════════════════════════════════════════════════════════
#  ANSI colors (no external dependencies)
# ═══════════════════════════════════════════════════════════════

class Color:
    CYAN = "\033[36m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    RED = "\033[31m"
    DIM = "\033[2m"
    BOLD = "\033[1m"
    RESET = "\033[0m"
    CLEAR = "\033[2J\033[H"


def c(color, text):
    return f"{color}{text}{Color.RESET}"


# ═══════════════════════════════════════════════════════════════
#  State
# ═══════════════════════════════════════════════════════════════

class CLIState:
    def __init__(self):
        self.region = "uk"          # uk | au | us
        self.lang = "zh"            # zh | en
        self.pdf_path = None
        self.csv_path = None
        self.ranges = []            # [{title, start, end}]
        self.grid = (3, 2)          # rows, cols (US)
        self.margins = (0, 40, 0, 40)  # L, T, R, B pt (US)
        self.last_result = None
        self.output_dir = None      # set per-process

    def _(self, key, **kwargs):
        """Translate a key with format arguments."""
        text = lang.get(key, self.lang)
        if kwargs:
            return text.format(**kwargs)
        return text

    def out_dir(self):
        if not self.output_dir:
            base = Path.cwd() / "_sku_output"
            base.mkdir(exist_ok=True)
            self.output_dir = str(base)
        return self.output_dir


state = CLIState()


# ═══════════════════════════════════════════════════════════════
#  Progress callback
# ═══════════════════════════════════════════════════════════════

def on_progress(stage, current, total, message):
    """Display progress messages inline from the engine."""
    parts = message.split("|")
    key = parts[0]

    if key == "scan_page":
        emit(state._("scan_page", cur=parts[1], total=parts[2]))
    elif key == "skip_range":
        emit("  " + state._("skip_range", s=parts[1], e=parts[2], title=parts[3]),
             color="dim")
    elif key == "export_label":
        label = f"  {state._('export_label', i=parts[1], n=parts[2], title=parts[3], count=parts[4])}"
        if len(parts) > 6 and parts[6] == "FAIL":
            emit(label + " " + state._("verify_fail", order=parts[5]), color="red")
        else:
            emit(label + f" [{parts[5]}]", color="green")
    elif key == "verify_fail":
        emit("  " + state._("verify_fail", order=parts[1]), color="red")
    elif key == "us_scan_page":
        emit(state._("us_scan_page", cur=parts[1], total=parts[2]))
    elif key == "us_export_sku":
        emit("  " + state._("us_export_sku", i=parts[1], n=parts[2],
                            sku=parts[3], count=parts[4]), color="green")


def emit(text, color=None):
    """Print a line with optional color."""
    if color == "green":
        print(c(Color.GREEN, text))
    elif color == "red":
        print(c(Color.RED, text))
    elif color == "dim":
        print(c(Color.DIM, text))
    elif color == "cyan":
        print(c(Color.CYAN, text))
    elif color == "yellow":
        print(c(Color.YELLOW, text))
    else:
        print(text)


def _(key, **kwargs):
    return state._(key, **kwargs)


# ═══════════════════════════════════════════════════════════════
#  Command handlers
# ═══════════════════════════════════════════════════════════════

def cmd_help(args):
    """显示帮助 / Show help"""
    width = shutil.get_terminal_size((80, 20)).columns
    sep = "─" * width

    print(f"\n{c(Color.BOLD, 'SKU Label Splitter (Lite)')}  {c(Color.DIM, 'v1.0')}")
    print(c(Color.DIM, sep))
    print(f"  {c(Color.CYAN, '/region <uk|au|us>')}    {_('region_uk')} / {_('region_au')} / {_('region_us')}")
    print(f"  {c(Color.CYAN, '/pdf <path>')}           {_('pdf_loaded')}")
    print(f"  {c(Color.CYAN, '/csv <path>')}           {_('csv_loaded')} ({_('region_uk')}/{_('region_au')})")
    print(f"  {c(Color.CYAN, '/range <add|list|clear>')}  {_('status_ranges')} ({_('region_uk')}/{_('region_au')})")
    print(f"  {c(Color.CYAN, '/process')}              {_('processing_start')} ({_('region_uk')}/{_('region_au')})")
    print(f"  {c(Color.CYAN, '/grid <rows> <cols>')}   {_('grid_set')} ({_('region_us')})")
    print(f"  {c(Color.CYAN, '/margin <L> <T> <R> <B>')}  {_('margin_set')} ({_('region_us')})")
    print(f"  {c(Color.CYAN, '/us-process')}           US {_('processing_start')}")
    print(f"  {c(Color.CYAN, '/lang <zh|en>')}         {_('lang_set')}")
    print(f"  {c(Color.CYAN, '/status')}               {_('status_header')}")
    print(f"  {c(Color.CYAN, '/clear')}                Clear screen")
    print(f"  {c(Color.CYAN, '/exit')}                 Exit")
    print(c(Color.DIM, sep))
    print(f"  {c(Color.DIM, _('help_hint'))}\n")


def cmd_region(args):
    if not args:
        emit(f"  {_('status_region')}: {c(Color.CYAN, state.region.upper())}", color="dim")
        return
    r = args[0].lower()
    if r not in ("uk", "au", "us"):
        emit(_("region_invalid"), color="red")
        return
    state.region = r
    state.last_result = None
    emit(f"  {_('region_set')}: {c(Color.CYAN, r.upper())}", color="green")


def cmd_pdf(args):
    if not args:
        emit(f"  {_('status_pdf')}: {c(Color.DIM, state.pdf_path or _('status_none'))}", color="dim")
        return
    path = os.path.abspath(args[0])
    if not os.path.exists(path):
        emit(f"  {_('file_not_found')}: {path}", color="red")
        return
    if not path.lower().endswith(".pdf"):
        emit(_("invalid_type"), color="red")
        return
    state.pdf_path = path
    state.last_result = None
    emit(f"  {_('pdf_loaded')}: {c(Color.DIM, path)}", color="green")


def cmd_csv(args):
    if state.region == "us":
        emit(c(Color.YELLOW, "  CSV is only used for UK/AU mode"), color="yellow")
        return
    if not args:
        emit(f"  {_('status_csv')}: {c(Color.DIM, state.csv_path or _('status_none'))}", color="dim")
        return
    path = os.path.abspath(args[0])
    if not os.path.exists(path):
        emit(f"  {_('file_not_found')}: {path}", color="red")
        return
    ext = os.path.splitext(path)[1].lower()
    if ext not in (".csv", ".xlsx", ".xls"):
        emit(_("invalid_csv"), color="red")
        return
    state.csv_path = path

    # Auto-parse ranges
    try:
        if ext == ".csv":
            ranges = proc_engine.parse_ranges_from_csv(path)
        else:
            # Convert xlsx to csv first
            import openpyxl
            import tempfile
            wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
            ws = wb.active
            tmp_csv = os.path.join(tempfile.gettempdir(), "_sku_csv_import.csv")
            with open(tmp_csv, "w", encoding="utf-8", newline="") as f:
                csv_w = csv.writer(f)
                for row in ws.iter_rows(values_only=True):
                    csv_w.writerow([str(c) if c is not None else "" for c in row])
            wb.close()
            ranges = proc_engine.parse_ranges_from_csv(tmp_csv)
            os.unlink(tmp_csv)

        state.ranges = ranges or []
        emit(f"  {_('csv_loaded')}: {c(Color.DIM, path)}", color="green")
        if ranges:
            emit(f"  {_('ranges_parsed', count=len(ranges))}", color="cyan")
            for r in ranges:
                emit(f"    [{r['start']}-{r['end']}] {r.get('title', '')}", color="dim")
        else:
            emit(f"  {c(Color.YELLOW, _('no_ranges'))}", color="yellow")
    except Exception as e:
        state.ranges = []
        err_msg = f"{_('error')}: {e}"
        emit(f"  {c(Color.RED, err_msg)}", color="red")


def cmd_range(args):
    if state.region == "us":
        emit(c(Color.YELLOW, "  Ranges are only used for UK/AU mode"), color="yellow")
        return
    sub = args[0].lower() if args else "list"

    if sub == "add":
        if len(args) < 3:
            emit("  Usage: /range add <start> <end> [title]", color="yellow")
            return
        try:
            s, e = int(args[1]), int(args[2])
        except ValueError:
            emit("  Start and end must be integers", color="red")
            return
        title = args[3] if len(args) > 3 else f"{s}-{e}"
        state.ranges.append({"title": title, "start": s, "end": e})
        state.ranges.sort(key=lambda x: x["start"])
        state.last_result = None
        emit(f"  {_('range_added', s=s, e=e, title=title, total=len(state.ranges))}",
             color="green")

    elif sub == "remove":
        if len(args) < 2:
            emit("  Usage: /range remove <index>", color="yellow")
            return
        try:
            idx = int(args[1]) - 1
        except ValueError:
            emit("  Index must be an integer (1-based)", color="red")
            return
        if idx < 0 or idx >= len(state.ranges):
            emit(f"  Index out of range (1-{len(state.ranges)})", color="red")
            return
        removed = state.ranges.pop(idx)
        emit(f"  {_('range_removed', s=removed['start'], e=removed['end'], title=removed.get('title', ''))}",
             color="green")

    elif sub == "clear":
        state.ranges = []
        state.last_result = None
        emit(f"  {_('ranges_cleared')}", color="green")

    elif sub == "list":
        if not state.ranges:
            emit(f"  {c(Color.DIM, _('no_ranges'))}", color="dim")
            return
        emit(f"  {_('status_ranges')} ({len(state.ranges)}):", color="cyan")
        for i, r in enumerate(state.ranges):
            emit(f"    {i+1}. [{r['start']}-{r['end']}] {r.get('title', '')}", color="dim")

    else:
        emit(f"  Unknown: {sub}. Use: add, list, remove, clear", color="yellow")


def cmd_process(args):
    if state.region == "us":
        emit(f"  {c(Color.YELLOW, 'Use /us-process for US mode')}", color="yellow")
        return
    if not state.pdf_path:
        emit(f"  {_('no_pdf')}", color="red")
        return
    if not state.ranges:
        emit(f"  {_('no_ranges_proc')}", color="red")
        return

    out_dir = state.out_dir()
    emit(f"  {_('processing_start')}", color="cyan")

    try:
        result = proc_engine.process_uk_au(
            input_pdf=state.pdf_path,
            output_dir=out_dir,
            csv_path=state.csv_path,
            manual_ranges=state.ranges,
            on_progress=on_progress,
        )
        state.last_result = result
        emit(f"  {_('processing_done', count=len(result['files']))}", color="green")
        for fname in result["files"]:
            fpath = os.path.join(out_dir, fname)
            size = os.path.getsize(fpath)
            emit(f"    {c(Color.DIM, fname)} ({_format_size(size)})", color="dim")
        if result.get("errors"):
            emit(f"  {c(Color.YELLOW, '; '.join(result['errors']))}", color="yellow")
    except Exception as e:
        emit(f"  {_('processing_fail')}: {e}", color="red")
        import traceback
        traceback.print_exc()


def cmd_us_process(args):
    if state.region != "us":
        emit(f"  {c(Color.YELLOW, 'Switch to US mode first: /region us')}", color="yellow")
        return
    if not state.pdf_path:
        emit(f"  {_('no_pdf')}", color="red")
        return

    out_dir = state.out_dir()
    rows, cols = state.grid
    ml, mt, mr, mb = state.margins
    emit(f"  {_('processing_start')}", color="cyan")

    try:
        result = proc_engine.process_us(
            input_pdf=state.pdf_path,
            output_dir=out_dir,
            rows=rows, cols=cols,
            margin_l=ml, margin_t=mt, margin_r=mr, margin_b=mb,
            on_progress=on_progress,
        )
        state.last_result = result
        emit(f"  {_('us_done', count=len(result['files']))}", color="green")
        for fname in result["files"]:
            fpath = os.path.join(out_dir, fname)
            size = os.path.getsize(fpath)
            emit(f"    {c(Color.DIM, fname)} ({_format_size(size)})", color="dim")
        if result.get("errors"):
            emit(f"  {c(Color.YELLOW, '; '.join(result['errors']))}", color="yellow")
    except Exception as e:
        emit(f"  {_('processing_fail')}: {e}", color="red")
        import traceback
        traceback.print_exc()


def cmd_grid(args):
    if not args:
        r, c = state.grid
        emit(f"  {_('status_grid')}: {r}x{c}", color="dim")
        return
    if len(args) < 2:
        emit("  Usage: /grid <rows> <cols>", color="yellow")
        return
    try:
        rows, cols = int(args[0]), int(args[1])
    except ValueError:
        emit("  Rows and cols must be integers", color="red")
        return
    state.grid = (rows, cols)
    emit(f"  {_('grid_set', rows=rows, cols=cols)}", color="green")


def cmd_margin(args):
    if not args:
        l, t, r, b = state.margins
        emit(f"  {_('status_margins')}: L={l} T={t} R={r} B={b}", color="dim")
        return
    if len(args) < 4:
        emit("  Usage: /margin <left> <top> <right> <bottom>", color="yellow")
        return
    try:
        margins = tuple(float(x) for x in args[:4])
    except ValueError:
        emit("  Margins must be numbers (pt)", color="red")
        return
    state.margins = margins
    emit(f"  {_('margin_set', l=margins[0], t=margins[1], r=margins[2], b=margins[3])}",
         color="green")


def cmd_lang(args):
    if not args:
        emit(f"  Lang: {state.lang}", color="dim")
        return
    l = args[0].lower()
    if l not in ("zh", "en"):
        emit(_("lang_invalid"), color="red")
        return
    state.lang = l
    emit(c(Color.GREEN, f"  {_('lang_set')}"), color="green")


def cmd_status(args):
    sep = c(Color.DIM, "─" * 40)
    emit(f"\n  {c(Color.BOLD, _('status_header'))}")
    emit(sep)
    emit(f"  {_('status_region')}:  {c(Color.CYAN, state.region.upper())}")
    emit(f"  {_('status_lang')}:    {c(Color.CYAN, state.lang)}")
    emit(f"  {_('status_pdf')}:     {c(Color.DIM, state.pdf_path or _('status_none'))}")
    if state.region != "us":
        emit(f"  {_('status_csv')}:     {c(Color.DIM, state.csv_path or _('status_none'))}")
        emit(f"  {_('status_ranges')}:  {c(Color.CYAN, str(len(state.ranges)))}")
    else:
        r, c = state.grid
        l, t, r2, b = state.margins
        emit(f"  {_('status_grid')}:    {c(Color.CYAN, f'{r}x{c}')}")
        emit(f"  {_('status_margins')}: {c(Color.CYAN, f'L={l} T={t} R={r2} B={b}')}")
    if state.last_result:
        n = len(state.last_result.get("files", []))
        emit(f"  {_('status_result')}:  {c(Color.GREEN, _('status_files', n=n))}")
    emit(sep + "\n")


def cmd_clear(args):
    print(Color.CLEAR, end="")


# ═══════════════════════════════════════════════════════════════
#  Command dispatch table
# ═══════════════════════════════════════════════════════════════

COMMANDS = {
    "help": cmd_help,
    "h": cmd_help,
    "region": cmd_region,
    "pdf": cmd_pdf,
    "csv": cmd_csv,
    "range": cmd_range,
    "process": cmd_process,
    "proc": cmd_process,
    "grid": cmd_grid,
    "margin": cmd_margin,
    "us-process": cmd_us_process,
    "usproc": cmd_us_process,
    "lang": cmd_lang,
    "status": cmd_status,
    "info": cmd_status,
    "clear": cmd_clear,
    "cls": cmd_clear,
    "exit": lambda a: sys.exit(0),
    "quit": lambda a: sys.exit(0),
}


# ═══════════════════════════════════════════════════════════════
#  Tab completion
# ═══════════════════════════════════════════════════════════════

COMPLETIONS = [
    "/help", "/region", "/pdf", "/csv", "/range",
    "/process", "/grid", "/margin", "/us-process",
    "/lang", "/status", "/clear", "/exit", "/quit",
]

def completer(text, state_index):
    text = text.lower()
    # Strip the leading / for matching
    options = [c for c in COMPLETIONS if c.startswith(text)]
    if state_index < len(options):
        return options[state_index]
    return None


# ═══════════════════════════════════════════════════════════════
#  REPL (Read-Eval-Print Loop)
# ═══════════════════════════════════════════════════════════════

def repl():
    """Main REPL loop — Claude Code-style interactive CLI."""

    if _HAS_READLINE:
        readline.set_completer(completer)
        readline.parse_and_bind("tab: complete")
        readline.set_completer_delims(" \t\n")

        # Persistent history file
        hist_file = os.path.join(str(Path.home()), ".sku_cli_history")
        try:
            readline.read_history_file(hist_file)
        except FileNotFoundError:
            pass
        atexit.register(readline.write_history_file, hist_file)

    # Welcome
    width = shutil.get_terminal_size((80, 20)).columns
    sep = c(Color.DIM, "═" * width)
    print(f"\n{sep}")
    title = f"  {c(Color.BOLD, _('welcome_title'))}  {c(Color.DIM, 'v1.0')}"
    print(title)
    print(f"  {c(Color.DIM, _('welcome_hint'))}")
    print(f"  {c(Color.DIM, f'Region: {state.region.upper()}  |  Lang: {state.lang}')}")
    print(f"{sep}\n")

    # Main loop
    while True:
        try:
            prompt = c(Color.CYAN, "sku") + c(Color.DIM, "> ")
            line = input(prompt).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            emit(f"  {c(Color.DIM, _('goodbye'))}")
            break

        if not line:
            continue

        # Normalize: allow both /command and command (without slash)
        cmd_text = line
        if cmd_text.startswith("/"):
            cmd_text = cmd_text[1:]

        parts = _parse_cmd(cmd_text)
        if not parts:
            continue

        cmd_name = parts[0].lower()
        cmd_args = parts[1:]

        handler = COMMANDS.get(cmd_name)
        if handler:
            handler(cmd_args)
            print()
        else:
            emit(f"  {c(Color.RED, _('unknown_cmd'))}: {cmd_name}")
            emit(f"  {c(Color.DIM, _('help_hint'))}\n")


def _parse_cmd(text):
    """Split into tokens, respecting quotes."""
    tokens = []
    current = ""
    in_quote = False
    for ch in text:
        if ch == '"':
            in_quote = not in_quote
        elif ch == " " and not in_quote:
            if current:
                tokens.append(current)
                current = ""
        else:
            current += ch
    if current:
        tokens.append(current)
    return tokens


# ═══════════════════════════════════════════════════════════════
#  Utilities
# ═══════════════════════════════════════════════════════════════

def _format_size(size_bytes):
    """Human-readable file size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


# ═══════════════════════════════════════════════════════════════
#  Entry point
# ═══════════════════════════════════════════════════════════════

def main():
    """Entry point. Supports both interactive REPL and one-shot commands."""
    if len(sys.argv) > 1:
        # One-shot mode: python sku.py <command>
        # Useful for batch scripts
        full_cmd = " ".join(sys.argv[1:])
        cmd_text = full_cmd
        if cmd_text.startswith("/"):
            cmd_text = cmd_text[1:]
        parts = _parse_cmd(cmd_text)
        if parts:
            cmd_name = parts[0].lower()
            cmd_args = parts[1:]
            handler = COMMANDS.get(cmd_name)
            if handler:
                handler(cmd_args)
            else:
                emit(f"  {c(Color.RED, _('unknown_cmd'))}: {cmd_name}")
    else:
        # Interactive REPL
        repl()


if __name__ == "__main__":
    main()

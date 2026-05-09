"""
FBA Label Splitter V2.6 Redesigned 1 — Web Backend
Start: python app.py  /  python start.py
"""
import os, sys, json, shutil, uuid, threading, zipfile, io, csv
import logging
from collections import deque

logger = logging.getLogger(__name__)

# Determine base directory (compatible with EXE packaging)
if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

from datetime import datetime, timedelta
from functools import wraps
from flask import Flask, request, jsonify, send_file, render_template, session, g
import main as fba_engine
import us_engine
import config_manager as cfg
import cli_engine
import lang

# Template directory: read from sys._MEIPASS in EXE mode, relative path in dev
_template_dir = os.path.join(BASE_DIR, 'templates')
if getattr(sys, 'frozen', False):
    meipass = getattr(sys, '_MEIPASS', BASE_DIR)
    _template_dir = os.path.join(meipass, 'templates')

app = Flask(__name__, template_folder=_template_dir)
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024

# Load runtime config
_runtime_config = cfg.load_config()
app.config['LOGIN_REQUIRED'] = _runtime_config.get('login_required', False)
app.config['CLI_MODE'] = _runtime_config.get('cli_mode', False)
app.config['SERVER_PORT'] = _runtime_config.get('port', 5000)
app.secret_key = os.urandom(24)  # session encryption
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=30)

TEMP_DIR = os.path.join(BASE_DIR, 'temp_jobs')
os.makedirs(TEMP_DIR, exist_ok=True)

jobs = {}
JOB_TTL = timedelta(hours=1)


def cleanup_old_jobs():
    now = datetime.now()
    expired = [jid for jid, j in jobs.items() if now - j['created'] > JOB_TTL]
    for jid in expired:
        job_dir = os.path.join(TEMP_DIR, jid)
        if os.path.exists(job_dir): shutil.rmtree(job_dir, ignore_errors=True)
        jobs.pop(jid, None)


def _create_job(temp_dir, pdf_file, pdf_filename=None):
    """Set up job directory, save PDF, init jobs dict. Returns (job_id, job_dir, output_dir, pdf_path)."""
    job_id = str(uuid.uuid4())[:8]
    job_dir = os.path.join(temp_dir, job_id)
    os.makedirs(job_dir, exist_ok=True)
    pdf_path = os.path.join(job_dir, pdf_filename or pdf_file.filename)
    pdf_file.save(pdf_path)
    output_dir = os.path.join(job_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    jobs[job_id] = {
        "created": datetime.now(),
        "status": "processing",
        "progress": {"stage": "scan", "current": 0, "total": 0, "message": "准备中..."},
        "result": None, "error": None
    }
    return job_id, job_dir, output_dir, pdf_path


def _make_on_progress(job_id):
    """Return an on_progress callback that updates jobs[job_id]['progress']."""
    def on_progress(stage, current, total, message):
        jobs[job_id]["progress"] = {"stage": stage, "current": current, "total": total, "message": message}
    return on_progress


def xlsx_to_csv(xlsx_path):
    """Convert the first worksheet of XLSX/XLS to CSV, return the CSV file path."""
    import openpyxl
    csv_path = xlsx_path.rsplit('.', 1)[0] + '.csv'
    wb = openpyxl.load_workbook(xlsx_path, read_only=True, data_only=True)
    ws = wb.active
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for row in ws.iter_rows(values_only=True):
            writer.writerow([str(c) if c is not None else '' for c in row])
    wb.close()
    return csv_path


# ═══════════════════════════════════════════════════
#  Security utilities
# ═══════════════════════════════════════════════════

import re as _re

def _safe_path(base_dir, filename):
    """Prevent path traversal: ensure the resulting path stays within base_dir."""
    requested = os.path.realpath(os.path.join(base_dir, filename))
    base_real = os.path.realpath(base_dir)
    if not requested.startswith(base_real + os.sep) and requested != base_real:
        return None
    return requested

def _sanitize_filename(name):
    """Remove dangerous characters like path separators."""
    return _re.sub(r'[\\/:*?"<>|]', '_', os.path.basename(name))

def _validate_username(username):
    """Validate username: 1-32 chars, alphanumeric and underscore only."""
    if not username or len(username) > 32:
        return False
    return bool(_re.match(r'^[a-zA-Z0-9_]+$', username))

# Simple rate limiting
_rate_limits = {}
def _check_rate_limit(key, max_req=30, window_sec=60):
    """Sliding window rate limiter using deque. Returns True to allow."""
    now = datetime.now()
    if key not in _rate_limits:
        _rate_limits[key] = deque()
    window = now - timedelta(seconds=window_sec)
    q = _rate_limits[key]
    while q and q[0] < window:
        q.popleft()
    if len(q) >= max_req:
        return False
    q.append(now)
    return True


@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Cache-Control'] = 'no-store'
    response.headers['Content-Security-Policy'] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.tailwindcss.com https://unpkg.com; "
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
        "img-src 'self' data:; "
        "connect-src 'self' https://api.ipify.org; "
        "font-src 'self' https://fonts.gstatic.com; "
        "frame-ancestors 'none'; "
        "base-uri 'self'; "
        "form-action 'self'"
    )
    return response


# ============================================================
#  Authentication system
# ============================================================

def require_auth(f):
    """Decorator: require login if authentication is enabled."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if app.config['LOGIN_REQUIRED'] and 'user' not in session:
            return jsonify({"error": lang.get('api_login_required', g.lang), "code": "LOGIN_REQUIRED"}), 401
        return f(*args, **kwargs)
    return decorated


def get_current_permissions():
    """Return permissions for the current session; defaults to full access if not logged in."""
    if not app.config['LOGIN_REQUIRED'] or 'user' not in session:
        return {"cli": True, "regions": ["uk", "au", "us"]}
    return session.get('permissions', {"cli": False, "regions": []})


@app.before_request
def detect_language():
    g.lang = request.args.get('lang', '')
    if g.lang not in ('zh', 'en', 'ja'):
        g.lang = request.accept_languages.best_match(['zh', 'en', 'ja']) or 'zh'


@app.route('/api/login', methods=['POST'])
def api_login():
    lang_code = g.lang
    # Rate limit: max 10 attempts per IP per minute
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr) or 'unknown'
    if not _check_rate_limit(f'login:{client_ip}', max_req=10, window_sec=60):
        return jsonify({"error": lang.get('login_error_too_many', lang_code)}), 429

    data = request.get_json(silent=True) or {}
    username = (data.get('username') or '').strip()
    password = data.get('password', '') if isinstance(data.get('password'), str) else ''

    if not _validate_username(username):
        return jsonify({"error": lang.get('login_error_invalid_user', lang_code)}), 400
    if len(password) > 128:
        return jsonify({"error": "密码过长"}), 400

    perms = cfg.authenticate(username, password)
    if perms is None:
        return jsonify({"error": lang.get('login_error_wrong', lang_code)}), 401
    session['user'] = username
    session['permissions'] = perms
    # "Remember me": persist cookie for 30 days
    if data.get('remember'):
        session.permanent = True
    return jsonify({"username": username, "permissions": perms})


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({"ok": True})


@app.route('/api/session')
def api_session():
    if 'user' not in session:
        return jsonify({"logged_in": False})
    return jsonify({
        "logged_in": True,
        "username": session['user'],
        "permissions": session.get('permissions', {})
    })


# ============================================================
#  UK/AU FBA Label Processing
# ============================================================

@app.route('/')
def index():
    lang_code = g.lang
    lang_strings_zh = lang.get_all('zh')
    lang_strings_en = lang.get_all('en')
    lang_strings_ja = lang.get_all('ja')
    return render_template('index.html',
        login_required=app.config['LOGIN_REQUIRED'],
        cli_mode=app.config['CLI_MODE'],
        lang_strings_zh=lang_strings_zh,
        lang_strings_en=lang_strings_en,
        lang_strings_ja=lang_strings_ja,
        lang=lang_code)


@app.route('/api/config')
def api_config():
    """Return current runtime config (for frontend consumption)."""
    return jsonify({
        "login_required": app.config['LOGIN_REQUIRED'],
        "cli_mode": app.config['CLI_MODE']
    })


@app.route('/api/process', methods=['POST'])
def api_process():
    lang_code = g.lang
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr) or 'unknown'
    if not _check_rate_limit(f'process:{client_ip}', max_req=10, window_sec=60):
        return jsonify({"error": lang.get('api_too_many_req', lang_code)}), 429
    cleanup_old_jobs()
    pdf_file = request.files.get('pdf')
    csv_file = request.files.get('csv')
    manual_ranges = None
    manual_raw = request.form.get('ranges')
    if manual_raw:
        try: manual_ranges = json.loads(manual_raw)
        except json.JSONDecodeError: pass
    if not pdf_file or not pdf_file.filename:
        return jsonify({"error": lang.get('api_no_pdf', lang_code)}), 400
    if not manual_ranges and (not csv_file or not csv_file.filename):
        return jsonify({"error": lang.get('api_no_ranges', lang_code), "code": "NO_RANGES"}), 400

    job_id, job_dir, output_dir, pdf_path = _create_job(TEMP_DIR, pdf_file)
    csv_path = None
    if csv_file and csv_file.filename:
        csv_path = os.path.join(job_dir, csv_file.filename)
        csv_file.save(csv_path)
        # If it's an Excel format, auto-convert to CSV
        ext = os.path.splitext(csv_file.filename)[1].lower()
        if ext in ('.xlsx', '.xls'):
            try:
                csv_path = xlsx_to_csv(csv_path)
            except Exception as e:
                jobs[job_id]["status"] = "error"
                jobs[job_id]["error"] = f"{lang.get('api_xlsx_failed', lang_code)}：{e}"
                return jsonify({"error": f"{lang.get('api_xlsx_failed', lang_code)}：{e}"}), 400

    on_progress = _make_on_progress(job_id)

    def run_processing():
        try:
            result = fba_engine.process_pdf(input_pdf=pdf_path, output_dir=output_dir,
                csv_path=csv_path, manual_ranges=manual_ranges, on_progress=on_progress)
            jobs[job_id]["status"] = "done"
            jobs[job_id]["result"] = {"files": result["files"], "ranges": result["ranges"],
                "source": result["source"], "errors": result["errors"], "job_id": job_id}
        except Exception as e:
            jobs[job_id]["status"] = "error"; jobs[job_id]["error"] = str(e)

    threading.Thread(target=run_processing, daemon=True).start()
    return jsonify({"job_id": job_id, "status": "processing"})


@app.route('/api/preview-csv', methods=['POST'])
def api_preview_csv():
    """Upload Excel/CSV file, return parsed label ranges for frontend preview."""
    lang_code = g.lang
    upload_file = request.files.get('file')
    if not upload_file or not upload_file.filename:
        return jsonify({"error": lang.get('api_upload_file', lang_code)}), 400
    fname = upload_file.filename.lower()
    job_id = str(uuid.uuid4())[:8]
    job_dir = os.path.join(TEMP_DIR, f'preview_{job_id}')
    os.makedirs(job_dir, exist_ok=True)
    saved_path = os.path.join(job_dir, upload_file.filename)
    upload_file.save(saved_path)
    ext = os.path.splitext(fname)[1]
    try:
        if ext in ('.xlsx', '.xls'):
            csv_path = xlsx_to_csv(saved_path)
        else:
            csv_path = saved_path
        ranges = fba_engine.parse_ranges_from_csv(csv_path)
        return jsonify({"ranges": ranges})
    except Exception as e:
        return jsonify({"error": f"{lang.get('api_parse_failed', lang_code)}：{e}"}), 400
    finally:
        shutil.rmtree(job_dir, ignore_errors=True)


@app.route('/api/progress/<job_id>')
def api_progress(job_id):
    job = jobs.get(job_id)
    if not job: return jsonify({"error": lang.get('api_job_expired', g.lang)}), 404
    return jsonify({"status": job["status"], "progress": job["progress"], "result": job["result"], "error": job["error"]})


@app.route('/api/download/<job_id>/<filename>')
def api_download(job_id, filename):
    # Validate job_id format (hex only, prevent path traversal)
    if not _re.match(r'^[a-fA-F0-9_-]+$', job_id):
        return jsonify({"error": lang.get('api_invalid_job_id', g.lang)}), 400
    safe_name = _sanitize_filename(filename)
    base = os.path.join(TEMP_DIR, job_id, 'output')
    file_path = _safe_path(base, safe_name)
    if not file_path or not os.path.isfile(file_path):
        return jsonify({"error": lang.get('api_file_not_found', g.lang)}), 404
    return send_file(file_path, as_attachment=True, download_name=safe_name)


@app.route('/api/download-all/<job_id>')
def api_download_all(job_id):
    if not _re.match(r'^[a-fA-F0-9_-]+$', job_id):
        return jsonify({"error": lang.get('api_invalid_job_id', g.lang)}), 400
    job = jobs.get(job_id)
    if not job or not job.get("result"): return jsonify({"error": lang.get('api_job_expired', g.lang)}), 404
    output_dir = os.path.join(TEMP_DIR, job_id, 'output')
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fname in job["result"]["files"]:
            safe_name = _sanitize_filename(fname)
            fpath = _safe_path(output_dir, safe_name)
            if fpath and os.path.exists(fpath):
                zf.write(fpath, safe_name)
    buf.seek(0)
    return send_file(buf, mimetype='application/zip', as_attachment=True,
                     download_name=f"FBA_Labels_{job_id}.zip")


# ============================================================
#  US TransferSKU Processing
# ============================================================

@app.route('/api/us-process', methods=['POST'])
def api_us_process():
    lang_code = g.lang
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr) or 'unknown'
    if not _check_rate_limit(f'process:{client_ip}', max_req=10, window_sec=60):
        return jsonify({"error": lang.get('api_too_many_req', lang_code)}), 429
    cleanup_old_jobs()
    pdf_file = request.files.get('pdf')
    if not pdf_file or not pdf_file.filename:
        return jsonify({"error": lang.get('api_no_pdf_us', lang_code)}), 400
    rows, cols = int(request.form.get('rows', 3)), int(request.form.get('cols', 2))
    ml, mt = float(request.form.get('ml', 0)), float(request.form.get('mt', 40))
    mr, mb = float(request.form.get('mr', 0)), float(request.form.get('mb', 40))
    if ml < 0 or mt < 0 or mr < 0 or mb < 0:
        return jsonify({"error": "Margins cannot be negative"}), 400
    if ml > 1000 or mt > 1000 or mr > 1000 or mb > 1000:
        return jsonify({"error": "Margins exceed maximum (1000pt)"}), 400

    job_id, job_dir, output_dir, pdf_path = _create_job(TEMP_DIR, pdf_file)
    on_progress = _make_on_progress(job_id)

    def run_us():
        try:
            result = us_engine.process_sku_pdf(input_pdf=pdf_path, output_dir=output_dir,
                rows=rows, cols=cols, margin_l=ml, margin_t=mt, margin_r=mr, margin_b=mb,
                on_progress=on_progress)
            jobs[job_id]["status"] = "done"
            jobs[job_id]["result"] = {"files": result["files"], "skus": result["skus"],
                "errors": result["errors"], "job_id": job_id, "source": "US TransferSKU"}
        except Exception as e:
            jobs[job_id]["status"] = "error"; jobs[job_id]["error"] = str(e)

    threading.Thread(target=run_us, daemon=True).start()
    return jsonify({"job_id": job_id, "status": "processing"})


# ============================================================
#  CLI command-line mode
# ============================================================

@app.route('/api/cli', methods=['POST'])
def api_cli():
    """Execute CLI command. Body: {session_id, command}"""
    data = request.get_json(silent=True) or {}
    sid = (data.get('session_id') or 'default').strip()
    command = (data.get('command') or '').strip()

    # Security check
    if not _re.match(r'^[a-zA-Z0-9_-]+$', sid):
        return jsonify({"output": "Invalid session ID", "error": True}), 400
    if len(command) > 2000:
        return jsonify({"output": "Command too long (max 2000 chars)", "error": True}), 400
    if not command:
        return jsonify({"output": "", "error": False})

    # Rate limiting
    client_ip = request.headers.get('X-Forwarded-For', request.remote_addr) or 'unknown'
    if not _check_rate_limit(f'cli:{client_ip}', max_req=60, window_sec=60):
        return jsonify({"output": "Rate limit exceeded. Please slow down.", "error": True}), 429

    # CLI state directory
    cli_temp = os.path.join(TEMP_DIR, 'cli_sessions')
    os.makedirs(cli_temp, exist_ok=True)

    output, is_error = cli_engine.execute(command, sid, cli_temp, g.lang)
    return jsonify({"output": output, "error": is_error})


@app.route('/api/cli-download/<session_id>/<filename>')
def api_cli_download(session_id, filename):
    if not _re.match(r'^[a-fA-F0-9_-]+$', session_id):
        return jsonify({"error": lang.get('api_invalid_session', g.lang)}), 400
    safe_name = _sanitize_filename(filename)
    base = os.path.join(TEMP_DIR, 'cli_sessions', session_id, 'downloads')
    file_path = _safe_path(base, safe_name)
    if not file_path or not os.path.isfile(file_path):
        return jsonify({"error": lang.get('api_file_not_found', g.lang)}), 404
    return send_file(file_path, as_attachment=True, download_name=filename)


# ============================================================
#  User Info & Logging
# ============================================================

LOG_FILE = os.path.join(BASE_DIR, 'process_log.json')

def _read_logs():
    if not os.path.exists(LOG_FILE): return []
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except Exception: return []

def _write_log(entry):
    logs = _read_logs(); logs.insert(0, entry)
    if len(logs) > 100: logs = logs[:100]
    with open(LOG_FILE, 'w', encoding='utf-8') as f: json.dump(logs, f, ensure_ascii=False, indent=2)

@app.route('/api/user-info')
def api_user_info():
    ip = request.headers.get('X-Forwarded-For', request.remote_addr) or 'unknown'
    return jsonify({"ip": ip, "user_agent": request.headers.get('User-Agent', ''), "accept_language": request.headers.get('Accept-Language', '')})

@app.route('/api/log', methods=['GET', 'POST', 'DELETE'])
def api_log():
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        _write_log({"time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "source": data.get("source", ""),
            "files": data.get("files", 0), "ranges": data.get("ranges", 0), "files_list": data.get("files_list", "")})
        return jsonify({"ok": True})
    elif request.method == 'DELETE':
        if os.path.exists(LOG_FILE): os.remove(LOG_FILE)
        return jsonify({"ok": True})
    return jsonify(_read_logs())


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    port = app.config['SERVER_PORT']
    public = _runtime_config.get('public_access', False)
    host = '0.0.0.0' if public else '127.0.0.1'
    bind_info = f"http://0.0.0.0:{port} (public)" if public else f"http://localhost:{port}"
    logger.info("=" * 50)
    logger.info("  FBA Label Splitter V2.6 Redesigned 1")
    logger.info("  %s", bind_info)
    logger.info("=" * 50)
    app.run(host=host, debug=False, port=port)

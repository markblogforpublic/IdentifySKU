"""
FBA Label Splitter V2.5 — Launcher
Double-click to start the server + auto-open browser
Includes advanced settings: port/account management/CLI mode
"""
import os, sys, threading, webbrowser, time
import subprocess

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)
sys.path.insert(0, BASE_DIR)

try:
    import customtkinter as ctk
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter", "--break-system-packages"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    import customtkinter as ctk

import config_manager as cfg
import lang

flask_thread = None
server_running = False
config = cfg.load_config()
PORT = config.get('port', 5000)


def run_flask():
    global server_running
    try:
        config = cfg.load_config()
        host = '0.0.0.0' if config.get('public_access', False) else '127.0.0.1'
        import app as web_app
        web_app.app.config['TEMPLATE_FOLDER'] = os.path.join(BASE_DIR, 'templates')
        web_app.app.run(host=host, port=PORT, debug=False, use_reloader=False)
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        server_running = False


# ═══════════════════════════════════════════════════
#  First run — force set root password
# ═══════════════════════════════════════════════════

def check_first_run():
    """If root password is empty, show a mandatory setup dialog. Returns True on completion."""
    users = cfg.load_users()
    root = users.get('root', {})
    if root.get('password', '') == '':
        return show_root_setup()
    return True


def show_root_setup():
    """First run: force set root admin password. Cannot be skipped."""
    dialog = ctk.CTkToplevel()
    dialog.title(lang.get('launcher_first_run_title', 'zh'))
    dialog.geometry("440x340")
    dialog.resizable(False, False)
    dialog.attributes('-topmost', True)
    dialog.grab_set()  # modal
    result = {"done": False}

    def center():
        dialog.update_idletasks()
        sw, sh = dialog.winfo_screenwidth(), dialog.winfo_screenheight()
        dialog.geometry(f"+{(sw-440)//2}+{(sh-340)//2}")

    center()

    ctk.CTkLabel(dialog, text=lang.get('launcher_first_run_heading', 'zh'), font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(30, 5))
    ctk.CTkLabel(dialog, text=lang.get('launcher_first_run_welcome', 'zh'),
                 font=ctk.CTkFont(size=13)).pack()
    ctk.CTkLabel(dialog, text=lang.get('launcher_first_run_desc', 'zh'),
                 font=ctk.CTkFont(size=11), text_color="#6B7280").pack(pady=(8, 20))

    pwd_frame = ctk.CTkFrame(dialog, fg_color="transparent")
    pwd_frame.pack(padx=40, fill="x")
    ctk.CTkLabel(pwd_frame, text=lang.get('launcher_first_run_new_pwd', 'zh'), font=ctk.CTkFont(size=12)).pack(anchor="w")
    pwd_entry = ctk.CTkEntry(pwd_frame, show="*", height=36, font=ctk.CTkFont(size=13))
    pwd_entry.pack(fill="x", pady=(4, 10))
    ctk.CTkLabel(pwd_frame, text=lang.get('launcher_first_run_confirm', 'zh'), font=ctk.CTkFont(size=12)).pack(anchor="w")
    confirm_entry = ctk.CTkEntry(pwd_frame, show="*", height=36, font=ctk.CTkFont(size=13))
    confirm_entry.pack(fill="x", pady=(4, 4))

    error_label = ctk.CTkLabel(dialog, text="", font=ctk.CTkFont(size=11), text_color="#EF4444")
    error_label.pack(pady=(8, 0))

    def do_setup():
        pwd = pwd_entry.get()
        confirm = confirm_entry.get()
        if len(pwd) < 4:
            error_label.configure(text=lang.get('launcher_first_run_short', 'zh'))
            return
        if pwd != confirm:
            error_label.configure(text=lang.get('launcher_first_run_mismatch', 'zh'))
            return
        cfg.update_user("root", password=pwd)
        result["done"] = True
        dialog.destroy()

    ctk.CTkButton(dialog, text=lang.get('launcher_first_run_btn', 'zh'), height=42, corner_radius=21,
                  font=ctk.CTkFont(size=14, weight="bold"),
                  fg_color="#4F46E5", hover_color="#4338CA",
                  command=do_setup).pack(padx=40, pady=(20, 10), fill="x")

    pwd_entry.bind('<Return>', lambda e: confirm_entry.focus_set())
    confirm_entry.bind('<Return>', lambda e: do_setup())
    dialog.protocol("WM_DELETE_WINDOW", lambda: None)  # prevent closing
    dialog.wait_window()
    return result["done"]


# ═══════════════════════════════════════════════════
#  User management dialog
# ═══════════════════════════════════════════════════

class UserDialog:
    """Add/Edit user dialog"""
    def __init__(self, parent, mode='add', username=''):
        self.result = None
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(lang.get('userdlg_add_title', 'zh') if mode == 'add' else lang.get('userdlg_edit_title', 'zh') + username)
        self.dialog.geometry("400x450")
        self.dialog.resizable(False, False)
        self.dialog.attributes('-topmost', True)
        self.dialog.grab_set()

        self.mode = mode
        self.editing = username

        self._center()
        self._build(mode, username)

    def _center(self):
        self.dialog.update_idletasks()
        sw = self.dialog.winfo_screenwidth()
        sh = self.dialog.winfo_screenheight()
        self.dialog.geometry(f"+{(sw-400)//2}+{(sh-450)//2}")

    def _build(self, mode, username):
        padx = 30

        ctk.CTkLabel(self.dialog, text=lang.get('userdlg_info', 'zh'),
                     font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(25, 20))

        # Username
        ctk.CTkLabel(self.dialog, text=lang.get('userdlg_username', 'zh'), font=ctk.CTkFont(size=12),
                     anchor="w").pack(padx=padx, fill="x")
        self.user_entry = ctk.CTkEntry(self.dialog, height=36, font=ctk.CTkFont(size=13))
        self.user_entry.pack(padx=padx, fill="x", pady=(4, 10))
        if mode == 'edit':
            self.user_entry.insert(0, username)
            self.user_entry.configure(state="disabled")

        # Password
        pwd_text = lang.get('userdlg_edit_pwd', 'zh') if mode == 'edit' else lang.get('userdlg_new_pwd', 'zh')
        ctk.CTkLabel(self.dialog, text=pwd_text, font=ctk.CTkFont(size=12),
                     anchor="w").pack(padx=padx, fill="x")
        self.pwd_entry = ctk.CTkEntry(self.dialog, show="*", height=36, font=ctk.CTkFont(size=13))
        self.pwd_entry.pack(padx=padx, fill="x", pady=(4, 10))

        # Permissions section
        perm_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        perm_frame.pack(padx=padx, fill="x", pady=(5, 0))
        ctk.CTkLabel(perm_frame, text=lang.get('userdlg_perms', 'zh'), font=ctk.CTkFont(size=12, weight="bold"),
                     anchor="w").pack(fill="x")

        self.cli_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(perm_frame, text=lang.get('userdlg_perm_cli', 'zh'), variable=self.cli_var,
                        font=ctk.CTkFont(size=12)).pack(anchor="w", pady=(8, 2))

        ctk.CTkLabel(perm_frame, text=lang.get('userdlg_perm_regions', 'zh'), font=ctk.CTkFont(size=11),
                     text_color="#6B7280", anchor="w").pack(fill="x", pady=(8, 2))

        regions_frame = ctk.CTkFrame(perm_frame, fg_color="transparent")
        regions_frame.pack(fill="x")
        self.uk_var = ctk.BooleanVar(value=True)
        self.au_var = ctk.BooleanVar(value=True)
        self.us_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(regions_frame, text=lang.get('region_uk', 'zh'), variable=self.uk_var,
                        font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 10))
        ctk.CTkCheckBox(regions_frame, text=lang.get('region_au', 'zh'), variable=self.au_var,
                        font=ctk.CTkFont(size=12)).pack(side="left", padx=(0, 10))
        ctk.CTkCheckBox(regions_frame, text=lang.get('region_us', 'zh'), variable=self.us_var,
                        font=ctk.CTkFont(size=12)).pack(side="left")

        # If edit mode, load current permissions
        if mode == 'edit':
            users = cfg.load_users()
            perms = users.get(username, {}).get('permissions', {})
            self.cli_var.set(perms.get('cli', True))
            regions = perms.get('regions', ['uk', 'au', 'us'])
            self.uk_var.set('uk' in regions)
            self.au_var.set('au' in regions)
            self.us_var.set('us' in regions)

        # Error label
        self.err_label = ctk.CTkLabel(self.dialog, text="", font=ctk.CTkFont(size=11),
                                      text_color="#EF4444")
        self.err_label.pack(pady=(12, 0))

        # Buttons
        btn_frame = ctk.CTkFrame(self.dialog, fg_color="transparent")
        btn_frame.pack(padx=padx, pady=(15, 20), fill="x")
        ctk.CTkButton(btn_frame, text=lang.get('cancel', 'zh'), fg_color="transparent",
                      text_color="#6B7280", border_width=1, border_color="#D1D5DB",
                      height=36, command=self.dialog.destroy).pack(side="left", fill="x", expand=True, padx=(0, 6))
        save_text = lang.get('userdlg_save_edit', 'zh') if mode == 'edit' else lang.get('userdlg_save_add', 'zh')
        ctk.CTkButton(btn_frame, text=save_text, height=36,
                      fg_color="#4F46E5", hover_color="#4338CA",
                      command=self._save).pack(side="left", fill="x", expand=True, padx=(6, 0))

    def _get_permissions(self):
        regions = []
        if self.uk_var.get(): regions.append('uk')
        if self.au_var.get(): regions.append('au')
        if self.us_var.get(): regions.append('us')
        return {"cli": self.cli_var.get(), "regions": regions}

    def _save(self):
        username = self.user_entry.get().strip()
        password = self.pwd_entry.get()
        perms = self._get_permissions()

        if not username:
            self.err_label.configure(text=lang.get('userdlg_enter_user', 'zh'))
            return
        if self.mode == 'add' and not password:
            self.err_label.configure(text=lang.get('userdlg_enter_pwd', 'zh'))
            return
        if self.mode == 'add' and len(password) < 4:
            self.err_label.configure(text=lang.get('userdlg_pwd_short', 'zh'))
            return

        if self.mode == 'add':
            ok, msg = cfg.add_user(username, password, perms)
        else:
            ok, msg = cfg.update_user(self.editing,
                                      password=password if password else None,
                                      permissions=perms)
        if ok:
            self.result = username
            self.dialog.destroy()
        else:
            self.err_label.configure(text=msg)


# ═══════════════════════════════════════════════════
#  Main launcher window
# ═══════════════════════════════════════════════════

class Launcher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(lang.get('app_title', 'zh') + " " + lang.get('app_version', 'zh'))
        self.geometry("440x460")
        self.resizable(False, False)
        ctk.set_appearance_mode("Light")
        ctk.set_default_color_theme("blue")

        self.update_idletasks()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw-440)//2}+{(sh-460)//2}")

        self.build_ui()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(pady=(30, 5))
        icon_frame = ctk.CTkFrame(header, width=56, height=56, corner_radius=14, fg_color="#4F46E5")
        icon_frame.pack(); icon_frame.pack_propagate(False)
        ctk.CTkLabel(icon_frame, text="📦", font=ctk.CTkFont(size=28)).pack(expand=True)

        ctk.CTkLabel(self, text="FBA Label Splitter",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(10, 2))
        ctk.CTkLabel(self, text=lang.get('app_subtitle', 'zh'),
                     font=ctk.CTkFont(size=12), text_color="#6B7280").pack()

        # Status card
        self.status_card = ctk.CTkFrame(self, fg_color="#F3F4F6", corner_radius=12)
        self.status_card.pack(padx=40, pady=(20, 8), fill="x")
        self.status_dot = ctk.CTkLabel(self.status_card, text="⚫", font=ctk.CTkFont(size=10),
                                       text_color="#9CA3AF")
        self.status_dot.pack(side="left", padx=(14, 4), pady=12)
        self.status_label = ctk.CTkLabel(self.status_card, text=lang.get('launcher_status_off', 'zh'),
                                         font=ctk.CTkFont(size=13, weight="bold"),
                                         text_color="#6B7280")
        self.status_label.pack(side="left", pady=12)
        self.url_label = ctk.CTkLabel(self.status_card, text="",
                                      font=ctk.CTkFont(size=11), text_color="#4F46E5")
        self.url_label.pack(side="right", padx=14, pady=12)

        # Config info line
        config = cfg.load_config()
        login_on = config.get('login_required', False)
        cli_on = config.get('cli_mode', False)
        tags = []
        if login_on: tags.append(lang.get('launcher_info_login', 'zh'))
        if cli_on: tags.append(lang.get('launcher_info_cli', 'zh'))
        info_text = " · ".join(tags) if tags else lang.get('launcher_info_anonymous', 'zh')
        ctk.CTkLabel(self, text=info_text, font=ctk.CTkFont(size=10),
                     text_color="#9CA3AF").pack(pady=(0, 5))

        # Start / Stop button
        self.btn_launch = ctk.CTkButton(self, text=lang.get('launcher_btn_start', 'zh'), height=46, corner_radius=23,
            font=ctk.CTkFont(size=14, weight="bold"), fg_color="#4F46E5",
            hover_color="#4338CA", command=self.toggle_server)
        self.btn_launch.pack(padx=60, pady=(0, 6), fill="x")

        # Open browser button
        self.btn_open = ctk.CTkButton(self, text=lang.get('launcher_btn_open', 'zh'), height=38, corner_radius=19,
            font=ctk.CTkFont(size=12), fg_color="transparent", text_color="#4F46E5",
            border_width=1.5, border_color="#4F46E5", hover_color="#EEF2FF",
            command=self.open_browser, state="disabled")
        self.btn_open.pack(padx=80, fill="x")

        # Advanced settings button
        self.btn_settings = ctk.CTkButton(self, text=lang.get('launcher_btn_settings', 'zh'), height=38, corner_radius=19,
            font=ctk.CTkFont(size=12), fg_color="transparent", text_color="#6B7280",
            border_width=1, border_color="#D1D5DB", hover_color="#F3F4F6",
            command=self.open_settings)
        self.btn_settings.pack(padx=80, pady=(6, 0), fill="x")

        # Footer
        ctk.CTkLabel(self,
            text=lang.get('launcher_hint', 'zh'),
            font=ctk.CTkFont(size=10), text_color="#9CA3AF"
        ).pack(pady=(0, 4))
        ctk.CTkLabel(self, text=lang.get('launcher_footer', 'zh'),
                     font=ctk.CTkFont(size=10), text_color="#9CA3AF").pack(side="bottom", pady=(0, 16))

    # ── Server control ──

    def toggle_server(self):
        if server_running: self.stop_server()
        else: self.start_server()

    def start_server(self):
        global flask_thread, server_running, PORT
        config = cfg.load_config()
        PORT = config.get('port', 5000)
        server_running = True
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        time.sleep(2)
        self.status_dot.configure(text="🟢", text_color="#10B981")
        self.status_label.configure(text=lang.get('launcher_status_on', 'zh'), text_color="#059669")
        self.url_label.configure(text=f"http://localhost:{PORT}")
        self.btn_launch.configure(text=lang.get('launcher_btn_stop', 'zh'), fg_color="#EF4444", hover_color="#DC2626")
        self.btn_open.configure(state="normal")
        webbrowser.open(f"http://localhost:{PORT}")

    def stop_server(self):
        global server_running
        server_running = False
        self.destroy()

    def open_browser(self):
        webbrowser.open(f"http://localhost:{PORT}")

    def on_close(self):
        global server_running
        server_running = False
        self.destroy()

    def refresh_info(self):
        """Refresh the config info label"""
        config = cfg.load_config()
        login_on = config.get('login_required', False)
        cli_on = config.get('cli_mode', False)
        public_on = config.get('public_access', False)
        tags = []
        if login_on: tags.append(lang.get('launcher_info_login', 'zh'))
        if cli_on: tags.append(lang.get('launcher_info_cli', 'zh'))
        if public_on: tags.append(lang.get('launcher_info_public', 'zh'))
        info_text = " · ".join(tags) if tags else lang.get('launcher_info_anonymous', 'zh')
        for w in self.winfo_children():
            if isinstance(w, ctk.CTkLabel) and w.cget("text") in (
                lang.get('launcher_info_login', 'zh'), lang.get('launcher_info_cli', 'zh'), lang.get('launcher_info_anonymous', 'zh'),
                lang.get('launcher_info_login', 'zh') + " · " + lang.get('launcher_info_cli', 'zh'), " · ".join(tags)
            ):
                w.configure(text=info_text)
                return
        # fallback: update any matching label
        for w in self.winfo_children():
            if isinstance(w, ctk.CTkLabel):
                txt = w.cget("text")
                if txt and (lang.get('launcher_info_login', 'zh')[:2] in txt or "CLI" in txt or lang.get('launcher_info_anonymous', 'zh')[:2] in txt):
                    w.configure(text=info_text)

    # ── Advanced settings ──

    def open_settings(self):
        SettingsWindow(self)


# ═══════════════════════════════════════════════════
#  Advanced settings window
# ═══════════════════════════════════════════════════

class SettingsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.win = ctk.CTkToplevel(parent)
        self.win.title(lang.get('settings_title', 'zh'))
        self.win.geometry("520x500")
        self.win.resizable(False, False)
        self.win.attributes('-topmost', True)
        self.win.grab_set()
        self._center()

        self.config = cfg.load_config()
        self.users = cfg.load_users()

        self._build_tabs()

    def _center(self):
        self.win.update_idletasks()
        sw, sh = self.win.winfo_screenwidth(), self.win.winfo_screenheight()
        self.win.geometry(f"+{(sw-520)//2}+{(sh-500)//2}")

    def _build_tabs(self):
        tab = ctk.CTkTabview(self.win)
        tab.pack(padx=10, pady=10, fill="both", expand=True)

        tab.add(lang.get('settings_tab_env', 'zh'))
        tab.add(lang.get('settings_tab_users', 'zh'))
        tab.add(lang.get('settings_tab_cli', 'zh'))

        self._build_env_tab(tab.tab(lang.get('settings_tab_env', 'zh')))
        self._build_users_tab(tab.tab(lang.get('settings_tab_users', 'zh')))
        self._build_cli_tab(tab.tab(lang.get('settings_tab_cli', 'zh')))

        ctk.CTkButton(self.win, text=lang.get('close', 'zh'), height=36, fg_color="transparent",
                      text_color="#6B7280", border_width=1, border_color="#D1D5DB",
                      command=self.win.destroy).pack(padx=20, pady=(0, 15))

    # ── Environment config tab ──

    def _build_env_tab(self, tab):
        ctk.CTkLabel(tab, text=lang.get('settings_env_title', 'zh'), font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=15, pady=(15, 15))

        # Port number
        ctk.CTkLabel(tab, text=lang.get('settings_env_port', 'zh'), font=ctk.CTkFont(size=12), anchor="w").pack(padx=15, fill="x")
        self.port_var = ctk.StringVar(value=str(self.config.get('port', 5000)))
        port_entry = ctk.CTkEntry(tab, textvariable=self.port_var, height=36, font=ctk.CTkFont(size=13))
        port_entry.pack(padx=15, fill="x", pady=(4, 15))

        # Login toggle
        self.login_var = ctk.BooleanVar(value=self.config.get('login_required', False))
        login_switch = ctk.CTkSwitch(tab, text=lang.get('settings_env_login_switch', 'zh'),
                                     variable=self.login_var, font=ctk.CTkFont(size=13),
                                     command=self._on_login_toggle)
        login_switch.pack(padx=15, anchor="w", pady=(5, 5))

        self.login_hint = ctk.CTkLabel(tab,
            text=lang.get('settings_env_login_on', 'zh'),
            font=ctk.CTkFont(size=11), text_color="#6B7280", anchor="w", justify="left")
        self.login_hint.pack(padx=15, fill="x", pady=(2, 5))

        # Public access
        self.public_var = ctk.BooleanVar(value=self.config.get('public_access', False))
        public_switch = ctk.CTkSwitch(tab, text=lang.get('settings_env_public_switch', 'zh'),
                                      variable=self.public_var, font=ctk.CTkFont(size=13))
        public_switch.pack(padx=15, anchor="w", pady=(5, 5))
        ctk.CTkLabel(tab,
            text=lang.get('settings_env_public_hint', 'zh'),
            font=ctk.CTkFont(size=11), text_color="#6B7280", anchor="w", justify="left"
        ).pack(padx=15, fill="x", pady=(0, 15))

        # Save button
        ctk.CTkButton(tab, text=lang.get('settings_env_save', 'zh'), height=36,
                      fg_color="#4F46E5", hover_color="#4338CA",
                      command=self._save_env).pack(padx=15, fill="x", pady=(10, 0))

        self.env_msg = ctk.CTkLabel(tab, text="", font=ctk.CTkFont(size=11), text_color="#10B981")
        self.env_msg.pack(padx=15, pady=(8, 0))

    def _on_login_toggle(self):
        if self.login_var.get():
            self.login_hint.configure(
                text=lang.get('settings_env_login_on', 'zh'))
        else:
            self.login_hint.configure(text=lang.get('settings_env_login_off', 'zh'))

    def _save_env(self):
        try:
            port = int(self.port_var.get())
            if port < 1 or port > 65535:
                raise ValueError("port range 1-65535")
        except ValueError:
            self.env_msg.configure(text=lang.get('settings_env_port_invalid', 'zh'), text_color="#EF4444")
            return

        # If login is enabled, check if root password is set
        if self.login_var.get():
            users = cfg.load_users()
            root_pwd = users.get('root', {}).get('password', '')
            if not root_pwd:
                self.env_msg.configure(text=lang.get('settings_env_root_no_pwd', 'zh'), text_color="#4F46E5")
                self.win.update()
                # Show password setup dialog
                if not show_root_setup():
                    self.env_msg.configure(text=lang.get('settings_env_root_cancel', 'zh'), text_color="#EF4444")
                    self.login_var.set(False)
                    return

        self.config['port'] = port
        self.config['login_required'] = self.login_var.get()
        self.config['public_access'] = self.public_var.get()
        cfg.save_config(self.config)
        self.parent.refresh_info()
        self.env_msg.configure(text=lang.get('restart_hint', 'zh'), text_color="#10B981")

    # ── User management tab ──

    def _build_users_tab(self, tab):
        top_frame = ctk.CTkFrame(tab, fg_color="transparent")
        top_frame.pack(padx=15, fill="x", pady=(15, 10))
        ctk.CTkLabel(top_frame, text=lang.get('settings_users_title', 'zh'), font=ctk.CTkFont(size=15, weight="bold")).pack(side="left")
        ctk.CTkButton(top_frame, text=lang.get('settings_users_add', 'zh'), height=32, width=100,
                      font=ctk.CTkFont(size=12), fg_color="#4F46E5", hover_color="#4338CA",
                      command=self._add_user).pack(side="right")

        self.users_frame = ctk.CTkScrollableFrame(tab, height=260)
        self.users_frame.pack(padx=15, fill="both", expand=True, pady=(0, 10))
        self._refresh_user_list()

    def _refresh_user_list(self):
        for w in self.users_frame.winfo_children():
            w.destroy()
        users = cfg.get_user_list()
        for u in users:
            name = u['username']
            perms = u.get('permissions', {})
            cli = "CLI" if perms.get('cli') else ""
            regions = ", ".join(perms.get('regions', [])).upper()
            info = " · ".join(filter(None, [cli, regions])) or lang.get('settings_users_no_perm', 'zh')

            row = ctk.CTkFrame(self.users_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)

            icon = "👑" if name == 'root' else "👤"
            ctk.CTkLabel(row, text=f"{icon} {name}", font=ctk.CTkFont(size=13, weight="bold"),
                         width=100, anchor="w").pack(side="left", padx=(5, 5))
            ctk.CTkLabel(row, text=info, font=ctk.CTkFont(size=11),
                         text_color="#6B7280", anchor="w").pack(side="left", fill="x", expand=True)

            if name != 'root':
                ctk.CTkButton(row, text=lang.get('edit', 'zh'), height=26, width=50,
                              font=ctk.CTkFont(size=11), fg_color="transparent",
                              text_color="#4F46E5", border_width=1, border_color="#4F46E5",
                              command=lambda n=name: self._edit_user(n)
                              ).pack(side="right", padx=2)
                ctk.CTkButton(row, text=lang.get('delete', 'zh'), height=26, width=50,
                              font=ctk.CTkFont(size=11), fg_color="transparent",
                              text_color="#EF4444", border_width=1, border_color="#EF4444",
                              command=lambda n=name: self._delete_user(n)
                              ).pack(side="right", padx=2)
            else:
                ctk.CTkButton(row, text=lang.get('settings_users_edit_pwd', 'zh'), height=26, width=80,
                              font=ctk.CTkFont(size=11), fg_color="transparent",
                              text_color="#4F46E5", border_width=1, border_color="#4F46E5",
                              command=lambda n=name: self._edit_user(n)
                              ).pack(side="right", padx=2)

    def _add_user(self):
        dlg = UserDialog(self.win, mode='add')
        self.win.wait_window(dlg.dialog)
        self._refresh_user_list()

    def _edit_user(self, username):
        dlg = UserDialog(self.win, mode='edit', username=username)
        self.win.wait_window(dlg.dialog)
        self._refresh_user_list()

    def _delete_user(self, username):
        ok, msg = cfg.delete_user(username)
        if not ok:
            ctk.CTkLabel(self.users_frame, text=msg, font=ctk.CTkFont(size=11),
                         text_color="#EF4444").pack()
        self._refresh_user_list()

    # ── CLI mode tab ──

    def _build_cli_tab(self, tab):
        ctk.CTkLabel(tab, text=lang.get('settings_cli_title', 'zh'), font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=15, pady=(15, 15))

        self.cli_var = ctk.BooleanVar(value=self.config.get('cli_mode', False))
        ctk.CTkSwitch(tab, text=lang.get('settings_cli_switch', 'zh'),
                      variable=self.cli_var, font=ctk.CTkFont(size=13)).pack(padx=15, anchor="w", pady=(5, 10))

        ctk.CTkLabel(tab,
            text=lang.get('settings_cli_desc', 'zh'),
            font=ctk.CTkFont(size=11), text_color="#6B7280", anchor="w", justify="left"
        ).pack(padx=15, fill="x", pady=(0, 15))

        ctk.CTkButton(tab, text=lang.get('settings_cli_save', 'zh'), height=36,
                      fg_color="#4F46E5", hover_color="#4338CA",
                      command=self._save_cli).pack(padx=15, fill="x", pady=(10, 0))

        self.cli_msg = ctk.CTkLabel(tab, text="", font=ctk.CTkFont(size=11), text_color="#10B981")
        self.cli_msg.pack(padx=15, pady=(8, 0))

    def _save_cli(self):
        self.config['cli_mode'] = self.cli_var.get()
        cfg.save_config(self.config)
        self.parent.refresh_info()
        self.cli_msg.configure(text=lang.get('restart_hint', 'zh'), text_color="#10B981")


# ═══════════════════════════════════════════════════
#  Entry point
# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    Launcher().mainloop()

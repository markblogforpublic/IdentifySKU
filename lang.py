"""
i18n / Localization module — Chinese (zh) and English (en)
All user-facing strings are centralized here.
"""
import os

LANG = {
    # ═══════════════════════════════════════════════════
    #  Common / General
    # ═══════════════════════════════════════════════════
    "app_title":       {"zh": "FBA Label Splitter", "en": "FBA Label Splitter"},
    "app_subtitle":    {"zh": "Amazon FBA 标签智能拆分工具", "en": "Amazon FBA Label Intelligent Splitter"},
    "app_version":     {"zh": "V2.5", "en": "V2.5"},
    "save":            {"zh": "保存", "en": "Save"},
    "cancel":          {"zh": "取消", "en": "Cancel"},
    "close":           {"zh": "关闭", "en": "Close"},
    "confirm":         {"zh": "确认", "en": "Confirm"},
    "delete":          {"zh": "删除", "en": "Delete"},
    "edit":            {"zh": "编辑", "en": "Edit"},
    "add":             {"zh": "添加", "en": "Add"},
    "download":        {"zh": "下载", "en": "Download"},
    "loading":         {"zh": "加载中...", "en": "Loading..."},
    "error":           {"zh": "错误", "en": "Error"},
    "success":         {"zh": "成功", "en": "Success"},
    "unknown":         {"zh": "未知", "en": "Unknown"},
    "none":            {"zh": "无", "en": "None"},
    "guest":           {"zh": "访客", "en": "Guest"},
    "logout":          {"zh": "退出", "en": "Logout"},
    "login":           {"zh": "登 录", "en": "Login"},
    "username":        {"zh": "用户名", "en": "Username"},
    "password":        {"zh": "密码", "en": "Password"},
    "remember_me":     {"zh": "记住登录状态（30 天）", "en": "Remember me (30 days)"},
    "no_permission":   {"zh": "无权限", "en": "No permission"},
    "restart_hint":    {"zh": "已保存（需重启服务生效）", "en": "Saved (restart server to apply)"},

    # ═══════════════════════════════════════════════════
    #  Launcher
    # ═══════════════════════════════════════════════════
    "launcher_first_run_heading":   {"zh": "🔐  首次使用", "en": "🔐  First Run"},
    "launcher_first_run_title":     {"zh": "首次使用 — 设置管理员密码", "en": "First Run — Set Admin Password"},
    "launcher_first_run_welcome":   {"zh": "欢迎使用 FBA Label Splitter！", "en": "Welcome to FBA Label Splitter!"},
    "launcher_first_run_desc":      {"zh": "请为管理员账户 root 设置一个密码。\n此密码用于登录网页管理界面和命令行。",
                                     "en": "Please set a password for the root admin account.\nThis password is used to access the web interface and CLI."},
    "launcher_first_run_new_pwd":   {"zh": "新密码", "en": "New Password"},
    "launcher_first_run_confirm":   {"zh": "确认密码", "en": "Confirm Password"},
    "launcher_first_run_btn":       {"zh": "设置密码并进入", "en": "Set Password & Enter"},
    "launcher_first_run_short":     {"zh": "密码长度至少 4 位", "en": "Password must be at least 4 characters"},
    "launcher_first_run_mismatch":  {"zh": "两次输入的密码不一致", "en": "Passwords do not match"},
    "launcher_status_off":          {"zh": "未启动", "en": "Stopped"},
    "launcher_status_on":           {"zh": "服务运行中", "en": "Server Running"},
    "launcher_btn_start":           {"zh": "🚀  启动服务", "en": "🚀  Start Server"},
    "launcher_btn_stop":            {"zh": "⏹  停止服务", "en": "⏹  Stop Server"},
    "launcher_btn_open":            {"zh": "🌐  打开网页", "en": "🌐  Open Browser"},
    "launcher_btn_settings":        {"zh": "⚙  高级设置", "en": "⚙  Advanced Settings"},
    "launcher_hint":                {"zh": "💡 如需部署至服务器或限制他人操作，请打开高级设置",
                                     "en": "💡 To deploy on a server or restrict access, open Advanced Settings"},
    "launcher_info_anonymous":      {"zh": "本机访问 · 匿名", "en": "Local · Anonymous"},
    "launcher_info_login":          {"zh": "🔐 登录验证", "en": "🔐 Auth Required"},
    "launcher_info_cli":            {"zh": "💻 CLI模式", "en": "💻 CLI Mode"},
    "launcher_info_public":         {"zh": "🌐 公网开放", "en": "🌐 Public Access"},
    "launcher_footer":              {"zh": "本工具由 markblogforpublic.github.io 与 Claude 协同开发",
                                     "en": "Built by markblogforpublic.github.io & Claude"},

    # ═══════════════════════════════════════════════════
    #  Settings Window
    # ═══════════════════════════════════════════════════
    "settings_title":            {"zh": "高级设置", "en": "Advanced Settings"},
    "settings_tab_env":          {"zh": "环境配置", "en": "Environment"},
    "settings_tab_users":        {"zh": "用户管理", "en": "Users"},
    "settings_tab_cli":          {"zh": "CLI 模式", "en": "CLI Mode"},
    "settings_env_title":        {"zh": "服务环境配置", "en": "Server Environment"},
    "settings_env_port":         {"zh": "HTTP 端口号", "en": "HTTP Port"},
    "settings_env_port_invalid": {"zh": "端口号无效", "en": "Invalid port number"},
    "settings_env_login_switch": {"zh": "启用用户登录验证", "en": "Enable Login Authentication"},
    "settings_env_login_on":     {"zh": "开启后，访问网页需要输入用户名和密码。\nroot 用户拥有全部权限，可在「用户管理」中添加其他用户。",
                                  "en": "When enabled, users must log in to access the web interface.\nThe root account has full permissions. Add other users in the Users tab."},
    "settings_env_login_off":    {"zh": "已关闭登录验证，所有人可直接访问。", "en": "Login disabled. Anyone can access directly."},
    "settings_env_public_switch":{"zh": "允许来自公网的访问（绑定 0.0.0.0）", "en": "Allow public network access (bind 0.0.0.0)"},
    "settings_env_public_hint":  {"zh": "默认仅允许本机访问 (127.0.0.1)。\n开启后局域网/公网均可连接，建议同时开启登录验证。",
                                  "en": "Default: localhost only (127.0.0.1).\nWhen enabled, LAN/public connections are allowed. Enable login auth is recommended."},
    "settings_env_save":         {"zh": "保存环境配置", "en": "Save Environment Config"},
    "settings_env_root_no_pwd":  {"zh": "root 密码未设置，正在跳转...", "en": "Root password not set, redirecting..."},
    "settings_env_root_cancel":  {"zh": "未设置 root 密码，登录验证未开启", "en": "Root password not set. Login not enabled."},
    "settings_users_title":      {"zh": "用户管理", "en": "User Management"},
    "settings_users_add":        {"zh": "+ 添加用户", "en": "+ Add User"},
    "settings_users_edit_pwd":   {"zh": "修改密码", "en": "Change Password"},
    "settings_users_no_perm":    {"zh": "无权限", "en": "No permissions"},
    "settings_cli_title":        {"zh": "命令行模式 (CLI)", "en": "Command Line Mode (CLI)"},
    "settings_cli_switch":       {"zh": "启用 Web 命令行模式", "en": "Enable Web CLI Mode"},
    "settings_cli_desc":         {"zh": "启用后网页右侧会出现命令行终端，可以用英文命令\n直接操作处理流程，无需鼠标点击。\n\n命令包括：region / pdf / csv / range / process /\nus-pdf / us-grid / us-process / status / download 等",
                                  "en": "When enabled, the web interface switches to a full CLI terminal.\nOperate the tool entirely with English commands — no mouse needed.\n\nCommands: region / pdf / csv / range / process /\nus-pdf / us-grid / us-process / status / download etc."},
    "settings_cli_save":         {"zh": "保存 CLI 设置", "en": "Save CLI Settings"},

    # ═══════════════════════════════════════════════════
    #  User Dialog (Launcher)
    # ═══════════════════════════════════════════════════
    "userdlg_add_title":     {"zh": "添加用户", "en": "Add User"},
    "userdlg_edit_title":    {"zh": "编辑用户 — ", "en": "Edit User — "},
    "userdlg_info":          {"zh": "👤  用户信息", "en": "👤  User Info"},
    "userdlg_username":      {"zh": "用户名", "en": "Username"},
    "userdlg_new_pwd":       {"zh": "密码", "en": "Password"},
    "userdlg_edit_pwd":      {"zh": "新密码（留空则不修改）", "en": "New password (leave blank to keep)"},
    "userdlg_perms":         {"zh": "权限设置", "en": "Permissions"},
    "userdlg_perm_cli":      {"zh": "命令行模式 (CLI)", "en": "CLI Access"},
    "userdlg_perm_regions":  {"zh": "可用区域：", "en": "Available Regions:"},
    "userdlg_save_add":      {"zh": "添加用户", "en": "Add User"},
    "userdlg_save_edit":     {"zh": "保存修改", "en": "Save Changes"},
    "userdlg_user_exists":   {"zh": "用户已存在", "en": "User already exists"},
    "userdlg_enter_user":    {"zh": "请输入用户名", "en": "Please enter a username"},
    "userdlg_enter_pwd":     {"zh": "请输入密码", "en": "Please enter a password"},
    "userdlg_pwd_short":     {"zh": "密码长度至少 4 位", "en": "Password must be at least 4 characters"},
    "userdlg_added":         {"zh": "添加成功", "en": "Added successfully"},
    "userdlg_updated":       {"zh": "更新成功", "en": "Updated successfully"},
    "userdlg_not_found":     {"zh": "用户不存在", "en": "User not found"},
    "userdlg_root_protect":  {"zh": "不能删除 root 用户", "en": "Cannot delete root user"},

    # ═══════════════════════════════════════════════════
    #  Web UI — Navigation
    # ═══════════════════════════════════════════════════
    "nav_uk":         {"zh": "英国版", "en": "UK"},
    "nav_au":         {"zh": "澳洲版", "en": "AU"},
    "nav_us":         {"zh": "美国版", "en": "US"},
    "nav_about":      {"zh": "关于", "en": "About"},
    "nav_region_badge":{"zh": "当前区域", "en": "Region"},

    # ═══════════════════════════════════════════════════
    #  Web UI — UK/AU Tab
    # ═══════════════════════════════════════════════════
    "uk_step1_title":    {"zh": "上传 FBA 标签源文件", "en": "Upload FBA Label PDF"},
    "uk_step1_required": {"zh": "* 必选", "en": "* Required"},
    "uk_step1_hint":     {"zh": "点击选择 或拖拽 PDF 到此处", "en": "Click or drag PDF here"},
    "uk_step2_title":    {"zh": "上传装箱单（CSV / Excel，可选）", "en": "Upload Packing List (CSV / Excel, optional)"},
    "uk_step2_hint":     {"zh": "点击选择 或拖拽 CSV / Excel 到此处", "en": "Click or drag CSV / Excel here"},
    "uk_step2_auto":     {"zh": "上传后自动填充下方区间表格", "en": "Ranges will be auto-populated after upload"},
    "uk_step3_title":    {"zh": "标签区间配置", "en": "Label Range Configuration"},
    "uk_step3_add":      {"zh": "添加区间", "en": "Add Range"},
    "uk_step3_hint":     {"zh": "上传 CSV 自动填充，或手动添加。必须至少配置一个区间才能处理。",
                           "en": "Auto-filled from CSV, or add manually. At least one range required."},
    "uk_step3_empty":    {"zh": "暂无区间 — 上传 CSV 或点击「添加区间」", "en": "No ranges — upload CSV or click Add Range"},
    "uk_step3_count":    {"zh": " 个", "en": ""},
    "uk_step3_col_title": {"zh": "标题", "en": "Title"},
    "uk_step3_col_start": {"zh": "起始", "en": "Start"},
    "uk_step3_col_end":   {"zh": "结束", "en": "End"},
    "uk_step4_title":    {"zh": "开始处理", "en": "Process"},
    "uk_step4_btn":      {"zh": "开始拆分", "en": "Start Splitting"},
    "uk_step4_hint":     {"zh": "请先选择 PDF 并配置至少一个区间", "en": "Please select a PDF and configure at least one range"},
    "uk_progress_scan":  {"zh": "扫描标签...", "en": "Scanning labels..."},
    "uk_progress_split": {"zh": "切分导出...", "en": "Splitting & exporting..."},
    "uk_result_title":   {"zh": "生成结果", "en": "Results"},
    "uk_result_dl_all":  {"zh": "打包下载全部", "en": "Download All as ZIP"},
    "uk_placeholder":    {"zh": "SKU名称", "en": "SKU Name"},

    # ═══════════════════════════════════════════════════
    #  Web UI — US Tab
    # ═══════════════════════════════════════════════════
    "us_step1_title":    {"zh": "上传 SKU 标签 PDF", "en": "Upload SKU Label PDF"},
    "us_step1_hint":     {"zh": "支持含 \"Single SKU\" 标记的标签 PDF", "en": "Supports PDFs with \"Single SKU\" markers"},
    "us_step2_title":    {"zh": "网格布局设置", "en": "Grid Layout Settings"},
    "us_step2_rows":     {"zh": "行数", "en": "Rows"},
    "us_step2_cols":     {"zh": "列数", "en": "Columns"},
    "us_step2_adv":      {"zh": "高级边距设置", "en": "Advanced Margin Settings"},
    "us_step2_hide_adv": {"zh": "隐藏边距设置", "en": "Hide Margin Settings"},
    "us_step2_ml":       {"zh": "左边距", "en": "Left Margin"},
    "us_step2_mt":       {"zh": "上边距", "en": "Top Margin"},
    "us_step2_mr":       {"zh": "右边距", "en": "Right Margin"},
    "us_step2_mb":       {"zh": "下边距", "en": "Bottom Margin"},
    "us_step3_title":    {"zh": "开始处理", "en": "Process"},
    "us_step3_btn":      {"zh": "开始转换", "en": "Start Conversion"},
    "us_step3_hint":     {"zh": "请先选择 PDF 文件", "en": "Please select a PDF file first"},
    "us_progress_scan":  {"zh": "扫描标签...", "en": "Scanning labels..."},
    "us_progress_export": {"zh": "导出SKU...", "en": "Exporting SKUs..."},
    "us_result_title":   {"zh": "导出结果", "en": "Export Results"},

    # ═══════════════════════════════════════════════════
    #  Web UI — AU Tab (placeholder)
    # ═══════════════════════════════════════════════════
    "au_dev_title":  {"zh": "澳洲版 — 开发中", "en": "AU Version — Under Development"},
    "au_dev_desc":   {"zh": "Amazon Australia FBA 标签拆分功能正在开发中，敬请期待。",
                      "en": "Amazon Australia FBA label splitting is under development. Stay tuned."},
    "au_dev_eta":    {"zh": "预计上线：2026 Q3", "en": "ETA: 2026 Q3"},

    # ═══════════════════════════════════════════════════
    #  Web UI — About Tab
    # ═══════════════════════════════════════════════════
    "about_log":       {"zh": "日志", "en": "Logs"},
    "about_theme":     {"zh": "主题", "en": "Theme"},
    "about_user":      {"zh": "个人信息", "en": "User Info"},
    "about_dev":       {"zh": "开发者", "en": "Developer"},
    "about_log_title": {"zh": "处理日志", "en": "Processing Logs"},
    "about_log_desc":  {"zh": "每次上传和处理的记录", "en": "Record of each upload and processing task"},
    "about_log_empty": {"zh": "暂无日志记录", "en": "No log records"},
    "about_log_clear": {"zh": "清空日志", "en": "Clear Logs"},
    "about_log_source": {"zh": "来源", "en": "Source"},
    "about_theme_title":{"zh": "主题设置", "en": "Theme Settings"},
    "about_theme_desc": {"zh": "选择一款主题，即刻应用", "en": "Choose a theme to apply instantly"},
    "about_theme_water":  {"zh": "睡莲", "en": "Water Lilies"},
    "about_theme_sunrise":{"zh": "日出", "en": "Sunrise"},
    "about_theme_garden": {"zh": "花园", "en": "Garden"},
    "about_theme_dark":   {"zh": "暗夜", "en": "Dark Mode"},
    "about_user_title":  {"zh": "个人信息", "en": "Personal Info"},
    "about_user_ip":     {"zh": "IP 地址", "en": "IP Address"},
    "about_user_lang":   {"zh": "语言", "en": "Language"},
    "about_user_browser":{"zh": "浏览器", "en": "Browser"},
    "about_user_os":     {"zh": "操作系统", "en": "Operating System"},
    "about_user_screen": {"zh": "屏幕分辨率", "en": "Screen Resolution"},
    "about_dev_title":   {"zh": "开发者信息", "en": "Developer Info"},
    "about_dev_name":    {"zh": "开发者", "en": "Developer"},
    "about_dev_engine":  {"zh": "后端引擎", "en": "Backend Engine"},
    "about_dev_web":     {"zh": "Web 框架", "en": "Web Framework"},
    "about_dev_frontend":{"zh": "前端技术", "en": "Frontend"},
    "about_dev_ai":      {"zh": "AI 协作", "en": "AI Collaboration"},
    "about_dev_footer":  {"zh": "由 markblogforpublic.github.io 与 Claude 协同开发",
                          "en": "Built by markblogforpublic.github.io & Claude"},

    # ═══════════════════════════════════════════════════
    #  Web UI — Login
    # ═══════════════════════════════════════════════════
    "login_title":  {"zh": "FBA Label Splitter", "en": "FBA Label Splitter"},
    "login_hint":   {"zh": "服务器已启用账号验证。管理员 root 已开启此功能，请输入您的用户名和密码。",
                     "en": "Account verification is enabled. The root admin has activated this feature. Please enter your username and password."},
    "login_error_enter_user": {"zh": "请输入用户名", "en": "Please enter a username"},
    "login_error_failed":     {"zh": "登录失败", "en": "Login failed"},
    "login_error_network":    {"zh": "网络错误", "en": "Network error"},
    "login_error_invalid_user":{"zh": "用户名格式无效", "en": "Invalid username format"},
    "login_error_too_many":   {"zh": "尝试过于频繁，请稍后再试", "en": "Too many attempts. Please try again later."},
    "login_error_wrong":      {"zh": "用户名或密码错误", "en": "Incorrect username or password"},

    # ═══════════════════════════════════════════════════
    #  Web UI — CLI Terminal
    # ═══════════════════════════════════════════════════
    "cli_terminal_title":   {"zh": "CLI Terminal", "en": "CLI Terminal"},
    "cli_return_gui":       {"zh": "返回图形界面", "en": "Return to GUI"},
    "cli_welcome_line1":    {"zh": "║   FBA Label Splitter CLI v2.5          ║", "en": "║   FBA Label Splitter CLI v2.5          ║"},
    "cli_welcome_line2":    {"zh": "输入 'help' 查看所有可用命令。", "en": "Type 'help' for available commands."},
    "cli_welcome_line3":    {"zh": "按 ↑↓ 键浏览命令历史。", "en": "Press ↑↓ for command history."},
    "cli_input_placeholder":{"zh": "输入命令，例如: help  /  region uk  /  pdf C:\\labels.pdf ...",
                             "en": "Enter command, e.g.: help  /  region uk  /  pdf C:\\labels.pdf ..."},
    "cli_ref_title":        {"zh": "Command Reference", "en": "Command Reference"},
    "cli_ref_hint":         {"zh": "在终端中输入 help 查看完整指南和示例", "en": "Type help in terminal for full guide with examples"},
    "cli_ref_uk_mode":      {"zh": "UK / AU Mode", "en": "UK / AU Mode"},
    "cli_ref_us_mode":      {"zh": "US Mode", "en": "US Mode"},
    "cli_ref_output":       {"zh": "Output", "en": "Output"},
    "cli_ref_general":      {"zh": "General", "en": "General"},
    "cli_ref_paths_hint":   {"zh": "所有文件路径须为绝对路径。按 ↑↓ 键浏览历史。",
                             "en": "All file paths must be absolute. Press ↑↓ for history."},

    # ═══════════════════════════════════════════════════
    #  API Error Messages
    # ═══════════════════════════════════════════════════
    "api_no_pdf":           {"zh": "请上传 FBA 标签 PDF 文件", "en": "Please upload an FBA label PDF file"},
    "api_no_ranges":        {"zh": "请上传装箱单 CSV 或手动添加标签区间", "en": "Please upload a packing list CSV or manually add label ranges"},
    "api_no_pdf_us":        {"zh": "请上传 PDF 文件", "en": "Please upload a PDF file"},
    "api_xlsx_failed":      {"zh": "Excel 转换失败", "en": "Excel conversion failed"},
    "api_parse_failed":     {"zh": "解析失败", "en": "Parse failed"},
    "api_file_not_found":   {"zh": "文件不存在", "en": "File not found"},
    "api_job_expired":      {"zh": "任务不存在或已过期", "en": "Job not found or expired"},
    "api_invalid_job_id":   {"zh": "无效的任务 ID", "en": "Invalid job ID"},
    "api_invalid_session":  {"zh": "无效的会话 ID", "en": "Invalid session ID"},
    "api_login_required":   {"zh": "请先登录", "en": "Please log in first"},
    "api_too_many_req":     {"zh": "请求过于频繁，请稍后再试", "en": "Too many requests. Please try again later."},
    "api_rate_limit":       {"zh": "请求过于频繁，请稍后再试", "en": "Rate limit exceeded"},
    "api_upload_file":      {"zh": "请上传文件", "en": "Please upload a file"},
    "api_no_preview_file":  {"zh": "请上传文件", "en": "Please upload a file"},
    "api_cli_too_long":     {"zh": "命令过长（最长 2000 字符）", "en": "Command too long (max 2000 chars)"},

    # ═══════════════════════════════════════════════════
    #  CLI Engine Messages
    # ═══════════════════════════════════════════════════
    "cli_unknown_cmd":  {"zh": "未知命令", "en": "Unknown command"},
    "cli_help_hint":    {"zh": "输入 'help' 查看可用命令。", "en": "Type 'help' for available commands."},
    "cli_region_set":   {"zh": "区域已设置为", "en": "Region set to"},
    "cli_invalid_region":{"zh": "无效的区域。请使用: uk, au, us", "en": "Invalid region. Use: uk, au, or us"},
    "cli_pdf_loaded":   {"zh": "PDF 已加载", "en": "PDF loaded"},
    "cli_pdf_not_found": {"zh": "文件未找到", "en": "File not found"},
    "cli_invalid_type": {"zh": "无效的文件类型", "en": "Invalid file type"},
    "cli_csv_loaded":   {"zh": "CSV 已加载", "en": "CSV loaded"},
    "cli_ranges_parsed": {"zh": "解析到区间", "en": "Parsed ranges"},
    "cli_range_added":  {"zh": "区间已添加", "en": "Range added"},
    "cli_range_removed": {"zh": "已移除", "en": "Removed"},
    "cli_ranges_cleared": {"zh": "所有区间已清空。", "en": "All ranges cleared."},
    "cli_no_ranges":    {"zh": "未配置区间。", "en": "No ranges configured."},
    "cli_processing_done": {"zh": "处理完成！生成", "en": "Processing complete! Generated"},
    "cli_us_done":      {"zh": "US 处理完成！", "en": "US processing complete!"},
    "cli_no_pdf":       {"zh": "未加载 PDF。请先用 'pdf <路径>' 或 'us-pdf <路径>'。", "en": "No PDF loaded. Use 'pdf <path>' or 'us-pdf <path>' first."},
    "cli_no_ranges_proc":{"zh": "未配置区间。请先用 'csv <路径>' 或 'range add'。", "en": "No ranges configured. Use 'csv <path>' or 'range add' first."},
    "cli_switch_us":    {"zh": "请先切换到 US 模式: 'region us'", "en": "Switch to US mode first: 'region us'"},
    "cli_use_us_process":{"zh": "US 模式请使用 'us-process'。或切换区域: 'region uk'", "en": "Use 'us-process' for US mode, or switch with 'region uk'."},
    "cli_no_results":   {"zh": "暂无结果。请先运行 'process' 或 'us-process'。", "en": "No results. Run 'process' or 'us-process' first."},
    "cli_file_ready":   {"zh": "文件就绪", "en": "File ready"},
    "cli_zip_ready":    {"zh": "ZIP 就绪", "en": "ZIP ready"},
    "cli_no_history":   {"zh": "无命令历史。", "en": "No command history."},

    # ═══════════════════════════════════════════════════
    #  Theme names
    # ═══════════════════════════════════════════════════
    "region_uk":         {"zh": "UK 英国", "en": "UK"},
    "region_au":         {"zh": "AU 澳洲", "en": "AU"},
    "region_us":         {"zh": "US 美国", "en": "US"},
    "theme_water":   {"zh": "睡莲", "en": "Water Lilies"},
    "theme_sunrise": {"zh": "日出", "en": "Sunrise"},
    "theme_garden":  {"zh": "花园", "en": "Garden"},
    "theme_dark":    {"zh": "暗夜", "en": "Dark"},
}

# ═══════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════

def get(key, lang='zh'):
    """Get a single translated string."""
    entry = LANG.get(key, {})
    return entry.get(lang, entry.get('zh', key))


def get_all(lang='zh'):
    """Return all strings as a flat dict for the given language (for JS consumption)."""
    return {k: v.get(lang, v.get('zh', k)) for k, v in LANG.items()}


def detect_lang(request):
    """Detect preferred language from request. Returns 'zh' or 'en'."""
    # Check query param first
    qp = request.args.get('lang', '').lower()
    if qp in ('en', 'zh'):
        return qp
    # Check Accept-Language header
    al = request.headers.get('Accept-Language', '')
    if 'zh' in al.lower():
        return 'zh'
    if 'en' in al.lower():
        return 'en'
    return 'zh'  # default

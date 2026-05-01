"""
i18n / Localization module — Chinese (zh) and English (en)
Lite version — only CLI-relevant strings.
"""

LANG = {
    # App info
    "app_title":     {"zh": "SKU Label Splitter (Lite)", "en": "SKU Label Splitter (Lite)"},
    "app_version":   {"zh": "v1.0", "en": "v1.0"},
    "welcome_title": {"zh": "SKU 标签拆分工具 (Lite CLI版)", "en": "SKU Label Splitter (Lite CLI)"},
    "welcome_hint":  {"zh": "输入 /help 查看所有命令", "en": "Type /help for available commands"},

    # Regions
    "region_uk":     {"zh": "UK 英国", "en": "UK"},
    "region_au":     {"zh": "AU 澳洲", "en": "AU"},
    "region_us":     {"zh": "US 美国", "en": "US"},
    "region_set":    {"zh": "区域已设置为", "en": "Region set to"},
    "region_invalid":{"zh": "无效的区域。请使用: uk, au, us", "en": "Invalid region. Use: uk, au, or us"},

    # Files
    "pdf_loaded":    {"zh": "PDF 已加载", "en": "PDF loaded"},
    "csv_loaded":    {"zh": "CSV 已加载", "en": "CSV loaded"},
    "file_not_found":{"zh": "文件未找到", "en": "File not found"},
    "invalid_type":  {"zh": "无效的文件类型，需要 .pdf", "en": "Invalid file type, expected .pdf"},
    "invalid_csv":   {"zh": "无效的文件类型，需要 .csv / .xlsx", "en": "Invalid file type, expected .csv / .xlsx"},

    # Ranges
    "ranges_parsed": {"zh": "解析到 {count} 个区间", "en": "Parsed {count} range(s)"},
    "range_added":   {"zh": "已添加区间 [{s}-{e}] {title} (共 {total} 个)", "en": "Range [{s}-{e}] {title} added ({total} total)"},
    "range_removed": {"zh": "已移除区间 [{s}-{e}] {title}", "en": "Range [{s}-{e}] {title} removed"},
    "ranges_cleared":{"zh": "所有区间已清空", "en": "All ranges cleared"},
    "no_ranges":     {"zh": "未配置区间", "en": "No ranges configured"},
    "no_ranges_proc":{"zh": "未配置区间。请先使用 /csv 或 /range add", "en": "No ranges. Use /csv or /range add first"},

    # Processing
    "processing_start":{"zh": "开始处理...", "en": "Processing..."},
    "processing_done": {"zh": "处理完成！生成 {count} 个文件", "en": "Done! Generated {count} file(s)"},
    "processing_fail": {"zh": "处理失败", "en": "Processing failed"},
    "no_pdf":          {"zh": "未加载 PDF。请先使用 /pdf", "en": "No PDF loaded. Use /pdf first"},
    "us_done":         {"zh": "US 处理完成！生成 {count} 个文件", "en": "US processing complete! {count} file(s)"},

    # Grid / Margins (US mode)
    "grid_set":    {"zh": "网格已设置为 {rows} 行 x {cols} 列", "en": "Grid set to {rows} rows x {cols} cols"},
    "margin_set":  {"zh": "边距已设置为 L={l} T={t} R={r} B={b}", "en": "Margins set to L={l} T={t} R={r} B={b}"},

    # Language
    "lang_set":    {"zh": "已切换至中文", "en": "Switched to English"},
    "lang_invalid":{"zh": "无效的语言选项。请使用: zh, en", "en": "Invalid language. Use: zh, or en"},

    # General
    "unknown_cmd":  {"zh": "未知命令", "en": "Unknown command"},
    "help_hint":    {"zh": "输入 /help 查看可用命令", "en": "Type /help for available commands"},
    "goodbye":      {"zh": "再见！", "en": "Goodbye!"},
    "error":        {"zh": "错误", "en": "Error"},
    "done":         {"zh": "完成", "en": "Done"},
    "scanning":     {"zh": "扫描标签...", "en": "Scanning labels..."},
    "exporting":    {"zh": "导出中...", "en": "Exporting..."},

    # Status display
    "status_header":  {"zh": "当前状态", "en": "Current Status"},
    "status_region":  {"zh": "区域", "en": "Region"},
    "status_lang":    {"zh": "语言", "en": "Language"},
    "status_pdf":     {"zh": "PDF", "en": "PDF"},
    "status_csv":     {"zh": "CSV", "en": "CSV"},
    "status_ranges":  {"zh": "区间", "en": "Ranges"},
    "status_grid":    {"zh": "网格", "en": "Grid"},
    "status_margins": {"zh": "边距", "en": "Margins"},
    "status_result":  {"zh": "上次结果", "en": "Last Result"},
    "status_none":    {"zh": "无", "en": "None"},
    "status_files":   {"zh": "{n} 个文件就绪", "en": "{n} file(s) ready"},

    # Scanning progress
    "scan_page":     {"zh": "扫描中 {cur}/{total} 页", "en": "Scanning {cur}/{total} pages"},
    "skip_range":    {"zh": "跳过 [{s}-{e}] {title}: 无匹配标签", "en": "Skipping [{s}-{e}] {title}: no matching labels"},
    "export_label":  {"zh": "[{i}/{n}] {title} → {count} 个标签", "en": "[{i}/{n}] {title} → {count} label(s)"},
    "verify_ok":     {"zh": "验证通过: {order}", "en": "Verified: {order}"},
    "verify_fail":   {"zh": "验证失败! 实际顺序: {order}", "en": "Verification FAILED! Actual: {order}"},

    # US progress
    "us_scan_page":  {"zh": "扫描中 {cur}/{total} 页", "en": "Scanning {cur}/{total} pages"},
    "us_export_sku": {"zh": "[{i}/{n}] {sku} → {count} 个标签", "en": "[{i}/{n}] {sku} → {count} label(s)"},
    "us_no_skus":    {"zh": "未找到 SKU 标签。请检查 PDF 格式或网格参数。", "en": "No SKU labels found. Check PDF format or grid parameters."},
}


def get(key, lang="zh"):
    """Get a single translated string."""
    entry = LANG.get(key, {})
    return entry.get(lang, entry.get("zh", key))

# FBA Label Splitter V2.6 Redesigned 1

**Amazon FBA 标签智能拆分工具** | *Amazon FBA Label Intelligent Splitter*
[![Python Version](https://img.shields.io/badge/python-3.8+-blue)]()

Automatically split multi-label PDF sheets into individual SKU/range-based PDF files. Supports UK, AU, and US Amazon marketplace label formats.

自动将多标签 PDF 按 SKU / 编号区间拆分为独立 PDF 文件。支持英国、澳洲、美国亚马逊站点标签格式。

---

## 🆕 V2.6 Redesigned 1 更新内容 | What's New

### 界面重设计
- **侧边栏导航布局** — 导航从顶部移至左侧，类似 ChatGPT 风格，用户信息和语言切换放在侧边栏底部
- **Inter 字体 + Material 3** — 引入 Anthropic 同款 Inter 字体，卡片和按钮圆角增大，视觉更现代
- **主题选择器移至关于页** — 顶部区域更简洁

### 修复
- **UK/AU 标签扫描重写** — 旧版按页面四等分裁剪提取文字，标签位于中心边界时会被重复识别或遗漏。新版改用文本块中心坐标分配象限，每个标签唯一归属一个区间，彻底解决切片被错误归类的问题
- **导出验证增强** — 输出 PDF 时会自动检查每个标签的编号是否落在对应的区间范围内，发现越界立即告警

### 优化
- **后台日志升级** — 所有 `print()` 统一迁移至 `logging` 模块，带时间戳和日志等级，排查问题更方便
- **操作响应优化** — 速率限制器改用高效数据结构，多人同时使用时更稳定
- **命令行语言跟随** — CLI 终端不再只显示中文，而是跟随网页界面的语言设置（中文/英文）
- **代码精简** — 消除多处重复逻辑，移除未使用的导入，运行更轻量
- **tkinter 延迟加载** — 服务端无图形界面时也能正常启动，不再强制依赖 GUI

### 安全
- **密码加密升级** — 账户密码从 SHA256 升级为 PBKDF2（60 万次迭代），登录更安全

### Other Changes
- Version bump: V2.5 → V2.6 → V2.6 Redesigned 1

## 🎉 V2.5 首个版本 | First Release (2026-05-01)

V2.5 是 FBA Label Splitter 的第一个公开发布版本，实现了完整的标签拆分功能：

- **UK/AU 模式**：按 FBA 标签编号区间拆分 PDF，支持 CSV/Excel 装箱单自动解析
- **US 模式**：按 "Single SKU" 文本标记拆分 PDF，支持自定义网格和边距
- **Web 图形界面**：拖拽上传、实时进度条、一键下载 ZIP
- **CLI 命令行模式**：17 条英文命令，支持历史记录浏览
- **桌面启动器**：一键启动/停止服务，高级设置面板
- **中英文双语**：所有界面、提示、日志均支持中英文切换
- **4 套主题**：睡莲、日出、花园、暗夜
- **用户登录**：可选登录验证，支持权限管理

---
## License

This project is licensed under the **GNU Lesser General Public License v3**. See the [LICENSE](LICENSE) file for details.

[![License: LGPL v3](https://img.shields.io/badge/License-LGPL%20v3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)

## 许可证变更说明 / License Change Notice

本项目原采用 MIT 许可证，现已变更为 **GNU Lesser General Public License v3**.

This project was originally licensed under the MIT License, and has been re-licensed under the **GNU Lesser General Public License v3**.


## More Version:SKU Label Splitter (Lite)
**
Amazon FBA 标签智能拆分工具 — 轻量 CLI 版
Amazon FBA Label Intelligent Splitter — Lightweight CLI Edition 
**

You can see in IdentifySKU_2.5_lite

More Info: Please read its readme.md

## 与完整版的区别 | Differences from Full Version

| 特性 | 完整版 V2.5 | Lite 版 |
|------|-------------|---------|
| 交互方式 | Flask Web UI + Desktop Launcher | 命令行 CLI |
| 启动耗时 | 需要启动 Web 服务和浏览器 | 即时启动 |
| CPU/内存占用 | 较高（Flask + 浏览器） | 极低 |
| UK/AU/US | 支持 | 支持 |
| 双语切换 | 支持 | 支持 |
| 依赖数量 | Flask, customtkinter, openpyxl 等 | 仅 pymupdf |
| 打包体积 | ~150MB | ~40MB |


---
**免责声明 (Disclaimer)：**



**本项目不侵犯 Amazon 的任何权益。 本工具为独立开源 PDF 处理程序，仅根据用户提供的标签编号拆分 PDF，不与 Amazon 网站、API 或服务器发生任何交互，不使用或分发 Amazon 商标、Logo 或专有数据。"FBA" 仅为描述性指示性合理使用。所有处理的标签均为用户自有商业文档。
This project does NOT infringe on Amazon's rights. It is an independent, open-source PDF utility. It does not access, scrape, or interact with Amazon's services, APIs, or trademarks in any form. "FBA" is used solely in a descriptive, nominative fair-use capacity. All labels processed are the user's own business documents.**

## ✨ Features · 功能

- **UK / AU Mode** — Split labels by FBA label-number ranges (e.g. `FBA15XXXU0` through `FBA15XXXU58`), parsed automatically from your packing-list CSV or Excel file.
- **US Mode** — Split labels by SKU name using "Single SKU" text markers on each label, with configurable grid layout and page margins.
- **Web GUI** — Clean single-page interface with drag-and-drop upload, live progress bar, and one-click ZIP download.
- **CLI Terminal** — Full command-line mode with 17 English commands (`region`, `pdf`, `csv`, `range`, `process`, `download`, etc.) and command history.
- **Desktop Launcher** — One-click start/stop from a native desktop window. Includes advanced settings panel.
- **User Authentication** — Optional login system with role-based permissions (region access, CLI access). `root` admin account with full control.
- **Excel Support** — Automatically converts `.xlsx` / `.xls` packing lists to CSV.
- **Public Network Mode** — Toggle to bind to `0.0.0.0` for LAN/public access (recommend enabling auth).
- **Security** — Path-traversal protection, input validation, rate limiting, CSP headers, secure session cookies with "Remember Me" support.
- **🌐 Bilingual** — Full Chinese (中文) and English support. Click the **中/EN** button in the web UI header to switch instantly. All error messages, UI labels, CLI output, and launcher text available in both languages. Language preference is saved in your browser.
- **4 Color Themes** — Water Lilies, Sunrise, Garden, Dark Mode.

---

## 📦 Installation · 安装

```bash
# Clone the repository
git clone https://github.com/markblogforpublic/IdentifySKU.git
cd fba-label-splitter

# Install dependencies
pip install -r requirements.txt --break-system-packages
```

**Dependencies:**
- Python 3.10+
- `pymupdf` — PDF processing
- `flask` — Web backend
- `customtkinter` — Desktop launcher GUI
- `openpyxl` — Excel-to-CSV conversion

---

## 🚀 Quick Start · 快速启动

### Method 1: Desktop Launcher (Recommended)
```bash
python start.py
```
A desktop window opens. Click **启动服务** (Start Server). Your browser opens automatically.

### Method 2: Web Server Only
```bash
python app.py
```
Open `http://localhost:5000` in your browser.

---

## 📖 Usage Guide · 使用指南

### UK / AU Mode

![Workflow: Upload PDF → Upload CSV → Auto-fill ranges → Process → Download]

1. Click the **UK** or **AU** tab at the top.
2. Upload your FBA label PDF (drag-and-drop or click to select).
3. Upload your packing list (`.csv` / `.xlsx` / `.xls`). Ranges are auto-parsed and filled into the table.
4. Alternatively, manually add ranges: click **添加区间** (Add Range), enter start/end numbers and optional SKU title.
5. Click **开始拆分** (Start Split). Watch the progress bar.
6. Download individual files or **打包下载全部** (Download All as ZIP).

**Example packing list CSV format:**
```
Column1,SKU_Name,Column3,...
...,GPETNPET1000,...,FBA15XXXU0-58,...
...,GPETNPET2000,...,FBA15XXXU59-120,...
```

### US Mode

1. Click the **US** tab.
2. Upload your SKU label PDF (must contain "Single SKU" text followed by the SKU name on the next line).
3. Configure grid layout (default: 3 rows × 2 columns). Expand **高级边距设置** (Advanced Margins) if needed.
4. Click **开始转换** (Start Convert).
5. Each unique SKU gets its own PDF file. Download individually or as ZIP.

### CLI Mode

Enable CLI mode in the launcher's **高级设置** (Advanced Settings). The web interface switches to a full-screen terminal:

```
$ region uk
$ pdf C:\Users\Public\labels\FBA_sheet.pdf
$ csv C:\Users\Public\labels\packing_list.xlsx
$ process
$ download-all
```

Type `help` for the full command reference with examples.

---

## ⚙️ Advanced Settings · 高级设置

Click **⚙ 高级设置** in the launcher to access:

| Tab | Options |
|-----|---------|
| **环境配置** (Environment) | Custom port, login toggle, public network access |
| **用户管理** (Users) | Add/edit/delete users, grant permissions (CLI, UK/AU/US regions) |
| **CLI 模式** (CLI Mode) | Enable/disable the web terminal |

**First-run:** When you first enable login verification, you'll be prompted to set the `root` admin password (minimum 4 characters).

---

## 🛡️ Security · 安全

- All processing is local — no data leaves your machine.
- Path-traversal protection on all file-download endpoints.
- Input validation: usernames limited to `[a-zA-Z0-9_]`, passwords capped at 128 chars.
- Rate limiting on login (10/min), processing (10/min), and CLI (60/min).
- Security headers: `Content-Security-Policy`, `X-Frame-Options`, `X-Content-Type-Options`, etc.
- Session cookies with configurable "Remember Me" persistence (30 days).

---

## 📂 Project Structure · 项目结构

```
fba-label-splitter/
├── start.py              # Desktop launcher (customtkinter GUI)
├── app.py                # Flask web backend + API routes
├── main.py               # UK/AU engine: FBA label-number matching
├── us_engine.py          # US engine: Single SKU text matching
├── cli_engine.py         # CLI command parser & executor (17 commands)
├── config_manager.py     # Config + user management + password hashing
├── lang.py               # i18n module — all translatable strings (zh/en)
├── build_exe.py          # PyInstaller packaging script
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html        # Single-page web frontend
└── README.md
```

---

## 🔧 Build EXE · 打包

```bash
python build_exe.py
```

Output: `dist/FBA Label Splitter/FBA Label Splitter.exe`

Copy the entire `FBA Label Splitter` folder to distribute. The EXE bundles all dependencies — no Python installation required for end users.

---

## 🌐 Browser Support · 浏览器支持

- Chrome / Edge (latest)
- Firefox (latest)
- Safari (latest)

---



## ⚠️ Document Format Compatibility · 文档格式兼容性

This tool was originally custom-built for **a specific company's FBA label workflow** as a goodwill, non-commercial public-service project. The label PDF layout and packing-list CSV/Excel format it expects are based on that company's specific template.

本工具最初是为**某一家公司的 FBA 标签处理流程定制开发**的公益项目（无商业活动，纯属好心公益）。它所期望的标签 PDF 版式和装箱单 CSV/Excel 格式均基于该公司特定的模板。

**Before using this tool, please ensure your documents match the expected format:**

- **UK/AU Mode:** Your PDF must contain FBA label numbers in the format `FBA[A-Z0-9]+U<number>` (e.g. `FBA15XXXU0`). Your packing list CSV/Excel must include these numbers in a recognizable `U<start>-<end>` range pattern.
- **US Mode:** Your PDF must contain the text "Single SKU" followed by the SKU name on the next line, arranged in a consistent grid layout.

**使用前请确保你的文档格式与工具预期一致：**

- **UK/AU 模式：** PDF 中须包含 `FBA[A-Z0-9]+U<数字>` 格式的标签编号（如 `FBA15XXXU0`）。装箱单 CSV/Excel 须包含对应的 `U<起始>-<结束>` 区间模式。
- **US 模式：** PDF 中须包含 "Single SKU" 文本，下一行为 SKU 名称，且标签按统一网格排列。

If your label format differs, you may need to modify the parsing logic in `main.py` or `us_engine.py` accordingly.

---

## 👨‍💻 Credits · 致谢

Developed by **[markblogforpublic.github.io](https://markblogforpublic.github.io)** 

---

*Built with Python, Flask, PyMuPDF, customtkinter, and Tailwind CSS.*

# SKU Label Splitter (Lite)

> Amazon FBA 标签智能拆分工具 — 轻量 CLI 版  
> Amazon FBA Label Intelligent Splitter — Lightweight CLI Edition

[![Python Version](https://img.shields.io/badge/python-3.8+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()

---

## 简介 | Introduction

**SKU Label Splitter (Lite)** 是一款轻量级的 Amazon FBA 标签 PDF 拆分工具。它从原版 [FBA Label Splitter V2.5](https://github.com/markblogforpublic/FBA-Label-Splitter) 精简而来，移除了 Flask Web 界面和桌面启动器，仅保留核心 CLI 交互，以最小的系统资源完成标签拆分任务。

支持三个区域的操作：

| 区域 | 拆分方式 | 说明 |
|------|----------|------|
| **UK** | FBA 标签号范围匹配 | 按装箱单中的 `FBA15XXXU0-58` 范围裁剪 PDF |
| **AU** | 同 UK 引擎 | Amazon Australia 同 UK 格式 |
| **US** | "Single SKU" 文本匹配 | 按网格裁剪，识别 "Single SKU" 文本分组导出 |

---

## 快速开始 | Quick Start

### 安装依赖

```bash
pip install pymupdf --break-system-packages
```

> 如果需要导入 `.xlsx` 装箱单，还需安装：
> ```bash
> pip install openpyxl --break-system-packages
> ```

### 启动

```bash
python sku.py
```

你会看到类似 Claude Code 风格的交互式命令行：

```
══════════════════════════════════════════
  SKU 标签拆分工具 (Lite CLI版)  v1.0
  输入 /help 查看所有命令
  Region: UK  |  Lang: zh
══════════════════════════════════════════

sku>
```

### 打包成独立 EXE（可选）

```bash
python build_exe.py
```

输出 `dist/sku-lite.exe`，可独立运行，无需 Python 环境。

---

## 命令参考 | Command Reference

所有命令支持 `/command` 和 `command` 两种写法（和 Claude Code 风格一致）。

### `/region <uk|au|us>` — 切换区域

```bash
sku> /region uk      # 切换到英国模式
sku> /region us      # 切换到美国模式
```

### `/pdf <path>` — 加载 PDF

```bash
sku> /pdf C:\labels\FBA_labels.pdf
sku> /pdf "C:\my files\labels.pdf"   # 路径含空格时用引号
```

### `/csv <path>` — 加载装箱单（UK/AU 模式）

自动解析装箱单 CSV 中的 FBA 标签区间（支持 `.csv` 和 `.xlsx`）。

```bash
sku> /csv C:\labels\packing_list.csv
```

### `/range` — 管理标签区间（UK/AU 模式）

```bash
sku> /range add 0 58 GPETNPET1000    # 添加区间
sku> /range list                      # 列出所有区间
sku> /range clear                     # 清空区间
```

### `/process` — 执行 UK/AU 拆分

```bash
sku> /process
```

### `/grid <rows> <cols>` — 设置 US 网格（US 模式）

```bash
sku> /grid 3 2    # 每页 3 行 2 列（默认）
```

### `/margin <L> <T> <R> <B>` — 设置 US 边距（US 模式）

```bash
sku> /margin 0 40 0 40    # 单位：pt（默认）
```

### `/us-process` — 执行 US 拆分

```bash
sku> /us-process
```

### `/lang <zh|en>` — 切换语言

```bash
sku> /lang zh    # 切换到中文
sku> /lang en    # Switch to English
```

### `/status` — 查看当前状态

显示当前区域、语言、加载的文件、区间配置等信息。

### `/help` — 显示帮助

### `/exit` — 退出程序

---

## 典型工作流 | Typical Workflows

### UK/AU 模式

```
sku> /region uk
sku> /pdf C:\labels\FBA_labels.pdf
sku> /csv C:\labels\packing_list.csv
sku> /process
```

### US 模式

```
sku> /region us
sku> /pdf C:\labels\US_labels.pdf
sku> /grid 3 2
sku> /us-process
```

---

## 输出说明 | Output

处理完成后，拆分结果保存在当前目录下的 `_sku_output/` 文件夹中：

```
_sku_output/
├── FBA_Labels_0_58.pdf
├── FBA_Labels_59_100.pdf
└── ...
```

US 模式会按 SKU 名称命名文件：

```
_sku_output/
├── GPETNPET1000.pdf
├── GPETNPET2000.pdf
└── ...
```

---

## 项目结构 | Project Structure

```
sku-cli/
├── sku.py              # 主入口 — Claude Code 风格 CLI (REPL)
├── engine.py           # 核心引擎 — UK/AU/US 处理逻辑
├── lang.py             # 双语模块 (zh/en)
├── build_exe.py        # PyInstaller 打包脚本
├── run.bat             # Windows 快捷启动
├── requirements.txt    # Python 依赖
└── README.md           # 本文件
```

---

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

## 依赖 | Dependencies

- **pymupdf** — PDF 处理（核心依赖，必须安装）
- **openpyxl** — Excel 导入（可选，仅加载 `.xlsx` 时需要）
- **pyinstaller** — 打包工具（可选，仅打包 EXE 时需要）

---

## License

MIT

"""
FBA Label Splitter V2.6 Redesigned 1 — EXE 打包脚本
运行: python build_exe.py
输出: dist/FBA Label Splitter/FBA Label Splitter.exe
"""
import os
import sys
import shutil
import subprocess
import site

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, 'dist')
NAME = "FBA Label Splitter"

def run(cmd):
    print(f"  > {cmd}")
    subprocess.check_call(cmd, shell=True)

print("=" * 55)
print(f"  {NAME} — EXE 打包工具")
print("=" * 55)

# 1. 确保 PyInstaller 已安装
print("\n[1/4] 检查 PyInstaller...")
try:
    import PyInstaller
    print("  PyInstaller 已安装 ✓")
except ImportError:
    print("  正在安装 PyInstaller...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller", "--break-system-packages"])

# 2. 清理旧构建
print("\n[2/4] 清理旧构建...")
for d in ['build', 'dist']:
    path = os.path.join(BASE_DIR, d)
    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"  已删除 {d}/")

# 3. PyInstaller 打包
print("\n[3/4] PyInstaller 打包中...（约 1-3 分钟）")
os.chdir(BASE_DIR)

# --onedir: 输出文件夹（EXE + 依赖），启动更快
# --noconsole: 不显示命令行窗口
# --add-data: 打包模板和数据文件
# --hidden-import: 确保隐式导入的模块被打包
# --collect-all: 收集包的所有数据文件

cmd = (
    f'pyinstaller '
    f'--onedir '
    f'--noconsole '
    f'--name "{NAME}" '
    f'--add-data "templates;templates" '
    f'--add-data "main.py;." '
    f'--add-data "us_engine.py;." '
    f'--add-data "app.py;." '
    f'--add-data "config_manager.py;." '
    f'--add-data "cli_engine.py;." '
    f'--add-data "lang.py;." '
    f'--hidden-import customtkinter '
    f'--hidden-import flask '
    f'--hidden-import fitz '
    f'--hidden-import pymupdf '
    f'--hidden-import main '
    f'--hidden-import us_engine '
    f'--hidden-import app '
    f'--hidden-import config_manager '
    f'--hidden-import cli_engine '
    f'--hidden-import lang '
    f'--hidden-import jinja2.ext '
    f'--hidden-import markupsafe '
    f'--hidden-import werkzeug '
    f'--hidden-import openpyxl '
    f'--collect-all customtkinter '
    f'start.py'
)
run(cmd)

# 4. 验证输出
print("\n[4/4] 验证输出...")
exe_path = os.path.join(BASE_DIR, 'dist', NAME, f'{NAME}.exe')
if os.path.exists(exe_path):
    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"  ✓ 打包成功！")
    print(f"  EXE 路径: {exe_path}")
    print(f"  EXE 大小: {size_mb:.1f} MB")
    print(f"\n{'=' * 55}")
    print(f"  输出目录: {os.path.join(BASE_DIR, 'dist', NAME)}")
    print(f"  将整个 '{NAME}' 文件夹复制给其他人即可使用")
    print(f"{'=' * 55}")
else:
    print("  ✗ 打包失败，请检查上方错误信息")
    sys.exit(1)

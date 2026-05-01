"""
SKU Label Splitter (Lite) — EXE 打包脚本
运行: python build_exe.py
输出: dist/sku-lite.exe
"""
import os
import sys
import shutil
import subprocess

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DIST_DIR = os.path.join(BASE_DIR, 'dist')
NAME = "sku-lite"

def run(cmd):
    print(f"  > {cmd}")
    subprocess.check_call(cmd, shell=True)

print("=" * 55)
print(f"  {NAME} — EXE 打包工具 (Lite)")
print("=" * 55)

# 1. 确保 PyInstaller 已安装
print("\n[1/4] 检查 PyInstaller...")
try:
    import PyInstaller
    print("  PyInstaller 已安装")
except ImportError:
    print("  正在安装 PyInstaller...")
    pip = [sys.executable, "-m", "pip", "install", "pyinstaller"]
    if sys.platform == "linux":
        pip.append("--break-system-packages")
    subprocess.check_call(pip)

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

# --onefile: 单文件 EXE，方便携带
# --console: CLI 程序需要控制台窗口
# --hidden-import: 确保隐式导入的模块被打包
cmd = (
    f'pyinstaller '
    f'--onefile '
    f'--console '
    f'--name "{NAME}" '
    f'--add-data "lang.py;." '
    f'--hidden-import fitz '
    f'--hidden-import pymupdf '
    f'--hidden-import lang '
    f'--hidden-import engine '
    f'sku.py'
)
run(cmd)

# 4. 验证输出
print("\n[4/4] 验证输出...")
exe_path = os.path.join(BASE_DIR, 'dist', f'{NAME}.exe')
if os.path.exists(exe_path):
    size_mb = os.path.getsize(exe_path) / (1024 * 1024)
    print(f"  \\u2713 打包成功！")
    print(f"  EXE 路径: {exe_path}")
    print(f"  EXE 大小: {size_mb:.1f} MB")
    print(f"\n{'=' * 55}")
    print(f"  将 dist/{NAME}.exe 复制到任意位置即可使用")
    print(f"  （无需安装 Python，双击运行）")
    print(f"{'=' * 55}")
else:
    print(f"  \\u2717 打包失败，请检查上方错误信息")
    sys.exit(1)

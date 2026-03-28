"""
SuperMap iObjectsPy 环境初始化脚本
用途：在任何 Python 脚本中调用此模块，自动完成 iObjectsPy 环境配置
用法：import idesktop_init  （放在所有 iobjectspy 导入之前）

使用前请修改 IDESKTOP_VERSIONS，填写你本机的 iDesktopX 安装路径。
多个路径按优先级排列，脚本会自动选择第一个存在的路径。
"""

import os
import sys

# ============================================================
# 【配置项】iDesktopX 安装目录候选列表（按优先级排列）
# 请修改为你本机的实际安装路径，例如：
#   Windows: r"D:\software\supermap-idesktopx-2025-windows-x64-bin"
#   Linux:   "/opt/SuperMap/iDesktopX-2025"
# ============================================================
IDESKTOP_VERSIONS = [
    # r"<你的iDesktopX安装路径>",   # ← 取消注释并填写实际路径
    # 以下为常见默认安装路径，按需启用：
    r"C:\SuperMap\iDesktopX-2025",
    r"D:\SuperMap\iDesktopX-2025",
    r"C:\Program Files\SuperMap\iDesktopX",
]

# 也可通过环境变量指定（优先级最高）
_env_path = os.environ.get("IDESKTOP_HOME")
if _env_path:
    IDESKTOP_VERSIONS.insert(0, _env_path)

IDESKTOP_DIR = None
for path in IDESKTOP_VERSIONS:
    if os.path.exists(path):
        IDESKTOP_DIR = path
        break

if IDESKTOP_DIR is None:
    raise RuntimeError(
        "未找到 SuperMap iDesktopX 安装目录。\n"
        "请在 idesktop_init.py 的 IDESKTOP_VERSIONS 中填写你的安装路径，\n"
        "或设置环境变量 IDESKTOP_HOME=<安装路径>"
    )

BIN_DIR = os.path.join(IDESKTOP_DIR, "bin")
BIN_PYTHON_DIR = os.path.join(IDESKTOP_DIR, "bin_python")
JRE_BIN = os.path.join(IDESKTOP_DIR, "jre", "bin")

# ============================================================
# 配置 iObjectsPy 路径
# ============================================================
def setup_iobjectspy():
    """将 iObjectsPy 添加到 Python 路径"""
    python_version = f"{sys.version_info.major}{sys.version_info.minor}"
    iobjectspy_dir = os.path.join(
        BIN_PYTHON_DIR, "iobjectspy",
        f"iobjectspy-py{python_version}_64"
    )
    if not os.path.exists(iobjectspy_dir):
        # 回退到 py310
        iobjectspy_dir = os.path.join(
            BIN_PYTHON_DIR, "iobjectspy", "iobjectspy-py310_64"
        )
    
    if iobjectspy_dir not in sys.path:
        sys.path.insert(0, iobjectspy_dir)
    if BIN_PYTHON_DIR not in sys.path:
        sys.path.insert(0, BIN_PYTHON_DIR)
    
    return iobjectspy_dir


def setup_java_env():
    """配置 Java 环境变量"""
    os.environ["JAVA_HOME"] = os.path.join(IDESKTOP_DIR, "jre")
    path = os.environ.get("PATH", "")
    if JRE_BIN not in path:
        os.environ["PATH"] = JRE_BIN + os.pathsep + path


def init():
    """完整初始化：配置路径 + 设置 iObjectsPy Java 路径"""
    iobjectspy_dir = setup_iobjectspy()
    setup_java_env()
    
    try:
        import iobjectspy as spy
        spy.set_iobjects_java_path(BIN_DIR)
        print(f"✓ iObjectsPy 初始化成功")
        print(f"  iDesktopX 目录: {IDESKTOP_DIR}")
        print(f"  iObjectsPy 路径: {iobjectspy_dir}")
        return spy
    except ImportError as e:
        print(f"✗ 无法导入 iObjectsPy：{e}")
        print("  请先安装 iObjectsPy：")
        print(f"    cd {BIN_PYTHON_DIR}")
        print(f"    pip install .")
        raise


# 模块导入时自动执行初始化
if __name__ != "__main__":
    init()

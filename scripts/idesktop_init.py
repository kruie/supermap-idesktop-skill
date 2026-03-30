"""
SuperMap iObjectsPy 环境初始化脚本（增强版）
================================================

用途：在任何 Python 脚本中调用此模块，自动完成 iObjectsPy 环境配置
用法：import idesktop_init  （放在所有 iobjectspy 导入之前）

v2.0 更新：
- 支持 iObjectsJava 独立运行方案
- 自动 Python 版本适配（py38/py39/py310/py311）
- 路径统一使用 Windows 反斜杠
- 更好的错误提示和回退机制

使用前请修改 IDESKTOP_VERSIONS，填写你本机的 iDesktopX 安装路径。
多个路径按优先级排列，脚本会自动选择第一个存在的路径。
"""

import os
import sys
from pathlib import Path

# ============================================================
# 【配置项 1】iDesktopX 安装目录候选列表（按优先级排列）
# ============================================================
IDESKTOP_VERSIONS = [
    # 环境变量优先级最高
    os.environ.get("IDESKTOP_HOME"),
    os.environ.get("SUPERMAP_IDESKTOP_HOME"),
    # 你的实际安装路径（取消注释并修改）
    r"D:\software\supermap-idesktopx-2025-windows-x64-bin",
    # 其他常见路径
    r"C:\SuperMap\iDesktopX-2025",
    r"D:\SuperMap\iDesktopX-2025",
    r"C:\Program Files\SuperMap\iDesktopX",
]

# ============================================================
# 【配置项 2】iObjectsJava 安装目录（用于独立运行方案）
# ============================================================
IOBJECTS_JAVA_VERSIONS = [
    os.environ.get("IOBJECTS_JAVA_HOME"),
    r"D:\software\supermap-iobjectsjava-2025-win64-all-Bin",
    r"C:\SuperMap\iObjectsJava-2025",
    r"D:\SuperMap\iObjectsJava-2025",
]

# ============================================================
# 自动探测
# ============================================================
def _find_dir(candidates) -> Path:
    """从候选路径中找到第一个存在的目录"""
    for path in candidates:
        if path and os.path.exists(path):
            return Path(str(path).replace("/", "\\"))
    return None


IDESKTOP_DIR = _find_dir(IDESKTOP_VERSIONS)
IOBJECTS_JAVA_DIR = _find_dir(IOBJECTS_JAVA_VERSIONS)

if IDESKTOP_DIR is None:
    raise RuntimeError(
        "未找到 SuperMap iDesktopX 安装目录。\n"
        "请在 idesktop_init.py 的 IDESKTOP_VERSIONS 中填写你的安装路径，\n"
        "或设置环境变量 IDESKTOP_HOME=<安装路径>"
    )

BIN_DIR = IDESKTOP_DIR / "bin"
BIN_PYTHON_DIR = IDESKTOP_DIR / "bin_python"
JRE_BIN = IDESKTOP_DIR / "jre" / "bin"
PY4J_DIR = IDESKTOP_DIR / "support" / "PythonLib" / "py4j"


# ============================================================
# 核心函数
# ============================================================

def get_python_version_tag() -> str:
    """获取当前 Python 版本标记（如 '310'、'38'）"""
    return f"{sys.version_info.major}{sys.version_info.minor}"


def find_iobjectspy_dir() -> Path:
    """
    自动找到最合适的 iObjectsPy 版本目录

    优先匹配当前 Python 版本，找不到则按 310→39→38 回退。
    """
    iobjectspy_root = BIN_PYTHON_DIR / "iobjectspy"
    
    # 优先：当前 Python 版本
    current_ver = get_python_version_tag()
    target = iobjectspy_root / f"iobjectspy-py{current_ver}_64"
    if target.exists():
        return target
    
    # 回退顺序
    for ver in ["310", "39", "38", "311", "312"]:
        fallback = iobjectspy_root / f"iobjectspy-py{ver}_64"
        if fallback.exists():
            print(f"ℹ  当前 Python {current_ver} 版本不存在，回退到 py{ver}")
            return fallback
    
    # 通配匹配
    available = sorted(iobjectspy_root.glob("iobjectspy-py*_64"), reverse=True)
    if available:
        print(f"ℹ  使用找到的版本: {available[0].name}")
        return available[0]
    
    raise RuntimeError(
        f"未在 {iobjectspy_root} 找到任何 iObjectsPy 版本目录。\n"
        "请确认 iDesktopX 安装完整，bin_python/iobjectspy/ 目录存在。"
    )


def setup_iobjectspy() -> Path:
    """将 iObjectsPy 添加到 Python 路径，返回实际使用的目录"""
    iobjectspy_dir = find_iobjectspy_dir()
    
    paths_to_add = [str(iobjectspy_dir), str(BIN_PYTHON_DIR)]
    
    # 添加 Py4J（如果存在）
    if PY4J_DIR.exists():
        paths_to_add.append(str(PY4J_DIR))
    
    for path in reversed(paths_to_add):
        if path not in sys.path:
            sys.path.insert(0, path)
    
    return iobjectspy_dir


def setup_java_env(use_iobjects_java: bool = False):
    """
    配置 Java 环境变量

    Args:
        use_iobjects_java: True = 使用 iObjectsJava，False = 使用 iDesktopX JRE
    """
    if use_iobjects_java and IOBJECTS_JAVA_DIR:
        # 方案 2：iObjectsJava 独立运行
        libx64_dir = IOBJECTS_JAVA_DIR / "libx64"
        lib_dir = IOBJECTS_JAVA_DIR / "lib"
        
        # 构建 CLASSPATH
        if lib_dir.exists():
            jar_paths = [str(j) for j in lib_dir.glob("*.jar")]
            if jar_paths:
                existing_cp = os.environ.get("CLASSPATH", "")
                os.environ["CLASSPATH"] = os.pathsep.join(jar_paths) + (
                    os.pathsep + existing_cp if existing_cp else ""
                )
        
        # 添加 libx64 到 PATH
        if libx64_dir.exists():
            current_path = os.environ.get("PATH", "")
            if str(libx64_dir) not in current_path:
                os.environ["PATH"] = str(libx64_dir) + os.pathsep + current_path
    
    else:
        # 方案 1：iDesktopX 内置 JRE
        if JRE_BIN.exists():
            os.environ["JAVA_HOME"] = str(IDESKTOP_DIR / "jre")
            current_path = os.environ.get("PATH", "")
            if str(JRE_BIN) not in current_path:
                os.environ["PATH"] = str(JRE_BIN) + os.pathsep + current_path


def init(use_iobjects_java: bool = False):
    """
    完整初始化：配置路径 + 初始化 iObjectsPy

    Args:
        use_iobjects_java: True = 使用 iObjectsJava 独立运行，False = 使用 iDesktopX JRE

    Returns:
        iobjectspy 模块实例
    """
    iobjectspy_dir = setup_iobjectspy()
    setup_java_env(use_iobjects_java=use_iobjects_java)
    
    try:
        import iobjectspy as spy
        
        # 设置 iObjects Java 路径（必须使用反斜杠）
        if use_iobjects_java and IOBJECTS_JAVA_DIR:
            java_path = str(IOBJECTS_JAVA_DIR / "libx64")
        else:
            java_path = str(BIN_DIR)
        
        spy.set_iobjects_java_path(java_path)
        
        print(f"✓ iObjectsPy 初始化成功")
        print(f"  iDesktopX 目录: {IDESKTOP_DIR}")
        print(f"  iObjectsPy 路径: {iobjectspy_dir}")
        print(f"  Java 路径: {java_path}")
        
        return spy
    
    except ImportError as e:
        print(f"✗ 无法导入 iObjectsPy：{e}")
        print("  请先安装 iObjectsPy：")
        print(f"    cd {BIN_PYTHON_DIR}")
        print(f"    pip install .")
        raise
    
    except Exception as e:
        print(f"✗ iObjectsPy 初始化失败: {e}")
        print("\n环境信息:")
        print(f"  Python 版本: {sys.version}")
        print(f"  iDesktopX 目录: {IDESKTOP_DIR}")
        print(f"  iObjectsJava 目录: {IOBJECTS_JAVA_DIR}")
        raise


# ============================================================
# 模块导入时自动执行初始化
# ============================================================
if __name__ != "__main__":
    # 先尝试 iDesktopX 方案
    try:
        init(use_iobjects_java=False)
    except Exception as e:
        # 回退到 iObjectsJava 方案
        if IOBJECTS_JAVA_DIR:
            print(f"→ iDesktopX 方案失败，尝试 iObjectsJava 方案...")
            try:
                init(use_iobjects_java=True)
            except Exception as e2:
                print(f"✗ 两种方案均失败: {e2}")
                raise
        else:
            raise

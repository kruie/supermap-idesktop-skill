"""
SuperMap iObjectsJava + Python 完整环境配置脚本
=================================================

功能：
1. 自动检测 iDesktopX 和 iObjectsJava 安装路径
2. 配置所有必要的环境变量（支持反斜杠路径）
3. 初始化 iObjectsPy（方案 1：iDesktopX bin 目录）
4. 支持通过 iObjectsJava 独立运行（方案 2）

使用方式：
    # 在脚本最开头导入（必须在 iobjectspy 之前）
    import supermap_env_config

    # 或者从指定路径加载
    from supermap_env_config import SuperMapEnv
    env = SuperMapEnv(idesktop_dir=r"D:\\software\\supermap-idesktopx-2025")
    env.init()
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)

# =============================================================
# 【配置区域】根据实际安装路径修改
# =============================================================

# 候选的 iDesktopX 安装路径（按优先级排列）
IDESKTOP_CANDIDATES = [
    # 环境变量优先（可由用户设置）
    os.environ.get("IDESKTOP_HOME"),
    os.environ.get("SUPERMAP_IDESKTOP_HOME"),
    # 常见安装路径
    r"D:\software\supermap-idesktopx-2025-windows-x64-bin",
    r"C:\SuperMap\iDesktopX-2025",
    r"D:\SuperMap\iDesktopX-2025",
    r"C:\Program Files\SuperMap\iDesktopX",
]

# 候选的 iObjectsJava 安装路径（用于独立运行方案）
IOBJECTS_JAVA_CANDIDATES = [
    os.environ.get("IOBJECTS_JAVA_HOME"),
    r"D:\software\supermap-iobjectsjava-2025-win64-all-Bin",
    r"C:\SuperMap\iObjectsJava-2025",
    r"D:\SuperMap\iObjectsJava-2025",
]


# =============================================================
# 核心类
# =============================================================

class SuperMapEnv:
    """SuperMap Python 环境自动配置器"""
    
    def __init__(
        self,
        idesktop_dir: Optional[str] = None,
        iobjects_java_dir: Optional[str] = None,
        python_version: Optional[str] = None,
        verbose: bool = True
    ):
        """
        初始化配置器

        Args:
            idesktop_dir:       iDesktopX 安装目录（可选，自动检测）
            iobjects_java_dir:  iObjectsJava 安装目录（可选，自动检测）
            python_version:     指定 Python 版本（如 '310', '38'），None 表示自动检测
            verbose:            是否打印初始化信息
        """
        self.verbose = verbose
        
        # 自动检测路径
        self.idesktop_dir = Path(idesktop_dir) if idesktop_dir else self._find_path(IDESKTOP_CANDIDATES)
        self.iobjects_java_dir = Path(iobjects_java_dir) if iobjects_java_dir else self._find_path(IOBJECTS_JAVA_CANDIDATES)
        self.python_version = python_version or self._get_python_version()
        
        # 派生路径
        if self.idesktop_dir:
            self.idesktop_dir = Path(str(self.idesktop_dir).replace("/", "\\"))
            self.bin_dir = self.idesktop_dir / "bin"
            self.bin_python_dir = self.idesktop_dir / "bin_python"
            self.jre_bin = self.idesktop_dir / "jre" / "bin"
            self.py4j_dir = self.idesktop_dir / "support" / "PythonLib" / "py4j"
            self.iobjectspy_dir = self.bin_python_dir / "iobjectspy" / f"iobjectspy-py{self.python_version}_64"
        
        if self.iobjects_java_dir:
            self.iobjects_java_dir = Path(str(self.iobjects_java_dir).replace("/", "\\"))
    
    @staticmethod
    def _find_path(candidates: List[Optional[str]]) -> Optional[Path]:
        """从候选路径中找到第一个存在的目录"""
        for path in candidates:
            if path and os.path.exists(path):
                return Path(path)
        return None
    
    @staticmethod
    def _get_python_version() -> str:
        """获取当前 Python 版本号（如 310, 38）"""
        return f"{sys.version_info.major}{sys.version_info.minor}"
    
    def _log(self, msg: str, level: str = "info"):
        """输出日志"""
        if self.verbose:
            getattr(logger, level)(msg)
            print(msg)
    
    def check(self) -> dict:
        """
        检查环境状态，返回检查报告

        Returns:
            dict: 包含各项检查结果
        """
        results = {}
        
        # 检查 iDesktopX
        results["idesktop_found"] = self.idesktop_dir is not None
        results["idesktop_path"] = str(self.idesktop_dir) if self.idesktop_dir else "未找到"
        
        if self.idesktop_dir:
            results["bin_dir_exists"] = (self.idesktop_dir / "bin").exists()
            results["jre_exists"] = self.jre_bin.exists()
            
            # 检查 iObjectsPy 包
            results["iobjectspy_dir"] = str(self.iobjectspy_dir)
            results["iobjectspy_exists"] = self.iobjectspy_dir.exists()
            
            # 如果当前版本不存在，尝试回退
            if not self.iobjectspy_dir.exists():
                fallback = self.bin_python_dir / "iobjectspy" / "iobjectspy-py310_64"
                results["iobjectspy_fallback"] = str(fallback)
                results["iobjectspy_fallback_exists"] = fallback.exists()
            
            # 检查 Py4J
            results["py4j_dir_exists"] = self.py4j_dir.exists()
        
        # 检查 iObjectsJava
        results["iobjects_java_found"] = self.iobjects_java_dir is not None
        results["iobjects_java_path"] = str(self.iobjects_java_dir) if self.iobjects_java_dir else "未找到"
        
        if self.iobjects_java_dir:
            lib_dir = self.iobjects_java_dir / "lib"
            libx64_dir = self.iobjects_java_dir / "libx64"
            results["iobjects_java_lib_exists"] = lib_dir.exists()
            results["iobjects_java_libx64_exists"] = libx64_dir.exists()
            
            # 计算 JAR 文件数量
            if lib_dir.exists():
                jar_count = len(list(lib_dir.glob("*.jar")))
                results["iobjects_java_jar_count"] = jar_count
        
        # 检查 License
        license_dir = Path(
            os.environ.get("SUPERMAP_LICENSE", r"C:\Program Files\Common Files\SuperMap\License")
        )
        results["license_dir"] = str(license_dir)
        results["license_dir_exists"] = license_dir.exists()
        
        if license_dir.exists():
            license_files = (
                list(license_dir.glob("*.lic")) +
                list(license_dir.glob("*.licx")) +
                list(license_dir.glob("*.lic12")) +
                list(license_dir.glob("*.udlx"))
            )
            results["license_files_count"] = len(license_files)
        
        # 检查 iObjectsPy 是否可导入
        try:
            import importlib.util
            spec = importlib.util.find_spec("iobjectspy")
            results["iobjectspy_importable"] = spec is not None
            results["iobjectspy_module_path"] = spec.origin if spec else "无法找到"
        except Exception as e:
            results["iobjectspy_importable"] = False
            results["iobjectspy_import_error"] = str(e)
        
        return results
    
    def print_check_report(self):
        """打印环境检查报告"""
        results = self.check()
        
        print("\n" + "=" * 60)
        print("SuperMap 环境检查报告")
        print("=" * 60)
        
        print("\n📁 iDesktopX 安装:")
        status = "✓" if results["idesktop_found"] else "✗"
        print(f"  {status} 路径: {results['idesktop_path']}")
        
        if results["idesktop_found"]:
            print(f"  {'✓' if results['bin_dir_exists'] else '✗'} bin 目录")
            print(f"  {'✓' if results['jre_exists'] else '✗'} JRE 目录")
            print(f"  {'✓' if results['iobjectspy_exists'] else '✗'} iObjectsPy ({results['iobjectspy_dir']})")
            print(f"  {'✓' if results['py4j_dir_exists'] else '✗'} Py4J 库")
        
        print("\n📁 iObjectsJava:")
        status = "✓" if results["iobjects_java_found"] else "✗"
        print(f"  {status} 路径: {results['iobjects_java_path']}")
        
        if results["iobjects_java_found"]:
            print(f"  {'✓' if results.get('iobjects_java_lib_exists', False) else '✗'} lib 目录")
            print(f"  {'✓' if results.get('iobjects_java_libx64_exists', False) else '✗'} libx64 目录")
            jar_count = results.get("iobjects_java_jar_count", 0)
            print(f"  ℹ  JAR 文件数: {jar_count}")
        
        print("\n📄 License:")
        status = "✓" if results["license_dir_exists"] else "✗"
        print(f"  {status} 目录: {results['license_dir']}")
        if results["license_dir_exists"]:
            lic_count = results.get("license_files_count", 0)
            print(f"  {'✓' if lic_count > 0 else '⚠'} License 文件数: {lic_count}")
        
        print("\n🐍 iObjectsPy 模块:")
        status = "✓" if results["iobjectspy_importable"] else "✗"
        print(f"  {status} 可导入: {results.get('iobjectspy_module_path', '')}")
        if not results["iobjectspy_importable"]:
            print(f"  ⚠  错误: {results.get('iobjectspy_import_error', '未知')}")
        
        print("\n" + "=" * 60)
    
    def setup_iobjectspy_path(self) -> bool:
        """
        将 iObjectsPy 添加到 sys.path

        Returns:
            bool: 成功返回 True
        """
        if not self.idesktop_dir:
            self._log("✗ 未找到 iDesktopX 安装目录", "error")
            return False
        
        # 选择最合适的 iObjectsPy 版本
        target_dir = self.iobjectspy_dir
        if not target_dir.exists():
            # 回退到 Python 3.10
            fallback = self.bin_python_dir / "iobjectspy" / "iobjectspy-py310_64"
            if fallback.exists():
                target_dir = fallback
                self._log(f"⚠  当前 Python{self.python_version} 版本不存在，回退到 py310")
            else:
                # 搜索所有可用版本
                available = list((self.bin_python_dir / "iobjectspy").glob("iobjectspy-py*_64"))
                if available:
                    target_dir = available[0]
                    self._log(f"ℹ  使用可用版本: {target_dir.name}")
                else:
                    self._log("✗ 未找到任何 iObjectsPy 版本", "error")
                    return False
        
        # 添加到 sys.path
        paths_to_add = [
            str(target_dir),
            str(self.bin_python_dir),
        ]
        
        # 添加 Py4J
        if self.py4j_dir.exists():
            paths_to_add.append(str(self.py4j_dir))
        
        for path in reversed(paths_to_add):  # 反向插入以保持优先级
            if path not in sys.path:
                sys.path.insert(0, path)
        
        self._log(f"✓ iObjectsPy 路径已添加: {target_dir}")
        return True
    
    def setup_java_env(self, use_iobjects_java: bool = False) -> bool:
        """
        配置 Java 相关环境变量

        Args:
            use_iobjects_java: True = 使用 iObjectsJava 独立组件，False = 使用 iDesktopX 内置 JRE

        Returns:
            bool: 成功返回 True
        """
        if use_iobjects_java:
            # 方案 2：使用 iObjectsJava 独立组件
            if not self.iobjects_java_dir:
                self._log("✗ 未找到 iObjectsJava，请设置 IOBJECTS_JAVA_HOME 环境变量", "error")
                return False
            
            libx64_dir = self.iobjects_java_dir / "libx64"
            lib_dir = self.iobjects_java_dir / "lib"
            
            # 构建 CLASSPATH（包含所有 JAR）
            classpath = []
            if lib_dir.exists():
                for jar in lib_dir.glob("*.jar"):
                    classpath.append(str(jar))
            
            if classpath:
                existing_cp = os.environ.get("CLASSPATH", "")
                new_cp = os.pathsep.join(classpath)
                os.environ["CLASSPATH"] = new_cp + (os.pathsep + existing_cp if existing_cp else "")
                self._log(f"✓ CLASSPATH 已设置（{len(classpath)} 个 JAR）")
            
            # 添加 libx64 到 PATH（本地 DLL）
            if libx64_dir.exists():
                current_path = os.environ.get("PATH", "")
                os.environ["PATH"] = str(libx64_dir) + os.pathsep + current_path
                self._log(f"✓ libx64 已添加到 PATH: {libx64_dir}")
        
        else:
            # 方案 1：使用 iDesktopX 内置 JRE
            if not self.idesktop_dir:
                return False
            
            if self.jre_bin.exists():
                # 设置 JAVA_HOME
                os.environ["JAVA_HOME"] = str(self.idesktop_dir / "jre")
                
                # 添加 JRE bin 到 PATH
                current_path = os.environ.get("PATH", "")
                if str(self.jre_bin) not in current_path:
                    os.environ["PATH"] = str(self.jre_bin) + os.pathsep + current_path
                
                self._log(f"✓ Java 环境配置（iDesktopX JRE）: {self.jre_bin}")
            else:
                self._log(f"⚠  JRE 目录不存在: {self.jre_bin}，使用系统 Java")
        
        return True
    
    def init(self, use_iobjects_java: bool = False) -> Optional[object]:
        """
        完整初始化：配置所有路径 + 初始化 iObjectsPy

        Args:
            use_iobjects_java: True = 使用 iObjectsJava 独立运行，False = 使用 iDesktopX

        Returns:
            iobjectspy 模块实例，失败返回 None
        """
        self._log("\n🚀 正在初始化 SuperMap 环境...")
        
        # 步骤 1：添加 iObjectsPy 到 sys.path
        if not self.setup_iobjectspy_path():
            self._log("✗ 初始化失败：无法设置 iObjectsPy 路径", "error")
            return None
        
        # 步骤 2：配置 Java 环境
        self.setup_java_env(use_iobjects_java=use_iobjects_java)
        
        # 步骤 3：导入 iObjectsPy
        try:
            import iobjectspy as spy
            
            # 步骤 4：设置 iObjects Java 路径
            if use_iobjects_java and self.iobjects_java_dir:
                java_path = str(self.iobjects_java_dir / "libx64")
            else:
                java_path = str(self.bin_dir)
            
            spy.set_iobjects_java_path(java_path)
            
            self._log(f"✓ iObjectsPy 初始化成功")
            self._log(f"  版本: {spy.__version__}")
            self._log(f"  Java 路径: {java_path}")
            
            return spy
        
        except ImportError as e:
            self._log(f"✗ 无法导入 iObjectsPy: {e}", "error")
            self._log(f"  请先安装 iObjectsPy:")
            if self.idesktop_dir:
                self._log(f"    cd {self.bin_python_dir}")
                self._log(f"    pip install .")
            return None
        
        except Exception as e:
            self._log(f"✗ iObjectsPy 初始化失败: {e}", "error")
            return None


# =============================================================
# 模块级别的快速初始化（直接 import 时自动执行）
# =============================================================

def _auto_init():
    """模块被 import 时自动初始化"""
    env = SuperMapEnv(verbose=True)
    spy = env.init(use_iobjects_java=False)
    
    if spy is None:
        # 尝试使用 iObjectsJava
        print("→ 尝试使用 iObjectsJava 方案...")
        spy = env.init(use_iobjects_java=True)
    
    if spy is None:
        print("\n⚠  自动初始化失败。请手动配置 SuperMapEnv:")
        print('    from supermap_env_config import SuperMapEnv')
        print('    env = SuperMapEnv(idesktop_dir=r"你的安装路径")')
        print('    spy = env.init()')
    
    return spy


# 在 import 时自动执行（非直接运行时）
if __name__ != "__main__":
    _auto_init()


# =============================================================
# 直接运行：检查环境
# =============================================================

if __name__ == "__main__":
    """
    直接运行此脚本以检查环境状态：
        python supermap_env_config.py
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="SuperMap 环境配置与检查工具")
    parser.add_argument("--check", action="store_true", help="仅检查环境，不初始化")
    parser.add_argument("--iobjects-java", action="store_true", help="使用 iObjectsJava 独立方案")
    parser.add_argument("--idesktop", type=str, help="iDesktopX 安装路径")
    parser.add_argument("--iobjects", type=str, help="iObjectsJava 安装路径")
    args = parser.parse_args()
    
    env = SuperMapEnv(
        idesktop_dir=args.idesktop,
        iobjects_java_dir=args.iobjects,
        verbose=True
    )
    
    if args.check:
        env.print_check_report()
    else:
        # 初始化
        spy = env.init(use_iobjects_java=args.iobjects_java)
        
        if spy:
            print(f"\n✓ 初始化成功！iObjectsPy 版本: {spy.__version__}")
            print("\n现在可以在代码中这样使用:")
            print("    import supermap_env_config  # 自动初始化")
            print("    import iobjectspy as spy    # 直接使用")
        else:
            print("\n✗ 初始化失败，请查看上方的错误信息")
            print("\n运行以下命令查看详细环境报告:")
            print("    python supermap_env_config.py --check")
            sys.exit(1)

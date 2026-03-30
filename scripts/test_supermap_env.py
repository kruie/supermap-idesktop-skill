#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SuperMap Python 环境完整测试脚本
=================================

功能：验证 SuperMap 环境的所有关键配置是否正常

使用方式：
    python test_supermap_env.py
    
或导入使用：
    from test_supermap_env import TestSuperMapEnv
    tester = TestSuperMapEnv()
    report = tester.run_all_tests()
"""

import os
import sys
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Optional


@dataclass
class TestResult:
    """单项测试结果"""
    name: str
    passed: bool
    message: str
    details: Optional[str] = None


class TestSuperMapEnv:
    """SuperMap 环境完整测试套件"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.results: List[TestResult] = []
    
    def _print(self, msg: str):
        if self.verbose:
            print(msg)
    
    def _test(self, name: str, condition: bool, message: str, details: str = None) -> TestResult:
        """记录一个测试结果"""
        status = "✓" if condition else "✗"
        self._print(f"  {status} {message}")
        result = TestResult(name, condition, message, details)
        self.results.append(result)
        return result
    
    # ============================================================
    # 【测试组 1】基础 Python 环境
    # ============================================================
    def test_python_version(self):
        """检查 Python 版本"""
        self._print("\n【测试组 1】基础 Python 环境")
        
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        passed = version.major >= 3 and version.minor >= 6
        
        self._test(
            "python_version",
            passed,
            f"Python 版本: {version_str}",
            f"兼容版本为 3.6+，推荐 3.8+。当前版本为 {version_str}。"
        )
    
    def test_pip_available(self):
        """检查 pip 是否可用"""
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            passed = result.returncode == 0
            message = result.stdout.split('\n')[0] if passed else "pip 不可用"
        except Exception as e:
            passed = False
            message = str(e)
        
        self._test("pip_available", passed, f"pip: {message}")
    
    # ============================================================
    # 【测试组 2】iDesktopX 环装
    # ============================================================
    def test_idesktop_path(self):
        """检查 iDesktopX 安装目录"""
        self._print("\n【测试组 2】iDesktopX 安装")
        
        candidates = [
            os.environ.get("IDESKTOP_HOME"),
            r"D:\software\supermap-idesktopx-2025-windows-x64-bin",
            r"C:\SuperMap\iDesktopX-2025",
        ]
        
        for path in candidates:
            if path and os.path.exists(path):
                self._test("idesktop_path", True, f"iDesktopX 目录: {path}")
                return path
        
        self._test("idesktop_path", False, "iDesktopX 目录未找到")
        return None
    
    def test_idesktop_structure(self, idesktop_dir: str):
        """检查 iDesktopX 目录结构"""
        if not idesktop_dir:
            return
        
        paths_to_check = {
            "bin": "Java 核心库",
            "bin_python": "Python 绑定",
            "jre\\bin": "内置 JRE",
            "support\\PythonLib\\py4j": "Py4J 库",
        }
        
        for subpath, desc in paths_to_check.items():
            full_path = os.path.join(idesktop_dir, subpath)
            exists = os.path.exists(full_path)
            self._test(f"idesktop_{subpath.replace(chr(92), '_')}", exists, f"{desc}: {'存在' if exists else '缺失'}")
    
    # ============================================================
    # 【测试组 3】iObjectsPy 配置
    # ============================================================
    def test_iobjectspy_installed(self):
        """检查 iObjectsPy 是否已安装"""
        self._print("\n【测试组 3】iObjectsPy 配置")
        
        try:
            import iobjectspy
            self._test(
                "iobjectspy_installed",
                True,
                f"iObjectsPy 已安装（版本 {iobjectspy.__version__}）"
            )
            return True
        except ImportError:
            self._test(
                "iobjectspy_installed",
                False,
                "iObjectsPy 未安装",
                "需要运行: cd <iDesktopX>/bin_python && pip install ."
            )
            return False
    
    def test_iobjectspy_importable(self):
        """检查 iObjectsPy 是否能在脚本中导入"""
        try:
            import importlib.util
            spec = importlib.util.find_spec("iobjectspy")
            passed = spec is not None
            message = f"位置: {spec.origin}" if passed else "模块未找到"
        except Exception as e:
            passed = False
            message = str(e)
        
        self._test("iobjectspy_importable", passed, f"iObjectsPy 可导入: {message}")
    
    # ============================================================
    # 【测试组 4】Java 环境
    # ============================================================
    def test_java_path(self):
        """检查 Java 环境变量"""
        self._print("\n【测试组 4】Java 环境")
        
        java_home = os.environ.get("JAVA_HOME")
        passed = java_home is not None
        message = java_home if passed else "未设置 JAVA_HOME"
        
        self._test("java_home", passed, f"JAVA_HOME: {message}")
        
        # 尝试调用 java -version
        try:
            result = subprocess.run(
                ["java", "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            java_ver = result.stderr.split('\n')[0] if result.returncode == 0 else None
            passed_exec = result.returncode == 0
            message_exec = f"java 可执行（{java_ver}）" if passed_exec else "java 不可执行"
        except Exception as e:
            passed_exec = False
            message_exec = f"无法执行 java: {e}"
        
        self._test("java_executable", passed_exec, message_exec)
    
    # ============================================================
    # 【测试组 5】License 配置
    # ============================================================
    def test_license_path(self):
        """检查 License 文件"""
        self._print("\n【测试组 5】License 配置")
        
        license_dir = Path(
            os.environ.get("SUPERMAP_LICENSE", r"C:\Program Files\Common Files\SuperMap\License")
        )
        
        exists = license_dir.exists()
        self._test("license_dir_exists", exists, f"License 目录: {license_dir}")
        
        if exists:
            # 查找 license 文件
            patterns = ["*.lic", "*.licx", "*.lic12", "*.udlx"]
            files = []
            for pattern in patterns:
                files.extend(license_dir.glob(pattern))
            
            passed = len(files) > 0
            message = f"找到 {len(files)} 个 license 文件"
            self._test("license_files", passed, message)
            
            if files:
                for f in files[:3]:
                    self._print(f"    - {f.name}")
                if len(files) > 3:
                    self._print(f"    ... 还有 {len(files) - 3} 个文件")
    
    # ============================================================
    # 【测试组 6】集成测试
    # ============================================================
    def test_iobjectspy_integration(self):
        """完整的 iObjectsPy 集成测试"""
        self._print("\n【测试组 6】集成测试")
        
        try:
            import iobjectspy as spy
            
            # 创建 Workspace 对象
            from iobjectspy import Workspace
            ws = Workspace()
            
            self._test(
                "iobjectspy_workspace",
                ws is not None,
                "iObjectsPy Workspace 创建成功"
            )
            
            # 关闭 workspace
            ws.close()
        
        except ImportError:
            self._test(
                "iobjectspy_integration",
                False,
                "iObjectsPy 未安装，跳过集成测试"
            )
        
        except Exception as e:
            self._test(
                "iobjectspy_integration",
                False,
                f"集成测试失败: {e}"
            )
    
    # ============================================================
    # 【测试组 7】环境变量
    # ============================================================
    def test_environment_vars(self):
        """检查关键环境变量"""
        self._print("\n【测试组 7】环境变量")
        
        env_vars = {
            "PATH": "系统 PATH",
            "JAVA_HOME": "Java 主目录",
            "CLASSPATH": "Java 类路径",
            "IDESKTOP_HOME": "iDesktopX 主目录",
            "SUPERMAP_LICENSE": "SuperMap License 目录",
            "SUPERMAP_IOBJECTSPY_PATH": "iObjectsPy 路径",
            "SUPERMAP_JAVA_PATH": "SuperMap Java 路径",
        }
        
        for var, desc in env_vars.items():
            value = os.environ.get(var)
            passed = value is not None
            message = desc + (f": 已设置 ({len(value)} 字符)" if passed else ": 未设置")
            self._test(f"env_{var}", passed, message)
    
    # ============================================================
    # 报告生成
    # ============================================================
    def run_all_tests(self) -> Dict:
        """运行所有测试"""
        self._print("\n" + "=" * 60)
        self._print("SuperMap Python 环境完整测试")
        self._print("=" * 60)
        
        # 测试 1-2：基础
        self.test_python_version()
        self.test_pip_available()
        
        # 测试 3-4：iDesktopX
        idesktop_dir = self.test_idesktop_path()
        if idesktop_dir:
            self.test_idesktop_structure(idesktop_dir)
        
        # 测试 5-7：iObjectsPy 和 Java
        self.test_iobjectspy_installed()
        self.test_iobjectspy_importable()
        self.test_java_path()
        
        # 测试 8-9：License 和集成
        self.test_license_path()
        self.test_iobjectspy_integration()
        
        # 测试 10：环境变量
        self.test_environment_vars()
        
        # 生成报告
        return self.generate_report()
    
    def generate_report(self) -> Dict:
        """生成测试报告"""
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        report = {
            "total": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": f"{(passed / total * 100):.1f}%",
            "results": self.results,
            "summary": self._get_summary()
        }
        
        self._print_report(report)
        return report
    
    def _get_summary(self) -> str:
        """获取总结信息"""
        failed = [r for r in self.results if not r.passed]
        
        if not failed:
            return "✓ 所有测试通过！环境配置正常。"
        
        messages = []
        for r in failed[:3]:  # 最多显示 3 个失败
            messages.append(f"  - {r.name}: {r.message}")
        
        if len(failed) > 3:
            messages.append(f"  ... 还有 {len(failed) - 3} 个失败")
        
        return "✗ 某些配置有问题:\n" + "\n".join(messages)
    
    def _print_report(self, report: Dict):
        """打印最终报告"""
        self._print("\n" + "=" * 60)
        self._print(f"测试结果: {report['passed']}/{report['total']} 通过（{report['pass_rate']}）")
        self._print("=" * 60)
        self._print(report["summary"])
        self._print("=" * 60 + "\n")


def main():
    """主入口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="SuperMap Python 环境测试工具")
    parser.add_argument("-q", "--quiet", action="store_true", help="仅输出最终结果")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式报告")
    args = parser.parse_args()
    
    tester = TestSuperMapEnv(verbose=not args.quiet)
    report = tester.run_all_tests()
    
    if args.json:
        import json
        
        # 转换为可序列化的格式
        json_report = {
            "total": report["total"],
            "passed": report["passed"],
            "failed": report["failed"],
            "pass_rate": report["pass_rate"],
            "summary": report["summary"],
            "results": [
                {
                    "name": r.name,
                    "passed": r.passed,
                    "message": r.message,
                    "details": r.details
                }
                for r in report["results"]
            ]
        }
        print("\n" + json.dumps(json_report, indent=2, ensure_ascii=False))
    
    # 返回退出码
    return 0 if report["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

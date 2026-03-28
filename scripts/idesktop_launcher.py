"""
SuperMap iDesktop 启动与进程管理脚本
用途：启动、检测、关闭 iDesktopX 进程
"""

import subprocess
import time
import os
import sys

# 【配置项】修改为你本机的 iDesktopX 安装路径
# 也可通过环境变量 IDESKTOP_HOME 指定（优先）
IDESKTOP_DIR = os.environ.get("IDESKTOP_HOME", r"C:\SuperMap\iDesktopX-2025")
STARTUP_BAT = os.path.join(IDESKTOP_DIR, "startup.bat")


def is_idesktop_running() -> bool:
    """检测 iDesktopX 是否正在运行（通过 java 进程判断）"""
    result = subprocess.run(
        ["tasklist", "/FI", "IMAGENAME eq java.exe", "/FO", "CSV"],
        capture_output=True, text=True, encoding="gbk"
    )
    # iDesktopX 是 Java 程序，检查 java 进程的命令行中是否含 iDesktop
    result2 = subprocess.run(
        ["wmic", "process", "where", "name='java.exe'", "get", "CommandLine"],
        capture_output=True, text=True, encoding="gbk"
    )
    return "iDesktop" in result2.stdout or "supermap" in result2.stdout.lower()


def launch_idesktop(idesktop_dir: str = None,
                    wait_seconds: int = 30,
                    headless: bool = False) -> subprocess.Popen:
    """
    启动 iDesktopX
    
    Args:
        idesktop_dir: iDesktopX 安装目录
        wait_seconds: 等待启动完成的秒数
        headless: 是否无界面模式（暂不支持，预留）
    
    Returns:
        subprocess.Popen 进程对象
    """
    if idesktop_dir is None:
        idesktop_dir = IDESKTOP_DIR
    startup_bat = os.path.join(idesktop_dir, "startup.bat")
    if not os.path.exists(startup_bat):
        raise FileNotFoundError(f"未找到启动脚本：{startup_bat}")
    
    print(f"正在启动 iDesktopX...")
    print(f"  目录: {idesktop_dir}")
    
    proc = subprocess.Popen(
        startup_bat,
        cwd=idesktop_dir,
        shell=True,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    
    print(f"  进程已启动（PID: {proc.pid}），等待 {wait_seconds} 秒加载...")
    time.sleep(wait_seconds)
    print("✓ iDesktopX 启动完成")
    return proc


def kill_idesktop():
    """强制关闭所有 iDesktopX 相关进程"""
    killed = []
    for proc_name in ["java.exe"]:
        result = subprocess.run(
            ["taskkill", "/F", "/IM", proc_name, "/T"],
            capture_output=True, text=True, encoding="gbk"
        )
        if "成功" in result.stdout or "SUCCESS" in result.stdout.upper():
            killed.append(proc_name)
    
    if killed:
        print(f"✓ 已关闭进程: {killed}")
    else:
        print("未找到需要关闭的 iDesktopX 进程")


def run_python_script_in_idesktop(script_path: str,
                                   idesktop_dir: str = None):
    """
    使用 iDesktopX 内置 JRE 和 Python 环境运行脚本
    注意：此方式需要已安装 iObjectsPy
    
    Args:
        script_path: Python 脚本路径
        idesktop_dir: iDesktopX 安装目录
    """
    if idesktop_dir is None:
        idesktop_dir = IDESKTOP_DIR
    java_exe = os.path.join(idesktop_dir, "jre", "bin", "java.exe")
    bin_dir = os.path.join(idesktop_dir, "bin")
    
    print(f"通过 iDesktopX JRE 执行: {script_path}")
    result = subprocess.run(
        [sys.executable or "python", script_path],
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "JAVA_HOME": os.path.join(idesktop_dir, "jre")}
    )
    
    if result.stdout:
        print("输出：")
        print(result.stdout)
    if result.stderr:
        print("错误：")
        print(result.stderr)
    
    return result.returncode


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="iDesktopX 进程管理")
    parser.add_argument("action", choices=["start", "stop", "status"],
                        help="操作: start=启动, stop=关闭, status=检测状态")
    parser.add_argument("--wait", type=int, default=30,
                        help="启动等待时间（秒）")
    parser.add_argument("--dir", default=IDESKTOP_DIR,
                        help="iDesktopX 安装目录（默认从 IDESKTOP_HOME 环境变量读取）")
    args = parser.parse_args()
    
    if args.action == "start":
        launch_idesktop(args.dir, args.wait)
    elif args.action == "stop":
        kill_idesktop()
    elif args.action == "status":
        running = is_idesktop_running()
        print(f"iDesktopX 状态: {'运行中 ✓' if running else '未运行'}")

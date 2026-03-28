# SuperMap iDesktopX GUI 自动化操作指南

> 通过 pywinauto / pyautogui 控制 iDesktopX 界面，实现菜单点击、对话框操作等自动化任务。

## 前提条件

需要安装 GUI 自动化库（需要系统 Python 环境）：

```bash
pip install pywinauto pyautogui Pillow
```

---

## 1. 启动 iDesktop

### 方式 A：直接运行 startup.bat（推荐）

```python
import subprocess
import time

IDESKTOP_DIR = r"D:\software\supermap-idesktopx-2025-windows-x64-bin"
STARTUP_BAT = rf"{IDESKTOP_DIR}\startup.bat"

def launch_idesktop(wait_seconds=30):
    """启动 iDesktopX，等待其完全加载"""
    proc = subprocess.Popen(
        STARTUP_BAT,
        cwd=IDESKTOP_DIR,
        shell=True,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    print(f"iDesktopX 正在启动（PID: {proc.pid}）...")
    time.sleep(wait_seconds)
    return proc

proc = launch_idesktop(wait_seconds=30)
```

### 方式 B：用 pywinauto 启动并附加

```python
from pywinauto.application import Application
import time

app = Application(backend='uia').start(
    cmd_line=r"D:\software\supermap-idesktopx-2025-windows-x64-bin\startup.bat",
    work_dir=r"D:\software\supermap-idesktopx-2025-windows-x64-bin",
    wait_for_idle=False
)
time.sleep(30)  # 等待加载完成
```

### 方式 C：附加到已运行的 iDesktop

```python
from pywinauto.application import Application

# 按窗口标题附加（iDesktopX 窗口标题通常包含版本信息）
app = Application(backend='uia').connect(title_re=".*iDesktopX.*", timeout=10)
main_win = app.top_window()
print("已连接：", main_win.window_text())
```

---

## 2. 获取 iDesktop 主窗口

```python
from pywinauto import Desktop

# 列出所有顶级窗口（用于调试）
for win in Desktop(backend='uia').windows():
    print(win.window_text(), win.class_name())

# 获取 iDesktopX 主窗口
main_win = app.window(title_re=".*iDesktopX.*")
main_win.set_focus()
```

---

## 3. 菜单操作

iDesktopX 使用 Ribbon 菜单（类似 Office 风格），以下是常用菜单操作：

```python
# 点击菜单项（使用 pyautogui 截图+点击，更稳定）
import pyautogui
import time

# 点击"开始"选项卡
pyautogui.click(x=100, y=50)  # 坐标需根据实际屏幕调整
time.sleep(0.5)

# 使用 pywinauto 的菜单操作
main_win.menu_select("文件->打开工作空间")
```

---

## 4. 打开工作空间（GUI方式）

```python
import pyautogui
import time

def open_workspace_via_menu(smwu_path: str):
    """通过菜单打开工作空间"""
    # 点击"开始"选项卡
    main_win.set_focus()
    # 使用快捷键 Ctrl+O 打开文件对话框（如果支持）
    pyautogui.hotkey('ctrl', 'o')
    time.sleep(1)
    
    # 找到文件路径输入框，输入路径
    pyautogui.typewrite(smwu_path, interval=0.05)
    pyautogui.press('enter')
    time.sleep(3)
    print(f"工作空间 {smwu_path} 已打开")
```

---

## 5. 截图与视觉定位

```python
import pyautogui
from PIL import Image

def take_screenshot(save_path: str = None):
    """截取当前屏幕"""
    screenshot = pyautogui.screenshot()
    if save_path:
        screenshot.save(save_path)
    return screenshot

def find_and_click(image_template: str, confidence: float = 0.8):
    """在屏幕上找到图像模板并点击"""
    location = pyautogui.locateOnScreen(image_template, confidence=confidence)
    if location:
        pyautogui.click(pyautogui.center(location))
        return True
    return False

# 截图调试
take_screenshot(r"D:\debug\idesktop_screenshot.png")
```

---

## 6. 在 iDesktop Python 窗口中执行脚本

iDesktopX 内置 Python 窗口，可以直接执行脚本，这是**最稳定的自动化方式**：

```python
# 此代码在 iDesktopX Python 窗口中直接运行（不需要 pywinauto）
# 菜单路径：开始 → 浏览 → Python

# 获取当前工作空间（iDesktopX 内置对象）
from iobjectspy import *

# 在 Python 窗口中，iDesktopX 已经初始化好环境，可直接使用
ws = Workspace()
ds = ws.get_datasource(0)
dataset = ds.get_dataset("Countries")
print("数据集：", dataset.name, "要素数：", dataset.record_count)
```

### 通过脚本文件执行（推荐批量操作）

```python
# 步骤：
# 1. 将以下脚本保存为 .py 文件
# 2. 在 iDesktopX Python 窗口中点击"执行Python文件"
# 3. 选择该文件执行

import iobjectspy as spy

# 批量缓冲区分析
datasets = ["Cities", "Towns", "Villages"]
for name in datasets:
    spy.create_buffer(
        source_dataset=f'D:/data/world.udb/{name}',
        left_distance=1000,
        out_datasource='D:/output/result.udb',
        out_dataset=f'{name}_Buffer'
    )
    print(f"✓ {name} 缓冲区分析完成")
```

---

## 7. 常用 GUI 自动化操作模式

### 等待元素出现

```python
import time
from pywinauto import Desktop

def wait_for_window(title_re: str, timeout: int = 30):
    """等待指定标题的窗口出现"""
    start = time.time()
    while time.time() - start < timeout:
        wins = Desktop(backend='uia').windows(title_re=title_re)
        if wins:
            return wins[0]
        time.sleep(1)
    raise TimeoutError(f"窗口 '{title_re}' 未在 {timeout}s 内出现")
```

### 处理对话框

```python
def handle_dialog(expected_title: str, button_text: str = "确定"):
    """自动处理弹出对话框"""
    try:
        dialog = app.window(title_re=f".*{expected_title}.*")
        dialog.wait('visible', timeout=5)
        dialog.child_window(title=button_text, control_type="Button").click()
        return True
    except Exception:
        return False
```

---

## 8. 注意事项

1. **优先使用 iObjectsPy API**：对于数据处理任务，Python API 比 GUI 自动化更稳定、更快速
2. **GUI 自动化适用场景**：需要操作 iDesktop 独有界面功能（如地图编辑器、专题图向导等）
3. **坐标依赖屏幕分辨率**：pyautogui 坐标会随屏幕分辨率和窗口位置变化，建议用图像识别代替固定坐标
4. **iDesktopX 加载较慢**：启动后需等待 20-40 秒才能进行 GUI 操作
5. **Python 窗口脚本最稳定**：如果可以手动打开 iDesktop，直接在其 Python 窗口执行脚本是最可靠的方式

# SuperMap iDesktopX 环境配置指南

## 安装目录结构

SuperMap iDesktopX 的典型安装目录结构如下：

```
<安装根目录>/                          # 例：D:\software\supermap-idesktopx-2025-windows-x64-bin
├── bin/                               # Java核心库 & 本地DLL
├── bin_python/                        # iObjectsPy Python绑定
│   ├── iobjectspy/
│   │   ├── iobjectspy-py310_64/       # Python 3.10（推荐）
│   │   ├── iobjectspy-py39_64/        # Python 3.9
│   │   ├── iobjectspy-py38_64/        # Python 3.8
│   │   └── ...
│   ├── setup.py                       # 安装脚本
│   ├── requirements-conda-cpu.yml     # Conda CPU环境
│   └── requirements-conda-gpu.yml     # Conda GPU环境
├── jre/                               # 内置 OpenJDK（iDesktopX 自带，无需单独安装）
│   └── bin/java.exe
├── resources/
│   └── python-helpers/
│       └── python_toolkit/            # 内置Python工具包
├── support/
│   ├── PythonLib/py4j/                # py4j 通信库（iDesktopX内置Python用）
│   └── SuperMapLicenseCenter/         # 内置License管理中心
└── startup.bat                        # 启动脚本（Windows）
```

> **版本说明**：以下示例以 **iDesktopX 2025**（也称 11.x 系列最新版）为准，各版本路径结构相同，仅版本号不同。

---

## 启动 iDesktopX

### 标准启动

```bat
cd /d <安装根目录>
startup.bat
```

### 后台启动（不弹窗，适合脚本调用）

```bat
cd /d <安装根目录>
start /b startup.bat
```

---

## Java 环境

- **内置 JRE**：`<安装根目录>\jre\bin\java.exe`（OpenJDK 1.8.x 64位）
- `startup.bat` 会自动使用内置 JRE，**无需配置系统 JAVA_HOME**
- 若有系统级 JDK，不会干扰 iDesktopX 的运行

---

## Python / iObjectsPy 环境

### iObjectsPy 是什么

iObjectsPy 是 SuperMap Objects Java 的 Python 绑定层（基于 py4j），提供完整的 GIS 数据处理 API，可用于：
- 批量数据处理（导入/导出/转换）
- 空间分析自动化
- 地图制图脚本化

### 使用方式一：安装到已有 Python 环境（独立运行）

**前提**：本机已安装 Python 3.7 ~ 3.10（推荐 3.10），且拥有 iObjectsPy 独立 License。

```bash
cd <安装根目录>\bin_python
pip install .
```

安装后验证：

```python
import iobjectspy as spy
spy.set_iobjects_java_path(r"<安装根目录>\bin")
print(spy.__version__)
```

### 使用方式二：在 iDesktopX 内置 Python 窗口中运行（推荐）

无需额外 License，直接使用 iDesktopX 的授权：

1. 菜单栏 → **开始** → **浏览** → **Python**（打开内置 Python 窗口）
2. 工具栏点击 **「执行Python文件」** 按钮，选择脚本文件
3. 脚本中直接 `import iobjectspy as spy` 即可，无需手动初始化路径

内置 Python 环境说明：
- 内置 Python 版本随 iDesktopX 版本而定（通常为 3.8 ~ 3.10）
- py4j 通信库路径：`<安装根目录>\support\PythonLib\py4j`
- 工具包路径：`<安装根目录>\resources\python-helpers\python_toolkit`

### 使用方式三：通过 AI 扩展包（MiniConda）

若安装了 SuperMap AI 扩展包，扩展包内含 MiniConda：

```
<AI扩展包安装目录>\support\MiniConda\conda\python.exe
```

可使用该 Python 安装 iObjectsPy 并运行脚本（仍需 License 或在 iDesktopX 进程内）。

---

## License 管理

### License Center

SuperMap 提供独立的 License Center 应用管理授权：

- 启动：运行 `<LicenseCenter安装目录>\SuperMapLicenseCenter.exe`
- iDesktopX 也内置了 License Center：`<安装根目录>\support\SuperMapLicenseCenter\`
- License 类型：网络锁（可局域网共享）/ 单机锁（USB硬件锁）/ 在线激活

### iObjectsPy 独立运行 License

iObjectsPy 脱离 iDesktopX 进程独立运行时，需要额外的 **iObjects 组件 License**（`hasp_feature` 授权），与 iDesktopX 桌面版 License 不同。

**如无独立组件 License，建议在 iDesktopX 内置 Python 窗口中运行脚本**（复用 iDesktopX 桌面 License）。

---

## 版本兼容性说明

| iDesktopX 版本 | iObjectsPy 版本 | 推荐 Python |
|--------------|----------------|------------|
| 2025 (11.x)  | 11.x           | 3.10       |
| 11.2.x       | 11.2.x         | 3.8 ~ 3.10 |
| 11.1.x       | 11.1.x         | 3.7 ~ 3.9  |
| 11.0.x       | 11.0.x         | 3.7 ~ 3.8  |
| 10.x         | 10.x           | 3.6 ~ 3.7  |

> **注意**：iObjectsPy 版本须与 iDesktopX 版本一致（主版本号匹配），否则运行时会出现 DLL 找不到或 API 不兼容的问题。

---

## 常用环境变量

运行 iObjectsPy 脚本时，若出现 DLL 找不到报错，可在脚本开头手动设置 bin 路径：

```python
import iobjectspy as spy

IDESKTOP_BIN = r"<安装根目录>\bin"   # 替换为实际安装路径
spy.set_iobjects_java_path(IDESKTOP_BIN)
```

---

## 快速检查环境

```python
# 运行以下脚本验证 iObjectsPy 是否正常
import iobjectspy as spy
import os

print(f"iObjectsPy 版本: {spy.__version__}")
print(f"Python 版本: {__import__('sys').version}")

# 测试工作空间
from iobjectspy import Workspace
ws = Workspace()
print(f"工作空间创建成功: {ws is not None}")
ws.close()
print("环境检查通过")
```

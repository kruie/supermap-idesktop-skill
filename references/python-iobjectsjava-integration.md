# SuperMap iObjectsJava + Python 集成开发指南

## 问题分析：为什么 iDesktopX 内置 Python 有时找不到环境变量？

### 根本原因

iDesktopX 的 Python 集成基于 **Py4J**（Java-Python 网关框架）实现，工作流程如下：

```
┌─────────────────────────────────────────────────────────────┐
│                    iDesktopX 进程（Java）                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Python 窗口（内嵌的 Python 3.8～3.10）           │   │
│  ├─────────────────────────────────────────────────────┤   │
│  │  import iobjectspy as spy                          │   │
│  │       ↓                                              │   │
│  │  Py4J 网关客户端 ← → Py4J 服务器（Java侧）       │   │
│  │  (Python 进程)         (iDesktopX Java 进程)      │   │
│  │       ↓                                              │   │
│  │  iObjectsPy API（Java Objects 的 Python 绑定）    │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

**关键问题**：
1. **环境变量隔离**：内置 Python 运行在 iDesktopX 进程内，与系统 PATH 隔离
2. **路径解析错误**：脚本引用的外部工具（ffmpeg、gdal 等）可能找不到
3. **Py4J 通信中断**：Java 进程崩溃或环境变量不匹配导致网关断开

---

## 解决方案概述

### 方案对比

| 方案 | 适用场景 | 优点 | 缺点 |
|------|--------|------|------|
| **方案 1：iDesktopX Python 窗口（内置）** | 快速脚本、简单数据处理 | 无需 License、开箱即用 | 环境变量隔离、扩展困难 |
| **方案 2：通过 iObjectsJava 自建 Python 环境** | 生产环境、复杂工作流 | 环境完全控制、集成灵活 | 需要 License、配置复杂 |
| **方案 3：MCP + WorkBuddy（推荐）** | Agent 自动化、跨平台 | 标准化、可维护性强 | 需要理解 MCP 框架 |

---

## 方案 1：iDesktopX 内置 Python 窗口（优化版）

### 原理

iDesktopX 为 Python 脚本预配置了：
- py4j 通信库路径：`<安装目录>\support\PythonLib\py4j`
- iObjectsPy 模块路径：预加载到系统路径
- 自动 License 继承：无需单独配置

### 【推荐】快速入门步骤

1. **打开 Python 窗口**
   ```
   菜单栏 → 开始 → 浏览 → Python
   ```

2. **编写脚本并验证环境**
   ```python
   import sys
   import os
   
   # 检查 iObjectsPy 是否已加载
   try:
       import iobjectspy as spy
       print(f"✓ iObjectsPy 版本: {spy.__version__}")
   except ImportError as e:
       print(f"✗ 导入失败: {e}")
       sys.exit(1)
   
   # 检查外部工具环境变量（如需要）
   print(f"PATH: {os.environ.get('PATH', 'NOT SET')}")
   print(f"GDAL_DATA: {os.environ.get('GDAL_DATA', 'NOT SET')}")
   ```

3. **执行脚本**
   - 在 Python 窗口直接粘贴代码运行
   - 或点击工具栏「执行 Python 文件」加载 `.py` 脚本

### 解决环境变量问题

**问题**：外部工具（ffmpeg、gdal 等）找不到

**解决**：在脚本开头手动注入环境变量

```python
import os
import sys

# ========== 手动配置外部工具路径 ==========
# 方法 1：直接设置路径
os.environ['PATH'] = r"C:\tools\ffmpeg\bin" + os.pathsep + os.environ.get('PATH', '')
os.environ['GDAL_DATA'] = r"C:\tools\gdal\data"

# 方法 2：使用绝对路径调用工具
import subprocess
result = subprocess.run(
    [r"C:\tools\ffmpeg\bin\ffmpeg.exe", "-version"],
    capture_output=True,
    text=True
)
print(result.stdout)

# ========== 现在可以安全地导入 iObjectsPy ==========
import iobjectspy as spy

# 你的 GIS 脚本...
```

### 完整示例：批量处理 + 外部工具集成

```python
import os
import sys
import subprocess
from pathlib import Path

# 【第一步】配置环境
os.environ['GDAL_DATA'] = r"C:\osgeo4w\share\gdal"
os.environ['PROJ_LIB'] = r"C:\osgeo4w\share\proj"

# 【第二步】导入 iObjectsPy
import iobjectspy as spy
from iobjectspy import Workspace, DatasourceConnectionInfo, EngineType

# 【第三步】打开工作空间
ws = Workspace()
conn = DatasourceConnectionInfo()
conn.server = r"D:\data\project.udbx"
conn.engine_type = EngineType.UDBX
ds = spy.open_datasource(conn)

# 【第四步】GIS 数据处理
dataset = ds["cities"]
records = []
rs = dataset.get_recordset(True)
rs.move_first()
while not rs.is_EOF:
    name = rs.get_field_value("Name")
    geometry = rs.get_geometry()
    records.append({"name": name, "geom": geometry})
    rs.move_next()
rs.close()

# 【第五步】调用外部工具处理结果
for record in records:
    # 示例：使用 GDAL 工具处理
    result = subprocess.run(
        [r"C:\osgeo4w\bin\gdalinfo.exe", f"PG:host=localhost {record['name']}"],
        capture_output=True,
        text=True
    )
    print(result.stdout)

print(f"处理了 {len(records)} 个要素")
```

---

## 方案 2：通过 iObjectsJava 自建 Python 环境（推荐用于生产环境）

### 为什么要自建环境？

- ✅ **完全控制**：环境变量、依赖包、Python 版本
- ✅ **扩展性强**：可集成任意第三方库
- ✅ **调试能力强**：本地 IDE 支持、断点调试
- ✅ **自动化**：脚本可独立运行，无需打开 iDesktopX GUI

### 前置要求

1. **iObjectsJava 组件**
   - 路径：`D:\software\supermap-iobjectsjava-2025-win64-all-Bin`
   - 包含：Java JAR 包 + 本地库（DLL）

2. **Python 3.8 以上**
   - 推荐 Python 3.10（最稳定）
   - 或使用 MiniConda 中的 `python.exe`

3. **Py4J 库**
   ```bash
   pip install py4j
   ```

### 【实战】自建 Python 环境步骤

#### 步骤 1：识别 iObjectsJava 位置

```bash
# 确认以下目录结构存在
dir "D:\software\supermap-iobjectsjava-2025-win64-all-Bin"
    ├── lib\                          # 核心 JAR 包
    │   ├── SuperMap.iObjects.jar
    │   ├── *.jar
    │   └── ...
    ├── libx64\                       # 64位本地库（DLL）
    │   ├── jni_SuperMapJni.dll
    │   ├── SuperMapJava64.dll
    │   └── ...
    └── doc\                          # 文档
```

#### 步骤 2：创建 Python 虚拟环境（隔离依赖）

```bash
cd C:\Users\YourName\workspace
python -m venv idesktop-env

# 激活虚拟环境
idesktop-env\Scripts\activate  # Windows
# 或在 Linux: source idesktop-env/bin/activate

# 升级 pip
pip install --upgrade pip
```

#### 步骤 3：安装 iObjectsPy

```bash
# 从 iDesktopX 包中的 bin_python 安装
cd "D:\software\supermap-idesktopx-2025-windows-x64-bin\bin_python"
pip install .

# 验证安装
python -c "import iobjectspy; print(iobjectspy.__version__)"
```

#### 步骤 4：配置 Java 环境变量

创建文件 `supermap_env_config.py`：

```python
"""
SuperMap iObjectsJava + Python 环境配置脚本
在所有 iobjectspy 操作前执行此脚本
"""

import os
import sys
from pathlib import Path

# ========== 配置项 ==========
IOBJECTS_JAVA_HOME = r"D:\software\supermap-iobjectsjava-2025-win64-all-Bin"
IDESKTOP_JAVA_BIN = r"D:\software\supermap-idesktopx-2025-windows-x64-bin\bin"

# ========== 步骤 1：配置 Java 类路径 ==========
java_lib_dir = os.path.join(IOBJECTS_JAVA_HOME, "lib")
classpath = []
for jar_file in os.listdir(java_lib_dir):
    if jar_file.endswith(".jar"):
        classpath.append(os.path.join(java_lib_dir, jar_file))

os.environ["CLASSPATH"] = os.pathsep.join(classpath)

# ========== 步骤 2：配置 Java 库路径 ==========
libx64_dir = os.path.join(IOBJECTS_JAVA_HOME, "libx64")
current_path = os.environ.get("PATH", "")
os.environ["PATH"] = libx64_dir + os.pathsep + IDESKTOP_JAVA_BIN + os.pathsep + current_path

# 步骤 3：导入 iObjectsPy 并配置
import iobjectspy as spy
spy.set_iobjects_java_path(IDESKTOP_JAVA_BIN)

print("✓ SuperMap 环境配置成功")
print(f"  iObjectsJava: {IOBJECTS_JAVA_HOME}")
print(f"  Java Path: {IDESKTOP_JAVA_BIN}")
print(f"  CLASSPATH 条目数: {len(classpath)}")
```

#### 步骤 5：编写主脚本

创建文件 `gis_batch_process.py`：

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生产环境 GIS 批量处理脚本
使用自建 Python 环境 + iObjectsJava
"""

# 【第一步】导入环境配置（必须在最前面）
import supermap_env_config

# 【第二步】导入第三方库
import os
import sys
import logging
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

# 导入 iObjectsPy
import iobjectspy as spy
from iobjectspy import (
    Workspace, DatasourceConnectionInfo, EngineType,
    RecordsetType
)

# ========== 配置日志 ==========
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========== 批量处理函数 ==========
def process_dataset(datasource_path, dataset_name, output_dir):
    """
    处理单个数据集
    """
    try:
        # 打开数据源
        ds_conn = DatasourceConnectionInfo()
        ds_conn.server = datasource_path
        ds_conn.engine_type = EngineType.UDBX
        ds = spy.open_datasource(ds_conn)
        
        # 获取数据集
        if dataset_name not in ds:
            logger.warning(f"数据集 {dataset_name} 不存在")
            return None
        
        dataset = ds[dataset_name]
        
        # 统计要素
        recordset = dataset.get_recordset(RecordsetType.BRWS_EDITABLE)
        recordset.move_first()
        count = 0
        
        while not recordset.is_EOF:
            # 获取属性
            oid = recordset.get_field_value("SmID")
            name = recordset.get_field_value("Name") if "Name" in dataset.field_names else "N/A"
            
            # 你的处理逻辑...
            logger.info(f"处理要素 {oid}: {name}")
            
            recordset.move_next()
            count += 1
        
        recordset.close()
        logger.info(f"数据集 {dataset_name} 处理完成，共 {count} 条记录")
        
        # 导出结果
        output_path = os.path.join(output_dir, f"{dataset_name}_result.geojson")
        # spy.export_geojson(dataset, output_path)
        
        return {"dataset": dataset_name, "record_count": count, "output": output_path}
    
    except Exception as e:
        logger.error(f"处理 {dataset_name} 时出错: {e}", exc_info=True)
        return None

# ========== 主程序 ==========
def main():
    input_dir = r"D:\data\input"
    output_dir = r"D:\data\output"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # 找到所有 .udbx 文件
    udbx_files = list(Path(input_dir).glob("*.udbx"))
    logger.info(f"找到 {len(udbx_files)} 个数据源")
    
    # 批量处理（可并行）
    results = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = []
        for udbx_file in udbx_files:
            # 假设每个 .udbx 中有 "data" 数据集
            future = executor.submit(
                process_dataset,
                str(udbx_file),
                "data",
                output_dir
            )
            futures.append(future)
        
        for future in futures:
            result = future.result()
            if result:
                results.append(result)
    
    logger.info(f"批量处理完成，成功处理 {len(results)} 个数据集")
    return results

if __name__ == "__main__":
    main()
```

#### 步骤 6：运行脚本

```bash
# 激活虚拟环境
idesktop-env\Scripts\activate

# 运行脚本
python gis_batch_process.py

# 或后台运行（可选）
pythonw gis_batch_process.py
```

---

## 方案 3：通过 MCP Server 的标准化方案（推荐用于 Agent 自动化）

### MCP 架构下的优势

```
┌─────────────────────────────────────────────┐
│      WorkBuddy Agent / Claude               │
├─────────────────────────────────────────────┤
│   MCP 客户端                                │
│   ├─ mcp: tools/invoke                      │
│   └─ MCP 工具调用（自动路径处理）           │
├─────────────────────────────────────────────┤
│   MCP Server                                 │
│   (supermap_mcp_server.py)                  │
│   ├─ initialize_supermap (初始化)           │
│   ├─ iDesktopX 工具 (54 个)                 │
│   ├─ iServer 工具 (14 个)                   │
│   └─ 自动环境检测 + 路径标准化              │
├─────────────────────────────────────────────┤
│   iObjectsPy                                 │
│   (带自动环境配置)                          │
└─────────────────────────────────────────────┘
```

### MCP Server 核心特性

**自动环境变量处理**（在 `supermap_mcp_server.py` 中已实现）：

```python
# 反斜杠路径自动标准化（Windows 原生格式）
IOBJECTSPY_PATH = os.environ.get("SUPERMAP_IOBJECTSPY_PATH", ...).replace("/", "\\")
JAVA_PATH = os.environ.get("SUPERMAP_JAVA_PATH", ...).replace("/", "\\")
LICENSE_PATH = os.environ.get("SUPERMAP_LICENSE", ...).replace("/", "\\")

# 健康检查自动验证环境
def check_mcp_health():
    checks = {
        "iobjectspy_config_path": IOBJECTSPY_PATH,
        "iobjects_java_path": JAVA_PATH,
        "license_path": LICENSE_PATH,
        # ...更多检查
    }
```

### 如何使用 MCP 工具

**示例 1：通过 MCP 导入数据**

```python
# WorkBuddy Agent 中调用
result = await mcp_call("import_shapefile", {
    "source_path": "D:/data/cities.shp",
    "datasource_name": "output.udbx"
})

# MCP Server 自动：
# 1. 检查路径有效性
# 2. 配置 Java 环境
# 3. 调用 iObjectsPy
# 4. 返回结果
```

**示例 2：通过 MCP 执行空间分析**

```python
result = await mcp_call("create_buffer", {
    "source_datasource": "output.udbx",
    "source_dataset": "cities",
    "distance": 5000,
    "unit": "Meter",
    "out_dataset": "cities_buffer"
})
```

---

## 故障排查

### 问题 1：" hasp_feature_not_found" License 错误

**原因**：iObjectsPy 独立运行时需要单独的组件 License

**解决方案**：
```python
# 方案 A：在 iDesktopX Python 窗口中运行（推荐）
# → 自动继承 iDesktopX License

# 方案 B：使用 MCP Server 运行
# → MCP Server 在 iDesktopX License 下初始化

# 方案 C：申请 iObjects 组件 License
# → 联系 SuperMap 商务获取独立 License
```

### 问题 2："Python 找不到 Java"

**症状**：`RuntimeError: No module named 'py4j'` 或 `Java gateway process exited`

**排查步骤**：

```bash
# 1. 检查 Py4J 是否安装
pip list | findstr py4j

# 2. 检查 Java 路径是否正确
echo %JAVA_HOME%
dir "D:\software\supermap-idesktopx-2025-windows-x64-bin\bin\SuperMapJava64.dll"

# 3. 验证环境配置
python -c "import supermap_env_config"

# 4. 查看详细错误
python -c "import py4j; print(py4j.__version__)"
```

**解决**：

```python
import os
import sys

# 手动指定所有路径
JAVA_BIN = r"D:\software\supermap-idesktopx-2025-windows-x64-bin\bin"
os.environ["PATH"] = JAVA_BIN + os.pathsep + os.environ.get("PATH", "")

# 重新导入
import iobjectspy as spy
spy.set_iobjects_java_path(JAVA_BIN)
```

### 问题 3：内置 Python 窗口中外部工具找不到

**症状**：`FileNotFoundError: gdal_translate.exe not found`

**根本原因**：内置 Python 的 PATH 与系统 PATH 隔离

**解决**：

```python
import os
import subprocess

# 方案 1：绝对路径调用
result = subprocess.run([
    r"C:\osgeo4w\bin\gdal_translate.exe",
    "input.tif",
    "output.tif"
])

# 方案 2：手动注入 PATH
os.environ['PATH'] = r"C:\osgeo4w\bin" + os.pathsep + os.environ.get('PATH', '')
result = subprocess.run(["gdal_translate.exe", "input.tif", "output.tif"])

# 方案 3：迁移到自建 Python 环境（见方案 2）
```

---

## 总结与建议

### 快速决策树

```
你的需求是？

├─ 快速脚本 / 一次性任务
│  └─ 使用方案 1（iDesktopX 内置 Python 窗口）
│     ✓ 开箱即用，无需 License
│     ✓ 适合快速验证、学习
│
├─ 生产环境 / 独立运行 / 批量处理
│  └─ 使用方案 2（自建 Python 环境 + iObjectsJava）
│     ✓ 完全控制，可集成任意工具
│     ✓ 支持本地调试、定时任务、后台进程
│
└─ Agent 自动化 / WorkBuddy 集成
   └─ 使用方案 3（MCP Server）
      ✓ 标准化、可维护、跨平台
      ✓ 自动环境检测、错误恢复
```

### 检查清单

部署前使用以下清单验证环境：

- [ ] iDesktopX 已安装到 `D:\software\supermap-idesktopx-2025-windows-x64-bin`
- [ ] iObjectsJava 已安装到 `D:\software\supermap-iobjectsjava-2025-win64-all-Bin`
- [ ] Python 版本为 3.8+ (`python --version`)
- [ ] Py4J 已安装 (`pip list | findstr py4j`)
- [ ] 运行了 `supermap_env_config.py` 进行初始化
- [ ] License 文件在 `C:\Program Files\Common Files\SuperMap\License\`
- [ ] 测试脚本 `test_environment.py` 运行成功

### 推荐学习路径

1. **初学者**：方案 1（iDesktopX Python 窗口）
   - 阅读：本文档的"方案 1"章节
   - 实践：在 Python 窗口编写简单脚本

2. **中级用户**：方案 2（自建 Python 环境）
   - 阅读：本文档的"方案 2"章节 + `iobjectspy-api.md`
   - 实践：创建虚拟环境，运行独立脚本

3. **高级用户**：方案 3（MCP Server）
   - 阅读：MCP 文档 + 本文档的"方案 3"章节
   - 实践：编写 Agent 集成脚本

---

**版本**：2.0  
**更新日期**：2026-03-30  
**适配版本**：iDesktopX 2025 (11.x) + iObjectsJava 2025

# SuperMap iDesktopX Skill

基于 SuperMap iObjectsPy 和 MCP 的桌面端 GIS 数据处理自动化 Skill。

## 简介

本 Skill 为 WorkBuddy/Claude 提供 SuperMap iDesktopX 自动化能力，涵盖数据管理、空间分析、地图制图、三维分析等核心 GIS 功能。

## 功能

### 数据管理
- 数据源/数据集创建、删除、查询
- 数据导入导出（Shapefile、GeoJSON、KML、DXF 等）
- 格式转换、数据清洗

### 数据质量
- 拓扑检查（相交、重叠、空洞等）
- 属性校验（必填字段、唯一性、格式检查）
- 空间一致性检查

### 空间查询
- SQL 属性查询
- 空间关系查询（相交、包含、接触、缓冲区查询等）

### 空间分析
- 缓冲区分析
- 叠加分析（裁剪、合并、求交、求差）
- 临近分析、泰森多边形

### 地图制图
- 地图创建与图层管理
- 符号化（单值、分段、等级、标签）
- 图例、比例尺、指北针
- 地图输出为图片、PDF

### 三维分析
- 三维场景创建与管理
- 三维空间分析（通视分析、天际线、坡度坡向）
- 三维可视域分析、三维网络分析

## 依赖

### MCP 服务器
- **supermap-mcp-server** v3.0+：提供 50+ GIS 工具（需单独安装）

### Python 库
- iObjectsPy (SuperMap Python 组件)
- numpy, pandas, matplotlib

### 软件
- SuperMap iDesktopX 11i/12i

## 安装

### 1. 安装 MCP 服务器
```bash
# 将 supermap-mcp-server 添加到 WorkBuddy MCP 配置
```

### 2. 安装 Skill
```bash
# 克隆 Skill 到用户级目录
git clone https://github.com/kruie/supermap-idesktop-skill.git ~/.workbuddy/skills/
```

### 3. 配置环境
- 设置 SuperMap 许可证路径
- 配置 iObjectsPy 安装目录

## 使用

加载 Skill 后，可以直接在对话中使用自然语言描述 GIS 任务：

```
"帮我将 data.shp 导入到 udb 数据源中"
"对道路数据进行拓扑检查"
"创建一张人口分布地图，用分级符号表示"
```

## 目录结构

```
supermap-idesktop-skill/
├── SKILL.md              # Skill 主文档（决策树、工作流、FAQ）
├── scripts/              # 脚本工具
│   ├── idesktop_init.py        # 环境初始化（v2.0，支持 iObjectsJava 回退）
│   ├── supermap_env_config.py  # 完整环境检测与配置工具（NEW）
│   ├── test_supermap_env.py    # 环境测试脚本，输出 JSON 报告（NEW）
│   ├── idesktop_data.py        # 数据操作 API
│   ├── query_sql.py            # SQL 查询
│   ├── batch_process.py        # 批量处理
│   └── three_d_analysis.py     # 三维分析
├── references/           # 参考文档
│   ├── environment.md                       # 安装路径、License 配置
│   ├── python-iobjectsjava-integration.md  # iObjectsJava+Python 集成指南（NEW）
│   ├── gis-knowledge.md                    # GIS 知识
│   ├── iobjectspy-api.md                   # API 参考
│   ├── 3d-processing.md                    # 三维分析
│   ├── mapping-thematic.md                 # 地图制图
│   ├── data-quality.md                     # 数据质量检查
│   └── gui-automation.md                   # GUI 自动化
└── README.md
```

## Python 环境问题排查

### 常见问题：iDesktopX 内置 Python 环境变量找不到

iDesktopX 的内置 Python 窗口基于 **Py4J** 实现，与系统环境变量隔离。解决方案见 `references/python-iobjectsjava-integration.md`，提供三种方案：

| 方案 | 适用场景 |
|------|--------|
| **方案 1**：内置 Python 窗口（优化版） | 快速脚本、简单数据处理 |
| **方案 2**：通过 iObjectsJava 自建 Python 环境 | 生产环境、完全控制 |
| **方案 3**：MCP + WorkBuddy（推荐） | Agent 自动化 |

### 快速验证环境

```bash
# 测试当前环境配置
python scripts/test_supermap_env.py

# 输出 JSON 格式详细报告
python scripts/test_supermap_env.py --json
```

### iObjectsJava 路径（默认）

```
D:\software\supermap-iobjectsjava-2025-win64-all-Bin
```

如需使用不同路径，设置环境变量 `SUPERMAP_IOBJECTSJAVA_HOME` 覆盖默认值。

## 文档

详细使用指南请查看 `SKILL.md`：

- **决策树**: 指导如何选择合适的工具
- **工作流**: 10 个常见任务的标准流程
- **FAQ**: 常见问题解答（含 iObjectsJava 集成方案）

## 许可证

MIT License

## 作者

kruie

## 相关项目

- [supermap-mcp-server](https://github.com/kruie/supermap-mcp-server) - MCP 服务器
- [supermap-iserver-skill](https://github.com/kruie/supermap-iserver-skill) - iServer Skill
- [supermap-gis-agent](https://github.com/kruie/supermap-gis-agent) - GIS 智能体架构文档

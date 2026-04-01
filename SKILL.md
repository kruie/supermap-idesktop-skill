---
name: supermap-idesktop
description: This skill should be used when the user wants to operate, automate, or develop scripts for SuperMap iDesktopX GIS software. Covers: (1) Launching/managing iDesktopX; (2) Data management - workspace/datasource/dataset operations (UDB/UDBX/SMWU); (3) Data import/export in all formats (Shapefile, GeoJSON, KML, GeoTIFF, CSV, DWG, OSGB, S3M, LAS, IFC, etc.); (4) Spatial analysis - buffer, overlay/intersect/union/erase, clip, dissolve, kernel density, thiessen polygons, tabulate area; (5) Raster analysis - slope, aspect, interpolation, reclass, resample; (6) Network analysis - shortest path, service area; (7) 3D data processing - terrain/DEM, oblique photography (OSGB/S3M), point cloud (LAS), BIM (IFC), 3D scenes, visibility/sunlight/flood analysis; (8) Map cartography - thematic maps (single value, graduated, label, graph, heatmap), coordinate systems, projection conversion; (9) Batch data processing; (10) iObjectsPy Python API scripting; (11) GUI automation using pywinauto/pyautogui. Also covers GIS fundamentals: data sources, data organization, spatial indexing, coordinate systems, data versioning.
---

# SuperMap iDesktopX Skill

## ⚠️ 核心原则

**1. MCP 工具优先**: 所有可能的操作，首先检查是否有对应的 MCP 工具。
   - 有 MCP 工具 → 直接调用，不写 Python 脚本
   - 无 MCP 工具 → 使用 Skill scripts（scripts/ 目录）
   - scripts 不够 → 才考虑写 iObjectsPy 代码

**2. 禁止绕道**: 不要为了使用 MCP 工具而编写 Python 脚本来调用它。
   - ❌ 错误: 写 `supermap_mcp_client.py` 然后执行它
   - ✅ 正确: 直接通过 MCP 协议调用 `mcp_call_tool("import_shapefile", {...})`

**3. 失败降级**: MCP 工具调用失败时，按以下顺序降级：
   1. 检查参数是否正确
   2. 尝试 `check_mcp_health` 诊断
   3. 降级到 iObjectsPy API
   4. 向用户报告失败原因

---

## 快速开始 - 决策树

**Q: 你想做什么?** (使用下方决策树快速找到合适的工具)

```
数据导入/导出
├─ 单文件导入?
│   ├─ Shapefile → 使用 MCP: import_shapefile
│   ├─ GeoJSON → 使用 MCP: import_geojson
│   ├─ CSV → 使用 MCP: import_csv
│   ├─ TIFF (影像) → 使用 MCP: import_tiff
│   ├─ KML/KMZ → 使用 MCP: import_kml
│   ├─ DWG/DXF → 使用 MCP: import_dwg
│   └─ OSM → 使用 MCP: import_osm
├─ 单文件导出?
│   ├─ Shapefile → 使用 MCP: export_shapefile
│   ├─ GeoJSON → 使用 MCP: export_geojson
│   └─ TIFF → 使用 MCP: export_tiff
├─ 批量导入/导出?
│   └─ 使用 scripts/batch_process.py 或循环调用 MCP 工具
└─ 特殊格式 (OSGB/LAS/S3M)?
    └─ 使用 iObjectsPy API: spy.import_osgb / import_las

空间分析
├─ 缓冲区分析?
│   ├─ 单级缓冲 → MCP: create_buffer
│   └─ 多级缓冲 → MCP: create_multi_buffer
├─ 叠加分析?
│   ├─ 交集 → MCP: overlay (operation=INTERSECT)
│   ├─ 并集 → MCP: overlay (operation=UNION)
│   ├─ 裁剪 → MCP: clip_data
│   └─ 差集 → MCP: overlay (operation=ERASE)
├─ 融合 → MCP: dissolve
├─ 核密度分析 → MCP: kernel_density
├─ 插值分析?
│   ├─ 反距离权重 (IDW) → MCP: idw_interpolate
│   └─ 克里金 → MCP: kriging_interpolate
├─ DEM 分析?
│   ├─ 坡度 → MCP: calculate_slope
│   ├─ 坡向 → MCP: calculate_aspect
│   └─ 地形阴影 → MCP: calculate_hillshade
└─ 水文分析?
    ├─ 填洼 → MCP: fill_sink
    └─ 流域分析 → MCP: watershed

高级功能 (MCP 未覆盖)
├─ GUI 自动化 → references/gui-automation.md
├─ 3D 数据处理 → references/3d-processing.md
│   ├─ 三维场景操作
│   ├─ 地形/影像/倾斜摄影/点云/BIM
│   ├─ 三维分析 (12 种工具)
│   │   ├─ 可视域分析 → scripts/three_d_analysis.py: VisibilityAnalyzer
│   │   ├─ 通视分析 → scripts/three_d_analysis.py: VisibilityAnalyzer
│   │   ├─ 动态可视域 → scripts/three_d_analysis.py: VisibilityAnalyzer
│   │   ├─ 日照分析 → scripts/three_d_analysis.py: SunlightAnalyzer
│   │   ├─ 淹没分析 → scripts/three_d_analysis.py: FloodAnalyzer
│   │   ├─ 坡度坡向 → scripts/three_d_analysis.py: TerrainAnalyzer
│   │   ├─ 等值线 → scripts/three_d_analysis.py: TerrainAnalyzer
│   │   ├─ 地形剖面 → scripts/three_d_analysis.py: TerrainAnalyzer
│   │   ├─ 填挖方 → scripts/three_d_analysis.py: EarthworkAnalyzer
│   │   ├─ 天际线分析 → iObjectsPy API
│   │   └─ 视频投放 → iObjectsPy API
│   └─ 模型出图 (DSM/DOM/2.5D)
├─ 专题图制作 → references/mapping-thematic.md
├─ 数据质量检查 → references/data-quality.md
├─ SQL 属性查询 → scripts/query_sql.py
├─ 空间查询 → scripts/query_sql.py
└─ 工作空间管理 → MCP: open_workspace / save_workspace / get_workspace_info

坐标系统
├─ 查看坐标系 → MCP: get_coordinate_system
└─ 坐标转换 → MCP: reproject_dataset

数据集操作
├─ 创建数据集 → MCP: create_dataset
├─ 复制数据集 → MCP: copy_dataset
├─ 追加数据集 → MCP: append_to_dataset
├─ 添加字段 → MCP: add_field
└─ 计算字段 → MCP: calculate_field

几何转换
├─ 点转线 → MCP: dataset_point_to_line
├─ 线转面 → MCP: dataset_line_to_region
└─ 面转线 → MCP: dataset_region_to_line

地图制图（补充）
├─ 添加图层 → MCP: add_layer_to_map
├─ 导出地图图片 → MCP: export_map_image
└─ 生成瓦片 → MCP: generate_map_tiles [iServer]

工具函数
├─ 计算距离 → MCP: compute_distance
└─ 计算面积 → MCP: compute_geodesic_area

数据导入（补充）
└─ ESRI GDB → MCP: import_gdb

环境诊断
├─ 健康检查 → MCP: check_mcp_health
└─ 环境信息 → MCP: get_environment_info

地图制图
├─ 创建地图 → MCP: create_map
├─ 管理图层 → 打开 iDesktopX GUI
└─ 导出地图 → references/mapping-thematic.md

数据管理
├─ 数据质量检查?
│   ├─ 拓扑检查 → scripts/query_sql.py 或 iObjectsPy API
│   ├─ 几何错误修复 → references/data-quality.md
│   ├─ 重复要素删除 → MCP: query_dataset + delete_dataset
│   └─ 属性验证 → references/data-quality.md
└─ 空间查询?
    ├─ 属性查询筛选 → MCP: query_dataset (支持 SQL WHERE)
    ├─ 最近邻查询 → scripts/query_sql.py: query_nearest()
    ├─ 距离查询 → scripts/query_sql.py: query_by_distance()
    ├─ 多边形内查询 → scripts/query_sql.py: query_within_polygon()
    └─ 沿路径查询 → scripts/query_sql.py: query_along_path()
```

## 架构说明

SuperMap iDesktopX 自动化采用 **MCP + Skill 双层架构**:

```
┌─────────────────────────────────────────────────────┐
│           SuperMap iDesktopX 自动化体系              │
├─────────────────────────────────────────────────────┤
│                                                      │
│  MCP Server (核心工具层 - 已配置可用)                │
│  ├─ 68 个标准化工具（iDesktopX 58 + iServer 10）        │
│  ├─ 通过 mcp:// 前缀调用                            │
│  └─ 无需初始化,直接可用                              │
│                                                      │
│  Skill (智能指导层 - 本文档)                        │
│  ├─ 工作流指导: 串联 MCP 工具完成复杂任务           │
│  ├─ 决策支持: 帮助选择合适的工具和参数              │
│  ├─ 补充功能: MCP 未覆盖的高级功能                  │
│  ├─ examples/: 4 个典型场景示例 (buffer/overlay/DEM/batch)│
│  ├─ scripts/: 实用工具脚本和批处理                 │
│                                                      │
└─────────────────────────────────────────────────────┘
```

### MCP vs iObjectsPy API 何时使用?

| 场景 | 推荐方案 | 可用 MCP 工具 | 原因 |
|------|----------|-------------|------|
| 单步数据操作 (导入/导出) | **MCP 工具** | `import_*`, `export_*` | 参数清晰，结果可控 |
| 标准空间分析 (缓冲/叠加) | **MCP 工具** | `create_buffer`, `overlay` 等 14 个 | 无需写代码 |
| SQL 属性查询 | **MCP 工具** | `query_dataset` | 支持 WHERE/字段选择/排序/限制 |
| 数据集/字段管理 | **MCP 工具** | `create_dataset`, `add_field`, `calculate_field` | v3.0 新增 |
| 坐标系查看/转换 | **MCP 工具** | `get_coordinate_system`, `reproject_dataset` | v3.0 新增 |
| 工作空间操作 | **MCP 工具** | `open_workspace`, `save_workspace`, `get_workspace_info` | v3.0 新增 |
| 地图出图 | **MCP 工具** | `add_layer_to_map`, `export_map_image` | v3.0 新增 |
| 几何计算 | **MCP 工具** | `compute_distance`, `compute_geodesic_area` | v3.0 新增 |
| 空间关系查询 (相交/包含) | **Skill scripts** | `scripts/query_sql.py` | MCP 未覆盖空间查询 |
| 最近邻/距离/路径查询 | **Skill scripts** | `scripts/query_sql.py` | MCP 未覆盖 |
| 批量处理 (100+ 文件) | **iObjectsPy API** + 循环 | — | 灵活控制，性能更好 |
| 3D 数据处理 (OSGB/LAS/S3M) | **iObjectsPy API** | — | MCP 未覆盖 |
| 专题图制作 (符号化) | **iObjectsPy API** | — | MCP 未覆盖 |
| GUI 自动化 | **iDesktopX GUI** | — | 需要可视化交互 |

---

## 示例场景 (examples/)

| 编号 | 场景 | 难度 | 涉及工具 |
|------|------|------|---------|
| [01](examples/01_buffer_analysis.md) | 缓冲区分析 — POI 服务范围 | ⭐ | import_shapefile, create_buffer, query_dataset, export_geojson |
| [02](examples/02_overlay_analysis.md) | 叠加分析 — 土地适宜性评估 | ⭐⭐ | batch_import, overlay, clip_data, batch_export |
| [03](examples/03_dem_analysis.md) | DEM 地形分析 — 坡度适宜性 | ⭐⭐ | import_tiff, calculate_slope, reclassify, idw_interpolate |
| [04](examples/04_batch_processing.md) | 批量数据处理 — 多格式入库出库 | ⭐ | batch_import, batch_export, list_datasets, delete_dataset |

> 每个示例包含完整的 MCP 工具调用流程，可直接修改路径参数后使用。

---

## 常见工作流

### 工作流 1: 数据导入导出 (推荐初学者)

**场景**: 将 Shapefile 导入 UDBX 数据源,处理后导出为 GeoJSON

```
步骤 1: 导入数据
  → MCP: import_shapefile(
        source_path="D:/data/cities.shp",
        datasource_name="output.udbx"
      )

步骤 2: 查看数据集
  → MCP: list_datasets(
        datasource_name="output.udbx"
      )

步骤 3: (可选) 空间分析
  → MCP: create_buffer(
        source_datasource="output.udbx",
        source_dataset="cities",
        distance=5000,
        out_dataset="cities_buffer"
      )

步骤 4: 导出结果
  → MCP: export_geojson(
        datasource_name="output.udbx",
        dataset_name="cities_buffer",
        target_path="D:/output/cities_buffer.geojson"
      )
```

**批量处理版本**:
```python
# 使用 scripts/batch_process.py
from scripts.batch_process import batch_import, batch_export

# 批量导入目录下所有 .shp 文件
batch_import(
    source_dir="D:/data/input",
    datasource_name="output.udbx",
    pattern="*.shp"
)

# 批量导出所有数据集为 GeoJSON
batch_export(
    datasource_name="output.udbx",
    target_dir="D:/output",
    format="geojson"
)
```

---

### 工作流 2: 空间分析完整流程

**场景**: 找出距离城市 10km 范围内的道路

```
步骤 1: 数据准备
  ├─ 导入城市点 → MCP: import_shapefile(cities.shp)
  └─ 导入道路线 → MCP: import_shapefile(roads.shp)

步骤 2: 创建缓冲区
  → MCP: create_buffer(
        source_datasource="udbx",
        source_dataset="cities",
        distance=10000,
        unit="Meter",
        out_dataset="cities_buffer_10km"
      )

步骤 3: 叠加分析 (裁剪)
  → MCP: clip_data(
        source_datasource="udbx",
        source_dataset="roads",
        clip_datasource="udbx",
        clip_dataset="cities_buffer_10km",
        out_dataset="roads_in_city"
      )

步骤 4: 导出结果
  → MCP: export_shapefile(
        datasource_name="udbx",
        dataset_name="roads_in_city",
        target_path="D:/output/roads_in_city.shp"
      )
```

---

### 工作流 3: DEM 地形分析

**场景**: 从 DEM 影像计算坡度和坡向

```
步骤 1: 导入 DEM (TIFF)
  → MCP: import_tiff(
        source_path="D:/data/dem.tif",
        datasource_name="terrain.udbx",
        out_dataset="dem"
      )

步骤 2: 计算坡度
  → MCP: calculate_slope(
        source_datasource="terrain.udbx",
        source_dataset="dem",
        z_factor=1.0,
        unit="Degree",
        out_dataset="slope"
      )

步骤 3: 计算坡向
  → MCP: calculate_aspect(
        source_datasource="terrain.udbx",
        source_dataset="dem",
        out_dataset="aspect"
      )

步骤 4: 导出为 GeoTIFF
  → MCP: export_tiff(
        datasource_name="terrain.udbx",
        dataset_name="slope",
        target_path="D:/output/slope.tif"
      )
```

---

### 工作流 4: 点密度分析

**场景**: 分析 POI 点的空间分布密度

```
步骤 1: 导入 POI 点
  → MCP: import_csv(
        source_path="D:/data/poi.csv",
        x_field="lon",
        y_field="lat",
        datasource_name="poi.udbx"
      )

步骤 2: 核密度分析
  → MCP: kernel_density(
        source_datasource="poi.udbx",
        source_dataset="poi",
        search_radius=1000,
        cell_size=100,
        out_dataset="poi_density"
      )

步骤 3: (可选) 重分类
  → MCP: reclassify(
        source_datasource="poi.udbx",
        source_dataset="poi_density",
        reclass_table="低密度:0-10;中密度:10-50;高密度:50-9999",
        out_dataset="poi_density_classified"
      )
```

---

### 工作流 5: 多级缓冲区分析

**场景**: 创建 5km、10km、15km 三个级别的缓冲区

```
步骤 1: 导入数据
  → MCP: import_shapefile(
        source_path="D:/data/facilities.shp",
        datasource_name="buffer.udbx"
      )

步骤 2: 创建多级缓冲
  → MCP: create_multi_buffer(
        source_datasource="buffer.udbx",
        source_dataset="facilities",
        buffer_distances=[5000, 10000, 15000],
        unit="Meter",
        out_dataset="multi_buffer"
      )

步骤 3: 导出结果
  → MCP: export_geojson(
        datasource_name="buffer.udbx",
        dataset_name="multi_buffer",
        target_path="D:/output/multi_buffer.geojson"
      )
```

---

### 工作流 6: 三维可视域分析（监控布设）

**场景**: 为城市三维场景规划监控摄像头最佳布设位置

**适用**: 城市安防、监控规划、旅游景点设计

```
步骤 1: 打开三维场景
  → 使用 scripts/three_d_analysis.py: Scene3DAnalyzer()

步骤 2: 加载地形和模型
  ├─ 添加 DEM 地形 → scene.terrain_layers.add(dem_dataset)
  ├─ 添加 DOM 影像 → scene.image_layers.add(dom_dataset)
  └─ 添加倾斜摄影/建筑物 → scene.general_layers.add(model_dataset)

步骤 3: 执行可视域分析
  → scripts/three_d_analysis.py: VisibilityAnalyzer.visibility_analysis(
        observer_point=(116.4, 39.9, 100),
        horizontal_angle=360,
        vertical_angle=60,
        max_distance=500
      )

步骤 4: 评估可视效果
  ├─ 查看可视面积和比例
  ├─ 对比多个监控点的可视范围
  └─ 选择最佳监控点位置

步骤 5: 通视分析（验证关键目标）
  → scripts/three_d_analysis.py: VisibilityAnalyzer.line_of_sight(
        start_point=(116.4, 39.9, 100),
        end_point=(116.5, 39.95, 50)
      )
```

---

### 工作流 7: 洪水淹没模拟与影响评估

**场景**: 模拟不同水位下的淹没范围,评估影响区域

**适用**: 防洪减灾、流域管理、应急预案

```
步骤 1: 准备 DEM 地形
  → MCP: import_tiff(source_path="DEM.tif", datasource_name="flood.udbx")

步骤 2: 设置淹没水位参数
  ├─ 定义水位上涨过程: [50, 60, 70, 80, 90, 100] (米)
  ├─ 设置最低水位: 50 米
  └─ 设置最高水位: 100 米

步骤 3: 执行淹没分析
  → scripts/three_d_analysis.py: FloodAnalyzer.flood_simulation(
        water_levels=[50, 60, 70, 80, 90, 100],
        min_water_level=50,
        max_water_level=100,
        rise_speed=0.5,
        output_dataset_prefix="Flood_"
      )

步骤 4: 叠加分析（统计影响对象）
  ├─ 导入建筑物 → MCP: import_shapefile(buildings.shp)
  ├─ 执行叠加分析 → MCP: overlay(
        dataset=buildings,
        overlay_dataset=flood_dataset,
        operation=INTERSECT
      )
  └─ 统计影响建筑数量

步骤 5: 生成淹没影响报告
  ├─ 各水位淹没面积
  ├─ 受影响建筑数量
  └─ 建议避险区域
```

---

### 工作流 8: 建筑日照分析与规划合规性检查

**场景**: 分析建筑群日照情况,检查是否符合住宅日照标准（冬至日≥2小时）

**适用**: 城市规划、建筑设计、绿色建筑认证

```
步骤 1: 加载三维建筑模型
  → iObjectsPy: import_ifc(source_file="buildings.ifc")

步骤 2: 设置日照分析参数
  ├─ 分析日期: 冬至 (12月22日)
  ├─ 时间范围: 8:00 - 16:00
  ├─ 采样间隔: 15 分钟
  └─ 地理位置: 经纬度、时区

步骤 3: 执行日照分析
  → scripts/three_d_analysis.py: SunlightAnalyzer.analyze(
        buildings_dataset=buildings_3d,
        analysis_date="2025-12-22",
        start_time="8:00",
        end_time="16:00",
        time_interval=15
      )

步骤 4: 检查合规性
  ├─ 统计每栋建筑日照时长
  ├─ 识别日照不足建筑 (<2小时)
  └─ 生成日照分布图

步骤 5: 规划调整建议
  ├─ 不合规建筑: 需调整间距或高度
  ├─ 可行调整方案
  └─ 优化后的日照分析
```

---

### 工作流 9: 场地平整与土方计算

**场景**: 计算场地平整工程的填挖方量,评估土方平衡

**适用**: 工程建设、场地规划、造价估算

```
步骤 1: 准备地形数据
  ├─ 原始地形 DEM → MCP: import_tiff(dem_original.tif)
  └─ 设计后 DEM → MCP: import_tiff(dem_design.tif)

步骤 2: 执行填挖方分析
  → scripts/three_d_analysis.py: EarthworkAnalyzer.calculate_cut_fill(
        original_dem=dem_original,
        modified_dem=dem_design,
        region=site_boundary  # 场地边界（可选）
      )

步骤 3: 土方统计结果
  ├─ 挖方体积: xxx 立方米
  ├─ 填方体积: xxx 立方米
  ├─ 挖/填面积: xxx 平方米
  └─ 土方平衡: 是/否

步骤 4: 土方优化建议
  ├─ 若不平衡: 计算需要外运/外购土方量
  ├─ 优化设计标高
  └─ 重新分析直至平衡
```

---

### 工作流 10: 无人机航线规划与动态可视域

**场景**: 规划无人机巡航航线,分析沿途可视情况,生成飞行动画

**适用**: 无人机巡检、航拍规划、路线可视化

```
步骤 1: 定义巡航航点
  → 航点列表: [(X1,Y1,Z1), (X2,Y2,Z2), ...]

步骤 2: 动态可视域分析
  → scripts/three_d_analysis.py: VisibilityAnalyzer.dynamic_visibility_analysis(
        waypoints=waypoints,
        horizontal_angle=360,
        vertical_angle=60,
        max_distance=1000,
        sample_interval=100
      )

步骤 3: 创建飞行动画
  → iObjectsPy: spy.create_flight_animation(
        scene=scene,
        keyframes=[
            {"position": wp, "heading": 0, "tilt": 30, "time": i*2}
            for i, wp in enumerate(waypoints)
        ],
        loop=True
      )

步骤 4: 导出航拍预览视频
  → iObjectsPy: spy.export_scene_animation(
        scene=scene,
        output_path="drone_flight.mp4",
        width=1920, height=1080,
        fps=30
      )

步骤 5: 导出航线文件（用于无人机飞控）
  → MCP: export_geojson(
        dataset_name=flight_path,
        target_path="flight_path.geojson"
      )
```

---

## MCP 工具快速参考

### 数据源管理
| 工具 | 用途 |
|------|------|
| `create_udbx_datasource` | 创建 UDBX 数据源 |
| `open_udbx_datasource` | 打开 UDBX 数据源 |
| `create_memory_datasource` | 创建内存数据源（临时） |
| `list_datasets` | 列出数据集中的所有数据集 |
| `get_dataset_info` | 获取数据集详细信息 |
| `query_dataset` | SQL 属性查询（支持 WHERE、字段选择、排序） |
| `delete_dataset` | 删除数据集 |

### 数据导入
| 工具 | 支持格式 |
|------|----------|
| `import_shapefile` | Shapefile (.shp) |
| `import_csv` | CSV (需指定 X/Y 字段) |
| `import_tiff` | GeoTIFF (栅格影像) |
| `import_geojson` | GeoJSON |
| `import_kml` | KML/KMZ |
| `import_dwg` | DWG/DXF (CAD) |
| `import_osm` | OpenStreetMap |

### 数据导出
| 工具 | 输出格式 |
|------|----------|
| `export_shapefile` | Shapefile |
| `export_geojson` | GeoJSON |
| `export_tiff` | GeoTIFF |

### 几何操作
| 工具 | 功能 | 关键参数 |
|------|------|----------|
| `create_buffer` | 单级缓冲区 | distance, unit |
| `create_multi_buffer` | 多级缓冲区 | buffer_distances (数组) |
| `overlay` | 叠加分析 | operation (INTERSECT/UNION/IDENTITY/ERASE/UPDATE) |
| `clip_data` | 裁剪 | clip_dataset |
| `dissolve` | 融合 | dissolve_field |

### 空间分析
| 工具 | 功能 | 关键参数 |
|------|------|----------|
| `kernel_density` | 核密度分析 | search_radius, cell_size |
| `idw_interpolate` | IDW 插值 | z_field, cell_size, power |
| `kriging_interpolate` | 克里金插值 | z_field, cell_size, variogram_model |
| `calculate_slope` | 坡度计算 | z_factor, unit (Degree/Ratio) |
| `calculate_aspect` | 坡向计算 | - |
| `calculate_hillshade` | 地形阴影 | azimuth, altitude |
| `fill_sink` | 填洼 | - |
| `watershed` | 流域分析 | pour_point |

### 地图制图
| 工具 | 功能 |
|------|------|
| `create_map` | 创建新地图 |
| `list_maps` | 列出所有地图 |
| `get_map_info` | 获取地图详细信息 |
| `add_layer_to_map` | 向地图添加图层 |
| `export_map_image` | 导出地图为 PNG/JPG 图片 |
| `generate_map_tiles` | 生成地图瓦片缓存 [iServer] |

### 工作空间管理
| 工具 | 用途 |
|------|------|
| `open_workspace` | 打开工作空间文件 (.smwu/.sxwu) |
| `save_workspace` | 保存/另存为工作空间 |
| `get_workspace_info` | 获取数据源、地图、场景列表 |

### 坐标系统
| 工具 | 用途 |
|------|------|
| `get_coordinate_system` | 查看数据集的坐标系、EPSG 代码、坐标范围 |
| `reproject_dataset` | 坐标转换（如 WGS84→CGCS2000） |

### 数据集管理
| 工具 | 用途 |
|------|------|
| `create_dataset` | 创建空数据集（点/线/面/文本/属性表） |
| `copy_dataset` | 复制数据集到同/不同数据源 |
| `append_to_dataset` | 追加要素到目标数据集 |

### 字段操作
| 工具 | 用途 |
|------|------|
| `add_field` | 为数据集添加新字段 |
| `calculate_field` | 批量计算赋值（支持表达式） |

### 几何转换
| 工具 | 用途 |
|------|------|
| `dataset_point_to_line` | 点转线（按字段排序连线） |
| `dataset_line_to_region` | 线转面（封闭区域构面） |
| `dataset_region_to_line` | 面转线（提取边界） |

### 工具函数
| 工具 | 用途 |
|------|------|
| `compute_distance` | 计算两点间距离（投影/地理坐标） |
| `compute_geodesic_area` | 计算球面面积（平方米） |

### 环境诊断
| 工具 | 用途 |
|------|------|
| `check_mcp_health` | MCP 健康检查（不依赖初始化） |
| `get_environment_info` | 获取环境信息（路径/线程数） |
| `initialize_supermap` | 手动初始化 iObjectsPy 连接 |

### 其他分析工具
| 工具 | 用途 |
|------|------|
| `create_thiessen_polygons` | 创建泰森多边形（Voronoi 图） |
| `aggregate_points` | 点聚合分析 |
| `reclassify` | 栅格重分类 |
| `import_gdb` | 导入 ESRI FileGDB |
| `batch_import` | 批量导入（Shapefile/GeoJSON/CSV/KML/DWG 混合） |
| `batch_export` | 批量导出（Shapefile/GeoJSON/KML） |

---

## MCP 未覆盖功能 (使用 Skill 补充)

> 以下功能 MCP 工具**暂未覆盖**，使用 Skill 的 scripts/ 或 references/ 补充。
> 已有 MCP 工具的功能（如坐标转换 `reproject_dataset`、工作空间管理、SQL 查询 `query_dataset` 等）不在本表中。

| 功能 | 使用方式 | 参考文档 |
|------|----------|----------|
| **空间关系查询** | `scripts/query_sql.py`: query_by_spatial_relation() | 相交/包含/相离 |
| **最近邻查询** | `scripts/query_sql.py`: query_nearest() | 按 k 个最近邻排序 |
| **距离查询** | `scripts/query_sql.py`: query_by_distance() | 指定距离范围内 |
| **多边形内查询** | `scripts/query_sql.py`: query_within_polygon() | 多边形内要素 |
| **沿路径查询** | `scripts/query_sql.py`: query_along_path() | 路径缓冲区内 |
| **批量处理** | `scripts/batch_process.py` 或 MCP `batch_import`/`batch_export` | 见工作流 1 |
| **GUI 自动化** | `references/gui-automation.md` | pywinauto/pyautogui |
| **3D 数据处理** | `references/3d-processing.md` | OSGB/LAS/S3M/BIM |
| **专题图制作** | `references/mapping-thematic.md` | 单值/分级/标签专题图 |
| **数据质量检查** | `references/data-quality.md` | 拓扑/几何/重复/属性 |
| **网络分析** | `references/iobjectspy-api.md` §9 | 最短路径/服务区 |

---

## 环境配置

### 前置要求

在使用任何功能之前,确保:

1. **检查 MCP 服务器是否已配置**:
   ```bash
   # 查看 ~/.workbuddy/mcp.json 中是否有 supermap 配置
   cat ~/.workbuddy/mcp.json
   ```

2. **验证 iObjectsPy 安装** (需要高级功能时):
   ```bash
   python --version
   pip show iobjectspy
   ```

3. **如果 iObjectsPy 未安装**:
   ```bash
   # 导航到 iDesktopX 安装目录的 bin_python
   cd <iDesktopX_install_dir>\bin_python
   pip install .
   ```

### 快速环境检查

运行环境检测脚本，验证所有配置是否正常：

```bash
python scripts/test_supermap_env.py

# 或输出 JSON 格式报告
python scripts/test_supermap_env.py --json
```

### 初始化 iObjectsPy (可选)

**注意**: 使用 MCP 工具时不需要初始化 iObjectsPy,但使用 Skill 中的 scripts 时需要:

```python
import iobjectspy as spy
spy.set_iobjects_java_path(r"<iDesktopX_install_dir>\bin")
```

或使用**增强型**自动发现脚本（支持 iObjectsJava 独立运行）:
```python
import sys
sys.path.insert(0, r"<path_to_skill>\scripts")
import idesktop_init  # 自动初始化，支持回退机制

# 或完全手动配置
from supermap_env_config import SuperMapEnv
env = SuperMapEnv(verbose=True)
spy = env.init(use_iobjects_java=False)  # 或 True 使用 iObjectsJava
```

### iDesktopX 内置 Python 环境问题排查

**问题**：内置 Python 窗口中外部工具找不到，或环境变量隔离导致脚本失败

**原因**：iDesktopX Python 窗口基于 Py4J 实现，与系统 Python 环境隔离

**解决方案**：参考 `references/python-iobjectsjava-integration.md` 第一部分（方案 1 - 优化版）

---

## Skill Scripts 工具库

### scripts/query_sql.py

**功能**: SQL 属性查询 + 空间查询工具

#### SQL 属性查询

```python
from scripts.query_sql import query_and_export, query_dataset

# 查询人口超过 100 万的城市
results = query_dataset(
    datasource_path="D:/data/world.udbx",
    dataset_name="cities",
    sql_filter="Population > 1000000"
)

# 查询并导出为 CSV
query_and_export(
    datasource_path="D:/data/world.udbx",
    dataset_name="cities",
    sql_filter="Continent = 'Asia'",
    export_path="D:/output/asia_cities.csv"
)
```

#### 空间关系查询

```python
from scripts.query_sql import query_by_spatial_relation

# 查找与道路相交的城市
results = query_by_spatial_relation(
    datasource_path="D:/data/world.udbx",
    dataset_name="cities",
    target_dataset_name="roads",
    relation="intersect"  # intersect/contain/within/touch/disjoint
)

# 查找被省界包含的城市
results = query_by_spatial_relation(
    datasource_path="D:/data/world.udbx",
    dataset_name="cities",
    target_dataset_name="provinces",
    relation="within"
)
```

#### 最近邻查询

```python
from scripts.query_sql import query_nearest

# 查找距离北京最近的 10 个城市
results = query_nearest(
    datasource_path="D:/data/world.udbx",
    dataset_name="cities",
    point=(116.4, 39.9),  # 北京坐标
    max_distance=100000,   # 100 公里内
    k=10                    # 返回 10 个最近邻
)

for i, record in enumerate(results):
    print(f"{i+1}. {record['Name']} - 距离: {record['_distance']:.2f} 米")
```

#### 距离查询

```python
from scripts.query_sql import query_by_distance

# 查找距离北京 50 公里内的所有 POI
results = query_by_distance(
    datasource_path="D:/data/pois.udbx",
    dataset_name="poi",
    point=(116.4, 39.9),
    distance=50000  # 50 公里
)
```

#### 多边形内查询

```python
from scripts.query_sql import query_within_polygon

# 查找北京市内的所有 POI
beijing_coords = [
    (116.3, 39.9), (116.5, 39.9),
    (116.5, 40.0), (116.3, 40.0)
]

results = query_within_polygon(
    datasource_path="D:/data/pois.udbx",
    dataset_name="poi",
    polygon_coords=beijing_coords
)
```

#### 沿路径查询

```python
from scripts.query_sql import query_along_path

# 查找道路两侧 500 米内的所有建筑
results = query_along_path(
    datasource_path="D:/data/city.udbx",
    dataset_name="buildings",
    path_dataset_name="main_road",
    buffer_distance=500  # 米
)
```

### scripts/batch_process.py

**功能**: 批量导入/导出数据

```python
from scripts.batch_process import batch_import, batch_export

# 批量导入
batch_import(
    source_dir="D:/data/input",
    datasource_name="output.udbx",
    pattern="*.shp",  # 支持 *.geojson, *.csv, *.tiff
    recursive=True   # 递归子目录
)

# 批量导出
batch_export(
    datasource_name="output.udbx",
    target_dir="D:/output",
    format="shapefile",  # shapefile, geojson, tiff
    pattern="result_*"   # 仅导出匹配的数据集
)
```

### scripts/idesktop_launcher.py

**功能**: 启动/管理 iDesktopX 进程

```python
from scripts.idesktop_launcher import launch_idesktop, is_idesktop_running, close_idesktop

# 检查是否已运行
if not is_idesktop_running():
    launch_idesktop(wait_seconds=30)

# 关闭 iDesktopX
close_idesktop()
```

---

### scripts/three_d_analysis.py

**功能**: 三维分析工具库（新增 2026-03-27）

提供可视域分析、日照分析、淹没分析、填挖方计算等功能的封装。

**核心类**:

| 类 | 功能 | 主要方法 |
|----|------|---------|
| `Scene3DAnalyzer` | 三维场景管理 | 初始化场景,打开工作空间 |
| `VisibilityAnalyzer` | 可视域与通视分析 | `visibility_analysis()`, `line_of_sight()`, `dynamic_visibility_analysis()` |
| `FloodAnalyzer` | 淹没分析 | `flood_simulation()` |
| `SunlightAnalyzer` | 日照分析 | `analyze()` |
| `TerrainAnalyzer` | 地形分析 | `calculate_slope_aspect()`, `extract_contour()`, `terrain_profile()` |
| `EarthworkAnalyzer` | 填挖方分析 | `calculate_cut_fill()` |

**使用示例**:

```python
from scripts.three_d_analysis import (
    Scene3DAnalyzer, VisibilityAnalyzer, FloodAnalyzer,
    SunlightAnalyzer, TerrainAnalyzer, EarthworkAnalyzer
)

# 1. 打开三维场景
analyzer = Scene3DAnalyzer(r"D:\data\project.smwu", "Scene3D")

# 2. 可视域分析
vis_analyzer = VisibilityAnalyzer(analyzer.scene)
result = vis_analyzer.visibility_analysis(
    observer_point=(116.4, 39.9, 100),
    horizontal_angle=360,
    vertical_angle=60,
    max_distance=2000,
    output_dataset_name="Monitor_Visibility"
)

# 3. 淹没分析
flood_analyzer = FloodAnalyzer(dem_dataset, None)
flood_result = flood_analyzer.flood_simulation(
    water_levels=[50, 60, 70, 80, 90, 100],
    min_water_level=50,
    max_water_level=100,
    output_dataset_prefix="Flood_"
)

# 4. 日照分析
sunlight_analyzer = SunlightAnalyzer(analyzer.scene, latitude=39.9, longitude=116.4)
sunlight_result = sunlight_analyzer.analyze(
    buildings_dataset=buildings_3d,
    analysis_date="2025-12-22",  # 冬至
    start_time="8:00",
    end_time="16:00",
    time_interval=15
)

# 5. 填挖方计算
earthwork = EarthworkAnalyzer(dem_before, dem_after)
cut_fill_result = earthwork.calculate_cut_fill()
print(f"挖方: {cut_fill_result['cut_volume']} 立方米")
print(f"填方: {cut_fill_result['fill_volume']} 立方米")
```

**应用场景**:
- 可视域分析: 监控摄像头布设、旅游景点规划、军事侦察
- 淹没分析: 防洪减灾、流域管理、应急预案
- 日照分析: 城市规划、建筑设计、绿色建筑认证
- 填挖方分析: 工程建设、场地规划、造价估算

---

## iObjectsPy API 核心示例

### 1. 启动 iDesktopX (需要 GUI 可视化时)

```bat
cd /d <iDesktopX_install_dir>
startup.bat
```

### 2. 打开工作空间和数据源

```python
import iobjectspy as spy
from iobjectspy import (Workspace, WorkspaceConnectionInfo, WorkspaceType,
                        DatasourceConnectionInfo, EngineType)

# 打开工作空间
ws = Workspace()
conn = WorkspaceConnectionInfo()
conn.server = r"D:\data\MyProject.smwu"
ws.open(conn)

# 打开 UDBX 数据源
ds_conn = DatasourceConnectionInfo()
ds_conn.server = r"D:\data\world.udbx"
ds_conn.engine_type = EngineType.UDBX
ds = spy.open_datasource(ds_conn)

# 访问数据集
dataset = ds["Countries"]
```

### 3. 查询和读取要素

```python
# 遍历所有要素
rs = dataset.get_recordset(True)   # True = 只读
rs.move_first()
while not rs.is_EOF:
    name = rs.get_field_value("Name")
    geom = rs.get_geometry()
    rs.move_next()
rs.close()

# SQL 查询
rs = dataset.query("Population > 1000000")

# 转换为 DataFrame (需要 pandas)
df = spy.datasetvector_to_df(dataset)
```

### 4. 高级空间分析 (iObjectsPy)

```python
# 可视域分析 (3D 场景)
spy.visibility_analysis(
    observer_point=(116.4, 39.9, 50),
    scene=spy.get_scene(ws, "MyScene")
)

# 日照分析
spy.sunlight_analysis(
    building_dataset=ds["Buildings"],
    date="2025-06-21",
    time="12:00"
)

# 洪水淹没分析
spy.flood_analysis(
    terrain_dataset=ds["DEM"],
    water_level=100,
    out_dataset="FloodArea"
)
```

---

## 使用 iDesktopX 内置 Python 窗口

**最可靠的脚本运行方式** — 内置 Python 窗口已预配置 iObjectsPy,并自动继承 iDesktopX 的 License:

1. 打开 iDesktopX
2. 菜单: **Start → Browse → Python**
3. 直接输入代码,或点击 **"Execute Python File"** 加载 `.py` 脚本
4. 直接调用 `from iobjectspy import *` — 无需初始化

---

## 参考文档

| 文件 | 内容 |
|------|------|
| `references/environment.md` | 安装路径、Python 环境配置、License 设置 |
| `references/python-iobjectsjava-integration.md` | **NEW** iObjectsJava + Python 集成指南（解决内置 Python 环境变量问题）|
| `references/iobjectspy-api.md` | 完整的 iObjectsPy API 参考 |
| `references/gis-knowledge.md` | GIS 基础知识、数据结构、分析方法 |
| `references/3d-processing.md` | **ENHANCED**: 3D 数据 + 12 种三维分析工具 + 5 个工作流 |
| `references/mapping-thematic.md` | 专题图制作、符号化、坐标系统、地图输出 |
| `references/gui-automation.md` | GUI 自动化: pywinauto/pyautogui 使用指南 |
| `references/data-quality.md` | 拓扑检查、几何修复、重复处理、属性验证 |

---

## FAQ

### 工作流 11: 环境诊断（推荐首次使用时执行）

**场景**: 验证 MCP Server 是否正常工作

```
步骤 1: 健康检查
  → MCP: check_mcp_health()

步骤 2: （如果健康检查失败）查看环境信息
  → MCP: get_environment_info()

步骤 3: 根据错误信息排查
  ├─ iObjectsPy not found → 检查安装路径
  ├─ Java path invalid → 检查 Java 路径
  └─ License not found → 检查 License 目录
```

### 工作流 12: 坐标系查看与转换

**场景**: 检查数据坐标系，并转换为项目统一坐标系

```
步骤 1: 查看原始坐标系
  → MCP: get_coordinate_system(
        datasource_path="D:/data/world.udbx",
        dataset_name="countries"
      )

步骤 2: 坐标转换（如 WGS84→CGCS2000）
  → MCP: reproject_dataset(
        datasource_path="D:/data/world.udbx",
        dataset_name="countries",
        output_dataset="countries_cgc2000",
        target_epsg=4490
      )
```

### 工作流 13: 数据集创建与字段操作

**场景**: 创建分析结果数据集并计算面积字段

```
步骤 1: 创建空数据集
  → MCP: create_dataset(
        datasource_path="D:/data/output.udbx",
        dataset_name="analysis_results",
        dataset_type="REGION"
      )

步骤 2: 添加字段
  → MCP: add_field(
        datasource_path="D:/data/output.udbx",
        dataset_name="analysis_results",
        field_name="area_sqkm",
        field_type="DOUBLE"
      )

步骤 3: 计算字段值（SmArea 单位为 m²，除以 10^6 转为 km²）
  → MCP: calculate_field(
        datasource_path="D:/data/output.udbx",
        dataset_name="analysis_results",
        field_name="area_sqkm",
        expression="SmArea / 1000000"
      )
```

### 工作流 14: 工作空间管理与地图出图

**场景**: 打开工作空间、添加图层、导出地图图片

```
步骤 1: 打开工作空间
  → MCP: open_workspace(workspace_path="D:/data/project.smwu")

步骤 2: 获取工作空间信息（数据源列表、地图列表）
  → MCP: get_workspace_info(workspace_path="D:/data/project.smwu")

步骤 3: 添加图层到地图
  → MCP: add_layer_to_map(
        workspace_path="D:/data/project.smwu",
        map_name="World",
        datasource_path="D:/data/world.udbx",
        dataset_name="countries"
      )

步骤 4: 导出地图图片
  → MCP: export_map_image(
        workspace_path="D:/data/project.smwu",
        map_name="World",
        output_path="D:/output/world_map.png",
        dpi=300
      )

步骤 5: 保存工作空间
  → MCP: save_workspace(workspace_path="D:/data/project.smwu")
```

### 工作流 15: 几何转换（点→线→面）

**场景**: GPS 轨迹点转线、线封闭构面

```
步骤 1: 创建/打开数据源（含轨迹点数据集 "track_points"）

步骤 2: 点转线（按时间字段排序连线）
  → MCP: dataset_point_to_line(
        datasource_path="D:/data/tracks.udbx",
        source_dataset="track_points",
        result_dataset="track_line",
        order_field="timestamp"
      )

步骤 3: 线转面（封闭区域自动构面）
  → MCP: dataset_line_to_region(
        datasource_path="D:/data/tracks.udbx",
        source_dataset="track_line",
        result_dataset="track_area"
      )
```

---

**Q: "MCP 工具找不到"错误**  
A: 检查 `~/.workbuddy/mcp.json` 中是否正确配置了 supermap 服务器,并重启 WorkBuddy。

**Q: "iObjectsPy not found" 错误**  
A: 从 iDesktopX 安装目录的 `bin_python/` 安装:
```bash
cd <iDesktopX_install_dir>\bin_python
pip install .
```

**Q: "Java gateway process exited" 错误**  
A: `set_iobjects_java_path()` 的路径不正确,必须指向包含 `SuperMap.iObjects.Java.jar` 的 `bin/` 目录。  
同时确认使用 Windows 反斜杠路径：`spy.set_iobjects_java_path(r"D:\software\...\bin")`

**Q: "hasp_feature_not_found" / License 错误 (独立运行时)**  
A: 独立运行 iObjectsPy 需要单独的 iObjectsPy License。建议使用 iDesktopX 内置的 Python 窗口,它自动继承 iDesktopX License。

**Q: 内置 Python 窗口找不到外部工具（ffmpeg/gdal等）**  
A: 内置 Python 环境变量与系统隔离。在脚本开头手动注入：
```python
import os
os.environ['PATH'] = r"C:\tools\your-tool\bin" + os.pathsep + os.environ.get('PATH', '')
```
或迁移到方案 2（自建 Python 环境）—— 参见 `references/python-iobjectsjava-integration.md`

**Q: 如何通过 iObjectsJava 独立运行 Python 脚本（不依赖 iDesktopX 进程）？**  
A: 参考 `references/python-iobjectsjava-integration.md` 方案 2，核心步骤：
1. 确认 iObjectsJava 安装在 `D:\software\supermap-iobjectsjava-2025-win64-all-Bin`
2. 创建 Python 虚拟环境并安装 iObjectsPy
3. 运行 `python scripts/supermap_env_config.py` 验证配置
4. 在脚本开头 `from supermap_env_config import SuperMapEnv; SuperMapEnv().init(use_iobjects_java=True)`

**Q: 没有可用的 Python 环境**  
A: 使用 SuperMap AI Extension 包中捆绑的 MiniConda (`support/MiniConda/conda/python.exe`)。

**Q: threedesigner 模块导入错误**  
A: `threedesigner` 模块需要 iObjectsPy 2025 或更高版本。确保从 `bin_python/` 安装了正确版本。

**Q: 倾斜摄影在 3D 场景中不显示**  
A: 检查 OSGB 目录是否包含 `metadata.xml` 文件,并确认坐标系统配置正确。

**Q: 如何批量处理 1000+ 个 Shapefile?**  
A: 使用 `scripts/batch_process.py`:
```python
from scripts.batch_process import batch_import
batch_import(
    source_dir="D:/data/large_dataset",
    datasource_name="output.udbx",
    pattern="*.shp",
    recursive=True
)
```

**Q: MCP 工具和 iObjectsPy API 的性能对比?**  
A: MCP 工具适合单步操作和标准分析;复杂批处理和多步骤工作流建议使用 iObjectsPy API + 循环,性能更好且控制更灵活。

---

## 扩展阅读

- **SuperMap 官方文档**: https://www.supermap.com/
- **iObjectsPy API 文档**: `<iDesktopX_install_dir>\help\iObjectsPy\`
- **SuperMap 知识社区**: https://ask.supermap.com/

---

**Skill 版本**: v3.0
**更新时间**: 2026-03-30
**适用版本**: SuperMap iDesktopX 2025 (11.x)
**MCP Server 版本**: v3.0 (68 工具, 其中 iDesktopX 58 个 + iServer 10 个)

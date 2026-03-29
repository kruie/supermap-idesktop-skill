# SuperMap iDesktopX Skill 示例场景

本目录包含基于 MCP 工具的典型 GIS 工作流示例，展示如何通过自然语言完成空间分析任务。

## 示例列表

| 编号 | 示例名称 | 难度 | 涉及工具 | 适用场景 |
|------|---------|------|---------|---------|
| [01](01_buffer_analysis.md) | 缓冲区分析 — POI 服务范围 | ⭐ 入门 | import_shapefile, create_buffer, export_geojson, query_dataset | 城市规划、服务设施分析 |
| [02](02_overlay_analysis.md) | 叠加分析 — 土地利用适宜性 | ⭐⭐ 进阶 | batch_import, overlay, clip_data, dissolve, batch_export | 环保评估、土地规划 |
| [03](03_dem_analysis.md) | DEM 地形分析 — 坡度适宜性 | ⭐⭐ 进阶 | import_tiff, calculate_slope, calculate_aspect, calculate_hillshade, reclassify | 农业、工程选址 |
| [04](04_batch_processing.md) | 批量数据处理 — 多格式入库出库 | ⭐ 入门 | batch_import, batch_export, list_datasets, query_dataset, delete_dataset | 数据管理、数据迁移 |

## 如何使用

1. **学习参考**: 阅读示例了解 MCP 工具的组合用法
2. **直接执行**: 将工具调用参数提供给 AI Agent，由 Agent 调用 MCP 工具执行
3. **修改适配**: 根据实际数据路径和参数需求修改示例中的路径和参数

## MCP 工具快速参考

### 数据管理
- `initialize_supermap` — 初始化环境
- `open_udbx_datasource` / `create_udbx_datasource` — 数据源管理
- `list_datasets` / `get_dataset_info` — 数据集查看
- `query_dataset` — SQL 属性查询
- `delete_dataset` — 删除数据集

### 数据导入导出
- `import_shapefile` / `import_geojson` / `import_csv` / `import_kml` / `import_tiff` — 单文件导入
- `batch_import` — 批量导入
- `export_shapefile` / `export_geojson` / `export_tiff` — 单文件导出
- `batch_export` — 批量导出

### 空间分析
- `create_buffer` / `create_multi_buffer` — 缓冲区
- `overlay` / `clip_data` — 叠加/裁剪
- `dissolve` — 融合
- `calculate_slope` / `calculate_aspect` / `calculate_hillshade` — 地形分析
- `reclassify` — 重分类

## 版本信息

- **适用 MCP Server**: v2.2+ (57 工具)
- **适用 iDesktopX**: 2025 (11.x)
- **创建日期**: 2026-03-29

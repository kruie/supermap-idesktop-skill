# SuperMap MCP 工具调用实战指南

> **本文档目标**: 提供完整的 MCP 工具调用示例，帮助开发者正确、高效地使用 SuperMap MCP Server 进行 GIS 数据处理。

---

## 目录

1. [快速开始](#快速开始)
2. [调用规范](#调用规范)
3. [数据源管理](#数据源管理)
4. [数据导入](#数据导入)
5. [数据导出](#数据导出)
6. [空间分析](#空间分析)
7. [几何操作](#几何操作)
8. [地图制图](#地图制图)
9. [批量处理](#批量处理)
10. [故障排查](#故障排查)
11. [最佳实践](#最佳实践)

---

## 快速开始

### 3 分钟上手

```python
# 示例: 创建 UDBX 数据源并导入 Shapefile

# 步骤 1: 获取工具描述
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "create_udbx_datasource"]]')

# 步骤 2: 创建数据源
mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="create_udbx_datasource",
    arguments='{"file_path": "E:/data/my_project.udbx"}'
)

# 步骤 3: 导入 Shapefile
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "import_shapefile"]]')
mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="import_shapefile",
    arguments='{"source_path": "E:/data/cities.shp", "datasource_name": "E:/data/my_project.udbx"}'
)
```

### 核心概念

| 概念 | 说明 |
|------|------|
| `serverName` | MCP Server 名称，固定为 `"supermap-mcp-server"` |
| `toolName` | 工具名称，如 `create_udbx_datasource`、`import_shapefile` |
| `arguments` | 工具参数，JSON 格式字符串 |
| `mcp_get_tool_description` | 获取工具参数描述的函数 |
| `mcp_call_tool` | 执行工具调用的函数 |

---

## 调用规范

### 标准调用流程

```
┌─────────────────────────────────────────┐
│  步骤 1: 获取工具描述                    │
│  mcp_get_tool_description(...)          │
│  → 了解参数名、类型、是否必填            │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  步骤 2: 构造参数                        │
│  根据描述构造 JSON 字符串                │
│  '{"param1": "value1", "param2": 123}'  │
└─────────────────────────────────────────┘
                   ↓
┌─────────────────────────────────────────┐
│  步骤 3: 执行调用                        │
│  mcp_call_tool(serverName, toolName,    │
│               arguments)                │
└─────────────────────────────────────────┘
```

### 参数构造规则

| 数据类型 | JSON 示例 | 说明 |
|----------|-----------|------|
| 字符串 | `"file_path": "E:/data/test.udbx"` | 使用双引号 |
| 数值 | `"distance": 5000` | 不加引号 |
| 布尔值 | `"overwrite": true` | true/false 小写 |
| 数组 | `"buffer_distances": [1000, 2000, 3000]` | 方括号包裹 |
| 对象 | `"options": {"key": "value"}` | 花括号包裹 |

### 路径格式规范

```python
# ✅ 正确 - 使用正斜杠或双反斜杠
"E:/data/test.udbx"
"E:\\data\\test.udbx"

# ❌ 错误 - 单反斜杠会被当作转义字符
"E:\data\test.udbx"  # \t 会被当作制表符!
```

---

## 数据源管理

### 1. 创建 UDBX 数据源

**工具**: `create_udbx_datasource`

```python
# 获取工具描述
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "create_udbx_datasource"]]')

# 调用示例
mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="create_udbx_datasource",
    arguments='{"file_path": "E:/data/new_datasource.udbx"}'
)
```

**参数说明**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `file_path` | string | ✅ | UDBX 文件完整路径 |

**返回值**:
```json
{
  "success": true,
  "datasource_path": "E:/data/new_datasource.udbx",
  "engine_type": "UDBX"
}
```

---

### 2. 打开 UDBX 数据源

**工具**: `open_udbx_datasource`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "open_udbx_datasource"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="open_udbx_datasource",
    arguments='{"file_path": "E:/data/existing.udbx", "read_only": false}'
)
```

**参数说明**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `file_path` | string | ✅ | UDBX 文件路径 |
| `read_only` | boolean | ❌ | 是否只读打开，默认 false |

---

### 3. 列出数据集

**工具**: `list_datasets`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "list_datasets"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="list_datasets",
    arguments='{"datasource_name": "E:/data/my_project.udbx"}'
)
```

**参数说明**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `datasource_name` | string | ✅ | 数据源路径 |

**返回值示例**:
```json
{
  "datasets": [
    {"name": "cities", "type": "Point", "record_count": 150},
    {"name": "roads", "type": "Line", "record_count": 2300},
    {"name": "districts", "type": "Region", "record_count": 45}
  ]
}
```

---

### 4. 删除数据集

**工具**: `delete_dataset`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "delete_dataset"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="delete_dataset",
    arguments='{"datasource_name": "E:/data/my_project.udbx", "dataset_name": "temp_layer"}'
)
```

**⚠️ 警告**: 此操作不可逆，删除前请确认!

---

### 5. 查询数据集

**工具**: `query_dataset`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "query_dataset"]]')

# 示例 1: 查询所有记录
mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="query_dataset",
    arguments='{"datasource_name": "E:/data/my_project.udbx", "dataset_name": "cities"}'
)

# 示例 2: 带条件查询
mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="query_dataset",
    arguments='{
        "datasource_name": "E:/data/my_project.udbx",
        "dataset_name": "cities",
        "where_clause": "Population > 1000000",
        "fields": ["Name", "Population", "Province"],
        "limit": 100
    }'
)
```

**参数说明**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `datasource_name` | string | ✅ | 数据源路径 |
| `dataset_name` | string | ✅ | 数据集名称 |
| `where_clause` | string | ❌ | SQL WHERE 条件 |
| `fields` | array | ❌ | 返回字段列表 |
| `limit` | number | ❌ | 最大返回记录数 |
| `offset` | number | ❌ | 跳过记录数 |

---

## 数据导入

### 1. 导入 Shapefile

**工具**: `import_shapefile`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "import_shapefile"]]')

# 基础导入
mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="import_shapefile",
    arguments='{
        "source_path": "E:/data/cities.shp",
        "datasource_name": "E:/data/output.udbx"
    }'
)

# 高级选项
mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="import_shapefile",
    arguments='{
        "source_path": "E:/data/cities.shp",
        "datasource_name": "E:/data/output.udbx",
        "out_dataset_name": "city_points",
        "charset": "UTF-8",
        "overwrite": true
    }'
)
```

**参数说明**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `source_path` | string | ✅ | Shapefile 路径 (.shp) |
| `datasource_name` | string | ✅ | 目标数据源路径 |
| `out_dataset_name` | string | ❌ | 输出数据集名称，默认使用文件名 |
| `charset` | string | ❌ | 字符编码，默认 UTF-8 |
| `overwrite` | boolean | ❌ | 是否覆盖已存在数据集 |

---

### 2. 导入 CSV (生成点数据集)

**工具**: `import_csv`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "import_csv"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="import_csv",
    arguments='{
        "source_path": "E:/data/pois.csv",
        "datasource_name": "E:/data/output.udbx",
        "x_field": "longitude",
        "y_field": "latitude",
        "out_dataset_name": "poi_points",
        "coordinate_system": "EPSG:4326"
    }'
)
```

**参数说明**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `source_path` | string | ✅ | CSV 文件路径 |
| `datasource_name` | string | ✅ | 目标数据源路径 |
| `x_field` | string | ✅ | 经度字段名 |
| `y_field` | string | ✅ | 纬度字段名 |
| `out_dataset_name` | string | ❌ | 输出数据集名称 |
| `coordinate_system` | string | ❌ | 坐标系，默认 EPSG:4326 |

---

### 3. 导入 GeoTIFF

**工具**: `import_tiff`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "import_tiff"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="import_tiff",
    arguments='{
        "source_path": "E:/data/dem.tif",
        "datasource_name": "E:/data/terrain.udbx",
        "out_dataset_name": "dem",
        "build_pyramid": true
    }'
)
```

---

### 4. 导入 GeoJSON

**工具**: `import_geojson`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "import_geojson"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="import_geojson",
    arguments='{
        "source_path": "E:/data/boundaries.geojson",
        "datasource_name": "E:/data/output.udbx",
        "out_dataset_name": "admin_boundaries"
    }'
)
```

---

### 5. 批量导入

**工具**: `batch_import`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "batch_import"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="batch_import",
    arguments='{
        "source_dir": "E:/data/input",
        "datasource_name": "E:/data/combined.udbx",
        "pattern": "*.shp",
        "recursive": true
    }'
)
```

**支持的格式**: Shapefile, GeoJSON, CSV, KML, DWG

---

## 数据导出

### 1. 导出为 Shapefile

**工具**: `export_shapefile`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "export_shapefile"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="export_shapefile",
    arguments='{
        "datasource_name": "E:/data/my_project.udbx",
        "dataset_name": "cities",
        "target_path": "E:/output/cities_export.shp",
        "charset": "UTF-8"
    }'
)
```

---

### 2. 导出为 GeoJSON

**工具**: `export_geojson`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "export_geojson"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="export_geojson",
    arguments='{
        "datasource_name": "E:/data/my_project.udbx",
        "dataset_name": "cities",
        "target_path": "E:/output/cities.geojson",
        "pretty_print": true
    }'
)
```

---

### 3. 导出为 GeoTIFF

**工具**: `export_tiff`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "export_tiff"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="export_tiff",
    arguments='{
        "datasource_name": "E:/data/terrain.udbx",
        "dataset_name": "slope",
        "target_path": "E:/output/slope.tif",
        "compression": "LZW"
    }'
)
```

---

### 4. 批量导出

**工具**: `batch_export`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "batch_export"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="batch_export",
    arguments='{
        "datasource_name": "E:/data/my_project.udbx",
        "target_dir": "E:/output",
        "format": "geojson",
        "pattern": "result_*"
    }'
)
```

## 空间分析

### 1. 创建缓冲区 (单级)

**工具**: `create_buffer`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "create_buffer"]]')

# 基础缓冲
mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="create_buffer",
    arguments='{
        "source_datasource": "E:/data/my_project.udbx",
        "source_dataset": "cities",
        "distance": 5000,
        "out_dataset": "cities_buffer_5km"
    }'
)

# 高级选项
mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="create_buffer",
    arguments='{
        "source_datasource": "E:/data/my_project.udbx",
        "source_dataset": "cities",
        "distance": 10000,
        "unit": "Meter",
        "out_dataset": "cities_buffer_10km",
        "dissolve": false,
        "side_type": "Full"
    }'
)
```

**参数说明**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| `source_datasource` | string | ✅ | 源数据源路径 |
| `source_dataset` | string | ✅ | 源数据集名称 |
| `distance` | number | ✅ | 缓冲距离 |
| `unit` | string | ❌ | 单位: Meter/Kilometer/Degree，默认 Meter |
| `out_dataset` | string | ✅ | 输出数据集名称 |
| `dissolve` | boolean | ❌ | 是否融合重叠区域 |
| `side_type` | string | ❌ | 缓冲边类型: Full/Left/Right |

---

### 2. 创建多级缓冲区

**工具**: `create_multi_buffer`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "create_multi_buffer"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="create_multi_buffer",
    arguments='{
        "source_datasource": "E:/data/my_project.udbx",
        "source_dataset": "facilities",
        "buffer_distances": [1000, 2000, 5000, 10000],
        "unit": "Meter",
        "out_dataset": "facilities_multi_buffer"
    }'
)
```

---

### 3. 叠加分析

**工具**: `overlay`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "overlay"]]')

# 交集分析 (INTERSECT)
mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="overlay",
    arguments='{
        "source_datasource": "E:/data/my_project.udbx",
        "source_dataset": "roads",
        "overlay_datasource": "E:/data/my_project.udbx",
        "overlay_dataset": "city_buffer",
        "operation": "INTERSECT",
        "out_dataset": "roads_in_city"
    }'
)

# 并集分析 (UNION)
mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="overlay",
    arguments='{
        "source_datasource": "E:/data/my_project.udbx",
        "source_dataset": "districts_2023",
        "overlay_datasource": "E:/data/my_project.udbx",
        "overlay_dataset": "districts_2024",
        "operation": "UNION",
        "out_dataset": "districts_combined"
    }'
)
```

**操作类型**:
- `INTERSECT` - 交集 (保留两个图层重叠部分)
- `UNION` - 并集 (合并两个图层所有区域)
- `ERASE` - 擦除 (从源图层中移除叠加图层部分)
- `IDENTITY` - 标识 (保留源图层所有要素，添加叠加图层属性)
- `UPDATE` - 更新 (用叠加图层更新源图层)

---

### 4. 裁剪分析

**工具**: `clip_data`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "clip_data"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="clip_data",
    arguments='{
        "source_datasource": "E:/data/my_project.udbx",
        "source_dataset": "roads",
        "clip_datasource": "E:/data/my_project.udbx",
        "clip_dataset": "province_boundary",
        "out_dataset": "roads_clipped"
    }'
)
```

---

### 5. 融合分析

**工具**: `dissolve`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "dissolve"]]')

# 按字段融合
mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="dissolve",
    arguments='{
        "source_datasource": "E:/data/my_project.udbx",
        "source_dataset": "parcels",
        "dissolve_field": "land_use_type",
        "out_dataset": "land_use_zones"
    }'
)
```

---

### 6. 核密度分析

**工具**: `kernel_density`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "kernel_density"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="kernel_density",
    arguments='{
        "source_datasource": "E:/data/my_project.udbx",
        "source_dataset": "poi",
        "search_radius": 1000,
        "cell_size": 100,
        "out_dataset": "poi_density"
    }'
)
```

---

### 7. IDW 插值

**工具**: `idw_interpolate`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "idw_interpolate"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="idw_interpolate",
    arguments='{
        "source_datasource": "E:/data/my_project.udbx",
        "source_dataset": "temperature_stations",
        "z_field": "temperature",
        "cell_size": 500,
        "power": 2,
        "out_dataset": "temperature_surface"
    }'
)
```

---

### 8. 坡度计算

**工具**: `calculate_slope`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "calculate_slope"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="calculate_slope",
    arguments='{
        "source_datasource": "E:/data/terrain.udbx",
        "source_dataset": "dem",
        "z_factor": 1.0,
        "unit": "Degree",
        "out_dataset": "slope"
    }'
)
```

---

### 9. 坡向计算

**工具**: `calculate_aspect`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "calculate_aspect"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="calculate_aspect",
    arguments='{
        "source_datasource": "E:/data/terrain.udbx",
        "source_dataset": "dem",
        "out_dataset": "aspect"
    }'
)
```

---

## 几何操作

### 1. 点转线

**工具**: `dataset_point_to_line`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "dataset_point_to_line"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="dataset_point_to_line",
    arguments='{
        "source_datasource": "E:/data/my_project.udbx",
        "source_dataset": "gps_points",
        "order_field": "timestamp",
        "group_field": "vehicle_id",
        "out_dataset": "trajectories"
    }'
)
```

---

### 2. 线转面

**工具**: `dataset_line_to_region`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "dataset_line_to_region"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="dataset_line_to_region",
    arguments='{
        "source_datasource": "E:/data/my_project.udbx",
        "source_dataset": "boundaries",
        "out_dataset": "areas"
    }'
)
```

---

### 3. 面转线

**工具**: `dataset_region_to_line`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "dataset_region_to_line"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="dataset_region_to_line",
    arguments='{
        "source_datasource": "E:/data/my_project.udbx",
        "source_dataset": "districts",
        "out_dataset": "district_boundaries"
    }'
)
```

---

## 地图制图

### 1. 创建地图

**工具**: `create_map`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "create_map"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="create_map",
    arguments='{
        "workspace_path": "E:/data/project.smwu",
        "map_name": "CityMap",
        "extent": [116.3, 39.8, 116.6, 40.0]
    }'
)
```

---

### 2. 添加图层到地图

**工具**: `add_layer_to_map`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "add_layer_to_map"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="add_layer_to_map",
    arguments='{
        "workspace_path": "E:/data/project.smwu",
        "map_name": "CityMap",
        "datasource_name": "E:/data/my_project.udbx",
        "dataset_name": "cities",
        "layer_name": "城市"
    }'
)
```

---

### 3. 导出地图图片

**工具**: `export_map_image`

```python
mcp_get_tool_description(toolRequests='[["supermap-mcp-server", "export_map_image"]]')

mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="export_map_image",
    arguments='{
        "workspace_path": "E:/data/project.smwu",
        "map_name": "CityMap",
        "output_path": "E:/output/city_map.png",
        "width": 1920,
        "height": 1080,
        "dpi": 300
    }'
)
```

---

## 批量处理

### 批量工作流示例

```python
# 场景: 批量导入多个 Shapefile 并创建缓冲区

import json

# 定义处理列表
tasks = [
    {
        "tool": "import_shapefile",
        "args": {
            "source_path": "E:/data/input/cities.shp",
            "datasource_name": "E:/data/output.udbx"
        }
    },
    {
        "tool": "import_shapefile",
        "args": {
            "source_path": "E:/data/input/roads.shp",
            "datasource_name": "E:/data/output.udbx"
        }
    },
    {
        "tool": "create_buffer",
        "args": {
            "source_datasource": "E:/data/output.udbx",
            "source_dataset": "cities",
            "distance": 5000,
            "out_dataset": "cities_buffer"
        }
    }
]

# 执行批量任务
for task in tasks:
    print(f"执行: {task['tool']}")
    
    # 获取工具描述
    mcp_get_tool_description(
        toolRequests=f'[["supermap-mcp-server", "{task["tool"]}"]]'
    )
    
    # 执行调用
    result = mcp_call_tool(
        serverName="supermap-mcp-server",
        toolName=task["tool"],
        arguments=json.dumps(task["args"])
    )
    
    print(f"结果: {result}")
```

## 故障排查

### 错误代码速查表

| 错误代码/信息 | 原因 | 解决方案 |
|--------------|------|----------|
| `-32001: Request timed out` | MCP Server 启动慢或任务执行时间长 | 1. 等待 30 秒后重试<br>2. 改用 iObjectsPy API |
| `Command not found: mcp://...` | 误将 MCP 协议当命令执行 | 使用 `mcp_call_tool` 函数 |
| `Invalid parameters` | 参数名错误或类型不匹配 | 执行 `mcp_get_tool_description` 检查参数 |
| `Server not found` | MCP Server 未配置 | 检查 `~/.workbuddy/mcp.json` |
| `Datasource not found` | 数据源路径错误 | 检查路径是否存在，使用绝对路径 |
| `Dataset not found` | 数据集名称错误 | 使用 `list_datasets` 查看可用数据集 |
| `License error` | SuperMap License 问题 | 检查 License 配置或启动 iDesktopX |

---

### 常见问题诊断

#### 问题 1: MCP 调用超时

**症状**:
```
Error calling tool: MCP error -32001: Request timed out
```

**诊断步骤**:
```python
# 1. 检查 MCP Server 配置
import json
with open("~/.workbuddy/mcp.json") as f:
    config = json.load(f)
    print(config["mcpServers"]["supermap-mcp-server"])

# 2. 检查 SuperMap 环境
import os
print(f"SUPERMAP_HOME: {os.environ.get('SUPERMAP_HOME')}")
print(f"License 目录: {os.environ.get('SUPERMAP_LICENSE')}")

# 3. 如果持续超时，改用 iObjectsPy
import iobjectspy as spy
spy.set_iobjects_java_path(r"D:\software\supermap-idesktopx-2025-windows-x64-bin\bin")
ds = spy.create_datasource('E:/data/test.udbx')
```

**解决方案**:
1. 首次调用可能需要 10-30 秒启动 Java Gateway，请耐心等待
2. 如果多次超时，检查 SuperMap License 是否有效
3. 对于大数据处理任务，直接使用 iObjectsPy API 更高效

---

#### 问题 2: 参数错误

**症状**:
```
Invalid parameters: missing required field 'source_path'
```

**诊断步骤**:
```python
# 1. 获取正确的参数描述
result = mcp_get_tool_description(
    toolRequests='[["supermap-mcp-server", "import_shapefile"]]'
)
print(result)

# 2. 对比自己的参数
my_args = {
    "source_path": "E:/data/test.shp",  # 确保参数名正确
    "datasource_name": "E:/data/output.udbx"
}
```

**解决方案**:
1. 仔细查看 `mcp_get_tool_description` 返回的参数 schema
2. 注意参数名大小写（如 `source_path` 不是 `sourcePath`）
3. 确保必填参数都已提供

---

#### 问题 3: 路径问题

**症状**:
```
Datasource not found: E:\data\test.udbx
```

**诊断步骤**:
```python
import os

# 检查路径是否存在
path = "E:/data/test.udbx"
print(f"路径存在: {os.path.exists(path)}")
print(f"绝对路径: {os.path.abspath(path)}")

# 检查目录权限
print(f"目录可写: {os.access(os.path.dirname(path), os.W_OK)}")
```

**解决方案**:
1. 使用正斜杠 `/` 或双反斜杠 `\\`
2. 使用绝对路径而非相对路径
3. 确保目录存在且有写入权限
4. 在 Windows 上，确保盘符正确（如 `E:/`）

---

#### 问题 4: MCP Server 未配置

**症状**:
```
Server "supermap-mcp-server" not found
```

**诊断步骤**:
```bash
# 检查 MCP 配置文件
cat ~/.workbuddy/mcp.json
```

**解决方案**:
1. 创建/编辑 `~/.workbuddy/mcp.json`:
```json
{
  "mcpServers": {
    "supermap-mcp-server": {
      "command": "C:/Users/<username>/.workbuddy/binaries/python/versions/3.10.11/python.exe",
      "args": [
        "C:/Users/<username>/.workbuddy/mcp/supermap_mcp_server.py"
      ],
      "env": {
        "SUPERMAP_HOME": "D:/software/supermap-idesktopx-2025-windows-x64-bin",
        "SUPERMAP_LICENSE": "C:/Program Files/Common Files/SuperMap/License"
      },
      "type": "stdio",
      "disabled": false
    }
  }
}
```

2. 重启 WorkBuddy 使配置生效

---

### 调试技巧

#### 启用详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 执行 MCP 调用
result = mcp_call_tool(...)
print(f"详细结果: {result}")
```

#### 分步调试

```python
# 步骤 1: 检查工具描述
tool_desc = mcp_get_tool_description(
    toolRequests='[["supermap-mcp-server", "create_buffer"]]'
)
print(f"工具描述: {tool_desc}")

# 步骤 2: 构造参数
import json
args = {
    "source_datasource": "E:/data/test.udbx",
    "source_dataset": "cities",
    "distance": 5000,
    "out_dataset": "buffer"
}
args_json = json.dumps(args)
print(f"参数 JSON: {args_json}")

# 步骤 3: 执行调用
result = mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="create_buffer",
    arguments=args_json
)
print(f"调用结果: {result}")
```

---

## 最佳实践

### 1. 调用顺序原则

```
✅ 正确顺序:
1. mcp_get_tool_description (了解参数)
2. 构造参数
3. mcp_call_tool (执行调用)

❌ 错误做法:
- 跳过步骤 1 直接调用
- 不检查参数就批量调用
```

### 2. 错误处理模式

```python
import json

def safe_mcp_call(tool_name, arguments, fallback_fn=None):
    """安全的 MCP 调用包装器"""
    try:
        # 获取工具描述
        mcp_get_tool_description(
            toolRequests=f'[["supermap-mcp-server", "{tool_name}"]]'
        )
        
        # 执行调用
        result = mcp_call_tool(
            serverName="supermap-mcp-server",
            toolName=tool_name,
            arguments=json.dumps(arguments) if isinstance(arguments, dict) else arguments
        )
        
        return {"success": True, "result": result}
        
    except Exception as e:
        error_msg = str(e)
        
        # 超时错误，尝试回退方案
        if "timed out" in error_msg and fallback_fn:
            print(f"MCP 超时，使用回退方案...")
            return fallback_fn(arguments)
        
        # 其他错误
        return {"success": False, "error": error_msg}

# 使用示例
result = safe_mcp_call(
    "create_udbx_datasource",
    {"file_path": "E:/data/test.udbx"},
    fallback_fn=lambda args: create_datasource_fallback(args)  # iObjectsPy 回退
)
```

### 3. 批量处理策略

```python
# 策略 1: 小批量使用 MCP (推荐 < 10 个文件)
def batch_import_small(source_dir, datasource_name):
    import os
    import glob
    
    shp_files = glob.glob(os.path.join(source_dir, "*.shp"))
    
    for shp_file in shp_files[:10]:  # 限制数量
        mcp_call_tool(
            serverName="supermap-mcp-server",
            toolName="import_shapefile",
            arguments=json.dumps({
                "source_path": shp_file,
                "datasource_name": datasource_name
            })
        )

# 策略 2: 大批量使用 iObjectsPy (推荐 > 10 个文件)
def batch_import_large(source_dir, datasource_name):
    import sys
    sys.path.insert(0, r"C:\Users\jia\.workbuddy\skills\supermap-idesktop\scripts")
    from batch_process import batch_import
    
    batch_import(
        source_dir=source_dir,
        datasource_name=datasource_name,
        pattern="*.shp",
        recursive=True
    )
```

### 4. 路径管理最佳实践

```python
import os
from pathlib import Path

# 使用 Path 对象管理路径
BASE_DIR = Path("E:/data")
OUTPUT_DIR = BASE_DIR / "output"

# 确保目录存在
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 构建路径
datasource_path = OUTPUT_DIR / "project.udbx"
shp_path = BASE_DIR / "input" / "cities.shp"

# 转换为字符串 (MCP 需要字符串)
mcp_call_tool(
    serverName="supermap-mcp-server",
    toolName="import_shapefile",
    arguments=json.dumps({
        "source_path": str(shp_path),
        "datasource_name": str(datasource_path)
    })
)
```

### 5. 工作流模板

```python
"""
标准 GIS 工作流模板
"""
import json
from typing import Dict, Any

class SuperMapMCPWorkflow:
    def __init__(self, datasource_path: str):
        self.datasource_path = datasource_path
        self.results = []
    
    def create_datasource(self) -> Dict[str, Any]:
        """步骤 1: 创建数据源"""
        return self._call_tool("create_udbx_datasource", {
            "file_path": self.datasource_path
        })
    
    def import_data(self, source_path: str, dataset_name: str = None) -> Dict[str, Any]:
        """步骤 2: 导入数据"""
        ext = source_path.split('.')[-1].lower()
        
        tool_map = {
            'shp': 'import_shapefile',
            'geojson': 'import_geojson',
            'csv': 'import_csv',
            'tif': 'import_tiff',
            'tiff': 'import_tiff'
        }
        
        tool_name = tool_map.get(ext, 'import_shapefile')
        args = {
            "source_path": source_path,
            "datasource_name": self.datasource_path
        }
        
        if dataset_name:
            args["out_dataset_name"] = dataset_name
            
        return self._call_tool(tool_name, args)
    
    def create_buffer(self, dataset: str, distance: float, out_dataset: str) -> Dict[str, Any]:
        """步骤 3: 创建缓冲区"""
        return self._call_tool("create_buffer", {
            "source_datasource": self.datasource_path,
            "source_dataset": dataset,
            "distance": distance,
            "out_dataset": out_dataset
        })
    
    def export(self, dataset: str, target_path: str) -> Dict[str, Any]:
        """步骤 4: 导出结果"""
        ext = target_path.split('.')[-1].lower()
        
        tool_map = {
            'shp': 'export_shapefile',
            'geojson': 'export_geojson',
            'tif': 'export_tiff',
            'tiff': 'export_tiff'
        }
        
        tool_name = tool_map.get(ext, 'export_geojson')
        
        return self._call_tool(tool_name, {
            "datasource_name": self.datasource_path,
            "dataset_name": dataset,
            "target_path": target_path
        })
    
    def _call_tool(self, tool_name: str, arguments: Dict) -> Dict[str, Any]:
        """内部调用方法"""
        try:
            mcp_get_tool_description(
                toolRequests=f'[["supermap-mcp-server", "{tool_name}"]]'
            )
            
            result = mcp_call_tool(
                serverName="supermap-mcp-server",
                toolName=tool_name,
                arguments=json.dumps(arguments)
            )
            
            self.results.append({"tool": tool_name, "success": True, "result": result})
            return {"success": True, "result": result}
            
        except Exception as e:
            self.results.append({"tool": tool_name, "success": False, "error": str(e)})
            return {"success": False, "error": str(e)}

# 使用示例
workflow = SuperMapMCPWorkflow("E:/data/project.udbx")

# 执行完整工作流
workflow.create_datasource()
workflow.import_data("E:/data/input/cities.shp", "cities")
workflow.create_buffer("cities", 5000, "cities_buffer")
workflow.export("cities_buffer", "E:/output/result.geojson")

# 查看结果
for result in workflow.results:
    print(f"{result['tool']}: {'成功' if result['success'] else '失败'}")
```

---

## 附录

### A. 完整工具列表

| 类别 | 工具名 | 功能 |
|------|--------|------|
| **数据源** | `create_udbx_datasource` | 创建 UDBX 数据源 |
| | `open_udbx_datasource` | 打开 UDBX 数据源 |
| | `create_memory_datasource` | 创建内存数据源 |
| | `list_datasets` | 列出数据集 |
| | `get_dataset_info` | 获取数据集信息 |
| | `query_dataset` | 查询数据集 |
| | `delete_dataset` | 删除数据集 |
| **导入** | `import_shapefile` | 导入 Shapefile |
| | `import_geojson` | 导入 GeoJSON |
| | `import_csv` | 导入 CSV |
| | `import_tiff` | 导入 GeoTIFF |
| | `import_kml` | 导入 KML/KMZ |
| | `import_dwg` | 导入 DWG/DXF |
| | `import_osm` | 导入 OSM |
| | `batch_import` | 批量导入 |
| **导出** | `export_shapefile` | 导出 Shapefile |
| | `export_geojson` | 导出 GeoJSON |
| | `export_tiff` | 导出 GeoTIFF |
| | `batch_export` | 批量导出 |
| **几何** | `create_buffer` | 创建缓冲区 |
| | `create_multi_buffer` | 创建多级缓冲区 |
| | `overlay` | 叠加分析 |
| | `clip_data` | 裁剪分析 |
| | `dissolve` | 融合分析 |
| | `dataset_point_to_line` | 点转线 |
| | `dataset_line_to_region` | 线转面 |
| | `dataset_region_to_line` | 面转线 |
| **分析** | `kernel_density` | 核密度分析 |
| | `idw_interpolate` | IDW 插值 |
| | `kriging_interpolate` | 克里金插值 |
| | `calculate_slope` | 坡度计算 |
| | `calculate_aspect` | 坡向计算 |
| | `calculate_hillshade` | 地形阴影 |
| | `fill_sink` | 填洼分析 |
| | `watershed` | 流域分析 |
| **地图** | `create_map` | 创建地图 |
| | `list_maps` | 列出地图 |
| | `get_map_info` | 获取地图信息 |
| | `add_layer_to_map` | 添加图层 |
| | `export_map_image` | 导出地图图片 |

### B. 坐标系代码参考

| 坐标系 | EPSG 代码 | 说明 |
|--------|-----------|------|
| WGS84 | EPSG:4326 | 全球通用地理坐标系 |
| 北京54 | EPSG:4214 | 中国旧坐标系 |
| 西安80 | EPSG:4610 | 中国旧坐标系 |
| CGCS2000 | EPSG:4490 | 中国现行国家坐标系 |
| Web墨卡托 | EPSG:3857 | 网络地图常用 |
| UTM Zone 50N | EPSG:32650 | 中国东部地区投影 |

### C. 相关文档

- [SKILL.md](SKILL.md) - SuperMap Skill 主文档
- [examples/](examples/) - 完整工作流示例
- [scripts/](scripts/) - 实用工具脚本

---

**文档版本**: v1.0  
**更新时间**: 2026-03-30  
**适用版本**: SuperMap iDesktopX 2025, MCP Server v2.1

# 示例 4: 批量数据处理 — 多格式数据入库与批量出库

## 场景描述

某数据管理部门收到一批多种格式的 GIS 数据，需要统一导入 UDBX 数据源进行管理，
然后再将特定数据集批量导出为 GeoJSON 格式供 Web 端使用。

## 数据准备

- **输入文件**:
  - `D:/data/roads.shp` — 道路网络
  - `D:/data/buildings.geojson` — 建筑物
  - `D:/data/pois.csv` — 兴趣点（含经纬度列）
  - `D:/data/boundary.kml` — 行政边界
  - `D:/data/dem.tif` — DEM 栅格
- **工作数据源**: `D:/data/project.udbx`

## MCP 工具调用流程

### 步骤 1: 初始化并创建数据源

```
工具: initialize_supermap
参数: 无

工具: create_udbx_datasource
参数: { "file_path": "D:/data/project.udbx" }
```

### 步骤 2: 批量导入所有文件

```
工具: batch_import
参数: {
  "file_paths": [
    "D:/data/roads.shp",
    "D:/data/buildings.geojson",
    "D:/data/pois.csv",
    "D:/data/boundary.kml",
    "D:/data/dem.tif"
  ],
  "datasource_path": "D:/data/project.udbx"
}
```

> 默认使用文件名（不含扩展名）作为数据集名称。

也可以指定自定义名称：

```
工具: batch_import
参数: {
  "file_paths": [
    "D:/data/roads.shp",
    "D:/data/buildings.geojson"
  ],
  "datasource_path": "D:/data/project.udbx",
  "dataset_names": ["RoadNetwork", "BuildingFootprints"]
}
```

### 步骤 3: 查看导入结果

```
工具: list_datasets
参数: { "datasource_path": "D:/data/project.udbx" }
```

### 步骤 4: 查询数据样本

```
工具: query_dataset
参数: {
  "datasource_path": "D:/data/project.udbx",
  "dataset_name": "buildings",
  "max_results": 3,
  "fields": ["name", "height", "type"]
}

工具: query_dataset
参数: {
  "datasource_path": "D:/data/project.udbx",
  "dataset_name": "pois",
  "sql_filter": "type = 'restaurant'",
  "max_results": 10
}
```

### 步骤 5: 批量导出矢量数据为 GeoJSON

```
工具: batch_export
参数: {
  "datasource_path": "D:/data/project.udbx",
  "dataset_names": ["roads", "buildings", "pois", "boundary"],
  "output_format": "geojson",
  "output_directory": "D:/output/geojson"
}
```

### 步骤 6: 导出栅格数据

```
工具: export_tiff
参数: {
  "datasource_path": "D:/data/project.udbx",
  "dataset_name": "dem",
  "output_path": "D:/output/dem_project.tif"
}
```

### 步骤 7: 批量导出为 Shapefile（备选）

```
工具: batch_export
参数: {
  "datasource_path": "D:/data/project.udbx",
  "dataset_names": ["roads", "buildings"],
  "output_format": "shapefile",
  "output_directory": "D:/output/shapefile"
}
```

### 步骤 8: 数据清理 — 删除不需要的数据集

```
工具: delete_dataset
参数: {
  "datasource_path": "D:/data/project.udbx",
  "dataset_name": "temp_import"
}
```

## 支持的批量导入格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| Shapefile | .shp | 需要同目录下有 .shx, .dbf 等关联文件 |
| GeoJSON | .geojson, .json | 自动检测几何类型 |
| CSV | .csv | 需含经纬度列（默认 longitude/latitude） |
| KML/KMZ | .kml, .kmz | Google Earth 格式 |
| DWG/DXF | .dwg, .dxf | AutoCAD 格式 |
| GeoTIFF | .tiff, .tif | 栅格数据 |

## 支持的批量导出格式

| 格式 | 扩展名 | 说明 |
|------|--------|------|
| Shapefile | .shp | 通用矢量格式 |
| GeoJSON | .geojson | Web 地图友好 |
| KML | .kml | Google Earth 兼容 |

## 预期结果

- 所有 5 个文件成功导入到 `project.udbx`
- `D:/output/geojson/` 目录下有 4 个 GeoJSON 文件
- `D:/output/shapefile/` 目录下有 2 组 Shapefile 文件
- `D:/output/dem_project.tif` 栅格文件

## 注意事项

1. 批量导入时会逐个处理，某个文件失败不会中断其他文件
2. CSV 导入需确保有经纬度列，默认列名为 `longitude` 和 `latitude`
3. 批量导出会自动创建输出目录
4. 大文件处理可能耗时，建议关注返回结果中的 success/failed 计数

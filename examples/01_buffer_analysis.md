# 示例 1: 缓冲区分析 — POI 兴趣点服务范围

## 场景描述

某城市规划部门需要分析全市 POI（兴趣点）的 500 米服务范围，识别服务盲区。
数据为 Shapefile 格式的 POI 点数据，需要创建缓冲区后导出为 GeoJSON 供前端可视化使用。

## 数据准备

- **输入数据**: `D:/data/city_pois.shp` — POI 点数据集（含 name、type、address 字段）
- **工作数据源**: `D:/data/analysis.udbx` — 分析用 UDBX 数据源
- **输出结果**: `D:/output/poi_buffer_500m.geojson`

## MCP 工具调用流程

### 步骤 1: 初始化环境

```
工具: initialize_supermap
参数: 无
```

### 步骤 2: 创建/打开数据源

```
工具: create_udbx_datasource
参数: { "file_path": "D:/data/analysis.udbx" }
```

### 步骤 3: 导入 POI 数据

```
工具: import_shapefile
参数: {
  "shapefile_path": "D:/data/city_pois.shp",
  "datasource_path": "D:/data/analysis.udbx",
  "dataset_name": "POI"
}
```

### 步骤 4: 查看导入数据

```
工具: list_datasets
参数: { "datasource_path": "D:/data/analysis.udbx" }
```

```
工具: query_dataset
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "dataset_name": "POI",
  "max_results": 5,
  "fields": ["name", "type"]
}
```

### 步骤 5: 创建 500 米缓冲区

```
工具: create_buffer
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "input_dataset": "POI",
  "output_dataset": "POI_Buffer_500m",
  "buffer_distance": 500
}
```

### 步骤 6: 按类型查询缓冲结果

```
工具: query_dataset
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "dataset_name": "POI_Buffer_500m",
  "sql_filter": "type = '医院'",
  "fields": ["name", "type"],
  "max_results": 10
}
```

### 步骤 7: 导出结果为 GeoJSON

```
工具: export_geojson
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "dataset_name": "POI_Buffer_500m",
  "output_path": "D:/output/poi_buffer_500m.geojson",
  "encode_to_epsg4326": true
}
```

## 进阶: 多级缓冲区

如果需要创建多个距离的同心缓冲区（如 200m、500m、1000m）：

```
工具: create_multi_buffer
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "input_dataset": "POI",
  "output_dataset": "POI_MultiBuffer",
  "buffer_distances": [200, 500, 1000],
  "dissolve": true
}
```

## 进阶: 融合重叠区域

如果需要将相邻 POI 的缓冲区融合为一个区域：

```
工具: dissolve
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "input_dataset": "POI_Buffer_500m",
  "output_dataset": "POI_Buffer_Dissolved",
  "dissolve_field": "type"
}
```

## 预期结果

- POI_Buffer_500m 数据集: 每个 POI 周围的 500 米缓冲多边形
- GeoJSON 文件: 可直接用于 Leaflet/Mapbox 等前端地图库
- 融合结果: 按类型聚合后的服务范围区域

## 注意事项

1. 缓冲距离单位取决于数据源的坐标系，投影坐标系下为米，地理坐标系下为度
2. 如需确保距离单位为米，建议先将数据投影到合适的投影坐标系
3. 大量要素的缓冲区分析可能耗时较长，建议先测试小数据集

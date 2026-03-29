# 示例 3: DEM 地形分析 — 坡度坡向与适宜性评价

## 场景描述

某农业部门需要基于 DEM 数据评估某区域的坡度和坡向，为农业种植选址提供参考。
需要生成坡度图、坡向图，并结合重分类功能划分适宜等级。

## 数据准备

- **输入数据**: `D:/data/dem_30m.tif` — 30 米分辨率 DEM 栅格数据
- **工作数据源**: `D:/data/analysis.udbx`
- **输出结果**: 坡度图、坡向图、适宜性分区 GeoJSON

## MCP 工具调用流程

### 步骤 1: 初始化并创建数据源

```
工具: initialize_supermap
参数: 无

工具: create_udbx_datasource
参数: { "file_path": "D:/data/analysis.udbx" }
```

### 步骤 2: 导入 DEM 数据

```
工具: import_tiff
参数: {
  "tiff_path": "D:/data/dem_30m.tif",
  "datasource_path": "D:/data/analysis.udbx",
  "dataset_name": "DEM_30m"
}
```

### 步骤 3: 查看导入结果

```
工具: get_dataset_info
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "dataset_name": "DEM_30m"
}
```

### 步骤 4: 计算坡度

```
工具: calculate_slope
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "dem_dataset": "DEM_30m",
  "output_dataset": "Slope"
}
```

### 步骤 5: 计算坡向

```
工具: calculate_aspect
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "dem_dataset": "DEM_30m",
  "output_dataset": "Aspect"
}
```

### 步骤 6: 计算山体阴影（地形可视化）

```
工具: calculate_hillshade
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "dem_dataset": "DEM_30m",
  "output_dataset": "Hillshade",
  "sun_azimuth": 315,
  "sun_altitude": 45
}
```

### 步骤 7: 坡度重分类 — 农业适宜性评价

根据农业种植要求，将坡度分为 4 个适宜等级：

| 等级 | 坡度范围 (度) | 适宜性 |
|------|-------------|--------|
| 1 | 0-5 | 最适宜（平原） |
| 2 | 5-15 | 适宜（缓坡） |
| 3 | 15-25 | 一般（中坡） |
| 4 | 25-90 | 不适宜（陡坡） |

```
工具: reclassify
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "input_dataset": "Slope",
  "output_dataset": "Slope_Suitability",
  "reclassify_table": [
    {"start": 0, "end": 5, "value": 1},
    {"start": 5, "end": 15, "value": 2},
    {"start": 15, "end": 25, "value": 3},
    {"start": 25, "end": 90, "value": 4}
  ]
}
```

### 步骤 8: 导出分析结果

```
工具: export_tiff
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "dataset_name": "Slope_Suitability",
  "output_path": "D:/output/slope_suitability.tif"
}

工具: export_tiff
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "dataset_name": "Hillshade",
  "output_path": "D:/output/hillshade.tif"
}
```

## 进阶: 水文分析链

基于 DEM 进行完整的水文分析流程：

```
工具: fill_sink
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "dem_dataset": "DEM_30m",
  "output_dataset": "DEM_Filled"
}
```

```
工具: calculate_slope  (注：需使用 flow_direction 工具，当前通过 watershed 间接使用)
```

## 进阶: 空间插值

如果有点数据（如气象站降雨量），可以插值为连续栅格面：

```
工具: idw_interpolate
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "input_dataset": "WeatherStations",
  "output_dataset": "Rainfall_IDW",
  "z_field": "rainfall",
  "power": 2,
  "cell_size": 100
}
```

## 预期结果

- `Slope`: 坡度栅格（0-90 度）
- `Aspect`: 坡向栅格（0-360 度）
- `Hillshade`: 山体阴影栅格（用于地形可视化）
- `Slope_Suitability`: 坡度适宜性分区（1-4 级）
- 输出 TIFF 文件可用于 QGIS/ArcGIS 等桌面 GIS 查看或发布为地图服务

## 注意事项

1. DEM 分辨率（像元大小）影响分析精度和计算速度，大数据量建议先用小范围测试
2. 坡度/坡向分析要求 DEM 无无效值（NoData），可先用 `fill_sink` 填洼
3. 重分类表的区间范围应覆盖所有可能的值，避免遗漏
4. 栅格数据导出为 TIFF 时，坐标信息会自动保留

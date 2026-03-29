# 示例 2: 叠加分析 + 结果导出 — 土地利用适宜性评估

## 场景描述

某环保部门需要评估工业用地与生态保护区的空间关系，识别潜在的生态冲突区域。
通过叠加分析找出工业用地与生态保护区相交的区域，并导出冲突地块报告。

## 数据准备

- **数据 1**: `D:/data/industrial_land.shp` — 工业用地范围（面数据）
- **数据 2**: `D:/data/ecological_zone.shp` — 生态保护区范围（面数据）
- **工作数据源**: `D:/data/analysis.udbx`
- **输出结果**: 冲突区域 Shapefile + 统计报告

## MCP 工具调用流程

### 步骤 1: 初始化并创建数据源

```
工具: initialize_supermap
参数: 无

工具: create_udbx_datasource
参数: { "file_path": "D:/data/analysis.udbx" }
```

### 步骤 2: 批量导入数据

```
工具: batch_import
参数: {
  "file_paths": [
    "D:/data/industrial_land.shp",
    "D:/data/ecological_zone.shp"
  ],
  "datasource_path": "D:/data/analysis.udbx",
  "dataset_names": ["IndustrialLand", "EcoZone"]
}
```

### 步骤 3: 查看数据概况

```
工具: get_dataset_info
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "dataset_name": "IndustrialLand"
}

工具: get_dataset_info
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "dataset_name": "EcoZone"
}
```

### 步骤 4: 执行叠加分析（求交）

找出工业用地与生态保护区的重叠区域：

```
工具: overlay
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "input_dataset": "IndustrialLand",
  "overlay_dataset": "EcoZone",
  "output_dataset": "ConflictZone",
  "operation": "INTERSECT"
}
```

### 步骤 5: 查询冲突区域统计

```
工具: query_dataset
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "dataset_name": "ConflictZone",
  "max_results": 20
}
```

### 步骤 6: 对冲突区域创建缓冲区（扩展 200 米预警范围）

```
工具: create_buffer
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "input_dataset": "ConflictZone",
  "output_dataset": "ConflictZone_Buffer",
  "buffer_distance": 200
}
```

### 步骤 7: 导出所有分析结果

```
工具: batch_export
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "dataset_names": ["ConflictZone", "ConflictZone_Buffer"],
  "output_format": "shapefile",
  "output_directory": "D:/output/ecological_assessment"
}
```

## 进阶: 裁剪分析

如果需要仅保留生态保护区范围内的工业用地（而非求交）：

```
工具: clip_data
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "input_dataset": "IndustrialLand",
  "clip_dataset": "EcoZone",
  "output_dataset": "IndustrialLand_InEcoZone"
}
```

## 进阶: 擦除分析

如果需要排除生态保护区范围内的工业用地，获取安全区域：

```
工具: overlay
参数: {
  "datasource_path": "D:/data/analysis.udbx",
  "input_dataset": "IndustrialLand",
  "overlay_dataset": "EcoZone",
  "output_dataset": "SafeIndustrialZone",
  "operation": "ERASE"
}
```

## 叠加分析操作类型参考

| 操作 | 说明 | 适用场景 |
|------|------|----------|
| `INTERSECT` | 求交集 | 找重叠区域 |
| `UNION` | 求并集 | 合并两个图层 |
| `ERASE` | 擦除 | 去除重叠部分 |
| `IDENTITY` | 标识叠加 | 保留输入全部 + 叠加属性 |
| `CLIP` | 裁剪 | 用裁剪区域截取输入 |
| `UPDATE` | 更新 | 用叠加区域更新输入 |
| `XOR` | 对称差 | 仅保留不重叠部分 |

## 预期结果

- `ConflictZone`: 工业用地与生态保护区重叠的地块
- `ConflictZone_Buffer`: 冲突区域扩展 200 米的预警范围
- 输出目录中包含所有结果的 Shapefile 文件

## 注意事项

1. 叠加分析的两个数据集建议使用相同的坐标系
2. 大面积面数据的叠加分析可能较慢，建议先用 SQL 查询筛选范围
3. 叠加结果可能产生碎部多边形，可用 `dissolve` 工具合并

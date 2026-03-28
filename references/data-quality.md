# SuperMap iDesktopX 数据质量检查指南

> 适用版本：iDesktopX 2025  
> 功能：拓扑检查、数据清洗、错误修复、数据验证

---

## 一、数据质量检查概述

### 1.1 数据质量问题类型

| 问题类型 | 说明 | 影响 |
|---------|------|------|
| **拓扑错误** | 要素之间空间关系不正确 | 空间分析失败、结果不准确 |
| **几何错误** | 要素几何本身有问题 (自相交、空几何、无效坐标) | 无法正确显示和分析 |
| **重复要素** | 相同要素存在多份 | 数据冗余、统计错误 |
| **属性错误** | 属性数据缺失、类型错误、格式不一致 | 属性查询和统计失败 |
| **一致性错误** | 数据之间逻辑不一致 (如总面积与分面积不符) | 数据可信度降低 |

### 1.2 数据质量检查流程

```
数据导入 → 拓扑检查 → 错误修复 → 数据清洗 → 验证 → 质量报告
```

---

## 二、拓扑检查

### 2.1 拓扑规则

SuperMap 支持的拓扑规则:

| 规则名称 | 说明 | 适用数据集类型 |
|---------|------|--------------|
| **不能重叠** | 同一图层的要素不能重叠 | 面 |
| **不能相交** | 同一图层的要素不能相交 | 线 |
| **必须被另一图层要素覆盖** | 当前图层要素必须被另一图层要素覆盖 | 面 |
| **必须在内部** | 当前图层要素必须在另一图层要素内部 | 点、线、面 |
| **不能有空隙** | 同一面图层要素之间不能有空隙 | 面 |
| **不能有悬挂点** | 线要素的端点必须与其他要素连接 | 线 |
| **不能有伪节点** | 线要素中间不能有节点 | 线 |
| **必须相交** | 线要素必须与其他要素相交 | 线 |

### 2.2 GUI 操作步骤

1. **创建拓扑数据集**:
   - 数据 → 数据集 → 创建拓扑数据集
   - 选择参与拓扑的数据集
   - 设置拓扑规则

2. **验证拓扑**:
   - 右键拓扑数据集 → 验证拓扑
   - 系统自动检查拓扑错误

3. **查看拓扑错误**:
   - 拓扑数据集 → 查看错误
   - 显示错误要素位置

4. **修复拓扑错误**:
   - 选择错误 → 右键 → 修复
   - 或手动编辑要素几何

### 2.3 iObjectsPy 操作

```python
import iobjectspy as spy
from iobjectspy import (DatasetTopology, TopologyRule, 
                        TopologyValidateOption)

# 1. 创建拓扑数据集
dataset_topology = spy.create_topology_dataset(
    out_datasource=ds,
    out_name="RoadTopology",
    datasets=[ds["Roads"]],  # 参与拓扑的数据集
    rules=[
        TopologyRule(
            rule_type="CannotOverlap",  # 不能重叠
            dataset_name="Roads",
            tolerance=0.001  # 容差 (米)
        ),
        TopologyRule(
            rule_type="CannotSelfIntersect",  # 不能自相交
            dataset_name="Roads",
            tolerance=0.001
        )
    ]
)

# 2. 验证拓扑
option = TopologyValidateOption()
option.tolerance = 0.001  # 检查容差

result = spy.validate_topology(
    dataset_topology=dataset_topology,
    validate_option=option
)

print(f"拓扑错误数: {result.error_count}")
print(f"拓扑错误详情: {result.errors}")

# 3. 获取拓扑错误
for error in result.errors:
    print(f"错误类型: {error.rule_type}")
    print(f"错误描述: {error.description}")
    print(f"错误要素: {error.feature_ids}")
    
# 4. 修复拓扑错误 (简单错误可自动修复)
for error in result.errors:
    if error.can_auto_fix:
        spy.fix_topology_error(
            dataset_topology=dataset_topology,
            error_id=error.id
        )
        print(f"已修复错误: {error.id}")

# 5. 导出拓扑错误为数据集
error_dataset = spy.export_topology_errors(
    dataset_topology=dataset_topology,
    out_datasource=ds,
    out_name="TopologyErrors"
)
```

---

## 三、几何错误修复

### 3.1 常见几何错误类型

| 错误类型 | 说明 | 自动修复 |
|---------|------|---------|
| **自相交** | 多边形边界自身相交 | ✅ 可以 |
| **空几何** | 要素几何为空 | ✅ 可以 (删除) |
| **无效坐标** | 坐标超出有效范围 | ❌ 需手动修复 |
| **几何太小** | 要素面积/长度小于容差 | ✅ 可以 (删除或合并) |
| **环方向错误** | 多边形外环和内环方向错误 | ✅ 可以 |
| **节点过密** | 线要素节点过多 | ✅ 可以 (简化) |

### 3.2 GUI 操作步骤

1. **检查几何错误**:
   - 数据 → 数据处理 → 几何检查
   - 选择数据集和检查规则

2. **查看错误**:
   - 系统列出所有几何错误
   - 可定位到错误要素

3. **修复错误**:
   - 选择错误 → 修复
   - 或批量修复所有错误

### 3.3 iObjectsPy 操作

```python
import iobjectspy as spy
from iobjectspy import GeometryCheckOption, GeometryFixOption

# 1. 检查几何错误
check_option = GeometryCheckOption()
check_option.check_self_intersection = True    # 检查自相交
check_option.check_empty_geometry = True      # 检查空几何
check_option.check_invalid_coordinates = True # 检查无效坐标
check_option.tolerance = 0.001                # 容差

errors = spy.check_geometry(
    dataset=ds["Cities"],
    check_option=check_option
)

print(f"几何错误数: {len(errors)}")

# 2. 分类统计错误
error_types = {}
for error in errors:
    error_type = error.type
    error_types[error_type] = error_types.get(error_type, 0) + 1

print("\n错误类型统计:")
for error_type, count in error_types.items():
    print(f"  {error_type}: {count}")

# 3. 修复几何错误
fix_option = GeometryFixOption()
fix_option.fix_self_intersection = True  # 修复自相交
fix_option.remove_empty_geometry = True  # 删除空几何
fix_option.simplify_geometry = True     # 简化几何
fix_option.tolerance = 0.001

fixed_count = spy.fix_geometry(
    dataset=ds["Cities"],
    fix_option=fix_option
)

print(f"\n已修复几何错误: {fixed_count} 个")

# 4. 导出几何错误为数据集
error_dataset = spy.export_geometry_errors(
    errors=errors,
    out_datasource=ds,
    out_name="GeometryErrors"
)

# 5. 简化几何 (减少节点数量)
simplified_dataset = spy.simplify_geometry(
    source_dataset=ds["Roads"],
    tolerance=1.0,  # 简化容差 (米)
    out_datasource=ds,
    out_name="Roads_Simplified"
)
print(f"简化后的道路数据集: {simplified_dataset.name}")
```

---

## 四、重复要素处理

### 4.1 重复要素类型

| 类型 | 说明 | 处理方式 |
|-----|------|---------|
| **完全重复** | 几何和属性完全相同 | 删除重复 |
| **几何重复** | 几何相同,属性不同 | 合并或选择其中一个 |
| **属性重复** | 几何不同,属性相同 | 保留所有 (可能合法) |

### 4.2 GUI 操作步骤

1. **查找重复要素**:
   - 数据 → 数据处理 → 查找重复
   - 选择数据集和比较字段

2. **查看重复**:
   - 系统列出重复要素组
   - 每组包含所有重复要素

3. **处理重复**:
   - 选择保留的要素
   - 删除其他重复要素

### 4.3 iObjectsPy 操作

```python
import iobjectspy as spy
from iobjectspy import DuplicateCheckOption

# 1. 查找完全重复要素 (几何和属性都相同)
option = DuplicateCheckOption()
option.check_geometry = True   # 比较几何
option.check_attributes = True # 比较属性
option.tolerance = 0.001       # 几何比较容差

duplicates = spy.find_duplicates(
    dataset=ds["Cities"],
    check_option=option
)

print(f"找到重复要素组: {len(duplicates)} 组")

# 2. 显示重复要素详情
for group_id, feature_ids in enumerate(duplicates):
    print(f"\n重复组 {group_id + 1}: {len(feature_ids)} 个要素")
    for fid in feature_ids:
        print(f"  Feature ID: {fid}")

# 3. 删除重复要素 (保留每组第一个)
deleted_count = 0
for feature_ids in duplicates:
    # 保留第一个,删除其余
    for fid in feature_ids[1:]:
        ds["Cities"].delete(fid)
        deleted_count += 1

print(f"\n已删除重复要素: {deleted_count} 个")

# 4. 导出重复要素为数据集 (用于人工审核)
duplicate_dataset = spy.export_duplicates(
    dataset=ds["Cities"],
    duplicates=duplicates,
    out_datasource=ds,
    out_name="DuplicateCities"
)

# 5. 基于几何查找重复 (仅比较几何,不比较属性)
option_geom_only = DuplicateCheckOption()
option_geom_only.check_geometry = True
option_geom_only.check_attributes = False  # 不比较属性
option_geom_only.tolerance = 0.001

duplicates_geom = spy.find_duplicates(
    dataset=ds["Cities"],
    check_option=option_geom_only
)

print(f"\n几何重复要素组: {len(duplicates_geom)} 组")
```

---

## 五、属性数据验证

### 5.1 属性验证规则

| 规则类型 | 说明 | 示例 |
|---------|------|------|
| **非空检查** | 字段不能为空 | 名称、ID 等关键字段 |
| **范围检查** | 数值字段必须在指定范围内 | 人口数 ≥ 0 |
| **格式检查** | 字符串格式必须正确 | 邮箱、电话号码 |
| **唯一性检查** | 字段值必须唯一 | ID 字段 |
| **一致性检查** | 字段之间逻辑关系正确 | 面积 ≥ 0 |
| **枚举检查** | 字段值必须在枚举列表中 | 土地利用类型 |

### 5.2 GUI 操作步骤

1. **设置验证规则**:
   - 数据 → 数据集属性 → 验证规则
   - 添加验证规则

2. **验证属性**:
   - 数据 → 数据处理 → 验证属性
   - 选择数据集和验证规则

3. **查看验证结果**:
   - 系统列出所有验证错误
   - 显示错误字段和错误值

4. **修复错误**:
   - 选择错误 → 编辑属性
   - 或批量修复

### 5.3 iObjectsPy 操作

```python
import iobjectspy as spy
from iobjectspy import AttributeValidationRule, AttributeValidationOption

# 1. 定义验证规则
rules = [
    # 非空检查
    AttributeValidationRule(
        field_name="Name",
        rule_type="NotNull",
        error_message="名称不能为空"
    ),
    
    # 范围检查
    AttributeValidationRule(
        field_name="Population",
        rule_type="Range",
        min_value=0,
        max_value=100000000,
        error_message="人口数必须在 0 到 1 亿之间"
    ),
    
    # 格式检查 (正则表达式)
    AttributeValidationRule(
        field_name="Email",
        rule_type="Pattern",
        pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        error_message="邮箱格式不正确"
    ),
    
    # 唯一性检查
    AttributeValidationRule(
        field_name="ID",
        rule_type="Unique",
        error_message="ID 必须唯一"
    ),
    
    # 枚举检查
    AttributeValidationRule(
        field_name="Type",
        rule_type="Enumeration",
        allowed_values=["省会", "地级市", "县级市", "县"],
        error_message="城市类型必须是: 省会/地级市/县级市/县"
    )
]

# 2. 执行属性验证
option = AttributeValidationOption()
option.rules = rules

validation_result = spy.validate_attributes(
    dataset=ds["Cities"],
    validation_option=option
)

print(f"验证错误数: {len(validation_result.errors)}")

# 3. 显示验证错误
for error in validation_result.errors:
    print(f"\n要素 ID: {error.feature_id}")
    print(f"字段: {error.field_name}")
    print(f"错误值: {error.field_value}")
    print(f"错误类型: {error.rule_type}")
    print(f"错误描述: {error.error_message}")

# 4. 导出验证错误为数据集
error_dataset = spy.export_validation_errors(
    validation_result=validation_result,
    out_datasource=ds,
    out_name="AttributeErrors"
)

# 5. 自动修复简单错误 (如去除字符串前后空格)
fixed_count = spy.trim_string_fields(
    dataset=ds["Cities"],
    fields=["Name", "Type"]
)
print(f"\n已修整字符串字段: {fixed_count} 条记录")

# 6. 批量更新属性 (修复范围错误)
# 将负数人口设为 0
from iobjectspy import QueryParameter

query = QueryParameter()
query.attribute_filter = "Population < 0"

rs = ds["Cities"].query(query)
while not rs.is_EOF:
    rs.set_field_value("Population", 0)
    rs.update()
    rs.move_next()
rs.close()

print("已修复负数人口数")
```

---

## 六、数据质量报告

### 6.1 生成质量报告

```python
import iobjectspy as spy
from datetime import datetime

def generate_quality_report(datasource, dataset_name, output_path):
    """生成数据质量报告"""
    
    dataset = datasource[dataset_name]
    
    # 收集质量指标
    report = {
        "数据集名称": dataset_name,
        "检查时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "要素总数": dataset.record_count,
        "字段数": dataset.field_count,
        "数据集类型": dataset.type.name
    }
    
    # 几何检查
    geom_errors = spy.check_geometry(dataset)
    report["几何错误数"] = len(geom_errors)
    
    # 重复要素检查
    duplicates = spy.find_duplicates(dataset)
    report["重复要素组数"] = len(duplicates)
    
    # 拓扑检查 (如果数据集参与拓扑)
    try:
        topo = datasource[f"{dataset_name}_Topology"]
        topo_result = spy.validate_topology(topo)
        report["拓扑错误数"] = topo_result.error_count
    except:
        report["拓扑错误数"] = "未检查"
    
    # 属性验证
    # 假设已有验证规则
    try:
        attr_errors = spy.validate_attributes(dataset)
        report["属性错误数"] = len(attr_errors.errors)
    except:
        report["属性错误数"] = "未检查"
    
    # 计算质量得分
    total_errors = (
        report["几何错误数"] if isinstance(report["几何错误数"], int) else 0
    )
    total_errors += report["重复要素组数"]
    total_errors += (
        report["拓扑错误数"] if isinstance(report["拓扑错误数"], int) else 0
    )
    total_errors += (
        report["属性错误数"] if isinstance(report["属性错误数"], int) else 0
    )
    
    # 质量得分: 100 - (错误数 / 要素总数 * 100)
    if dataset.record_count > 0:
        quality_score = max(0, 100 - (total_errors / dataset.record_count * 100))
        report["质量得分"] = f"{quality_score:.1f}分"
    else:
        report["质量得分"] = "无法计算"
    
    # 写入报告文件
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("SuperMap iDesktopX 数据质量报告\n")
        f.write("=" * 60 + "\n\n")
        
        for key, value in report.items():
            f.write(f"{key}: {value}\n")
        
        f.write("\n" + "=" * 60 + "\n")
    
    return report

# 生成质量报告
report = generate_quality_report(
    datasource=ds,
    dataset_name="Cities",
    output_path="D:/output/DataQualityReport.txt"
)

print("数据质量报告已生成:")
for key, value in report.items():
    print(f"  {key}: {value}")
```

---

## 七、工作流示例

### 工作流 1: 数据质量全面检查

```
步骤 1: 导入数据
  → MCP: import_shapefile(source_path="D:/data/cities.shp")

步骤 2: 拓扑检查
  → spy.create_topology_dataset()
  → spy.validate_topology()
  → 修复拓扑错误

步骤 3: 几何检查
  → spy.check_geometry()
  → spy.fix_geometry()

步骤 4: 查找重复要素
  → spy.find_duplicates()
  → 删除重复要素

步骤 5: 属性验证
  → 定义验证规则
  → spy.validate_attributes()
  → 修复属性错误

步骤 6: 生成质量报告
  → generate_quality_report()
```

### 工作流 2: 批量数据清洗

```python
def batch_clean_data(datasource, dataset_pattern, output_datasource):
    """批量清洗数据"""
    
    import fnmatch
    
    # 查找匹配的数据集
    datasets = [name for name in datasource if fnmatch.fnmatch(name, dataset_pattern)]
    
    for dataset_name in datasets:
        dataset = datasource[dataset_name]
        
        print(f"\n清洗数据集: {dataset_name}")
        
        # 1. 几何检查和修复
        errors = spy.check_geometry(dataset)
        if errors:
            print(f"  几何错误: {len(errors)} 个")
            fixed = spy.fix_geometry(dataset)
            print(f"  已修复: {fixed} 个")
        
        # 2. 删除重复要素
        duplicates = spy.find_duplicates(dataset)
        if duplicates:
            print(f"  重复要素组: {len(duplicates)} 组")
            # 删除重复逻辑...
        
        # 3. 属性修整
        fixed = spy.trim_string_fields(dataset)
        print(f"  修整字符串: {fixed} 条")
        
        # 4. 导出到目标数据源
        spy.export_to_shape(
            source_data=dataset,
            target_file_path=f"D:/cleaned/{dataset_name}.shp"
        )
        
        print(f"  清洗完成,已导出到: D:/cleaned/{dataset_name}.shp")

# 批量清洗所有以 "Roads_" 开头的数据集
batch_clean_data(
    datasource=ds,
    dataset_pattern="Roads_*",
    output_datasource="cleaned.udbx"
)
```

---

## 八、MCP 工具建议

### 建议新增的 MCP 工具

```python
# 1. 拓扑检查
tool_topology_check = {
    "name": "topology_check",
    "description": "检查数据集的拓扑错误",
    "parameters": {
        "datasource_name": "数据源名称",
        "dataset_name": "数据集名称",
        "rules": "拓扑规则列表",
        "tolerance": "检查容差 (米)"
    }
}

# 2. 修复几何错误
tool_fix_geometry_errors = {
    "name": "fix_geometry_errors",
    "description": "修复数据集中的几何错误",
    "parameters": {
        "datasource_name": "数据源名称",
        "dataset_name": "数据集名称",
        "fix_options": "修复选项"
    }
}

# 3. 删除重复要素
tool_remove_duplicates = {
    "name": "remove_duplicates",
    "description": "查找并删除重复要素",
    "parameters": {
        "datasource_name": "数据源名称",
        "dataset_name": "数据集名称",
        "check_geometry": "是否比较几何",
        "check_attributes": "是否比较属性",
        "tolerance": "几何比较容差 (米)"
    }
}

# 4. 验证属性
tool_validate_attributes = {
    "name": "validate_attributes",
    "description": "验证数据集的属性数据",
    "parameters": {
        "datasource_name": "数据源名称",
        "dataset_name": "数据集名称",
        "validation_rules": "验证规则列表"
    }
}
```

---

## 九、常见问题

**Q: 拓扑检查速度很慢?**  
A: 大数据量时建议:
1. 分区域检查
2. 增大容差值
3. 使用分布式分析 (大数据工具)

**Q: 几何错误无法自动修复?**  
A: 某些复杂几何错误需要手动修复:
1. 导出错误要素为数据集
2. 在 iDesktopX GUI 中手动编辑
3. 修复后重新导入

**Q: 重复要素删除后无法恢复?**  
A: 建议:
1. 导出重复要素为数据集 (备份)
2. 人工审核后再删除
3. 或使用版本管理功能

**Q: 属性验证规则太多,如何管理?**  
A: 建议:
1. 将验证规则保存为 JSON 文件
2. 按业务分类管理规则
3. 批量应用规则库

---

## 十、参考资料

- SuperMap iDesktopX 官方帮助文档 - 数据管理模块
- SuperMap iObjectsPy API 参考 - DatasetTopology、GeometryCheckOption
- GIS 数据质量标准 - GB/T 24356-2009

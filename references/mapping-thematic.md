# SuperMap iDesktopX 地图制图与专题图指南

> 适用版本：iDesktopX 2025

---

## 一、地图窗口基本操作

### 打开/新建地图

| 操作 | 路径 |
|------|------|
| 新建空白地图 | 工作空间管理器 → 地图 → 右键 → 新建地图 |
| 打开已有地图 | 工作空间管理器 → 地图 → 双击地图名称 |
| 添加图层 | 将数据集拖入地图窗口，或菜单 → 添加图层 |

### 地图操作工具

| 工具 | 快捷键/说明 |
|------|------------|
| 浏览（平移）| 按住鼠标左键拖拽 |
| 缩放 | 鼠标滚轮 / Ctrl+滚轮 |
| 全图显示 | 双击鼠标中键 / Home 键 |
| 选择要素 | 单击 / 框选 / 多边形选择 |
| 测量距离 | 菜单 → 查看 → 测量距离 |
| 测量面积 | 菜单 → 查看 → 测量面积 |

---

## 二、图层管理

### 图层操作

| 操作 | 说明 |
|------|------|
| 显示/隐藏图层 | 图层控制面板中勾选/取消勾选 |
| 图层顺序 | 拖拽调整（上方图层覆盖下方） |
| 设置图层比例尺范围 | 右键图层 → 属性 → 设置可见比例尺 |
| 图层分组 | 将相关图层组织为组，便于管理 |
| 图层重命名 | 双击图层名称 |
| 删除图层 | 右键 → 删除，或 Delete 键 |

### 图层风格设置

```
右键图层 → 属性 → 风格
├── 点风格：符号、大小、颜色、旋转角
├── 线风格：线型、线宽、颜色、端部形状
└── 面风格：填充颜色、填充样式、边框线型
```

---

## 三、专题图

### 3.1 单值专题图

**用途**：按字段的离散值给要素分配不同颜色/符号（如土地利用类型）

**GUI 操作**：
1. 右键图层 → 专题图 → 新建专题图
2. 选择"单值专题图"
3. 选择表达字段（如 LandType）
4. 设置每个值的颜色/符号

**iObjectsPy 操作**：
```python
from iobjectspy.mapping import ThematicLayerSingleValue, ThematicStyle

# 获取地图图层
layer = map_obj.layers["LandUse"]

# 创建单值专题图
thematic = ThematicLayerSingleValue()
thematic.expression = "LandType"   # 表达字段
thematic.styles = {
    "耕地": ThematicStyle(fill_color=(200, 255, 200)),
    "林地": ThematicStyle(fill_color=(0, 180, 0)),
    "水体": ThematicStyle(fill_color=(100, 150, 255)),
    "建筑": ThematicStyle(fill_color=(255, 100, 100)),
}
layer.thematic = thematic
```

### 3.2 分段专题图

**用途**：按数值字段的范围分级着色（如人口密度图）

**GUI 操作**：
1. 右键图层 → 专题图 → 新建专题图
2. 选择"分段专题图"
3. 选择数值字段（如 Population）
4. 选择分级方法（自然断点/等间距/百分位数）
5. 设置颜色方案

**分级方法**：

| 方法 | 适用场景 |
|------|----------|
| 自然断点（Jenks）| 数据分布有明显聚类时推荐 |
| 等间距 | 数据分布较均匀 |
| 等数量 | 确保每级要素数量相同 |
| 标准差 | 按偏离均值的标准差数分级 |
| 百分位数 | 0、25、50、75、100分位 |

### 3.3 标签专题图

**用途**：在地图上显示字段值作为注记

**GUI 操作**：
1. 右键图层 → 专题图 → 新建专题图
2. 选择"标签专题图"
3. 选择显示字段
4. 设置字体、字号、颜色、偏移量

**iObjectsPy 操作**：
```python
from iobjectspy.mapping import ThematicLayerLabel

thematic = ThematicLayerLabel()
thematic.label_expression = "CityName"   # 标注字段
thematic.uniform_style.font_size = 12
thematic.uniform_style.font_color = (0, 0, 0)
thematic.uniform_style.bold = True
layer.thematic = thematic
```

### 3.4 统计专题图（柱状图/饼图）

**用途**：在地图上每个要素位置显示统计图表

**GUI 操作**：
1. 右键图层 → 专题图 → 新建统计专题图
2. 选择"柱状图"或"饼图"
3. 选择参与统计的字段（可多字段）
4. 设置图表大小和颜色

```python
from iobjectspy.mapping import ThematicLayerGraph, GraphType

thematic = ThematicLayerGraph()
thematic.graph_type = GraphType.BAR       # 柱状图，或 PIE 饼图
thematic.fields = ["Pop2010", "Pop2020"]   # 统计字段
thematic.graph_size = 20                   # 图表大小（像素）
layer.thematic = thematic
```

### 3.5 密度图（热力图）

**用途**：将点数据可视化为连续热度分布

**GUI 操作**：
1. 右键图层 → 专题图 → 热力图
2. 设置权重字段和搜索半径
3. 选择颜色方案

### 3.6 等级符号图

**用途**：用大小比例的符号表达数量差异

---

## 四、符号资源管理

### 符号类型

| 类型 | 说明 |
|------|------|
| 点符号 | 各种形状、图标符号 |
| 线符号 | 实线、虚线、铁路线等线型 |
| 填充符号 | 纯色、渐变、图案填充 |
| 文本符号 | 字体、字号、字色 |

### 自定义符号

1. 菜单：**资源 → 符号管理器**
2. 可导入 SVG/PNG 作为点符号
3. 可定义复合线符号
4. 符号可保存到工作空间的资源库

---

## 五、投影设置与坐标系

### 为数据集设置坐标系

**GUI 操作**：
1. 右键数据集 → 属性 → 投影信息
2. 选择坐标系（地理坐标系 / 投影坐标系）
3. 确认

**iObjectsPy 操作**：
```python
from iobjectspy import PrjCoordSys, PrjCoordSysType

# 获取 WGS84 地理坐标系
prj = PrjCoordSys(PrjCoordSysType.EarthLongitudeLatitude)

# 设置数据集坐标系
dataset.prj_coord_sys = prj
```

### 投影转换（批量）

**GUI 操作**：数据 → 投影转换 → 选择源坐标系和目标坐标系

```python
# 批量投影转换：从 WGS84 转为 CGCS2000 / 3度带（中央经线 117°）
spy.prj_coord_sys_trans(
    source_dataset=dv,
    target_prj_type=PrjCoordSysType.GaussKruger_CGCS2000_3_117,
    out_datasource=ds,
    out_dataset="DataSet_CGCS2000"
)
```

### 常用坐标系

| 坐标系名称 | PrjCoordSysType | 说明 |
|-----------|----------------|------|
| WGS84 经纬度 | `EarthLongitudeLatitude` | 全球通用，GPS坐标 |
| CGCS2000 经纬度 | `GCS_China2000` | 中国国家大地坐标系 |
| 北京54（克拉索夫斯基） | `GCS_Beijing54` | 旧版中国坐标系 |
| 西安80 | `GCS_Xian80` | 中国旧坐标系 |
| CGCS2000 高斯（3度带）| `GaussKruger_CGCS2000_3_*` | 中国大比例尺地图常用 |
| CGCS2000 高斯（6度带）| `GaussKruger_CGCS2000_6_*` | 中国中小比例尺地图 |
| Web Mercator | `WGS1984WebMercatorAuxiliarySphere` | 互联网地图标准 |

---

## 六、地图输出

### 打印输出（布局）

1. 菜单：**开始 → 新建 → 布局**
2. 添加地图框：插入 → 地图框 → 选择地图
3. 添加图例：插入 → 图例
4. 添加比例尺：插入 → 比例尺
5. 添加指北针：插入 → 指北针
6. 添加标题：插入 → 文本
7. 打印：文件 → 打印

### 导出图片

```python
# 导出地图为 PNG
spy.export_map_to_image(
    map_obj=map_obj,
    output_path=r"D:\output\map.png",
    width=2480,     # A4 300dpi 宽度
    height=3508,    # A4 300dpi 高度
    dpi=300
)
```

### 发布为地图服务

1. 菜单：**开始 → 发布 → 发布iServer服务**
2. 选择要发布的地图
3. 配置 iServer 服务地址
4. 选择服务类型（REST/WMS/WMTS）

---

## 七、空间查询

### SQL 查询

```python
# 属性查询
rs = dv.query("Population > 1000000 AND Province = '北京市'")

# 空间查询（按范围）
from iobjectspy import SpatialQueryMode
rs = dv.spatial_query(
    geometry=search_region,       # 搜索范围（GeoRegion）
    query_mode=SpatialQueryMode.CONTAIN  # 包含关系
)
# 其他模式：INTERSECT（相交）/ WITHIN（被包含）/ TOUCH（相接触）
```

### 按空间位置查询

**GUI 操作**：
1. 菜单：查询 → 空间查询
2. 设置查询图层和范围
3. 选择空间关系（包含/相交/被包含等）

---

## 参考链接

- 帮助手册：https://help.supermap.com/iDesktopX/zh/
- iObjectsPy mapping 模块：https://iobjectspy.supermap.io/html_zh/

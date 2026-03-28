# SuperMap iDesktopX 三维数据处理与分析指南

> 适用版本：iDesktopX 2025
> iObjectsPy 三维模块：`iobjectspy.threedesigner`
> 更新时间：2026-03-27

---

## 一、三维数据类型

| 类型 | 格式/数据集 | 说明 | 适用场景 |
|------|------------|------|----------|
| 地形（DEM）| DatasetGrid | 高程栅格，构建三维地形表面 | 地形分析、流域计算、可视域 |
| 正射影像（DOM）| DatasetImage | 贴附于地形的正射影像 | 地图贴图、影像展示 |
| 倾斜摄影 | OSGB / S3M | 无人机采集的实景三维模型 | 城市三维重建、规划展示 |
| BIM 建筑 | IFC → S3M | 建筑信息模型，可导入挂接属性 | 建筑设计、设施管理 |
| 点云 | LAS / LAZ | LiDAR 扫描的三维点集合 | 地形测绘、三维建模 |
| 三维矢量 | DatasetPoint3D / Line3D / Region3D | 带 Z 值的矢量数据集 | 地下管网、电力线路 |
| 三维模型 | 3DS / OBJ / FBX | 单体三维模型 | 标志性建筑、独立设施 |
| 三维瓦片 | 3D Tiles | OGC 标准三维瓦片格式 | Web 三维展示、大规模数据 |

---

## 二、三维场景（Scene）基本操作

### 启动三维场景

在 iDesktopX 界面中：
1. 工作空间管理器 → 场景 → 双击场景名称（或右键 → 打开）
2. 或菜单：**开始 → 新建 → 场景**

### iObjectsPy 操作三维场景

```python
import iobjectspy as spy
from iobjectspy import Workspace, WorkspaceConnectionInfo

# 初始化
spy.set_iobjects_java_path(r"D:\software\supermap-idesktopx-2025-windows-x64-bin\bin")

ws = Workspace()
conn = WorkspaceConnectionInfo()
conn.server = r"D:\data\MyProject.smwu"
ws.open(conn)

# 获取已有场景
scene = spy.get_scene(ws, "MyScene")

# 新建场景
scene = spy.add_scene(ws, "NewScene3D")
```

---

## 三、地形与影像图层

```python
# 添加 DEM 地形图层
ds = spy.open_datasource(r"D:\data\terrain.udb")
dem_dataset = ds["DEM"]
terrain_layer = scene.terrain_layers.add(dem_dataset)
terrain_layer.transparency = 0          # 透明度 0-100

# 添加 DOM 影像图层（贴附于地形）
dom_dataset = ds["DOM"]
image_layer = scene.image_layers.add(dom_dataset)

# 设置图层顺序（地形在底部）
scene.terrain_layers.move_to(terrain_layer, 0)
```

---

## 四、倾斜摄影数据处理

### GUI 操作步骤

1. **导入 OSGB**：数据 → 数据导入 → 三维 → 倾斜摄影（OSGB）
2. **生成 S3M 缓存**：三维 → 场景缓存 → 生成S3M缓存
3. **添加到场景**：直接将 S3M 文件拖入场景窗口

### iObjectsPy 操作

```python
# 导入 OSGB 数据
spy.import_osgb(
    source_path=r"D:\data\osgb_tileset",   # OSGB 文件夹（含 metadata.xml）
    out_datasource=ds,
    out_dataset="OSGB_Model"
)

# 添加倾斜摄影到三维场景
osgb_layer = scene.general_layers.add_osgb(r"D:\data\osgb_tileset\metadata.xml")
osgb_layer.name = "倾斜摄影模型"

# 添加 S3M 缓存
s3m_layer = scene.general_layers.add_s3m(r"D:\data\model.s3m")
```

---

## 五、点云数据处理

### GUI 操作步骤

1. **导入点云**：数据 → 数据导入 → 点云（LAS/LAZ）
2. **显示点云**：添加点云数据集到三维场景图层
3. **点云分析**：三维 → 点云 → 地面点提取/建筑物提取等

### iObjectsPy 操作

```python
# 导入 LAS 点云
spy.import_las(
    source_file=r"D:\data\lidar.las",
    out_datasource=ds,
    out_dataset="PointCloud"
)

# 获取点云数据集
pc_dataset = ds["PointCloud"]   # DatasetPointCloud

# 转为 numpy 数组（获取 XYZ 坐标和属性）
arr = spy.datasetraster_to_numpy_array(pc_dataset)

# 添加点云到三维场景
pc_layer = scene.general_layers.add(pc_dataset)
pc_layer.point_size = 2    # 点显示大小
```

---

## 六、BIM 数据处理

### GUI 操作步骤

1. **导入 IFC**：数据 → 数据导入 → BIM → IFC格式
2. **坐标配准**：设置 BIM 模型的地理坐标原点
3. **属性挂接**：将 BIM 构件属性关联到三维对象

### iObjectsPy 操作

```python
# 导入 IFC 文件
spy.import_ifc(
    source_file=r"D:\data\building.ifc",
    out_datasource=ds,
    out_dataset="BIM_Building",
    coordinate_x=116.4,    # 模型原点经度
    coordinate_y=39.9,     # 模型原点纬度
    coordinate_z=0.0       # 高程
)
```

---

## 七、三维分析工具完整列表

根据 SuperMap iDesktopX 官方文档,三维空间分析包含以下 12 个核心工具:

### 7.1 坡度坡向分析

**功能**: 根据指定区域分析地形数据的坡度（倾斜程度）和坡向（倾斜方向）

**GUI 路径**: 三维 → 分析 → 坡度坡向

**iObjectsPy API**:
```python
# 计算坡度
slope_result = spy.calculate_slope(
    dem_dataset=dem_dataset,
    slope_unit="DEGREE",  # DEGREE（度）或 PERCENT（百分比）
    z_factor=1.0,          # 高程转换因子
    out_datasource=ds,
    out_dataset="Slope"
)

# 计算坡向
aspect_result = spy.calculate_aspect(
    dem_dataset=dem_dataset,
    out_datasource=ds,
    out_dataset="Aspect"
)
```

**参数说明**:
- `slope_unit`: 输出单位,DEGREE（0-90度）或 PERCENT（0-100%）
- `z_factor`: 高程单位转换因子,当 XY 和 Z 单位不同时使用

**应用场景**: 地形分析、水土流失评估、道路选址

---

### 7.2 等值线分析

**功能**: 提取高度值相等的所有相邻点连线,以线的分布表示数据表面值的变化

**GUI 路径**: 三维 → 分析 → 等值线

**iObjectsPy API**:
```python
contour_result = spy.extract_contour(
    dem_dataset=dem_dataset,
    base_value=0,           # 起始等值线值
    interval=10,             # 等距间隔
    smooth_method="BSPLINE", # 平滑方法: BSPLINE, POLYLINE
    smoothness=3,           # 平滑度
    out_datasource=ds,
    out_dataset="Contour"
)
```

**参数说明**:
- `base_value`: 起始等值线的高程值
- `interval`: 等值线间距（米）
- `smooth_method`: 平滑算法
  - `BSPLINE`: B样条平滑,更光滑但计算较慢
  - `POLYLINE`: 折线平滑,保留细节
- `smoothness`: 平滑程度,值越大越光滑

**应用场景**: 地形图制作、洪水淹没模拟、工程规划

---

### 7.3 可视域分析

**功能**: 基于一定的水平视角、垂直视角及指定范围半径,分析观察点的可见情况

**GUI 路径**: 三维 → 分析 → 可视域分析

**iObjectsPy API**:
```python
visibility_result = spy.visibility_analysis(
    scene=scene,
    observer_point=Point3D(116.4, 39.9, 100),  # 观察点（X, Y, Z）
    horizontal_angle=360,                     # 水平视角（度）,0-360
    vertical_angle=60,                         # 垂直视角（度）,0-90
    max_distance=2000,                         # 最大视距（米）
    min_distance=0,                           # 最小视距（米）
    out_datasource=ds,
    out_dataset='VisibilityResult'
)
```

**参数说明**:
- `observer_point`: 观察点坐标（场景坐标系）
- `horizontal_angle`: 水平视角范围（度）
- `vertical_angle`: 垂直视角范围（度）
- `max_distance`: 最大可视距离（米）
- `min_distance`: 最小可视距离（米）

**输出结果**:
- 可见区域（绿色）和不可见区域（红色）
- 可视区域面积、可视比例等统计信息

**应用场景**: 监控摄像头布设、观景台选址、军事侦察

---

### 7.4 通视分析

**功能**: 判断三维场景中任意两点之间的通视情况

**GUI 路径**: 三维 → 分析 → 通视分析

**iObjectsPy API**:
```python
los_result = spy.line_of_sight(
    scene=scene,
    start_point=Point3D(116.4, 39.9, 50),
    end_point=Point3D(116.5, 40.0, 50),
    out_datasource=ds,
    out_dataset="LineOfSight"
)

# 结果属性
print("是否通视:", los_result.visible)
print("障碍点坐标:", los_result.obstruction_point)
print("障碍类型:", los_result.obstacle_type)
```

**参数说明**:
- `start_point`: 起点坐标
- `end_point`: 终点坐标

**输出结果**:
- 可通视/不可通视布尔值
- 障碍点坐标（如有）
- 障碍类型（地形、建筑物等）

**应用场景**: 通信基站选址、视线走廊规划、景观视野评估

---

### 7.5 动态可视域分析

**功能**: 根据指定路线,分析沿路线行驶过程中的通视情况

**GUI 路径**: 三维 → 分析 → 动态可视域

**iObjectsPy API**:
```python
# 先定义路线（三维线）
path_line = GeoLine.make([(116.4, 39.9, 100), (116.5, 40.0, 100), ...])

dynamic_vis = spy.dynamic_visibility_analysis(
    scene=scene,
    path=path_line,
    horizontal_angle=360,
    vertical_angle=60,
    max_distance=2000,
    sample_interval=100,  # 沿路采样间隔（米）
    out_datasource=ds,
    out_dataset_prefix="DynVis_"
)
```

**参数说明**:
- `path`: 三维路径（GeoLine3D）
- `sample_interval`: 沿路采样间隔（米）

**应用场景**: 无人机巡航路径规划、高速公路监控评估、飞行航线分析

---

### 7.6 开敞度分析

**功能**: 构造视域半球体,分析观测点周围空间的视域范围

**GUI 路径**: 三维 → 分析 → 开敞度

**iObjectsPy API**:
```python
openness_result = spy.openness_analysis(
    scene=scene,
    observer_point=Point3D(116.4, 39.9, 100),
    radius=500,           # 观测半径（米）
    sample_count=360,     # 采样点数量
    out_datasource=ds,
    out_dataset="Openness"
)
```

**参数说明**:
- `radius`: 视域半球体半径（米）
- `sample_count`: 半球体表面采样点数量

**应用场景**: 城市天际线评估、开放空间分析、建筑密度评估

---

### 7.7 日照分析

**功能**: 计算指定区域在某段时间内的日照时长和阴影范围

**GUI 路径**: 三维 → 分析 → 日照分析

**iObjectsPy API**:
```python
sunlight_result = spy.sunlight_analysis(
    scene=scene,
    buildings=building_region3d,  # 建筑物三维面数据集
    latitude=39.9,                # 纬度
    longitude=116.4,              # 经度
    timezone=8,                   # 时区（东八区）
    analysis_date="2025-06-21",  # 分析日期（夏至）
    start_time="8:00",            # 开始时间
    end_time="18:00",             # 结束时间
    time_interval=30,             # 时间步长（分钟）
    out_datasource=ds,
    out_dataset="SunlightResult"
)
```

**参数说明**:
- `latitude/longitude`: 分析区域地理坐标
- `timezone`: 时区偏移（小时）
- `analysis_date`: 分析日期（影响太阳高度角）

**输出结果**:
- 各建筑物日照时长分布图
- 阴影范围动态展示
- 日照不足区域标注

**应用场景**: 城市规划、建筑设计、绿色建筑认证

---

### 7.8 淹没分析

**功能**: 动态模拟水位由最小高程涨到最大高程的淹没过程

**GUI 路径**: 三维 → 分析 → 淹没分析

**iObjectsPy API**:
```python
flood_result = spy.flood_analysis(
    dem=dem_dataset,
    water_levels=[10, 20, 30, 50],  # 水位高程列表（米）
    min_water_level=5,              # 最低水位
    max_water_level=50,             # 最高水位
    rise_speed=1.0,                 # 淹没速度（米/秒）
    region=study_area,              # 分析区域（可选）
    out_datasource=ds,
    out_dataset_prefix="Flood_"
)
```

**参数说明**:
- `water_levels`: 关键水位点列表
- `min_water_level`: 最低淹没水位
- `max_water_level`: 最高淹没水位
- `rise_speed`: 淹没速度（影响动态模拟）

**输出结果**:
- 各水位淹没范围图层
- 淹没面积、体积统计
- 动态淹没过程视频

**应用场景**: 防洪减灾、水库调度、气候变化研究

---

### 7.9 剖面分析

**功能**: 生成剖面线与地形或模型的轮廓线

**GUI 路径**: 三维 → 分析 → 剖面分析

**iObjectsPy API**:
```python
# 地形剖面
terrain_profile = spy.terrain_profile(
    scene=scene,
    profile_line=line_geom,         # 剖面线（GeoLine）
    sample_interval=10,             # 采样间隔（米）
    out_datasource=ds,
    out_dataset="TerrainProfile"
)

# 输出属性
print("距离列表:", terrain_profile.distances)  # 沿线距离（米）
print("高程列表:", terrain_profile.elevations) # 对应高程（米）

# 模型剖面（建筑物、管线等）
model_profile = spy.model_profile(
    scene=scene,
    profile_line=line_geom,
    target_layers=["Buildings", "Pipes"],
    out_datasource=ds,
    out_dataset="ModelProfile"
)
```

**参数说明**:
- `profile_line`: 剖面线（GeoLine/GeoLine3D）
- `sample_interval`: 采样间隔（米）
- `target_layers`: 目标图层列表（模型剖面）

**输出结果**:
- 剖面图（高程-距离曲线）
- 剖面线上的特征点坐标

**应用场景**: 道路选线设计、管线布局分析、地质剖面分析

---

### 7.10 视频投放

**功能**: 将视频投放到模型表面或地形表面播放

**GUI 路径**: 三维 → 分析 → 视频投放

**iObjectsPy API**:
```python
video_projection = spy.project_video(
    scene=scene,
    video_path=r"D:\data\simulation.avi",  # AVI 格式视频
    target_layer="Building_Model",          # 目标图层
    projection_area=polygon,                # 投影区域（GeoPolygon）
    loop=True,                             # 循环播放
    transparency=0.5,                      # 透明度 0-1
    scale_mode="FIT"                       # 缩放模式: FIT, STRETCH, TILE
)
```

**参数说明**:
- `video_path`: 视频文件路径（仅支持 AVI）
- `target_layer`: 目标三维图层
- `projection_area`: 投影区域范围
- `scale_mode`: 缩放模式
  - `FIT`: 适应区域（保持比例）
  - `STRETCH`: 拉伸填充
  - `TILE`: 平铺填充

**应用场景**: 模拟灯光秀、虚拟广告牌、应急演练

---

### 7.11 天际线分析

**功能**: 根据观察点生成场景中建筑物顶端边缘与天空的分离线

**GUI 路径**: 三维 → 分析 → 天际线

**iObjectsPy API**:
```python
skyline_result = spy.skyline_analysis(
    scene=scene,
    observer_point=Point3D(116.4, 39.9, 100),
    view_direction=0,       # 视线方向（度）
    view_angle=360,         # 视野角度（度）
    out_datasource=ds,
    out_dataset="Skyline"
)

# 输出天际线三维线
skyline_3d = skyline_result.skyline_3d
```

**参数说明**:
- `observer_point`: 观察点坐标
- `view_direction`: 视线方向（度,0=正北）
- `view_angle`: 视野角度（度）

**输出结果**:
- 天际线三维线（GeoLine3D）
- 天际线轮廓矢量面

**应用场景**: 城市天际线控制、景观规划、建筑高度限制

---

### 7.12 填挖方分析

**功能**: 计算指定范围内的填挖方体积及面积

**GUI 路径**: 三维 → 分析 → 填挖方

**iObjectsPy API**:
```python
cut_fill_result = spy.cut_fill_analysis(
    original_dem=dem_before,        # 施工前 DEM
    modified_dem=dem_after,         # 施工后 DEM（或目标高程）
    region=project_boundary,       # 分析区域（可选）
    base_height=None,               # 目标平整高程（可选）
    out_datasource=ds
)

# 输出结果
print("挖方体积:", cut_fill_result.cut_volume, "立方米")
print("填方体积:", cut_fill_result.fill_volume, "立方米")
print("挖方面积:", cut_fill_result.cut_area, "平方米")
print("填方面积:", cut_fill_result.fill_area, "平方米")
```

**参数说明**:
- `original_dem`: 原始地形 DEM
- `modified_dem`: 设计后 DEM 或 `base_height`
- `base_height`: 目标平整高程（填挖统一目标）

**应用场景**: 场地平整、土方计算、工程造价

---

---

## 八、模型出图功能

SuperMap iDesktopX 支持将三维场景导出为标准数据格式,用于后续分析或展示。

### 8.1 生成 DSM 数据

**功能**: 将场景数据生成为数字表面模型（DSM）

**iObjectsPy API**:
```python
dsm_result = spy.generate_dsm(
    scene=scene,
    output_path=r"D:\output\dsm.tif",
    resolution=0.5,          # 输出分辨率（米）
    region=study_area,      # 输出区域（可选）
    out_datasource=ds,
    out_dataset="DSM"
)
```

### 8.2 生成 DOM 数据

**功能**: 将场景数据生成为数字正射影像（DOM）

**iObjectsPy API**:
```python
dom_result = spy.generate_dom(
    scene=scene,
    output_path=r"D:\output\dom.tif",
    resolution=0.5,
    region=study_area,
    out_datasource=ds,
    out_dataset="DOM"
)
```

### 8.3 生成 2.5 维地图

**功能**: 将三维场景输出为 2.5D 地图（倾斜投影）

**iObjectsPy API**:
```python
map_25d = spy.generate_25d_map(
    scene=scene,
    output_path=r"D:\output\map_25d.udb",
    view_angle=45,          # 倾斜角度（度）
    direction=0,            # 视线方向（度）
    exaggeration=1.5        # 高程夸张倍数
)
```

### 8.4 生成立面图

**功能**: 生成建筑物的立面矢量图

**iObjectsPy API**:
```python
elevation_result = spy.generate_elevation(
    scene=scene,
    buildings=building_region3d,
    view_direction=90,     # 观察方向（度）
    out_datasource=ds,
    out_dataset="Elevation"
)
```

---

## 九、三维场景缓存生成

### S3M 缓存生成

S3M（SuperMap 3D Model）是SuperMap自研的三维瓦片缓存格式，用于高效显示海量三维数据。

**GUI 操作**：三维 → 场景缓存 → 生成S3M场景缓存

```python
# 为矢量数据集生成 S3M 缓存
spy.generate_s3m_cache(
    source_dataset=building_dv,
    output_path=r"D:\cache\buildings",
    lod_levels=5,              # LOD 层级数
    tile_size=128              # 每个瓦片大小（像素）
)

# 为 DEM 地形生成缓存
spy.generate_terrain_cache(
    dem_dataset=dem,
    output_path=r"D:\cache\terrain"
)
```

---

## 十、三维场景动画

### 10.1 飞行路径动画

**GUI**：三维 → 场景动画 → 飞行路径

**iObjectsPy API**:
```python
# 定义关键帧
keyframes = [
    {
        "position": (116.4, 39.9, 500),  # 相机位置 (X, Y, Z)
        "heading": 0,                   # 航向角（度）
        "tilt": 45,                      # 俯仰角（度）
        "time": 0                        # 时间（秒）
    },
    {
        "position": (116.5, 40.0, 300),
        "heading": 90,
        "tilt": 60,
        "time": 5
    },
    {
        "position": (116.6, 40.1, 200),
        "heading": 180,
        "tilt": 75,
        "time": 10
    }
]

# 创建飞行动画
animation = spy.create_flight_animation(
    scene=scene,
    keyframes=keyframes,
    loop=True,              # 循环播放
    easing="CUBIC_IN_OUT"   # 缓动函数: LINEAR, CUBIC_IN_OUT, EASE_IN_OUT
)
```

**参数说明**:
- `position`: 相机位置（场景坐标）
- `heading`: 航向角（度）,0=正北,90=正东
- `tilt`: 俯仰角（度）,0=平视,90=垂直向下
- `time`: 关键帧时间（秒）
- `easing`: 缓动函数（插值算法）

### 10.2 导出动画视频

**iObjectsPy API**:
```python
spy.export_scene_animation(
    scene=scene,
    output_path=r"D:\output\flythrough.mp4",
    width=1920,              # 视频宽度
    height=1080,             # 视频高度
    fps=30,                  # 帧率
    duration=60,             # 视频时长（秒）
    bitrate=5000,            # 比特率（kbps）
    codec="H264"            # 编码格式: H264, H265, VP9
)
```

---

## 十一、典型工作流

### 工作流 1: 城市三维可视化与监控规划

**目标**: 创建城市三维场景,分析监控摄像头最佳布设位置

**步骤**:

```python
import iobjectspy as spy
from iobjectspy import Workspace, Point3D, GeoLine

# 1. 打开工作空间和场景
ws = Workspace()
ws.open(r"D:\data\city.smwu")
scene = spy.get_scene(ws, "CityScene")

# 2. 添加地形和影像
ds = spy.open_datasource(r"D:\data\city.udb")
dem = ds["DEM"]
dom = ds["DOM"]

scene.terrain_layers.add(dem)
scene.image_layers.add(dom)

# 3. 添加倾斜摄影模型
osgb_layer = scene.general_layers.add_osgb(r"D:\data\osgb_tileset\metadata.xml")
osgb_layer.name = "城市实景"

# 4. 导入建筑物
buildings = ds["Buildings_3D"]
building_layer = scene.general_layers.add(buildings)

# 5. 可视域分析（监控规划）
monitor_points = [
    Point3D(116.4, 39.9, 100),
    Point3D(116.5, 39.9, 100),
    Point3D(116.4, 40.0, 100)
]

for i, point in enumerate(monitor_points):
    visibility = spy.visibility_analysis(
        scene=scene,
        observer_point=point,
        horizontal_angle=360,
        vertical_angle=60,
        max_distance=500,
        out_datasource=ds,
        out_dataset=f"Monitor_{i+1}_Visibility"
    )
    print(f"监控点 {i+1} 可视面积:", visibility.visible_area)

# 6. 导出场景截图
spy.export_scene_image(
    scene=scene,
    output_path=r"D:\output\city_scene.png",
    width=3840, height=2160
)
```

---

### 工作流 2: 洪水淹没模拟与影响评估

**目标**: 模拟洪水淹没过程,评估影响范围和人口

**步骤**:

```python
# 1. 准备 DEM 地形
dem = ds["DEM"]

# 2. 设置淹没水位（考虑河流水位上涨）
water_levels = [50, 60, 70, 80, 90, 100]  # 米

# 3. 执行淹没分析
flood_result = spy.flood_analysis(
    dem=dem,
    min_water_level=50,
    max_water_level=100,
    water_levels=water_levels,
    rise_speed=0.5,  # 水位上涨速度
    region=river_basin,  # 流域范围
    out_datasource=ds,
    out_dataset_prefix="Flood_"
)

# 4. 统计淹没影响
for level in water_levels:
    flood_dataset = ds[f"Flood_{level}"]
    flooded_area = flood_dataset.get_area()
    print(f"水位 {level}m 淹没面积: {flood_area:.2f} 平方公里")

# 5. 叠加分析（影响建筑物）
for level in [80, 90, 100]:  # 关键水位
    flood = ds[f"Flood_{level}"]
    buildings = ds["Buildings"]

    affected = spy.overlay(
        dataset=buildings,
        overlay_dataset=flood,
        operation="INTERSECT",
        out_datasource=ds,
        out_dataset=f"Affected_{level}"
    )
    print(f"水位 {level}m 影响建筑: {affected.get_record_count()} 栋")

# 6. 生成动态淹没视频（通过场景动画）
keyframes = [
    {"flood_level": 50, "time": 0},
    {"flood_level": 80, "time": 10},
    {"flood_level": 100, "time": 20}
]
# 创建淹没动画（简化示例）
```

---

### 工作流 3: 建筑日照分析与规划合规性检查

**目标**: 分析建筑群日照情况,检查是否符合日照标准

**步骤**:

```python
# 1. 加载建筑模型
buildings = ds["Buildings_3D"]
scene.general_layers.add(buildings)

# 2. 设置日照分析参数
# 住宅日照标准：冬至日至少 2 小时日照
analysis_date = "2025-12-22"  # 冬至
start_time = "8:00"
end_time = "16:00"
time_interval = 15  # 每15分钟采样一次

# 3. 执行日照分析
sunlight_result = spy.sunlight_analysis(
    scene=scene,
    buildings=buildings,
    latitude=39.9,
    longitude=116.4,
    timezone=8,
    analysis_date=analysis_date,
    start_time=start_time,
    end_time=end_time,
    time_interval=time_interval,
    out_datasource=ds,
    out_dataset="Sunlight_Analysis"
)

# 4. 分析日照时长分布
# 假设结果包含每栋建筑的日照时长属性
for record in sunlight_result:
    building_id = record["BuildingID"]
    sunlight_hours = record["SunlightHours"]

    if sunlight_hours < 2.0:
        print(f"警告: 建筑 {building_id} 日照不足 ({sunlight_hours:.2f}小时)")

# 5. 生成日照分布图
# 可视化不同日照时长的建筑（绿=充足,红=不足）
```

---

### 工作流 4: 场地平整与土方计算

**目标**: 计算场地平整工程的填挖方量

**步骤**:

```python
# 1. 加载原始地形
dem_before = ds["DEM_Original"]

# 2. 导入设计高程（设计后的 DEM 或目标平整高程）
dem_after = ds["DEM_Design"]

# 3. 执行填挖方分析
cut_fill = spy.cut_fill_analysis(
    original_dem=dem_before,
    modified_dem=dem_after,
    region=site_boundary,  # 场地边界
    out_datasource=ds
)

# 4. 输出土方统计
print("=" * 40)
print("土方计算结果")
print("=" * 40)
print(f"挖方体积: {cut_fill.cut_volume:,.2f} 立方米")
print(f"填方体积: {cut_fill.fill_volume:,.2f} 立方米")
print(f"挖方面积: {cut_fill.cut_area:,.2f} 平方米")
print(f"填方面积: {cut_fill.fill_area:,.2f} 平方米")

# 计算土方平衡
net_volume = cut_fill.fill_volume - cut_fill.cut_volume
if abs(net_volume) < 100:  # 允许误差范围内
    print("✓ 土方平衡")
else:
    print(f"✗ 土方不平衡,需要外运/外购 {abs(net_volume):,.2f} 立方米")

# 5. 生成填挖方分布图
# 可视化挖方区域（红色）和填方区域（蓝色）
```

---

### 工作流 5: 无人机航线规划与动态可视域分析

**目标**: 规划无人机巡航航线,分析沿途可视情况

**步骤**:

```python
# 1. 定义巡航路线（三维线）
waypoints = [
    (116.4, 39.9, 120),  # 起飞点
    (116.45, 39.9, 120),
    (116.5, 39.95, 120),
    (116.5, 40.0, 120),
    (116.45, 40.0, 120), # 返航
    (116.4, 39.9, 120)
]

flight_path = GeoLine3D.make(waypoints)

# 2. 动态可视域分析
dynamic_vis = spy.dynamic_visibility_analysis(
    scene=scene,
    path=flight_path,
    horizontal_angle=360,
    vertical_angle=60,
    max_distance=1000,
    sample_interval=100,  # 每100米采样一次
    out_datasource=ds,
    out_dataset_prefix="Drone_"
)

# 3. 导出航线为 KML（用于无人机飞控）
spy.export_to_kml(
    dataset=flight_path,
    output_path=r"D:\output\flight_path.kml"
)

# 4. 生成飞行动画（预览）
keyframes = [
    {"position": wp, "heading": 0, "tilt": 30, "time": i * 2}
    for i, wp in enumerate(waypoints)
]

spy.create_flight_animation(scene, keyframes, loop=True)

# 5. 导出动画视频
spy.export_scene_animation(
    scene=scene,
    output_path=r"D:\output\drone_flight.mp4",
    width=1920, height=1080,
    fps=30,
    duration=len(waypoints) * 2
)
```

---

## 十二、MCP 工具补充建议

为了方便调用三维分析功能,建议补充以下 MCP 工具:

| 工具名称 | 功能描述 | 参数 |
|---------|---------|------|
| `visibility_analysis_3d` | 可视域分析 | observer_point, horizontal_angle, vertical_angle, max_distance |
| `line_of_sight` | 通视分析 | start_point, end_point |
| `dynamic_visibility` | 动态可视域 | path, horizontal_angle, vertical_angle, max_distance, sample_interval |
| `sunlight_analysis` | 日照分析 | latitude, longitude, date, start_time, end_time |
| `flood_analysis` | 淹没分析 | water_levels, min_level, max_level, rise_speed |
| `terrain_profile` | 地形剖面 | profile_line, sample_interval |
| `cut_fill_analysis` | 填挖方分析 | original_dem, modified_dem, region |
| `skyline_analysis` | 天际线分析 | observer_point, view_direction, view_angle |
| `calculate_slope` | 坡度分析 | dem, slope_unit, z_factor |
| `extract_contour` | 等值线分析 | dem, base_value, interval, smooth_method |
| `generate_s3m_cache` | 生成 S3M 缓存 | source_dataset, output_path, lod_levels |
| `open_scene` | 打开三维场景 | scene_name |
| `add_scene_layer` | 添加图层到场景 | scene_name, layer_type, dataset |

---

## 十三、三维发布

### 发布为 iServer 三维服务

1. iDesktopX 菜单：**开始 → 发布 → 发布iServer服务**
2. 选择场景，配置 iServer 地址和端口
3. 发布后通过 iServer REST API 或 SuperMap iClient 访问

---

## 参考资料

- 帮助手册（三维）：https://help.supermap.com/iDesktopX/zh/
- iObjectsPy 三维模块：`iobjectspy.threeddesigner`
- S3M 格式规范：https://www.ogc.org/standards/s3m
